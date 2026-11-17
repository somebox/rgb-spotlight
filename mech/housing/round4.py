"""RGB Spotlight, square lamp, round 4: one door part for all four doors, edges cut to meet at the seams. Builds on round3.py.

THETA_D=45 uv run --python 3.12 --with cadquery python round4.py OUTDIR

What changes from round 3:
  pins   all eight at one height, 6.3 above the face, at +-31.5 (round 3: the side pins 1.5 higher, so the closed side
         doors lay over the top ones). With no stagger, neighbouring doors can't overlap: they meet edge to edge.
  doors  one part, four times, 45 mm wide at the hinge like round 3's side doors (the lugs at each corner of the face
         have to clear each other). Past the ears each side edge steps out to the seam line and runs along it to the
         tip: the line where two neighbouring doors meet when all four are closed to THETA_D. A flat door can meet its
         neighbours at one angle only: more closed than THETA_D they would collide, more open the seams open into gaps.
         Ears, foot and pins as round 3's top door.
  hood   eight identical lugs, all folded up from cut-outs on their inner side.
Unchanged: shell, carrier, cap, yoke, stack, boards, lenses.
"""
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out4"
sys.argv = sys.argv[:1] + ["/dev/null"]
import cadquery as cq  # noqa: E402
from cadquery import Vector as V  # noqa: E402

import round2 as R2  # noqa: E402
import round3 as R3  # noqa: E402
import sheet as S  # noqa: E402
from sheet import bx, cyl, bend, fuse, cut, polar, ANG, RIN  # noqa: E402

THETA_D = float(os.environ.get("THETA_D", "60"))
HF, HB = R3.HF, R3.HB
P, H, D, CL = R3.P, R3.HT, R3.D, R3.CL          # pins at +-31.5, 6.3 above the face; plate 4.6 in front of its pin
ZP = HF + H
WH = R3.W_S                                     # 22.45: half width over the ears, as round 3's side doors
KN, EAR_R, LUG_GAP = R3.KN, R3.EAR_R, R3.LUG_GAP
SEAM_GAP = float(os.environ.get("SEAM_GAP", "0.25"))   # trimmed off the seam line; tuned so neighbours clear by about 0.3
SHOULDER = 8.0                                  # the edge reaches the seam line this far from the hinge (the ears end at 5)
TIP_Y = S.TIP


def seam(s, theta=THETA_D):
    """Half width at distance s from the hinge line where two neighbouring plates' inner faces meet, all at theta."""
    th = math.radians(theta)
    return P + D * math.sin(th) - s * math.cos(th)


def hood():
    """Round 3's hood with all eight lugs at the side doors' position and height."""
    t = R2.H_T; r = RIN[t]; R = r + t
    W = R2.H_W2; e, zc = W - R, HF - R
    side = W - t - S.GAP
    parts = [bx((-e, e), (-e, e), (HB, HF))]
    for s in (-1, 1):
        parts.append(bend("x", -e, e, {"y": s * e, "z": zc}, {"y": s, "z": 1}, t))
        parts.append(bx((-W, W), (s * (W - t), s * W), (R2.H_BACK, zc)))
        parts.append(bend("y", -e, e, {"x": s * e, "z": zc}, {"x": s, "z": 1}, t))
        parts.append(bx((s * (W - t), s * W), (-side, side), (R2.H_BACK, zc)))
    h = fuse(parts)
    tools = [cyl("z", HB - 1, HF + 1, {"x": x, "y": y}, S.RET_WIN) for x, y in S.LEDS.values()]
    tools += [cyl("z", HB - 1, HF + 1, dict(zip("xy", polar(19, a))), 3.4) for a in ANG]
    adds, holes = [], []
    L = WH + LUG_GAP + R
    flat_len = (math.pi / 2) * (r + 0.44 * t) + (ZP + KN - (HF + r))
    for a, b in (("x", "y"), ("y", "x")):
        for sa in (-1, 1):
            for sb in (-1, 1):
                b0, b1 = sorted((sb * (P - KN), sb * (P + KN)))
                tools.append(bx(**{a: (sa * L, sa * (L - flat_len - 0.6)), b: (b0 - 0.5, b1 + 0.5), "z": (HB - 1, HF + 1)}))
                for edge in (b0 - 0.5, b1):
                    tools.append(bx(**{a: (sa * L, sa * (L + 1.0)), b: (edge, edge + 0.5), "z": (HB - 1, HF + 1)}))
                adds.append(bend(b, b0, b1, {a: sa * L, "z": HF + r}, {a: -sa, "z": -1}, t))
                adds.append(bx(**{a: (sa * (L - r), sa * (L - R)), b: (b0, b1), "z": (HF + r, ZP)}))
                adds.append(cyl(a, *sorted((sa * (L - r), sa * (L - R))), {b: sb * P, "z": ZP}, 2 * KN))
                holes.append(cyl(a, *sorted((sa * (L - R - 1), sa * (L - r + 1))), {b: sb * P, "z": ZP}, 3.2))
    h = cut(h, tools)
    return cut(fuse([h] + adds), holes)


