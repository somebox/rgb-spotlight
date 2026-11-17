"""Light leaks: which straight rays from the LEDs and the LED board get out of the lamp without going through a lens.

uv run --python 3.12 --with cadquery --with trimesh --with embreex python leaks.py OUTDIR

Two kinds of source, both inside the lamp, doors open 90/90 so the doors hide nothing:
  dies   direct light: the three LED dies, cosine-weighted over the upper hemisphere (their own domes see-through)
  board  scattered light: points on the LED board's top on a 0.5 mm grid, cosine-weighted (a diffuse white board)
A ray that reaches a lens first counts as optics, one that hits any other part is stopped, and one that hits nothing
leaves the lamp. By reciprocity, a board ray that leaves is a line of sight from outside onto the board: where the
PCB shows through a crack. Only straight paths: light that bounces off black parts on its way out is not counted.
A third source, spill, starts on the lenses' exit faces and glows evenly in every direction (a worst case: the real
beam is about +-15 deg): it shows how much light gets out sideways past the standing doors, at their feet or between
them at the corners, instead of through the front opening.
Writes leaks-r1.json .. leaks-r5.json (r5: round5.py at LEN, WID, CUT) with the totals, where the rays leave, and a sample of rays for the viewer.
"""
import json
import math
import os
import sys

OUT = sys.argv[1]
sys.argv = sys.argv[:1] + ["/dev/null"]
import numpy as np  # noqa: E402
import trimesh  # noqa: E402

import round2 as R2  # noqa: E402
import round3 as R3  # noqa: E402
import round4 as R4  # noqa: E402
import round5 as R5  # noqa: E402
import round6 as R6  # noqa: E402
import sheet as S  # noqa: E402

DOORS = tuple(float(a) for a in os.environ.get("DOORS", "90,90").split(","))
N_DIR_BOARD, N_DIR_DIE, N_DIR_SPILL = 96, 20000, 64
rng = np.random.default_rng(1)


def mesh_of(shapes, tol=0.03):
    vs, fs, n = [], [], 0
    for s in shapes:
        verts, tris = s.tessellate(tol, 0.15)
        vs.append(np.array([(v.x, v.y, v.z) for v in verts]))
        fs.append(np.array(tris) + n)
        n += len(verts)
    return np.vstack(vs), np.vstack(fs)


def hemisphere(n):
    """Cosine-weighted directions about +z."""
    u, v = rng.random(n), rng.random(n)
    r, phi = np.sqrt(u), 2 * math.pi * v
    return np.stack([r * np.cos(phi), r * np.sin(phi), np.sqrt(1 - u)], axis=1)


def split_led(step_solid):
    solids = step_solid.Solids()
    board = max(solids, key=lambda s: s.BoundingBox().xlen * s.BoundingBox().ylen)
    return board, [s for s in solids if s is not board]


def scene(rnd):
    if rnd == "r1":
        P = S.build(); items = S.lamp(P, *DOORS, with_yoke=True); hw = S.hardware()
    elif rnd == "r2":
        P = R2.build(); items = R2.lamp(P, *DOORS, with_yoke=True); hw = R2.hardware()
    elif rnd == "r3":
        P = R3.build(); items = R3.lamp(P, *DOORS, with_yoke=True); hw = R3.hardware()
    elif rnd == "r4":
        P = R4.build(); items = R4.lamp(P, *DOORS, with_yoke=True); hw = R4.hardware()
    elif rnd == "r5":
        P = R5.build(); items = R5.lamp(P, *DOORS, with_yoke=True); hw = R5.hardware()
    else:
        P = R6.build(); items = R6.lamp(P, *DOORS, with_yoke=True); hw = R6.hardware()
    lenses = [s for n, s in hw if n == "lens"]
    led = [s for n, s in hw if n == "led"][0]
    board, parts = split_led(led)
    opaque = [s for n, s in items] + [s for n, s in hw if n not in ("lens", "led", "knob")] + [board]
    return opaque, lenses, board, parts


