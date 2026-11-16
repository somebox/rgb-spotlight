"""Fit checks for round 7 (round7.py): the yoke pivot and cap screws as real parts.

ROT=45 uv run --python 3.12 --with cadquery python check7.py OUTDIR

1. Every part and fastener against every other, doors standing, closed as far as a pair goes, and folded back.
2. The tilt in the yoke: the lamp, its nuts and screws turned about the pivot against the yoke, knobs and washers.
3. What sits inside the cap: how close each nut, stud and screw comes to the driver board and its parts.
4. The press nuts' distance to the cap rims' edge, against PEM's minimum.
Needs the boards' STEPs in ../out (driver.step, led.step), exported centred on the board:
kicad-cli pcb export step --subst-models --no-dnp --user-origin 150x100mm -o ../out/driver.step boards/driver/driver.kicad_pcb
"""
import itertools
import json
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out/r7"
sys.argv = sys.argv[:1] + ["/dev/null"]
from cadquery import Vector as V  # noqa: E402

import round7 as R  # noqa: E402
import sheet as S  # noqa: E402

# parts that touch by design: the stack's tie rods, the LED screws in the plate, the doors' corner standoffs
EXPECTED = {("plate", "steel"), ("nylon", "steel"), ("plate", "screw"), ("corner", "plate")}
FIXED = ("yoke", "knob", "washer", "washer_pa")        # stay with the yoke when the lamp tilts


def overlaps(items, only=None, tol=0.05):
    out = []
    for (na, a), (nb, b) in itertools.combinations(items, 2):
        if only and na not in only and nb not in only:
            continue
        if only and na in only and nb in only:
            continue
        if tuple(sorted((na, nb))) in EXPECTED:
            continue
        ba, bb = a.BoundingBox(), b.BoundingBox()
        if ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin or ba.zmax < bb.zmin or bb.zmax < ba.zmin:
            continue
        v = a.intersect(b).Volume()
        if v > tol:
            out.append((na, nb, round(v, 2)))
    return out


P = R.build()
HW = R.hardware()
res = {"rot": R.R6.ROT}
print(f"=== round 7: pivot M4 (Elesa VC.692/25 p-M4x10, PEM S-M4-2), cap rims to z {R.CAP_FRONT} ===")
for dd in ((90, 90), (32, 90), (180, 180)):
    o = overlaps(R.lamp(P, *dd) + HW)
    print(f"1. assembled, doors {dd}, boards and hardware in:", o or "no overlaps")
    res[f"overlaps {dd}"] = o

fixed = [("yoke", P["yoke"])] + [h for h in HW if h[0] in FIXED]
res["tilt"] = {}
for dd in ((90, 90), (180, 180)):
    lampi = R.lamp(P, *dd, with_yoke=False) + [h for h in HW if h[0] in ("led", "steel", "pin", "screw", "nut", "m3")]
    bad = [phi for phi in range(-90, 91, 5)
           if overlaps([(n, s.rotate(V(0, 0, S.Z_NUT), V(1, 0, S.Z_NUT), phi)) for n, s in lampi] + fixed, only=FIXED)]
    print(f"2. tilt, doors {dd}: clashes at {bad or 'none'}"); res["tilt"][str(dd)] = bad

drv = next(s for n, s in HW if n == "drv")
board = max(drv.Solids(), key=lambda so: so.BoundingBox().xlen)
inside = [(n, s) for n, s in HW if n in ("nut", "m3")] + [(n, s) for n, s in HW if n == "knob"]
cl = {}
for n, s in inside:
    side = "right" if s.BoundingBox().center.x > 1 else "left" if s.BoundingBox().center.x < -1 else \
        "top" if s.BoundingBox().center.y > 0 else "bottom"
    cl[f"{n} {side} to the driver board"] = round(s.distance(board), 2)
    cl[f"{n} {side} to the driver's parts"] = round(min(s.distance(so) for so in drv.Solids() if so.BoundingBox().xlen < 40), 2)
for k, v in cl.items():
    print(f"3. {k:40s} {v:6.2f} mm")
res["clear"] = cl

edge = round(R.CAP_FRONT - S.Z_NUT, 2)
bend = round(S.Z_NUT - (S.ZB + S.RIN[S.SH_T] + S.SH_T), 2)
for k, m in R.EDGE_MIN.items():
    print(f"4. {k} nut hole centre to the rim's front edge {edge} mm (PEM minimum {m}): {'ok' if edge >= m else 'TOO CLOSE'}")
print(f"4. nut hole centre to the start of the rim's bend {bend} mm; M4 head radius {R.NUT_M4['head_d'] / 2:.2f}")
res["edge"] = {"to front edge": edge, "to bend": bend, "minimum": R.EDGE_MIN}
os.makedirs(OUT, exist_ok=True)
json.dump(res, open(os.path.join(OUT, f"check7-rot{R.R6.ROT:g}.json"), "w"), indent=1)
