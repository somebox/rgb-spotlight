"""Fit checks for round 6 (round6.py): the optics turned ROT deg. The doors and hinge are round 5's, so only what the
turn can change is checked: every part against every other with the doors standing, closed as far as a pair goes and
folded back; how close the turned screws and windows come to the lugs; and the tilt in the yoke.

ROT=45 uv run --python 3.12 --with cadquery python check6.py OUTDIR
"""
import itertools
import json
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out/r6"
sys.argv = sys.argv[:1] + ["/dev/null"]
from cadquery import Vector as V  # noqa: E402

import round6 as R  # noqa: E402
import sheet as S  # noqa: E402

EXPECTED = {("plate", "steel"), ("nylon", "steel"), ("plate", "screw"), ("corner", "plate")}


def overlaps(items, only=None, tol=0.05):
    out = []
    for (na, a), (nb, b) in itertools.combinations(items, 2):
        if only and na not in only and nb not in only:
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
res = {"rot": R.ROT}
print(f"=== round 6, optics turned {R.ROT:g} deg ===")
for dd in ((90, 90), (32, 90), (180, 180)):
    o = overlaps(R.lamp(P, *dd) + [h for h in HW if h[0] != "knob"])
    print(f"1. assembled, doors {dd}, boards and hardware in:", o or "no overlaps")
    res[f"overlaps {dd}"] = o
yk = [("yoke", P["yoke"])]
res["tilt"] = {}
for dd in ((90, 90), (180, 180)):
    lampi = R.lamp(P, *dd, with_yoke=False) + [h for h in HW if h[0] in ("led", "steel", "pin", "screw")]
    bad = [phi for phi in range(-90, 91, 5)
           if overlaps([(n, s.rotate(V(0, 0, S.Z_NUT), V(1, 0, S.Z_NUT), phi)) for n, s in lampi] + yk, only=("yoke",))]
    print(f"2. tilt, doors {dd}: clashes at {bad or 'none'}"); res["tilt"][str(dd)] = bad
screws = [s for n, s in HW if n == "screw"]
doors90 = [s for n, s in R.lamp(P, 90, 90, with_yoke=False) if n == "door"]
doors32 = [s for n, s in R.lamp(P, 32, 90, with_yoke=False) if n == "door"]
pins = [s for n, s in HW if n == "pin"]
cl = {"LED screw heads to the nearest door, doors at 90": min(a.distance(b) for a in screws for b in doors90),
      "LED screw heads to the nearest door, top pair at 32": min(a.distance(b) for a in screws for b in doors32),
      "LED screw heads to the nearest door pin": min(a.distance(b) for a in screws for b in pins)}
for k, v in cl.items():
    print(f"3. {k:52s} {v:6.2f} mm")
res["clear"] = {k: round(v, 2) for k, v in cl.items()}
os.makedirs(OUT, exist_ok=True)
json.dump(res, open(os.path.join(OUT, f"check6-rot{R.ROT:g}.json"), "w"), indent=1)
