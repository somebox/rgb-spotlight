"""RGB Spotlight, square lamp, round 5: round 4's one door part, made longer and wider, its shape set by three numbers
(the review page's sliders). Builds on round4.py: same hood, pins, ears, foot and hinge strip.

LEN=40 WID=71 CUT=90 uv run --python 3.12 --with cadquery python round5.py OUTDIR

  LEN  hinge line to tip, mm (round 4: 31, the tip 0.5 mm short of the axis)
  WID  width at the shoulder, 8 mm from the hinge line, where the edges have stepped out past the ears (round 4: 62.5)
  CUT  the angle the edges are cut for: closed to it, neighbouring edges run parallel (90 = straight sides). From the
       shoulder each edge comes in by cos(CUT) mm per mm towards the tip. At the shoulder width round 4 had for a
       CUT, the edges meet flush at CUT; wider, they cross there and stop the doors earlier.
The tip is never narrower than 2 x W_MIN: past that point the edges run straight on.
The page builds the same outline in JavaScript (door5.js); constants() is what it reads.
"""
import json
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out5"
sys.argv = sys.argv[:1] + ["/dev/null"]
import cadquery as cq  # noqa: E402

import round3 as R3  # noqa: E402
import round4 as R4  # noqa: E402
from sheet import bx, cyl, bend, fuse, cut, RIN  # noqa: E402

LEN = float(os.environ.get("LEN", "40"))
WID = float(os.environ.get("WID", "71"))
CUT = float(os.environ.get("CUT", "90"))
P, H, D, CL, ZP, HF = R4.P, R4.H, R4.D, R4.CL, R4.ZP, R4.HF
WH, EAR_R = R4.WH, R4.EAR_R
SHOULDER, W_MIN, FILLET = R4.SHOULDER, 8.0, 3.0


def outline(length=None, width=None, cut_deg=None):
    """The plate's outline in the top door's frame, before the tip fillets: (x, y) points, right half then mirrored."""
    length = LEN if length is None else length
    width = WID if width is None else width
    cut_deg = CUT if cut_deg is None else cut_deg
    b = WH - 1.8
    c = math.cos(math.radians(cut_deg))
    w_sh = max(width / 2, b)
    half = [(b, P), (b, P - 5.0), (w_sh, P - SHOULDER)]
    w_tip = w_sh - (length - SHOULDER) * c
    if w_tip < W_MIN:
        s_k = SHOULDER + (w_sh - W_MIN) / c
        half += [(W_MIN, P - s_k), (W_MIN, P - length)]
    else:
        half.append((w_tip, P - length))
    return half + [(-x, y) for x, y in reversed(half)]


def door(rho=H - CL, pts=None):
    """Round 4's door with this outline: ears, foot and hinge strip unchanged."""
    t = 1.0; r = RIN[t]; R = r + t
    zb = ZP + D
    b = WH - R
    body = cq.Workplane("XY").workplane(offset=zb).polyline(pts or outline()).close().extrude(t)
    body = body.edges("|Z").edges("<Y").fillet(FILLET).val()
    return fuse([body, hinge_part(rho)])


def hinge_part(rho=H - CL):
    """The door without its plate: the foot along the hinge edge and the two ears. Fixed, whatever the plate's shape."""
    t = 1.0; r = RIN[t]; R = r + t
    zb = ZP + D
    b = WH - R
    s = R3.foot_length(rho, t); be = math.radians(R3.BETA)
    cy, cz = P, zb - r
    outer = [(cy + R * math.sin(be * k / 8), cz + R * math.cos(be * k / 8)) for k in range(9)]
    inner = [(cy + r * math.sin(be * k / 8), cz + r * math.cos(be * k / 8)) for k in range(8, -1, -1)]
    uy, uz = math.cos(be), -math.sin(be)
    oe = (outer[-1][0] + s * uy, outer[-1][1] + s * uz)
    ie = (inner[0][0] + s * uy, inner[0][1] + s * uz)
    prof = [(P - 0.01, zb + t)] + outer + [oe, ie] + inner + [(P - 0.01, zb)]
    xf = b - 0.5
    foot = cq.Workplane("YZ").workplane(offset=-xf).polyline(prof).close().extrude(2 * xf).val()
    adds, holes = [foot], []
    for sg in (-1, 1):
        adds.append(bend("y", P - 5.0, P, {"x": sg * b, "z": zb - r}, {"x": sg, "z": 1}, t))
        x0, x1 = sorted((sg * (b + r), sg * (b + R)))
        adds.append(bx((x0, x1), (P - 5.0, P), (ZP, zb - r)))
        adds.append(cyl("x", x0, x1, {"y": P, "z": ZP}, 2 * EAR_R))
        holes.append(cyl("x", *sorted((sg * (b - 1), sg * (b + R + 1))), {"y": P, "z": ZP}, 3.2))
    return cut(fuse(adds), holes)


def constants():
    t = 1.0; r = RIN[t]; R = r + t
    return {"P": P, "HF": HF, "ZP": ZP, "D": D, "T": t, "RIN": r, "WH": WH, "B": WH - R, "XF": WH - R - 0.5,
            "EAR_R": EAR_R, "BETA": R3.BETA, "FOOT": R3.foot_length(H - CL, t), "SHOULDER": SHOULDER,
            "W_MIN": W_MIN, "FILLET": FILLET, "Z_SRC": None}


doors = R4.doors
lamp = R4.lamp
hardware = R4.hardware


def build():
    p = R4.build()
    p["door"] = door()
    return p


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    d = door()
    tag = f"L{LEN:g}-W{WID:g}-C{CUT:g}"
    cq.exporters.export(cq.Workplane().add(d), os.path.join(OUT, f"rgb-spotlight-r5-door-{tag}.step"))
    bb = d.BoundingBox()
    print(f"door {tag}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}, valid {d.isValid()}, solids {len(d.Solids())}, "
          f"mass {d.Volume() * 2.68e-3:.1f} g; outline {[(round(x, 2), round(y, 2)) for x, y in outline()[:5]]}")
    json.dump(constants(), open(os.path.join(OUT, "door5-constants.json"), "w"), indent=1)