def outline():
    """The plate's outline in the top door's frame, closed: (x, y) points, right half then mirrored."""
    b = WH - 1.8
    half = [(b, P), (b, P - 5.0)]
    s_tip = P - TIP_Y
    for s in (SHOULDER, s_tip):
        half.append((seam(s) - SEAM_GAP, P - s))
    pts = half + [(-x, y) for x, y in reversed(half)]
    return pts


def door(rho=H - CL):
    t = 1.0; r = RIN[t]; R = r + t
    zb = ZP + D
    b = WH - R
    body = cq.Workplane("XY").workplane(offset=zb).polyline(outline()).close().extrude(t)
    body = body.edges("|Z").edges("<Y").fillet(3.0).val()
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
    return cut(fuse([body] + adds), holes)


def turn(s, deg):
    return s.rotate(V(0, 0, 0), V(0, 0, 1), deg)


def doors(d, top_deg, side_deg):
    """Four copies of the one door, opened by the given angles. Order: top, bottom, left, right."""
    t = d.rotate(V(0, P, ZP), V(1, P, ZP), -top_deg)
    left = turn(d, 90).rotate(V(-P, 0, ZP), V(-P, 1, ZP), -side_deg)
    return [("door", t), ("door", turn(t, 180)), ("door", left), ("door", turn(left, 180))]


def lamp(parts, top_deg=0.0, side_deg=0.0, with_yoke=True):
    items = [("shell", parts["shell"]), ("cap", parts["cap"]), ("plate", parts["plate"]), ("hood", parts["hood"])]
    for i in range(S.N_FINS):
        zf = -(i + 1) * S.PITCH
        items.append(("fin", parts["fin"].translate(V(0, 0, zf))))
        items += [("spacer", parts["spacer"].translate(V(0, 0, zf + S.T + k * S.T))) for k in range(2)]
    items += doors(parts["door"], top_deg, side_deg)
    items.append(("carrier", parts["carrier"]))
    if with_yoke:
        items.append(("yoke", parts["yoke"]))
    return items


def hardware():
    hw = R2.hardware()
    top = R3.pins(WH, ZP)
    side = [turn(p, 90) for p in top]
    hw += [("pin", p) for p in top + [turn(p, 180) for p in top] + side + [turn(p, 180) for p in side]]
    return hw


def build():
    p = R2.build()
    p.update({"hood": hood(), "door": door()})
    return p


THICK = {"shell": 1.5, "cap": 1.5, "hood": 1.5, "door": 1.0, "yoke": 3.0, "plate": 3.0, "fin": 3.0, "spacer": 3.0}
QTY = {"shell": 1, "cap": 1, "hood": 1, "door": 4, "yoke": 1, "plate": 1, "fin": 4, "spacer": 8}
PRINTED = {"carrier": 1}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    parts = build()
    print(f"seams meet at {THETA_D:g} deg; outline {[(round(x, 2), round(y, 2)) for x, y in outline()[:4]]}")
    for name in ("hood", "door"):
        s = parts[name]
        cq.exporters.export(cq.Workplane().add(s), os.path.join(OUT, f"rgb-spotlight-r4-{name}-{THETA_D:g}.step"))
        bb = s.BoundingBox(); v, a = s.Volume(), s.Area()
        print(f"{name:6s} t {THICK[name]:.1f}  x{QTY[name]}  {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f}  "
              f"solids {len(s.Solids())}  valid {s.isValid()}  mass {v * 2.68e-3:5.1f} g")
    # neighbours at the seam angle, and a little either side
    for th in (THETA_D - 5, THETA_D, THETA_D + 5, 90):
        ds = [s for n, s in lamp(parts, th, th, with_yoke=False) if n == "door"]
        top, right = ds[0], ds[3]
        ov = top.intersect(right).Volume()
        print(f"   all at {th:g}: top to right door {top.distance(right):.2f} mm, overlap {ov:.2f} mm3")
