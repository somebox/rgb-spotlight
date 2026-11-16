"""RGB Spotlight, square lamp: the sheet-metal parts JLC unfolds, the square stack, and the assembly.

uv run --python 3.12 --with cadquery python sheet.py OUTDIR

Local frame: z = optical axis (front +z), y up, x right (the boards' own frame). The stack's front plate is
z 0..3 with the LED board on it (3..4.5); fins go back from there; the driver sits behind on 15 mm standoffs.
Every bent part is built as flat slabs joined by quarter-tube bends of one thickness, with the inner bend radius
from JLCCNC's sheet-metal guidelines (outer R 1.8 / 2.75 / 6 for 1 / 1.5 / 3 mm), so it unfolds.

Parts (all Al 5052):
  shell     1.5 mm  front face with the LED window, four walls bent back, vent slots over the fin gaps
  cap       1.5 mm  back cap, four rims bent forward into the shell; press nuts 2x M3 (top, bottom) and 2x M5 (sides)
  frame     1.5 mm  barn-door frame on 4 M3x10 standoffs; 8 lugs bent forward from its face
  leaf_top  1.0 mm  top and bottom doors (x2), two lugs bent back
  leaf_side 1.0 mm  left and right doors (x2), two lugs bent back
  yoke      3.0 mm  U bracket; pivots on M5 knobs into the cap's press nuts; 1/4"-20 hole and two M4 holes
  plate     3.0 mm  stack front plate, 58.5 square: 10x M3 threads
  fin       3.0 mm  61 square (x4)
  spacer    3.0 mm  D30 (x8)
  retainer  1.0 mm  flat disc D48 over the three lenses, three windows D18.6
and one printed part (MJF PA12, black):
  carrier   holds three 20 mm TIR lenses over the LEDs by their flanges; stands on three feet at the M3 screws
"""
import math
import os
import sys

import cadquery as cq
from cadquery import Vector as V

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
HERE = os.path.dirname(os.path.abspath(__file__))
BOARDS = os.path.join(HERE, "..", "out")

RIN = {1.0: 0.8, 1.5: 1.25, 3.0: 3.0}       # inner bend radius by thickness (JLC outer R less t)
AX = {"x": V(1, 0, 0), "y": V(0, 1, 0), "z": V(0, 0, 1)}
ANG = (30, 150, 270)

# stack
T = 3.0
N_FINS, PITCH = 4, 9.0
STACK_BACK = -N_FINS * PITCH                # -36
PLATE_W, FIN_W = 58.5, 61.0
STANDOFF = 15.0
DRV_Z = STACK_BACK - STANDOFF - 1.6         # driver board's back face, -52.6
CORNER = 24.0                               # front screws / standoffs at (+-24, +-24)
# shell and cap
SH_T, W2 = 1.5, 32.5                        # outer half width 32.5 -> 65 x 65
ZF, ZB = 4.5, -66.6                         # front face of the shell, back end
GAP = 0.3
CAP_W2 = W2 - SH_T - GAP                    # 30.7
CAP_FRONT = -52.0                           # front edge of the cap's rims
Z_NUT = -58.0                               # cap press nuts, shell holes, yoke pivot
# frame and doors
FR_T, FR_W2 = 1.5, 37.0                     # 74 x 74
ZFR = ZF + 10.0                             # frame on 10 mm standoffs: 14.5..16
F = ZFR + FR_T                              # frame front face, 16
ZP = F + 6.0                                # door pins, 22
PIN_T, PIN_S = 31.5, 31.5                   # top/bottom pins at y = +-31.5, side pins at x = +-31.5
LUG_B = 15.0                                # frame lugs' bend lines (x = +-15 for the top doors, y = +-15 for the sides)
D_TOP, D_SIDE = 5.0, 6.5                    # leaf back face in front of its pin
TIP = 0.5                                   # closed doors stop 0.5 mm short of the axis
# yoke
Y_T, Y_IN, Y_BASE, Y_HZ = 3.0, W2 + 1.0, -66.0, 12.0


def polar(r, a):
    return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))


