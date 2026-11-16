"""RGB Spotlight, square lamp, round 2: light-tight and fewer parts. Builds on sheet.py (round 1).

uv run --python 3.12 --with cadquery python round2.py OUTDIR

What changes from round 1:
  hood     1.5 mm  78 square, replaces the barn-door frame, the lens retainer and the four frame standoffs. Its face clamps the
                   lens flanges (three windows, the three LED screws go through it); four walls bent back overlap the
                   shell's front by 2 mm with a 5 mm gap, so the gap between the shell and the frame is closed; eight
                   lugs bent forward carry the doors, pins at +-29 (round 1: 31.5).
  door     1.0 mm  one part for all four doors (round 1 had two). The side doors' lugs on the hood are 1.5 mm longer,
                   so they still sit in front of the top and bottom doors.
  carrier  MJF     sits on the LED board on a continuous ring instead of three feet, and a skirt covers the board's
                   edge: the board is hidden everywhere except under the lenses. Focus is set by the carrier's height
                   (print +0.5 / +1.0 variants for the focus test) instead of washers under its feet.
  shell    as round 1 but its window is D54 (was 52); its face is screwed to the plate with four M3 x 6 instead of the standoffs, so it still takes
           the plate's heat (the housing carries about three quarters of it, thermal_sheet.py).
Unchanged: cap, yoke, plate, fins, spacers, boards, lenses.
"""
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out2"
sys.argv = sys.argv[:1] + ["/dev/null"]
import cadquery as cq  # noqa: E402
from cadquery import Vector as V  # noqa: E402

import sheet as S  # noqa: E402
from sheet import bx, cyl, bend, fuse, cut, polar, ANG, RIN  # noqa: E402

# hood
H_T, H_W2 = 1.5, 39.0                         # 78 x 78: the lugs' cut-outs end 3.25 mm short of the wall bends
HB = S.Z_RET                                  # back face on the lens flanges, 15.9
HF = HB + H_T                                 # front face, 17.4
H_BACK = 2.5                                  # walls run back to z 2.5: 2 mm over the shell, 5 mm outside it (longer ones hit the yoke at 50 deg down)
PIN = 29.0                                    # door pins at +-29 (round 1: 31.5)
LUG_B = 11.0                                  # lug bend lines (round 1: 15), so top and side cut-outs keep a 2 mm web
ZP_T = HF + 6.0                               # top/bottom pins, 23.4
ZP_S = ZP_T + 1.5                             # side pins, 24.9: the side doors sit 1.5 further forward
D = 5.0                                       # door back face in front of its pin
DOOR_B = LUG_B + 2.25                         # door lugs' bend lines, 13.25: just outside the hood's lugs
# carrier
LED_TOP = S.T + 1.51                          # board top in the KiCad STEP (S.BOARD is the nominal 1.6)
RING_IN = 21.0                                # ring foot r 21..25.7 sits on the board all round
SKIRT_IN, SKIRT_OUT, SKIRT_Z = 25.3, 26.5, 3.3   # 1.2 mm skirt down past the board's edge (r 25), inside the shell window
WINDOW = 54.0                                 # shell window, round 1: 52; makes room for a skirt MJF can print
# screws
LED_SCREW_L = 20.0                            # M3 x 20 through hood face, lens flanges, carrier, board, plate
CORNER_SCREW_L = 6.0                          # M3 x 6: shell face to the plate's corner threads


