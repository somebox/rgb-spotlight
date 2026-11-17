"""RGB Spotlight, square lamp, round 3: barn doors that reach the hood face and swing from 0 to 180. Builds on round2.py.

uv run --python 3.12 --with cadquery python round3.py OUTDIR

What changes from round 2:
  hood   the eight door lugs move out to the ends of each door's hinge line (round 2: +-11 from the centre line) and
         fold up from cut-outs on their inner side. Pins at +-31.5 (round 2: 29); the top and bottom pins 6.3 above
         the face, the side pins 7.8, so the closed side doors still lie over the top and bottom ones.
  doors  two parts again (round 2: one). Each door folds an ear down at both ends of its hinge edge; the ears take
         the pin and sit just inside the hood's lugs (round 2: the doors' lugs sat outside the hood's). A foot bent
         40 deg down along the hinge edge reaches to within about 0.5 mm of the face when the door stands at 90 deg.
         Nothing on a door reaches further from its pin than the pin's height above the face less CL, so a door
         swings from closed (0) through 90 to lying flat outward (180) without touching the face. The top and bottom
         doors are 57 wide at the hinge, the side doors 45: the side doors' lugs have to clear the top doors' lugs at
         the corners of the face.
  pins   M3 x 8 button head outside the hood lug, M3 nylock nut inside the door's ear (round 2 drew no pins).
Unchanged: shell, carrier, cap, yoke, stack, boards, lenses.
"""
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out3"
sys.argv = sys.argv[:1] + ["/dev/null"]
import cadquery as cq  # noqa: E402
from cadquery import Vector as V  # noqa: E402

import round2 as R2  # noqa: E402
import sheet as S  # noqa: E402
from sheet import bx, cyl, bend, fuse, cut, polar, ANG, RIN  # noqa: E402

HB, HF = R2.HB, R2.HF                         # hood face 15.9 .. 17.4, as round 2
P = 31.5                                      # pins at +-31.5: the lug knuckles end 0.25 short of the face's bend
HT, HS = 6.3, 7.8                             # pin heights above the face: top/bottom, sides
ZP_T, ZP_S = HF + HT, HF + HS                 # 23.7, 25.2
CL = 0.4                                      # a door keeps this far from the face anywhere in its swing
D = 4.6                                       # a closed door's plate: inner face 4.6 in front of its pin
BETA = 40.0                                   # the foot's bend below the plate
W_T, W_S = 28.5, 22.45                        # half width over the ears: top/bottom doors, side doors
KN = 3.5                                      # hood lug knuckle radius
EAR_R = 4.5                                   # door ear radius about the pin
LUG_GAP = 0.3                                 # door ear to hood lug
HEAD_D, HEAD_H, NUT_D, NUT_H, SCREW_L = 5.7, 1.65, 6.35, 4.0, 8.0   # ISO 7380 M3 button head, M3 nylock (across corners)


def hood():
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
    for a, b, wd, zp in (("x", "y", W_T, ZP_T), ("y", "x", W_S, ZP_S)):   # a: across the lug, b: along the pin's line
        L = wd + LUG_GAP + R                  # bend line: the lug stands at L-R .. L-r, folded up from a cut-out inside it
        flat_len = (math.pi / 2) * (r + 0.44 * t) + (zp + KN - (HF + r))      # unfolded lug, K = 0.44
        for sa in (-1, 1):
            for sb in (-1, 1):
                b0, b1 = sorted((sb * (P - KN), sb * (P + KN)))
                tools.append(bx(**{a: (sa * L, sa * (L - flat_len - 0.6)), b: (b0 - 0.5, b1 + 0.5), "z": (HB - 1, HF + 1)}))
                for edge in (b0 - 0.5, b1):                                # bend reliefs
                    tools.append(bx(**{a: (sa * L, sa * (L + 1.0)), b: (edge, edge + 0.5), "z": (HB - 1, HF + 1)}))
                adds.append(bend(b, b0, b1, {a: sa * L, "z": HF + r}, {a: -sa, "z": -1}, t))
                adds.append(bx(**{a: (sa * (L - r), sa * (L - R)), b: (b0, b1), "z": (HF + r, zp)}))
                adds.append(cyl(a, *sorted((sa * (L - r), sa * (L - R))), {b: sb * P, "z": zp}, 2 * KN))
                holes.append(cyl(a, *sorted((sa * (L - R - 1), sa * (L - r + 1))), {b: sb * P, "z": zp}, 3.2))
    h = cut(h, tools)
    return cut(fuse([h] + adds), holes)


def foot_length(rho, t=1.0):
    """Length of the foot's flat so that its outer end corner lies rho from the pin."""
    r = RIN[t]; R = r + t; b = math.radians(BETA)
    qy, qz = R * math.sin(b), (D - r) + R * math.cos(b)                    # outer face where the bend ends
    uy, uz = math.cos(b), -math.sin(b)
    qu = qy * uy + qz * uz
    return -qu + math.sqrt(qu * qu - (qy * qy + qz * qz) + rho * rho)