def bx(x, y, z):
    x0, x1 = sorted(x); y0, y1 = sorted(y); z0, z1 = sorted(z)
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def _pt(axis, at, c):
    d = {axis: at, **c}
    return V(d.get("x", 0), d.get("y", 0), d.get("z", 0))


def cyl(axis, lo, hi, c, d):
    """Cylinder of diameter d along axis from lo to hi, centred at c (the other two coordinates)."""
    return cq.Solid.makeCylinder(d / 2, hi - lo, _pt(axis, lo, c), AX[axis])


def bend(axis, lo, hi, c, q, t):
    """90 degree bend: quarter tube along axis (lo..hi) about centre c, inner radius RIN[t], quadrant q (+1/-1)."""
    r = RIN[t]; R = r + t
    tube = cyl(axis, lo, hi, c, 2 * R).cut(cyl(axis, lo, hi, c, 2 * r))
    rng = {axis: (lo, hi)}
    for k, v in c.items():
        rng[k] = (v, v + q[k] * (R + 1))
    return tube.intersect(bx(rng["x"], rng["y"], rng["z"]))


def slot(axis, lo, hi, a_name, a0, a1, b_name, b, w):
    """Stadium slot through `axis` (lo..hi), long along a_name from a0 to a1, centred at b on b_name, width w."""
    body = bx(**{axis: (lo, hi), a_name: (a0 + w / 2, a1 - w / 2), b_name: (b - w / 2, b + w / 2)})
    ends = [cyl(axis, lo, hi, {a_name: a, b_name: b}, w) for a in (a0 + w / 2, a1 - w / 2)]
    return body.fuse(*ends)


def fuse(parts):
    return parts[0].fuse(*parts[1:]).clean() if len(parts) > 1 else parts[0]


def cut(s, tools):
    for tl in tools:
        s = s.cut(tl)
    return s.clean()


def flat_sq(w, r, z0, t):
    return cq.Workplane("XY").workplane(offset=z0).rect(w, w).extrude(t).edges("|Z").fillet(r).val()


# ---------------------------------------------------------------- stack
def plate():
    p = flat_sq(PLATE_W, 2.0, 0.0, T)
    holes = [cyl("z", -1, T + 1, {"x": 0, "y": 0}, 8.0)]
    holes += [cyl("z", -1, T + 1, dict(zip("xy", polar(r, a))), 2.5) for r in (19, 11) for a in ANG]
    holes += [cyl("z", -1, T + 1, {"x": sx * CORNER, "y": sy * CORNER}, 2.5) for sx in (-1, 1) for sy in (-1, 1)]
    return cut(p, holes)


def fin(z0=0.0):
    p = flat_sq(FIN_W, 3.0, z0, T)
    holes = [cyl("z", z0 - 1, z0 + T + 1, {"x": 0, "y": 0}, 8.0)]
    holes += [cyl("z", z0 - 1, z0 + T + 1, dict(zip("xy", polar(r, a))), 3.2) for r in (19, 11) for a in ANG]
    return cut(p, holes)


def spacer(z0=0.0):
    p = cyl("z", z0, z0 + T, {"x": 0, "y": 0}, 30.0).cut(cyl("z", z0 - 1, z0 + T + 1, {"x": 0, "y": 0}, 8.0))
    return cut(p, [cyl("z", z0 - 1, z0 + T + 1, dict(zip("xy", polar(11, a))), 3.2) for a in ANG])


# ---------------------------------------------------------------- shell
SLOT_Z_STACK = [-(i * PITCH) - 3.0 for i in range(N_FINS)]     # -3, -12, -21, -30: the fin gaps
SLOT_Z_DRV = [-42.0, -47.5]                                     # behind the stack, top and bottom only
SLOT_W, SLOT_L = 3.5, 22.0