def exit_kind(o, d, zfront):
    """Where a ray leaves the box |x|, |y| <= 38, z in [-75, zfront + 12]."""
    lo, hi = np.array([-38.0, -38.0, -75.0]), np.array([38.0, 38.0, zfront + 12.0])
    with np.errstate(divide="ignore", invalid="ignore"):
        t1, t2 = (lo - o) / d, (hi - o) / d
    tmax = np.minimum(np.where(np.isnan(t1), np.inf, np.maximum(t1, t2)), np.inf)
    t = np.min(np.where(tmax > 0, tmax, np.inf), axis=1)
    p = o + d * t[:, None]
    kind = np.where(p[:, 2] >= hi[2] - 1e-6, "front", np.where(p[:, 2] <= lo[2] + 1e-6, "back", "side"))
    return kind, p


def run(rnd):
    opaque, lenses, board, led_parts = scene(rnd)
    vo, fo = mesh_of(opaque)
    vl, fl = mesh_of(lenses)
    vp, fp = mesh_of(led_parts)
    zfront = S.F if rnd == "r1" else R2.HF
    full = trimesh.Trimesh(np.vstack([vo, vl, vp]), np.vstack([fo, fl + len(vo), fp + len(vo) + len(vl)]), process=False)
    bare = trimesh.Trimesh(np.vstack([vo, vl]), np.vstack([fo, fl + len(vo)]), process=False)   # for the dies
    n_o, n_l = len(fo), len(fl)

    def kind_of(tri):
        return np.where(tri < 0, 2, np.where(tri < n_o, 0, np.where(tri < n_o + n_l, 1, 0)))  # 0 stop, 1 lens, 2 out

    top = board.BoundingBox().zmax
    out = {"round": rnd, "doors": DOORS, "sources": {}}
    sample = []
    # board points
    g = np.arange(-24.75, 25.0, 0.5)
    X, Y = np.meshgrid(g, g)
    pts = np.stack([X.ravel(), Y.ravel()], axis=1)
    r = np.hypot(pts[:, 0], pts[:, 1])
    keep = (r < 24.8) & (r > 3.4)
    for x, y in (R6.LEDS6 if rnd == "r6" else S.LEDS).values():
        keep &= ~((np.abs(pts[:, 0] - x) < 1.8) & (np.abs(pts[:, 1] - y) < 1.8))
    for a in (R6.ANG6 if rnd == "r6" else ANG19):
        hx, hy = 19 * math.cos(math.radians(a)), 19 * math.sin(math.radians(a))
        keep &= np.hypot(pts[:, 0] - hx, pts[:, 1] - hy) > 1.8
    pts = pts[keep]
    o = np.repeat(np.column_stack([pts, np.full(len(pts), top + 0.02)]), N_DIR_BOARD, axis=0)
    d = np.vstack([hemisphere(N_DIR_BOARD) for _ in range(len(pts))])
    tri = full.ray.intersects_first(o, d)
    k = kind_of(tri)
    esc = k == 2
    kinds, pexit = exit_kind(o[esc], d[esc], zfront)
    rr = np.hypot(o[esc][:, 0], o[esc][:, 1])
    by_r = {f"{a}-{b}": int(((rr >= a) & (rr < b)).sum()) for a, b in ((0, 20), (20, 24), (24, 25))}
    out["sources"]["board"] = {"points": int(len(pts)), "rays": int(len(o)), "lens": round(float((k == 1).mean()), 5),
                               "out": round(float(esc.mean()), 6), "out_rays": int(esc.sum()),
                               "exit": {kk: int((kinds == kk).sum()) for kk in ("front", "side", "back")},
                               "by_source_r": by_r,
                               "visible_board_area_mm2": round(float(len(np.unique(np.nonzero(esc)[0] // N_DIR_BOARD)) * 0.25), 2)}
    vis = np.unique(np.nonzero(esc)[0] // N_DIR_BOARD)
    cnt = np.bincount(np.nonzero(esc)[0] // N_DIR_BOARD, minlength=len(pts))
    out["sources"]["board"]["visible_pts"] = [[round(float(pts[i, 0]), 2), round(float(pts[i, 1]), 2), int(cnt[i])] for i in vis]
    out["sources"]["board"]["all_pts"] = int(len(pts))
    idx = np.nonzero(esc)[0]
    for i in rng.choice(idx, size=min(400, len(idx)), replace=False) if len(idx) else []:
        _, pe = exit_kind(o[i:i + 1], d[i:i + 1], zfront)
        sample.append({"src": "board", "o": [round(float(c), 2) for c in o[i]], "e": [round(float(c), 1) for c in pe[0]]})
    # dies
    die_out = {}
    for c, (x, y) in (R6.LEDS6 if rnd == "r6" else S.LEDS).items():
        o = np.tile([x, y, top + 0.75], (N_DIR_DIE, 1))
        d = hemisphere(N_DIR_DIE)
        tri = bare.ray.intersects_first(o, d)                # the die sees through its own dome
        k = kind_of(tri)
        esc = k == 2
        kinds, pexit = exit_kind(o[esc], d[esc], zfront) if esc.any() else (np.array([]), None)
        die_out[c] = {"lens": round(float((k == 1).mean()), 4), "out": round(float(esc.mean()), 6),
                      "exit": {kk: int((kinds == kk).sum()) for kk in ("front", "side", "back")}}
        idx = np.nonzero(esc)[0]
        for i in rng.choice(idx, size=min(60, len(idx)), replace=False) if len(idx) else []:
            sample.append({"src": "die", "o": [round(float(v), 2) for v in o[i]], "e": [round(float(v), 1) for v in pexit[list(idx).index(i)]]})
    out["sources"]["dies"] = die_out
    # spill: the lens exit faces, Lambertian, against everything opaque
    opq = trimesh.Trimesh(vo, fo, process=False)
    g = np.arange(-8.5, 8.6, 0.5)
    X, Y = np.meshgrid(g, g)
    disk = np.stack([X.ravel(), Y.ravel()], axis=1)
    disk = disk[np.hypot(disk[:, 0], disk[:, 1]) <= 8.5]
    src = np.vstack([disk + np.array([x, y]) for x, y in (R6.LEDS6 if rnd == "r6" else S.LEDS).values()])
    o = np.repeat(np.column_stack([src, np.full(len(src), S.Z_RET + 0.02)]), N_DIR_SPILL, axis=0)
    d = np.vstack([hemisphere(N_DIR_SPILL) for _ in range(len(src))])
    tri = opq.ray.intersects_first(o, d)
    esc = tri < 0
    lo, hi = np.array([-40.0, -40.0, -75.0]), np.array([40.0, 40.0, 62.0])
    oe, de = o[esc], d[esc]
    with np.errstate(divide="ignore", invalid="ignore"):
        t1, t2 = (lo - oe) / de, (hi - oe) / de
    tm = np.where(np.isnan(t1), np.inf, np.maximum(t1, t2))
    t = np.min(np.where(tm > 0, tm, np.inf), axis=1)
    pe = oe + de * t[:, None]
    zrel = pe[:, 2] - zfront
    side = pe[:, 2] < hi[2] - 1e-6
    corner = np.minimum(np.abs(pe[:, 0]), np.abs(pe[:, 1])) > 26.0
    n = len(o)
    out["sources"]["spill"] = {
        "rays": int(n), "front": round(float((~side).sum() / n), 5), "side": round(float(side.sum() / n), 5),
        "side_low": round(float((side & (zrel < 8)).sum() / n), 5),
        "side_low_mid": round(float((side & (zrel < 8) & ~corner).sum() / n), 5),
        "side_low_corner": round(float((side & (zrel < 8) & corner).sum() / n), 5),
        "side_high": round(float((side & (zrel >= 8)).sum() / n), 5),
        "stopped": round(float((~esc).mean()), 5)}
    low = np.nonzero(side & (zrel < 8))[0]
    for i in rng.choice(low, size=min(300, len(low)), replace=False) if len(low) else []:
        sample.append({"src": "spill", "o": [round(float(c), 2) for c in oe[i]], "e": [round(float(c), 1) for c in pe[i]]})
    out["sample"] = sample
    return out


ANG19 = S.ANG
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for rnd in os.environ.get("ROUNDS", "r1 r2").split():
        res = run(rnd)
        tag = os.environ.get("TAG", "")
        json.dump(res, open(os.path.join(OUT, f"leaks-{rnd}{tag}.json"), "w"))
        b = res["sources"]["board"]
        print(f"{rnd}: board rays {b['rays']}: to a lens {b['lens']:.3f}, out of the lamp {b['out']:.5f} ({b['out_rays']} rays) "
              f"exits {b['exit']} by source r {b['by_source_r']}; board visible from outside: {b['visible_board_area_mm2']} mm2")
        for c, v in res["sources"]["dies"].items():
            print(f"     die {c}: to its lens {v['lens']:.3f}, out without a lens {v['out']:.5f} exits {v['exit']}")
        print(f"     spill from the lens faces: {res['sources']['spill']}")
