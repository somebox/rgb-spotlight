"""Fit checks for round 7 (round7.py): the yoke pivot and cap screws as real parts.

ROT=45 uv run --python 3.12 --with cadquery python check7.py OUTDIR

1. Every part and fastener against every other, doors standing, closed as far as a pair goes, and folded back.
2. The tilt in the yoke: the lamp, its nuts and screws turned about the pivot against the yoke, knobs and washers.
3. What sits inside the cap: how close each nut, stud and screw comes to the driver board and its parts.
4. The press nuts' distance to the cap rims' edge, and the back nuts' to the cable cut-outs, against PEM's minimum.
5. Room for a box on the cap's back (D31): a 64 x 64 mm block of each depth, turned with the lamp against the yoke.
6. The heat stack's fasteners (D32): thread lengths, what sticks out where, and their clearance to the driver's parts.
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

import math  # noqa: E402

import round7 as R  # noqa: E402
import sheet as S  # noqa: E402

# parts that touch by design: the stack's tie rods, the LED screws in the plate, the doors' corner standoffs
EXPECTED = {("plate", "stud"), ("plate", "screw"), ("corner", "plate")}
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
    lampi = R.lamp(P, *dd, with_yoke=False) + [h for h in HW if h[0] in ("led", "pin", "screw", "corner", "nut", "m3", "nut_back")]
    bad = [phi for phi in range(-90, 91, 5)
           if overlaps([(n, s.rotate(V(0, 0, S.Z_NUT), V(1, 0, S.Z_NUT), phi)) for n, s in lampi] + fixed, only=FIXED)]
    print(f"2. tilt, doors {dd}: clashes at {bad or 'none'}"); res["tilt"][str(dd)] = bad

drv = next(s for n, s in HW if n == "drv")
board = max(drv.Solids(), key=lambda so: so.BoundingBox().xlen)
inside = [(n, s) for n, s in HW if n in ("nut", "m3", "nut_back")] + [(n, s) for n, s in HW if n == "knob"]
cl = {}
for n, s in inside:
    c = s.BoundingBox().center
    side = f"({c.x:+.0f}, {c.y:+.0f})" if n == "nut_back" else "right" if c.x > 1 else "left" if c.x < -1 else \
        "top" if c.y > 0 else "bottom"
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


def to_cutout(x, y, cx, cy, hw=7.0, hh=7.5, r=2.0):
    """Distance from (x, y) to a rounded rectangle's outline (the cap's 14 x 15 R2 cable cut-outs)."""
    dx, dy = max(abs(x - cx) - (hw - r), 0.0), max(abs(y - cy) - (hh - r), 0.0)
    return math.hypot(dx, dy) - r


flat = S.CAP_W2 - (S.RIN[S.SH_T] + S.SH_T)          # the back face's flat ends where its bends start, 27.95
back = []
for x, y in R.BACK_NUTS:
    dc = min(to_cutout(x, y, cx, cy) for cx, cy in S.J_CUT)
    db = flat - max(abs(x), abs(y)) - R.NUT_M3["head_d"] / 2
    back.append({"at": (x, y), "to cut-out": round(dc, 2), "head to bend": round(db, 2)})
    print(f"4. back nut ({x:+.0f}, {y:+.0f}): {dc:.2f} mm to a cable cut-out (PEM minimum {R.EDGE_MIN['M3']}), "
          f"head {db:.2f} mm short of the bend: {'ok' if dc >= R.EDGE_MIN['M3'] and db > 0.5 else 'TOO CLOSE'}")
res["back nuts"] = back

res["box"] = {}
for depth in (30, 40, 50, 60):
    env = S.bx((-32, 32), (-32, 32), (S.ZB - depth, S.ZB))
    bad = [phi for phi in range(-90, 91, 5)
           if overlaps([("box", env.rotate(V(0, 0, S.Z_NUT), V(1, 0, S.Z_NUT), phi))] + fixed, only=FIXED)]
    print(f"5. a 64 x 64 box {depth} mm deep behind the cap meets the yoke at: {bad or 'no angle'}")
    res["box"][depth] = bad

parts_of = [so for so in drv.Solids() if so.BoundingBox().xlen < 40]
stud_back = R.STUD["front"] - R.STUD["L"]
fast = {
    "stud: front end below the plate's front face": S.T - R.STUD["front"],
    "stud: thread in the plate": R.STUD["front"],
    "stud: thread in the standoff, behind the nut": R.Z_NUT3 - stud_back,
    "driver screw: thread in the standoff": R.DRV_Z + R.DRV_SCREW["L"] - R.Z_STANDOFF,
    "driver screw: its tip to the stud's end": stud_back - (R.DRV_Z + R.DRV_SCREW["L"]),
    "LED screw: thread in the plate": min(S.T, R.LED_SCREW_L - (R.R2.HF - S.T)),
    "LED screw: tip behind the plate": -(R.R2.HF - R.LED_SCREW_L),
    "LED screw: tip to the first fin": (R.R2.HF - R.LED_SCREW_L) - (-(S.PITCH - S.T)),
    "shell screw: thread in the plate": min(S.T, R.SHELL_SCREW_L - S.SH_T),
    "shell screw: tip behind the plate": -(S.ZF - R.SHELL_SCREW_L),
    "driver's front face behind the stack": S.STACK_BACK - R.Z_STANDOFF,
}
for name in ("nyscrew", "nylon", "nut3"):
    label = {"nyscrew": "driver screw heads", "nylon": "standoffs", "nut3": "stack nuts"}[name]
    fast[f"{label}: nearest driver part"] = min(s.distance(so) for n, s in HW if n == name for so in parts_of)
fast["driver screw heads: to the cap's back face"] = (R.DRV_Z - R.DRV_SCREW["head"]) - (S.ZB + S.SH_T)
for k, v in fast.items():
    print(f"6. {k:48s} {v:6.2f} mm")
res["stack"] = {k: round(v, 2) for k, v in fast.items()}
os.makedirs(OUT, exist_ok=True)
json.dump(res, open(os.path.join(OUT, f"check7-rot{R.R6.ROT:g}.json"), "w"), indent=1)