def shell():
    t = SH_T; R = RIN[t] + t
    e, zc = W2 - R, ZF - R                     # 29.75: end of the face's flat; 1.75: start of the walls' flats
    side = W2 - t - GAP                        # the side walls fit between the top and bottom walls
    parts = [bx((-e, e), (-e, e), (ZF - t, ZF))]
    for s in (-1, 1):
        parts.append(bend("x", -e, e, {"y": s * e, "z": zc}, {"y": s, "z": 1}, t))
        parts.append(bx((-W2, W2), (s * (W2 - t), s * W2), (ZB, zc)))
        parts.append(bend("y", -e, e, {"x": s * e, "z": zc}, {"x": s, "z": 1}, t))
        parts.append(bx((s * (W2 - t), s * W2), (-side, side), (ZB, zc)))
    sh = fuse(parts)
    tools = [cyl("z", ZF - 3, ZF + 1, {"x": 0, "y": 0}, 52.0)]
    tools += [cyl("z", ZF - 3, ZF + 1, {"x": sx * CORNER, "y": sy * CORNER}, 3.2) for sx in (-1, 1) for sy in (-1, 1)]
    for s in (-1, 1):
        for zc_ in SLOT_Z_STACK + SLOT_Z_DRV:
            tools.append(slot("y", s * W2 - 3, s * W2 + 3, "x", -SLOT_L, SLOT_L, "z", zc_, SLOT_W))
        for zc_ in SLOT_Z_STACK:
            tools.append(slot("x", s * W2 - 3, s * W2 + 3, "y", -SLOT_L, SLOT_L, "z", zc_, SLOT_W))
        tools.append(cyl("y", s * W2 - 3, s * W2 + 3, {"x": 0, "z": Z_NUT}, 3.4))     # cap screws M3
        tools.append(cyl("x", s * W2 - 3, s * W2 + 3, {"y": 0, "z": Z_NUT}, 5.5))     # yoke knobs M5
    return cut(sh, tools)


# ---------------------------------------------------------------- back cap
J_CUT = [(16.45, 9.5), (-16.45, 9.5)]          # J2 and J1 on the driver's back face
NUT_M3, NUT_M5 = 4.22, 7.14                    # press-nut mounting holes (PEM S-M3-1, S-M5-1)


def cap():
    t = SH_T; R = RIN[t] + t
    w = CAP_W2; e, zc = w - R, ZB + R          # 27.95, -63.85
    side = w - t - GAP
    parts = [bx((-e, e), (-e, e), (ZB, ZB + t))]
    for s in (-1, 1):
        parts.append(bend("x", -e, e, {"y": s * e, "z": zc}, {"y": s, "z": -1}, t))
        parts.append(bx((-w, w), (s * (w - t), s * w), (zc, CAP_FRONT)))
        parts.append(bend("y", -e, e, {"x": s * e, "z": zc}, {"x": s, "z": -1}, t))
        parts.append(bx((s * (w - t), s * w), (-side, side), (zc, CAP_FRONT)))
    c = fuse(parts)
    tools = []
    for x, y in J_CUT:
        tools.append(cq.Workplane("XY").workplane(offset=ZB - 1).center(x, y).rect(14, 15).extrude(t + 2)
                     .edges("|Z").fillet(2).val())
    for s in (-1, 1):
        tools.append(cyl("y", s * w - 3, s * w + 3, {"x": 0, "z": Z_NUT}, NUT_M3))
        tools.append(cyl("x", s * w - 3, s * w + 3, {"y": 0, "z": Z_NUT}, NUT_M5))
    return cut(c, tools)