def hood():
    t = H_T; r = RIN[t]; R = r + t
    W = H_W2; e, zc = W - R, HF - R
    side = W - t - S.GAP
    parts = [bx((-e, e), (-e, e), (HB, HF))]
    for s in (-1, 1):
        parts.append(bend("x", -e, e, {"y": s * e, "z": zc}, {"y": s, "z": 1}, t))
        parts.append(bx((-W, W), (s * (W - t), s * W), (H_BACK, zc)))
        parts.append(bend("y", -e, e, {"x": s * e, "z": zc}, {"x": s, "z": 1}, t))
        parts.append(bx((s * (W - t), s * W), (-side, side), (H_BACK, zc)))
    h = fuse(parts)
    tools = [cyl("z", HB - 1, HF + 1, {"x": x, "y": y}, S.RET_WIN) for x, y in S.LEDS.values()]
    tools += [cyl("z", HB - 1, HF + 1, dict(zip("xy", polar(19, a))), 3.4) for a in ANG]
    adds, holes = [], []
    for a, b in (("x", "y"), ("y", "x")):     # a: across the bend line (lug thickness), b: along it
        zp = ZP_T if a == "x" else ZP_S
        flat_len = (math.pi / 2) * (r + 0.44 * t) + (zp + 3.5 - (HF + r))      # unfolded lug, K = 0.44
        for sa in (-1, 1):
            for sb in (-1, 1):
                b0, b1 = sorted((sb * (PIN - 3.5), sb * (PIN + 3.5)))
                tools.append(bx(**{a: (sa * LUG_B, sa * (LUG_B + flat_len + 0.6)), b: (b0 - 0.5, b1 + 0.5), "z": (HB - 1, HF + 1)}))
                for edge in (b0 - 0.5, b1):                                # bend reliefs
                    tools.append(bx(**{a: (sa * (LUG_B - 1.0), sa * LUG_B), b: (edge, edge + 0.5), "z": (HB - 1, HF + 1)}))
                adds.append(bend(b, b0, b1, {a: sa * LUG_B, "z": HF + r}, {a: sa, "z": -1}, t))
                adds.append(bx(**{a: (sa * (LUG_B + r), sa * (LUG_B + R)), b: (b0, b1), "z": (HF + r, zp)}))
                adds.append(cyl(a, *sorted((sa * (LUG_B + r), sa * (LUG_B + R))), {b: sb * PIN, "z": zp}, 7.0))
                holes.append(cyl(a, *sorted((sa * (LUG_B - 1), sa * (LUG_B + R + 1))), {b: sb * PIN, "z": zp}, 3.2))
    h = cut(h, tools)
    return cut(fuse([h] + adds), holes)


def door():
    """The top door, closed, pin at (y PIN, z ZP_T). The other three are this part turned about z."""
    t = 1.0; r = RIN[t]; R = r + t
    zp = ZP_T; zb = zp + D
    lx, top = PIN - 3.5, PIN + 3.5
    body = (cq.Workplane("XY").workplane(offset=zb)
            .polyline([(-27.0, top), (27.0, top), (20.0, S.TIP), (-20.0, S.TIP)]).close().extrude(t))
    body = body.edges("|Z").edges("<Y").fillet(3.0).val()
    b = DOOR_B
    tools, adds, holes = [], [], []
    for s in (-1, 1):
        tools.append(bx((s * b, s * 28.0), (lx - 0.5, top + 1), (zb - 1, zb + t + 1)))
        tools.append(bx((s * (b - r), s * b), (lx - 0.5, lx), (zb - 1, zb + t + 1)))
        adds.append(bend("y", lx, top, {"x": s * b, "z": zb - r}, {"x": s, "z": 1}, t))
        adds.append(bx((s * (b + r), s * (b + R)), (lx, top), (zp, zb - r)))
        adds.append(cyl("x", *sorted((s * (b + r), s * (b + R))), {"y": PIN, "z": zp}, 7.0))
        holes.append(cyl("x", *sorted((s * (b - 1), s * (b + R + 1))), {"y": PIN, "z": zp}, 3.2))
    return cut(fuse([cut(body, tools)] + adds), holes)