def door(wd, zp, rho):
    """A door as the top door, closed, pin at (y P, z zp); wd: half width over the ears; rho: the furthest any part of
    it reaches from the pin. The side doors are the side part turned 90 deg about z."""
    t = 1.0; r = RIN[t]; R = r + t
    zb = zp + D
    b = wd - R                                                             # plate edge = the ears' bend lines
    body = (cq.Workplane("XY").workplane(offset=zb)
            .polyline([(-b, P), (b, P), (b, P - 5.0), (20.0, S.TIP), (-20.0, S.TIP), (-b, P - 5.0)]).close().extrude(t))
    body = body.edges("|Z").edges("<Y").fillet(3.0).val()
    # foot: bent down BETA along the hinge edge, between the ears (0.5 relief at each end)
    s = foot_length(rho, t); be = math.radians(BETA)
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
    for sg in (-1, 1):                                                     # ears: folded down at the hinge-end corners
        adds.append(bend("y", P - 5.0, P, {"x": sg * b, "z": zb - r}, {"x": sg, "z": 1}, t))
        x0, x1 = sorted((sg * (b + r), sg * (b + R)))
        adds.append(bx((x0, x1), (P - 5.0, P), (zp, zb - r)))
        adds.append(cyl("x", x0, x1, {"y": P, "z": zp}, 2 * EAR_R))
        holes.append(cyl("x", *sorted((sg * (b - 1), sg * (b + R + 1))), {"y": P, "z": zp}, 3.2))
    return cut(fuse([body] + adds), holes)


def pins(wd, zp):
    """The two pins of a door built as the top door: button head outside the hood lug, nylock inside the ear."""
    out = []
    for sg in (-1, 1):
        lug_out = wd + LUG_GAP + 1.5                                        # outer face of the hood lug
        ear_in = wd - 1.0                                                   # inner face of the door's ear
        c = {"y": P, "z": zp}
        head = cyl("x", *sorted((sg * lug_out, sg * (lug_out + HEAD_H))), c, HEAD_D)
        shank = cyl("x", *sorted((sg * lug_out, sg * (lug_out - SCREW_L))), c, 3.0)
        nut = cyl("x", *sorted((sg * ear_in, sg * (ear_in - NUT_H))), c, NUT_D)
        out.append(fuse([head, shank, nut]))
    return out


def turn(s, deg):
    return s.rotate(V(0, 0, 0), V(0, 0, 1), deg)


def doors(dt, ds, top_deg, side_deg):
    """The four doors opened by the given angles (0 = closed, 180 = flat outward). Order: top, bottom, left, right."""
    t = dt.rotate(V(0, P, ZP_T), V(1, P, ZP_T), -top_deg)
    left = turn(ds, 90).rotate(V(-P, 0, ZP_S), V(-P, 1, ZP_S), -side_deg)
    return [("door", t), ("door", turn(t, 180)), ("door_side", left), ("door_side", turn(left, 180))]


def lamp(parts, top_deg=0.0, side_deg=0.0, with_yoke=True):
    items = [("shell", parts["shell"]), ("cap", parts["cap"]), ("plate", parts["plate"]), ("hood", parts["hood"])]
    for i in range(S.N_FINS):
        zf = -(i + 1) * S.PITCH
        items.append(("fin", parts["fin"].translate(V(0, 0, zf))))
        items += [("spacer", parts["spacer"].translate(V(0, 0, zf + S.T + k * S.T))) for k in range(2)]
    items += doors(parts["door"], parts["door_side"], top_deg, side_deg)
    items.append(("carrier", parts["carrier"]))
    if with_yoke:
        items.append(("yoke", parts["yoke"]))
    return items


def hardware():
    hw = R2.hardware()
    top = pins(W_T, ZP_T)
    side = [turn(p, 90) for p in pins(W_S, ZP_S)]
    hw += [("pin", p) for p in top + [turn(p, 180) for p in top] + side + [turn(p, 180) for p in side]]
    return hw


def build():
    p = R2.build()
    p.update({"hood": hood(), "door": door(W_T, ZP_T, HT - CL), "door_side": door(W_S, ZP_S, HS - CL)})
    return p


THICK = {"shell": 1.5, "cap": 1.5, "hood": 1.5, "door": 1.0, "door_side": 1.0, "yoke": 3.0, "plate": 3.0, "fin": 3.0,
         "spacer": 3.0}
QTY = {"shell": 1, "cap": 1, "hood": 1, "door": 2, "door_side": 2, "yoke": 1, "plate": 1, "fin": 4, "spacer": 8}
PRINTED = {"carrier": 1}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    parts = build()
    print(f"foot flats: top/bottom {foot_length(HT - CL):.2f} mm, sides {foot_length(HS - CL):.2f} mm")
    for name in ("hood", "door", "door_side"):
        s = parts[name]
        cq.exporters.export(cq.Workplane().add(s), os.path.join(OUT, f"rgb-spotlight-r3-{name.replace('_', '-')}.step"))
        bb = s.BoundingBox(); v, a = s.Volume(), s.Area()
        print(f"{name:10s} t {THICK[name]:.1f}  x{QTY[name]}  {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f}  "
              f"solids {len(s.Solids())}  valid {s.isValid()}  2V/A {2 * v / a:.2f}  mass {v * 2.68e-3:5.1f} g")
    print("sheet-metal mass per lamp", round(sum(parts[n].Volume() * 2.68e-3 * QTY[n] for n in QTY), 0), "g")