# ---------------------------------------------------------------- frame and doors
def frame():
    t = FR_T; r = RIN[t]; R = r + t
    fr = flat_sq(2 * FR_W2, 4.0, ZFR, t)
    tools = [cyl("z", ZFR - 1, F + 1, {"x": 0, "y": 0}, 58.0)]
    tools += [cyl("z", ZFR - 1, F + 1, {"x": sx * CORNER, "y": sy * CORNER}, 3.2) for sx in (-1, 1) for sy in (-1, 1)]
    flat_len = (math.pi / 2) * (r + 0.44 * t) + (ZP + 3.5 - (F + r))      # unfolded lug, K = 0.44
    adds, holes = [], []
    for a, b in (("x", "y"), ("y", "x")):     # a: across the bend line (lug thickness), b: along it
        pin = PIN_T if a == "x" else PIN_S
        for sa in (-1, 1):
            for sb in (-1, 1):
                b0, b1 = sorted((sb * (pin - 3.5), sb * (pin + 3.5)))
                tools.append(bx(**{a: (sa * LUG_B, sa * (LUG_B + flat_len + 0.6)), b: (b0 - 0.5, b1 + 0.5), "z": (ZFR - 1, F + 1)}))
                for edge in (b0 - 0.5, b1):                                # bend reliefs
                    tools.append(bx(**{a: (sa * (LUG_B - 1.0), sa * LUG_B), b: (edge, edge + 0.5), "z": (ZFR - 1, F + 1)}))
                adds.append(bend(b, b0, b1, {a: sa * LUG_B, "z": F + r}, {a: sa, "z": -1}, t))
                adds.append(bx(**{a: (sa * (LUG_B + r), sa * (LUG_B + R)), b: (b0, b1), "z": (F + r, ZP)}))
                adds.append(cyl(a, *sorted((sa * (LUG_B + r), sa * (LUG_B + R))), {b: sb * pin, "z": ZP}, 7.0))
                holes.append(cyl(a, *sorted((sa * (LUG_B - 1), sa * (LUG_B + R + 1))), {b: sb * pin, "z": ZP}, 3.2))
    fr = cut(fr, tools)
    return cut(fuse([fr] + adds), holes)


def leaf_top():
    """Top door, closed, at the top of the frame. The bottom door is the same part turned 180 degrees about z."""
    t = 1.0; r = RIN[t]; R = r + t
    zb = ZP + D_TOP                                       # back face 27
    lx = PIN_T - 3.5                                      # lug from y = 28 to the hinge edge at 35
    top = PIN_T + 3.5
    body = (cq.Workplane("XY").workplane(offset=zb)          # tapers to +-20 at the tip, clear of the side doors
            .polyline([(-27.0, top), (27.0, top), (20.0, TIP), (-20.0, TIP)]).close().extrude(t))
    body = body.edges("|Z").edges("<Y").fillet(3.0).val()
    b = 17.25                                             # bend lines x = +-17.25 -> lugs at 18.05..19.05
    tools, adds, holes = [], [], []
    for s in (-1, 1):
        tools.append(bx((s * b, s * 28.0), (lx - 0.5, top + 1), (zb - 1, zb + t + 1)))
        tools.append(bx((s * (b - r), s * b), (lx - 0.5, lx), (zb - 1, zb + t + 1)))
        adds.append(bend("y", lx, top, {"x": s * b, "z": zb - r}, {"x": s, "z": 1}, t))
        adds.append(bx((s * (b + r), s * (b + R)), (lx, top), (ZP, zb - r)))
        adds.append(cyl("x", *sorted((s * (b + r), s * (b + R))), {"y": PIN_T, "z": ZP}, 7.0))
        holes.append(cyl("x", *sorted((s * (b - 1), s * (b + R + 1))), {"y": PIN_T, "z": ZP}, 3.2))
    return cut(fuse([cut(body, tools)] + adds), holes)


def leaf_side():
    """Left door, closed. The right door is the same part turned 180 degrees about z."""
    t = 1.0; r = RIN[t]; R = r + t
    zb = ZP + D_SIDE                                      # back face 28.5
    hinge, tip = -(PIN_S + 3.5), -TIP                     # x of the hinge edge (-35) and the tip (-0.5)
    body = (cq.Workplane("XY").workplane(offset=zb)
            .polyline([(hinge, -35.5), (tip, -20.0), (tip, 20.0), (hinge, 35.5)]).close().extrude(t))
    body = body.edges("|Z").edges(">X").fillet(3.0).val()
    b = 17.25
    x0, x1 = hinge, -(PIN_S - 3.5)                         # lug from x = -35 to -28
    flat_len = (math.pi / 2) * (r + 0.44 * t) + (zb - r - (ZP - 3.5))
    tools, adds, holes = [], [], []
    for s in (-1, 1):
        tools.append(bx((x0 - 1, x1 + 0.5), (s * b, s * (b + flat_len + 0.6)), (zb - 1, zb + t + 1)))
        tools.append(bx((x1, x1 + 0.5), (s * (b - r), s * b), (zb - 1, zb + t + 1)))
        adds.append(bend("x", x0, x1, {"y": s * b, "z": zb - r}, {"y": s, "z": 1}, t))
        adds.append(bx((x0, x1), (s * (b + r), s * (b + R)), (ZP, zb - r)))
        adds.append(cyl("y", *sorted((s * (b + r), s * (b + R))), {"x": -PIN_S, "z": ZP}, 7.0))
        holes.append(cyl("y", *sorted((s * (b - 1), s * (b + R + 1))), {"x": -PIN_S, "z": ZP}, 3.2))
    return cut(fuse([cut(body, tools)] + adds), holes)


