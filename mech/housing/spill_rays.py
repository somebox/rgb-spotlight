"""Rays for the review page's live light numbers (round 5), and the same rays traced against the CAD doors to check them.

uv run --python 3.12 --with cadquery --with trimesh --with embreex python spill_rays.py OUTDIR [GEOM:TOP,SIDE ...]
SCENE=r6 NAME=spill6 ... : the same for round 6, its lenses and hood windows turned (round6.py, ROT)

The source is leaks.py's spill source: the lenses' exit faces on a 0.5 mm grid, glowing evenly (Lambertian), 64
directions a point, here with its own seed. The rays are traced once against everything in the lamp except the doors;
the ones that get out and would count (out the sides: leaving the box |x|, |y| <= 40 below z 62, as leaks.py; or more
than 45 deg off the axis) are written for the page, which needs only to test them against its own doors.
spill5.bin: the source points (Int16 x, y at 0.01 mm), then per ray Uint16 point, Int16 x3 direction (/32767),
Uint8 flags (1 sides, 2 past 45 deg), Uint8 0.
With GEOM:TOP,SIDE arguments (GEOM r4, or r5 with LEN/WID/CUT set), the written rays are also traced against that
round's CAD doors at those angles: spill5-check.json, for comparing with the page's numbers.
"""
import json
import math
import os
import struct
import sys

OUT = sys.argv[1]
CASES = sys.argv[2:]
sys.argv = sys.argv[:1] + ["/dev/null"]
import numpy as np  # noqa: E402
import trimesh  # noqa: E402

import round4 as R4  # noqa: E402
import round5 as R5  # noqa: E402
import round6 as R6  # noqa: E402
import sheet as S  # noqa: E402
from leaks import mesh_of, split_led  # noqa: E402

N_DIR = 64
rng = np.random.default_rng(5)
os.makedirs(OUT, exist_ok=True)

SCENE, NAME = os.environ.get("SCENE", "r4"), os.environ.get("NAME", "spill5")
P4 = R4.build()
if SCENE == "r6":
    P6 = R6.build()
    items = [s for n, s in R6.lamp(P6, 90, 90, with_yoke=True) if n != "door"]
    hw = R6.hardware()
    LEDS = R6.LEDS6
else:
    items = [s for n, s in R4.lamp(P4, 90, 90, with_yoke=True) if n != "door"]
    hw = R4.hardware()
    LEDS = S.LEDS
board, _ = split_led([s for n, s in hw if n == "led"][0])
opaque = items + [s for n, s in hw if n not in ("lens", "led", "knob")] + [board]
vo, fo = mesh_of(opaque)
static = trimesh.Trimesh(vo, fo, process=False)

g = np.arange(-8.5, 8.6, 0.5)
X, Y = np.meshgrid(g, g)
disk = np.stack([X.ravel(), Y.ravel()], axis=1)
disk = disk[np.hypot(disk[:, 0], disk[:, 1]) <= 8.5]
src = np.vstack([disk + np.array([x, y]) for x, y in LEDS.values()])
z0 = S.Z_RET + 0.02
u, v = rng.random((len(src), N_DIR)), rng.random((len(src), N_DIR))
r, phi = np.sqrt(u), 2 * math.pi * v
d = np.stack([r * np.cos(phi), r * np.sin(phi), np.sqrt(1 - u)], axis=2).reshape(-1, 3)
idx = np.repeat(np.arange(len(src)), N_DIR)
o = np.column_stack([src[idx], np.full(len(idx), z0)])
n = len(o)
esc = static.ray.intersects_first(o, d) < 0


def side_of(o, d):
    lo, hi = np.array([-40.0, -40.0, -75.0]), np.array([40.0, 40.0, 62.0])
    with np.errstate(divide="ignore", invalid="ignore"):
        t1, t2 = (lo - o) / d, (hi - o) / d
    tm = np.where(np.isnan(t1), np.inf, np.maximum(t1, t2))
    t = np.min(np.where(tm > 0, tm, np.inf), axis=1)
    pe = o + d * t[:, None]
    return pe[:, 2] < hi[2] - 1e-6


side = np.zeros(n, bool); side[esc] = side_of(o[esc], d[esc])
wide = esc & (d[:, 2] < math.cos(math.radians(45)))
keep = side | wide
k = np.nonzero(keep)[0]
q = np.round(d[k] * 32767).astype(np.int16)
flags = (side[k].astype(np.uint8) | (wide[k].astype(np.uint8) << 1))
blob = bytearray(struct.pack(f"<{2 * len(src)}h", *np.round(src * 100).astype(np.int16).ravel().tolist()))
rec = np.zeros(len(k), dtype=[("i", "<u2"), ("d", "<i2", 3), ("f", "u1"), ("pad", "u1")])
rec["i"], rec["d"], rec["f"] = idx[k], q, flags
blob += rec.tobytes()
open(os.path.join(OUT, f"{NAME}.bin"), "wb").write(blob)
meta = {"rays": int(n), "points": int(len(src)), "kept": int(len(k)), "z": z0, "dirs": N_DIR, "seed": 5,
        "no_doors": {"side": round(float(side.mean()), 5), "wide": round(float(wide.mean()), 5),
                     "stopped": round(float((~esc).mean()), 5)}}
meta["leds"] = {c: [round(x, 4), round(y, 4)] for c, (x, y) in LEDS.items()}
json.dump(meta, open(os.path.join(OUT, f"{NAME}.json"), "w"))
print(f"{n} rays, {len(k)} kept ({len(blob) / 1e3:.0f} kB); without doors: out the sides {side.mean():.4f}, "
      f"past 45 deg {wide.mean():.4f}, stopped {(~esc).mean():.4f}")

check = {}
for case in CASES:
    geom, ang = case.split(":")
    top, sd = (float(a) for a in ang.split(","))
    if geom == "r4":
        doors = [s for nm, s in R4.lamp(P4, top, sd, with_yoke=False) if nm == "door"]
    else:
        p5 = dict(P4); p5["door"] = R5.door()
        doors = [s for nm, s in R5.lamp(p5, top, sd, with_yoke=False) if nm == "door"]   # r5 and r6: the same doors
    vd, fd = mesh_of(doors)
    dm = trimesh.Trimesh(vd, fd, process=False)
    ok = dm.ray.intersects_first(o[k], d[k]) < 0
    res = {"side": round(float((ok & side[k]).sum() / n), 5), "wide": round(float((ok & wide[k]).sum() / n), 5)}
    tag = case if geom == "r4" else f"{geom}[L{R5.LEN:g},W{R5.WID:g},C{R5.CUT:g}]:{ang}"
    check[tag] = res
    print(f"   {tag}: out the sides {res['side']:.4f}, past 45 deg {res['wide']:.4f}")
if CASES:
    path = os.path.join(OUT, f"{NAME}-check.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    old.update(check)
    json.dump(old, open(path, "w"), indent=1)
