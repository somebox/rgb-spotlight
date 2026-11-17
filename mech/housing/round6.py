"""RGB Spotlight, square lamp, round 6: round 5's pick with the LED board and the parts that locate it turned ROT deg
about the beam axis, so that the three LEDs have different x and different y positions: each door edge, horizontal or
vertical, then casts three colour bands instead of two.

ROT=45 uv run --python 3.12 --with cadquery python round6.py OUTDIR

Turned with the board: the LEDs, the carrier, the lenses, the three M3 x 20 LED screws, the hood face's lens windows and
screw holes, and the front plate's three LED-screw threads at r 19. Not turned: the hood's lugs and walls, the doors, the
stack behind the plate (its tie rods at r 11 carry the driver, whose connectors face the cap's cut-outs), the shell.
The LED board itself is unchanged: it is round, its holes turn with it, and its wires leave through the centre.
Round 5's doors as LEN, WID, CUT (default 40, 71, 90).
"""
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out6"
sys.argv = sys.argv[:1] + ["/dev/null"]
import cadquery as cq  # noqa: E402
from cadquery import Vector as V  # noqa: E402

import round4 as R4  # noqa: E402
import round5 as R5  # noqa: E402
import sheet as S  # noqa: E402
from sheet import cyl, cut, polar  # noqa: E402

ROT = float(os.environ.get("ROT", "45"))
ANG6 = tuple(a + ROT for a in S.ANG)                        # LED screws (were 30, 150, 270)
LEDS6 = {c: polar(12.0, a + ROT) for c, a in (("R", 90), ("G", 210), ("B", 330))}
TURNED = ("lens", "led", "screw")                           # hardware turned with the board


def rz(s):
    return s.rotate(V(0, 0, 0), V(0, 0, 1), ROT)


def hood():
    """Round 4's hood with its lens windows and screw holes at the turned positions."""
    leds, ang = S.LEDS, R4.ANG
    S.LEDS, R4.ANG = LEDS6, ANG6
    try:
        return R4.hood()
    finally:
        S.LEDS, R4.ANG = leds, ang


def plate():
    """The front plate with its three LED-screw threads at the turned positions; the tie-rod holes at r 11 stay."""
    p = S.flat_sq(S.PLATE_W, 2.0, 0.0, S.T)
    holes = [cyl("z", -1, S.T + 1, {"x": 0, "y": 0}, S.STACK_BORE)]
    holes += [cyl("z", -1, S.T + 1, dict(zip("xy", polar(19, a))), 2.5) for a in ANG6]
    holes += [cyl("z", -1, S.T + 1, dict(zip("xy", polar(11, a))), 2.5) for a in S.ANG]
    holes += [cyl("z", -1, S.T + 1, {"x": sx * S.CORNER, "y": sy * S.CORNER}, 2.5) for sx in (-1, 1) for sy in (-1, 1)]
    return cut(p, holes)


def build():
    p = R5.build()
    p.update({"hood": hood(), "plate": plate(), "carrier": rz(p["carrier"])})
    return p


def hardware():
    return [(n, rz(s) if n in TURNED else s) for n, s in R5.hardware()]


doors = R5.doors
lamp = R5.lamp

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    parts = build()
    for name in ("hood", "plate", "carrier"):
        s = parts[name]
        cq.exporters.export(cq.Workplane().add(s), os.path.join(OUT, f"rgb-spotlight-r6-{name}-rot{ROT:g}.step"))
        print(f"{name:8s} valid {s.isValid()} solids {len(s.Solids())}")
    print("LEDs at", {c: (round(x, 2), round(y, 2)) for c, (x, y) in LEDS6.items()}, "screws at", ANG6)