# ---------------------------------------------------------------- yoke
def yoke():
    t = Y_T; r = RIN[t]
    e = Y_IN - r                                          # 30.5
    z0, z1 = Z_NUT - Y_HZ, Z_NUT + Y_HZ
    parts = [bx((-e, e), (Y_BASE - t, Y_BASE), (z0, z1))]
    for s in (-1, 1):
        parts.append(bend("z", z0, z1, {"x": s * e, "y": Y_BASE + r}, {"x": s, "y": -1}, t))
        parts.append(bx((s * Y_IN, s * (Y_IN + t)), (Y_BASE + r, 0), (z0, z1)))
        parts.append(cyl("x", *sorted((s * Y_IN, s * (Y_IN + t))), {"y": 0, "z": Z_NUT}, 2 * Y_HZ))
    y = fuse(parts)
    tools = [cyl("x", -45, 45, {"y": 0, "z": Z_NUT}, 5.5)]
    tools += [cyl("y", Y_BASE - t - 1, Y_BASE + 1, {"x": x, "z": Z_NUT}, d) for x, d in ((0, 6.6), (-22, 4.5), (22, 4.5))]
    return cut(y, tools)


# ---------------------------------------------------------------- optics
# Generic 20 mm PMMA TIR lens (AliExpress, seller's drawing): flange D19.9 x 2.0 at the front, cone from D17.8 down
# to about D8 at the base, 10.8 tall, cavity D6.1 x 5.0 over the LED. Its own bracket (D22) is too wide for LEDs
# 20.8 mm apart, so one printed carrier holds all three by their flanges on a ledge, and a 1 mm retainer plate on top
# keeps them in. Three M3 x 18 go through retainer, carrier and LED board into the plate's r = 19 threads; they also
# hold the LED board down. The carrier stands on three feet at the screws: an M3 washer under each foot lifts the
# lenses 0.5 mm, for finding the focus.
BOARD = T + 1.6                               # LED board front, 4.6 (LED die about 0.67 above it, dome 1.84)
LEDS = {c: polar(12.0, a) for c, a in (("R", 90), ("G", 210), ("B", 330))}
LENS_D, LENS_FL, LENS_H, LENS_TOP_D, LENS_BASE_D, CAV_D, CAV_H = 19.9, 2.0, 10.8, 17.8, 8.0, 6.1, 5.0
LIFT = 0.5                                    # lens base above the board: the die sits just above its base plane
CAR_D, FOOT, FOOT_D = 48.0, 0.5, 7.0          # carrier diameter; feet at the screws, 0.5 below the body
POCKET, BORE = 20.4, 18.6                     # flange pocket and ledge bore; JLC3DP MJF holds +-0.3
RELIEF_D, RELIEF_H = 40.0, 2.5                # underside relief over the LEDs, wire pads and wires
RET_T, RET_WIN = 1.0, 18.6                    # retainer plate; windows clear the lenses' optical face (D17.5)
Z_LENS = BOARD + LIFT                         # lens base, 5.1
Z_LEDGE = Z_LENS + LENS_H - LENS_FL           # flange seat, 13.9
Z_RET = Z_LENS + LENS_H                       # lens top = retainer's back face, 15.9
Z_CAR = Z_RET - 0.1                           # carrier top: the flanges stand 0.1 proud, so the retainer clamps them
SCREW_L, HEAD_D, HEAD_H = 18.0, 5.5, 2.0      # M3 x 18 pan head