def carrier():
    screws = [dict(zip("xy", polar(19, a))) for a in ANG]
    body = fuse([cyl("z", LED_TOP, S.Z_CAR, {"x": 0, "y": 0}, S.CAR_D),
                 cyl("z", LED_TOP, S.BOARD + 0.5, {"x": 0, "y": 0}, 2 * SKIRT_OUT),
                 cyl("z", SKIRT_Z, LED_TOP + 0.2, {"x": 0, "y": 0}, 2 * SKIRT_OUT)
                 .cut(cyl("z", SKIRT_Z - 1, LED_TOP + 1, {"x": 0, "y": 0}, 2 * SKIRT_IN))])
    relief = cut(cyl("z", LED_TOP - 1, S.BOARD + S.RELIEF_H, {"x": 0, "y": 0}, 2 * RING_IN),
                 [cyl("z", LED_TOP - 2, S.BOARD + S.RELIEF_H + 1, p, 8.0) for p in screws])
    tools = [relief]
    tools += [cyl("z", LED_TOP - 1, S.Z_CAR + 1, {"x": x, "y": y}, S.BORE) for x, y in S.LEDS.values()]
    tools += [cyl("z", S.Z_LEDGE, S.Z_CAR + 1, {"x": x, "y": y}, S.POCKET) for x, y in S.LEDS.values()]
    pts = list(S.LEDS.values())
    for i in range(3):                        # neighbouring pockets leave a 0.4 mm web: open it where under 2 mm
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % 3]
        a = math.degrees(math.atan2(y2 - y1, x2 - x1))
        bb = bx((-1.0, 1.0), (-4.0, 4.0), (S.Z_LEDGE, S.Z_CAR + 1)).rotate(V(0, 0, 0), V(0, 0, 1), a)
        tools.append(bb.translate(V((x1 + x2) / 2, (y1 + y2) / 2, 0)))
    tools += [cyl("z", LED_TOP - 1, S.Z_CAR + 1, p, 3.2) for p in screws]
    return cut(body, tools)


def screw(x, y, top, length):
    return cyl("z", top - length, top, {"x": x, "y": y}, 3.0).fuse(cyl("z", top, top + S.HEAD_H, {"x": x, "y": y}, S.HEAD_D))


def doors(d, top_deg, side_deg):
    """The four doors, opened by the given angles (0 = closed). Order: top, bottom, left, right."""
    t = d.rotate(V(0, PIN, ZP_T), V(1, PIN, ZP_T), -top_deg)
    left = d.rotate(V(0, 0, 0), V(0, 0, 1), 90).translate(V(0, 0, ZP_S - ZP_T))
    left = left.rotate(V(-PIN, 0, ZP_S), V(-PIN, 1, ZP_S), -side_deg)
    return [("door", t), ("door", t.rotate(V(0, 0, 0), V(0, 0, 1), 180)),
            ("door", left), ("door", left.rotate(V(0, 0, 0), V(0, 0, 1), 180))]


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
    hw = [h for h in S.hardware() if h[0] not in ("screw",) and not (h[0] == "steel" and h[1].BoundingBox().zmin >= S.ZF - 0.01)]
    hw += [("screw", screw(*polar(19, a), HF, LED_SCREW_L)) for a in ANG]
    hw += [("corner", screw(sx * S.CORNER, sy * S.CORNER, S.ZF, CORNER_SCREW_L)) for sx in (-1, 1) for sy in (-1, 1)]
    return hw


def shell():
    return cut(S.shell(), [cyl("z", S.ZF - 3, S.ZF + 1, {"x": 0, "y": 0}, WINDOW)])


def build():
    p = S.build()
    p["shell"] = shell()
    for k in ("frame", "leaf_top", "leaf_side", "retainer"):
        del p[k]
    p.update({"hood": hood(), "door": door(), "carrier": carrier()})
    return p


THICK = {"shell": 1.5, "cap": 1.5, "hood": 1.5, "door": 1.0, "yoke": 3.0, "plate": 3.0, "fin": 3.0, "spacer": 3.0}
QTY = {"shell": 1, "cap": 1, "hood": 1, "door": 4, "yoke": 1, "plate": 1, "fin": 4, "spacer": 8}
PRINTED = {"carrier": 1}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    parts = build()
    for name in ("shell", "hood", "door", "carrier"):
        s = parts[name]
        cq.exporters.export(cq.Workplane().add(s), os.path.join(OUT, f"rgb-spotlight-r2-{name}.step"))
        bb = s.BoundingBox(); v, a = s.Volume(), s.Area()
        kind = f"t {THICK[name]:.1f}" if name in THICK else "MJF  "
        dens = 2.68e-3 if name in THICK else 1.01e-3
        print(f"{name:10s} {kind}  x{QTY.get(name, PRINTED.get(name))}  {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f}  "
              f"solids {len(s.Solids())}  valid {s.isValid()}  2V/A {2 * v / a:.2f}  mass {v * dens:5.1f} g  vol {v / 1000:.2f} cm3")
    print("sheet-metal mass per lamp", round(sum(parts[n].Volume() * 2.68e-3 * QTY[n] for n in QTY), 0), "g")
