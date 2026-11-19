"""RGB Spotlight, square lamp, round 8: round 7 with a new hood, for JLCCNC's review of the first order (2026-11-19).
Only the hood changes; the doors, the carriers and round 7's parts stay as ordered.

ROT=45 uv run --python 3.12 --with cadquery python round8.py order8

JLCCNC's limits for 1.5 mm sheet (its sheet-metal guideline, "Bending Design Constraints"): a flange at least 6.0 mm,
a rectangular hole at least 6.0 mm from a bend and a round hole 4.5 mm, measured to the outside of the bent leg as JLC's
other dimensions are. Its review of round 6's hood (SMS2611163003204) found two faults:
  1. "the minimum bending length for a single fold is 6.0 mm": each lug's window ended 3.5 mm from the outside of the
     wall beside it (y 35.5 against 39), so where the wall is bent the face had 3.5 mm left before the window.
  2. "the rectangular opening on the inner side must be at least 12 mm wide", or the punch doesn't fit: the windows the
     lugs fold up from were 8 mm along the bend line (a 7 mm lug with 0.5 mm either side).
Round 8's hood:
  face     84 mm square (H_W2 42, was 39): every window ends 6.5 mm from the wall's outside, 5.0 from its inside.
  windows  12.5 mm along the bend line, widened inwards (23.0 .. 35.5 from the centre, was 27.5 .. 35.5); the added width
           has a 1 mm relief past the bend line, like the lug's ends, so the punch's nose clears the window's edge. At each
           corner the windows of the two doors' lugs now run into one L-shaped opening.
Unchanged: the lugs (7 mm wide, knuckle R 3.5, pins 6.3 mm in front of the face at +-31.5), so the doors fit as before;
the face's height, where it clamps the lens flanges; the lens windows and LED screw holes, turned 45 deg (D23); the walls'
depth (back to z 2.5); Al 5052 1.5 mm.

Everything else in this module is round 7's, so check7.py runs on it: ROUND=round8 ... python check7.py OUTDIR.
"""
import math
import os
import sys

_OUT = sys.argv[1] if len(sys.argv) > 1 else "out8"
sys.argv = sys.argv[:1] + ["/dev/null"]
import cadquery as cq  # noqa: E402

import round2 as R2  # noqa: E402
import round4 as R4  # noqa: E402
import round6 as R6  # noqa: E402
import round7 as R7  # noqa: E402
from round7 import *  # noqa: E402,F401,F403  round 7's constants and hardware, which check7.py reads
import sheet as S  # noqa: E402
from sheet import bx, cyl, bend, fuse, cut, polar, RIN  # noqa: E402

OUT = _OUT                                        # round 7's OUT came in with the star import

H_W2 = 42.0            # hood half width (round 6: 39)
WIN = 12.5             # each lug's window along its bend line; JLCCNC needs 12 for the punch
WIN_GAP = 0.5          # lug to window at the lug's outer end, as round 6
RELIEF = 1.0           # reliefs past the bend line, as round 6
JLC_15 = {"flange": 6.0, "rect hole to bend": 6.0, "round hole to bend": 4.5, "window": 12.0}   # 1.5 mm, outside


def lug_frame():
    """Round 6's lug geometry: (L, flat_len, P, KN, ZP), L the lug's bend line from the centre."""
    t = R2.H_T; r = RIN[t]; R = r + t
    L = R4.WH + R4.LUG_GAP + R
    flat_len = (math.pi / 2) * (r + 0.44 * t) + (R4.ZP + R4.KN - (R2.HF + r))
    return L, flat_len, R4.P, R4.KN, R4.ZP


def hood(w2=H_W2, win=WIN):
    """The hood with its walls at +-w2 and each lug's window `win` long along the bend line (round 6: 39 and 8)."""
    t = R2.H_T; r = RIN[t]; R = r + t
    HB, HF = R2.HB, R2.HF
    e, zc = w2 - R, HF - R
    side = w2 - t - S.GAP
    parts = [bx((-e, e), (-e, e), (HB, HF))]
    for s in (-1, 1):
        parts.append(bend("x", -e, e, {"y": s * e, "z": zc}, {"y": s, "z": 1}, t))
        parts.append(bx((-w2, w2), (s * (w2 - t), s * w2), (R2.H_BACK, zc)))
        parts.append(bend("y", -e, e, {"x": s * e, "z": zc}, {"x": s, "z": 1}, t))
        parts.append(bx((s * (w2 - t), s * w2), (-side, side), (R2.H_BACK, zc)))
    h = fuse(parts)
    tools = [cyl("z", HB - 1, HF + 1, {"x": x, "y": y}, S.RET_WIN) for x, y in R6.LEDS6.values()]
    tools += [cyl("z", HB - 1, HF + 1, dict(zip("xy", polar(19, a))), 3.4) for a in R6.ANG6]
    L, flat_len, P, KN, ZP = lug_frame()
    adds, holes = [], []
    for a, b in (("x", "y"), ("y", "x")):            # a: across the lug (the pin's axis), b: along its bend line
        for sa in (-1, 1):
            for sb in (-1, 1):
                b0, b1 = sorted((sb * (P - KN), sb * (P + KN)))                      # the lug
                w0, w1 = sorted((sb * (P + KN + WIN_GAP - win), sb * (P + KN + WIN_GAP)))   # its window
                tools.append(bx(**{a: (sa * L, sa * (L - flat_len - 0.6)), b: (w0, w1), "z": (HB - 1, HF + 1)}))
                for lo, hi in ((w0, b0), (b1, w1)):  # window beside the lug: relief past the bend line
                    tools.append(bx(**{a: (sa * L, sa * (L + RELIEF)), b: (lo, hi), "z": (HB - 1, HF + 1)}))
                adds.append(bend(b, b0, b1, {a: sa * L, "z": HF + r}, {a: -sa, "z": -1}, t))
                adds.append(bx(**{a: (sa * (L - r), sa * (L - R)), b: (b0, b1), "z": (HF + r, ZP)}))
                adds.append(cyl(a, *sorted((sa * (L - r), sa * (L - R))), {b: sb * P, "z": ZP}, 2 * KN))
                holes.append(cyl(a, *sorted((sa * (L - R - 1), sa * (L - r + 1))), {b: sb * P, "z": ZP}, 3.2))
    h = cut(h, tools)
    return cut(fuse([h] + adds), holes)


def build():
    """Round 7's parts with round 8's hood."""
    p = R7.build()
    p["hood"] = hood()
    return p


lamp = R7.lamp
doors = R7.doors
hardware = R7.hardware

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    h = hood()
    f = os.path.join(OUT, "rgb-spotlight-r8-hood.step")
    cq.exporters.export(cq.Workplane().add(h), f)
    bb = h.BoundingBox()
    print(f"hood t 1.5 x1  {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}  valid {h.isValid()} solids {len(h.Solids())}  "
          f"vol {h.Volume() / 1000:.2f} cm3  mass {h.Volume() * 2.68e-3:.1f} g  JLCCNC sheet metal  {os.path.basename(f)}")
    r6 = R6.hood()
    print(f"round 6's hood for comparison: {r6.BoundingBox().xlen:.1f} square, mass {r6.Volume() * 2.68e-3:.1f} g")