def lens(x, y):
    body = cq.Solid.makeCone(LENS_BASE_D / 2, LENS_TOP_D / 2, LENS_H - LENS_FL, V(x, y, Z_LENS))
    body = body.fuse(cyl("z", Z_LEDGE, Z_RET, {"x": x, "y": y}, LENS_D))
    return body.cut(cyl("z", Z_LENS - 1, Z_LENS + CAV_H, {"x": x, "y": y}, CAV_D)).clean()


def carrier():
    screws = [dict(zip("xy", polar(19, a))) for a in ANG]
    c = fuse([cyl("z", BOARD + FOOT, Z_CAR, {"x": 0, "y": 0}, CAR_D)] +
             [cyl("z", BOARD, BOARD + FOOT + 1, p, FOOT_D) for p in screws])
    relief = cut(cyl("z", BOARD - 1, BOARD + RELIEF_H, {"x": 0, "y": 0}, RELIEF_D),
                 [cyl("z", BOARD - 2, BOARD + RELIEF_H + 1, p, FOOT_D + 1) for p in screws])
    tools = [relief]
    tools += [cyl("z", BOARD - 1, Z_CAR + 1, {"x": x, "y": y}, BORE) for x, y in LEDS.values()]
    tools += [cyl("z", Z_LEDGE, Z_CAR + 1, {"x": x, "y": y}, POCKET) for x, y in LEDS.values()]
    pts = list(LEDS.values())
    for i in range(3):                        # neighbouring pockets leave a 0.4 mm web: open it where under 2 mm
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % 3]
        a = math.degrees(math.atan2(y2 - y1, x2 - x1))
        b = bx((-1.0, 1.0), (-4.0, 4.0), (Z_LEDGE, Z_CAR + 1)).rotate(V(0, 0, 0), V(0, 0, 1), a)
        tools.append(b.translate(V((x1 + x2) / 2, (y1 + y2) / 2, 0)))
    tools += [cyl("z", BOARD - 1, Z_CAR + 1, p, 3.2) for p in screws]
    return cut(c, tools)


def retainer():
    p = cyl("z", Z_RET, Z_RET + RET_T, {"x": 0, "y": 0}, CAR_D)
    tools = [cyl("z", Z_RET - 1, Z_RET + RET_T + 1, {"x": x, "y": y}, RET_WIN) for x, y in LEDS.values()]
    tools += [cyl("z", Z_RET - 1, Z_RET + RET_T + 1, dict(zip("xy", polar(19, a))), 3.4) for a in ANG]
    return cut(p, tools)


def led_screw(x, y, lift=0.0):
    top = Z_RET + RET_T + lift
    return cyl("z", top - SCREW_L, top, {"x": x, "y": y}, 3.0).fuse(cyl("z", top, top + HEAD_H, {"x": x, "y": y}, HEAD_D))


# ---------------------------------------------------------------- assembly
def hexbar(x, y, z0, z1, af=5.5):
    return (cq.Workplane("XY").workplane(offset=z0).center(x, y).polygon(6, af / math.cos(math.pi / 6))
            .extrude(z1 - z0).val())


def open_leaves(lt, ls, top_deg, side_deg):
    """Four doors from the two leaf parts, opened by the given angles (0 = closed)."""
    out = []
    t = lt.rotate(V(0, PIN_T, ZP), V(1, PIN_T, ZP), -top_deg)
    out += [("leaf_top", t), ("leaf_top", t.rotate(V(0, 0, 0), V(0, 0, 1), 180))]
    s = ls.rotate(V(-PIN_S, 0, ZP), V(-PIN_S, 1, ZP), -side_deg)
    out += [("leaf_side", s), ("leaf_side", s.rotate(V(0, 0, 0), V(0, 0, 1), 180))]
    return out


def lamp(parts, top_deg=0.0, side_deg=0.0, with_yoke=True):
    """(name, solid) for everything in the lamp, doors at the given angles."""
    items = [("shell", parts["shell"]), ("cap", parts["cap"]), ("frame", parts["frame"]), ("plate", parts["plate"])]
    for i in range(N_FINS):
        zf = -(i + 1) * PITCH
        items.append(("fin", parts["fin"].translate(V(0, 0, zf))))
        items += [("spacer", parts["spacer"].translate(V(0, 0, zf + T + k * T))) for k in range(2)]
    items += open_leaves(parts["leaf_top"], parts["leaf_side"], top_deg, side_deg)
    items += [("carrier", parts["carrier"]), ("retainer", parts["retainer"])]
    if with_yoke:
        items.append(("yoke", parts["yoke"]))
    return items


def hardware():
    """Boards and bought parts, for the renders."""
    led = cq.importers.importStep(os.path.join(BOARDS, "led.step")).val().translate(V(0, 0, T))
    drv = cq.importers.importStep(os.path.join(BOARDS, "driver.step")).val().translate(V(0, 0, DRV_Z))
    hw = [("led", led), ("drv", drv)]
    hw += [("nylon", hexbar(*polar(11, a), STACK_BACK - STANDOFF, STACK_BACK)) for a in ANG]
    hw += [("steel", cyl("z", STACK_BACK - 6, T - 0.2, dict(zip("xy", polar(11, a))), 3.0)) for a in ANG]
    hw += [("steel", hexbar(sx * CORNER, sy * CORNER, ZF, ZFR)) for sx in (-1, 1) for sy in (-1, 1)]
    hw += [("lens", lens(x, y)) for x, y in LEDS.values()]
    hw += [("screw", led_screw(*polar(19, a))) for a in ANG]
    for s in (-1, 1):                                   # M5 star knobs on the yoke
        x0 = s * (Y_IN + Y_T)
        knob = cq.Workplane("YZ").workplane(offset=min(x0, x0 + s * 8)).center(0, Z_NUT).polygon(6, 22).extrude(8).val()
        hw.append(("knob", knob.fuse(cyl("x", *sorted((x0, x0 + s * 11)), {"y": 0, "z": Z_NUT}, 12)).clean()))
    return hw


def build():
    return {"shell": shell(), "cap": cap(), "frame": frame(), "leaf_top": leaf_top(), "leaf_side": leaf_side(),
            "yoke": yoke(), "plate": plate(), "fin": fin(), "spacer": spacer(), "retainer": retainer(),
            "carrier": carrier()}


THICK = {"shell": 1.5, "cap": 1.5, "frame": 1.5, "leaf_top": 1.0, "leaf_side": 1.0, "yoke": 3.0, "plate": 3.0,
         "fin": 3.0, "spacer": 3.0, "retainer": 1.0}
QTY = {"shell": 1, "cap": 1, "frame": 1, "leaf_top": 2, "leaf_side": 2, "yoke": 1, "plate": 1, "fin": 4, "spacer": 8,
       "retainer": 1}
PRINTED = {"carrier": 1}                      # MJF PA12, black: not sheet metal

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    parts = build()
    for name, s in parts.items():
        cq.exporters.export(cq.Workplane().add(s), os.path.join(OUT, f"rgb-spotlight-{name.replace('_', '-')}.step"))
        bb = s.BoundingBox()
        v, a = s.Volume(), s.Area()
        kind = f"t {THICK[name]:.1f}" if name in THICK else "MJF  "
        dens = 2.68e-3 if name in THICK else 1.01e-3
        print(f"{name:10s} {kind}  x{QTY.get(name, PRINTED.get(name))}  {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f}  "
              f"solids {len(s.Solids())}  valid {s.isValid()}  2V/A {2 * v / a:.2f}  mass {v * dens:5.1f} g  vol {v / 1000:.2f} cm3")
    asm = cq.Assembly()
    for i, (n, s) in enumerate(lamp(parts, 60, 75) + hardware()):
        asm.add(cq.Workplane().add(s), name=f"{n}-{i}")
    asm.save(os.path.join(OUT, "rgb-spotlight-lamp-assembly.step"))
    print("total sheet-metal mass per lamp",
          round(sum(parts[n].Volume() * 2.68e-3 * QTY[n] for n in QTY), 0), "g")
