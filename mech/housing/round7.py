"""RGB Spotlight, square lamp, round 7: round 6 with every fastener a real part, mounts on the cap's back and a wider
harness bore (DESIGN D30-D33). First, the yoke pivot (D30).

ROT=45 uv run --python 3.12 --with cadquery python round7.py OUTDIR

Round 6 drew each pivot as a 22 mm hex "knob" with a 12 mm hub and no stud, over 5.5 mm holes in the yoke and shell and
a 7.14 mm press-nut hole in the cap. No real part had those sizes: PEM's M5 nut (SS-M5 in carbon steel) takes a 6.35 mm
hole and needs 7.1 mm from the hole's centre to the sheet's edge, where the cap's side rims gave 6.0 (PEM bulletin CL,
2022, page CL-5). Round 7 uses M4, with these parts on each side, from the outside in:

  knob     Elesa VC.692/25 p-M4x10 (code 166132): five-lobe knob D 25, L 20, hub d1 12, zinc-plated steel stud M4 x 10
  washer   DIN 9021 4.3 steel, 12 x 1.0, under the knob's hub
  yoke     3 mm arm, hole 4.5 (was 5.5)
  washer   DIN 125-A 4.3 polyamide, 9 x 0.8, between yoke and shell: the friction face, in the 1.0 mm gap
  shell    1.5 mm wall, hole 4.5 (was 5.5)
  cap      1.5 mm side rim with a PEM S-M4-2 nut: hole 5.41, shank 1.38, head 7.87 x 2.0 on the inside

The cap's rims run 1.5 mm further forward (front edge -50.5, was -52.0), so the nuts sit 7.5 mm from the rims' edge
(PEM's minimum: M4 6.9, M3 4.8). The top and bottom cap screws are drawn now too: ISO 7380 M3 x 6 into PEM S-M3-2 (hole
4.22, head 6.35 x 1.5), the same sizes as before. Unchanged: the pivot's position (Z_NUT), the yoke's shape, the parts
in front of the cap. The knob's grip is drawn from the catalogue's D, L and d1 only: right for fit and clearance, not
for looks.

The cap's back face also takes four PEM S-M3-2 nuts on a 46 mm square, heads inside, for a box behind the lamp (a
controller and power supply, DESIGN D31). They sit 6.2 mm from the cable cut-outs (PEM's minimum 4.8) and their heads
1.8 mm short of the face's bends; M4 (6.9 mm from an edge) leaves no room for a square there.

The heat stack's fasteners are real parts too (DESIGN D32). Earlier rounds drew a 44.8 mm rod with a 15 mm nylon
standoff as its nut, and no screws under the driver. Round 7, on each of the three tie rods at r 11, from the front:

  stud      M3 x 45 threaded stud (DIN 976-1), locked into the plate's thread, its front end 0.2 below the plate's face
  stack     2 spacers, fin, four times (Ø3.2 holes)
  washer    DIN 125-A 3.2 steel, 7 x 0.5
  nut       ISO 4032 M3 steel: this clamps the stack, not the nylon
  standoff  polyamide hex M3 female-female x 12 (was 15), on the 3.3 mm of stud behind the nut
  driver    its front face 14.9 mm behind the stack (was 15)
  screw     polyamide pan head M3 x 6 from the back
The three LED screws are ISO 7380 M3 x 20 and the four shell screws ISO 7380 M3 x 6, the type of the cap screws and
door pins.

The hole down the middle of the plate, spacers and fins is 12 mm (was 8), so the LED harness's three JST XH 2-pin plugs
(XHP-2: 7.4 x 5.75 mm, 9.4 across the diagonal) pass through it one at a time, beside the wires of those already
through (DESIGN D33). The driver's three sockets stand 7.0 mm high, 9.8 with the plugs on, in the 14.9 mm behind the stack.
"""
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out7"
sys.argv = sys.argv[:1] + ["/dev/null"]
import cadquery as cq  # noqa: E402
from cadquery import Vector as V  # noqa: E402

import round2 as R2  # noqa: E402
import round6 as R6  # noqa: E402
import sheet as S  # noqa: E402
from sheet import cut, cyl  # noqa: E402

PIVOT_HOLE = 4.5                    # M4 medium clearance (ISO 273)
STACK_BORE = 12.0                   # the stack's middle hole: passes a JST XHP-2 plug with wires beside it (D33)
XH_PLUG = dict(w=7.4, d=5.75, header=7.0, mated=9.8)     # JST XH, 2 circuits (JST's XH sheet): plug section, heights
XH_PINS = dict(row=5.555, shift=1.63)                    # the driver's three sockets: pin row from the centre, its shift (gen_driver_pcb.py)
CAP_FRONT = -50.5                   # cap rims' front edge: 7.5 mm from the nut holes
NUT_M4 = dict(hole=5.41, shank_d=5.38, shank=1.38, head_d=7.87, head=2.0)    # PEM S-M4-2
NUT_M3 = dict(hole=4.22, shank_d=4.2, shank=1.38, head_d=6.35, head=1.5)     # PEM S-M3-2
EDGE_MIN = {"M4": 6.9, "M3": 4.8}                                            # PEM: hole centre to the sheet's edge
KNOB = dict(D=25.0, L=20.0, hub_d=12.0, hub=6.0, stud=10.0, thread=4.0)      # Elesa VC.692/25 p-M4x10
W_OUT = dict(d=12.0, t=1.0)         # DIN 9021 4.3, steel, under the knob
W_IN = dict(d=9.0, t=0.8)           # DIN 125-A 4.3, polyamide, yoke to shell
M3_SCREW = dict(head_d=5.7, head=1.65, d=3.0, L=6.0)                         # ISO 7380 M3 x 6
BACK_NUTS = [(sx * 23.0, sy * 23.0) for sx in (-1, 1) for sy in (-1, 1)]    # S-M3-2 on the cap's back, 46 mm square
# the heat stack (D32)
STUD = dict(d=3.0, L=45.0, front=S.T - 0.2)         # M3 x 45 stud (DIN 976-1); front end 0.2 below the plate's front face
WASHER_M3 = dict(d=7.0, t=0.5)                      # DIN 125-A 3.2, steel
HEXNUT_M3 = dict(af=5.5, m=2.4)                     # ISO 4032 M3, steel
STANDOFF = dict(af=5.5, L=12.0)                     # polyamide hex standoff, M3 female-female x 12
DRV_SCREW = dict(head_d=5.6, head=2.4, d=3.0, L=6.0)   # polyamide pan head M3 x 6 (ISO 7045 sizes)
LED_SCREW_L, SHELL_SCREW_L = 20.0, 6.0              # ISO 7380 M3 x 20 and M3 x 6
Z_WASHER = S.STACK_BACK - WASHER_M3["t"]            # -36.5: front of the nut
Z_NUT3 = Z_WASHER - HEXNUT_M3["m"]                  # -38.9: front of the standoff
Z_STANDOFF = Z_NUT3 - STANDOFF["L"]                 # -50.9: the driver's front face
DRV_Z = Z_STANDOFF - 1.6                            # the driver's back face, -52.5 (sheet.py: -52.6)


def patched(fn):
    """Call fn with sheet.py's pivot sizes, cap rims and stack bore set to round 7's."""
    saved = (S.PIVOT_HOLE, S.NUT_PIVOT, S.CAP_FRONT, S.STACK_BORE)
    S.PIVOT_HOLE, S.NUT_PIVOT, S.CAP_FRONT, S.STACK_BORE = PIVOT_HOLE, NUT_M4["hole"], CAP_FRONT, STACK_BORE
    try:
        return fn()
    finally:
        S.PIVOT_HOLE, S.NUT_PIVOT, S.CAP_FRONT, S.STACK_BORE = saved


def build():
    """Round 6's parts; the shell, cap, yoke, plate, fins and spacers rebuilt with round 7's holes and rims, and the
    cap's back with four nut holes."""
    p = patched(R6.build)
    p["cap"] = cut(p["cap"], [cyl("z", S.ZB - 1, S.ZB + S.SH_T + 1, {"x": x, "y": y}, NUT_M3["hole"]) for x, y in BACK_NUTS])
    return p


def ring(axis, a, b, c, d_out, d_in):
    lo, hi = sorted((a, b))
    return cyl(axis, lo, hi, c, d_out).cut(cyl(axis, lo - 1, hi + 1, c, d_in))


def lobes(x0, x1, c, d):
    """Five-lobe grip along x from x0 to x1, overall diameter d: five round lobes on a round core."""
    lo, hi = sorted((x0, x1))
    r = d / 2
    core = cyl("x", lo, hi, c, 0.62 * d)
    rl = 0.21 * d
    parts = [cyl("x", lo, hi, {"y": c["y"] + p[0], "z": c["z"] + p[1]}, 2 * rl) for p in
             [S.polar(r - rl, 90 + 72 * k) for k in range(5)]]
    return core.fuse(*parts).clean()


def pivot(s):
    """The knob, washers and press nut on side s (+1 right, -1 left), as (name, solid)."""
    c = {"y": 0, "z": S.Z_NUT}
    rim_in = s * (S.CAP_W2 - S.SH_T)                       # cap rim's inner face, x = +-29.2
    shell_out = s * S.W2                                   # shell's outer face, +-32.5
    yoke_out = s * (S.Y_IN + S.Y_T)                        # yoke arm's outer face, +-36.5
    face = yoke_out + s * W_OUT["t"]                       # knob hub face, on the outer washer
    nut = (cyl("x", *sorted((rim_in, rim_in + s * NUT_M4["shank"])), c, NUT_M4["shank_d"])
           .fuse(cyl("x", *sorted((rim_in, rim_in - s * NUT_M4["head"])), c, NUT_M4["head_d"])).clean()
           .cut(cyl("x", -60, 60, c, KNOB["thread"])))
    knob = (cyl("x", *sorted((face, face - s * KNOB["stud"])), c, KNOB["thread"])
            .fuse(cyl("x", *sorted((face, face + s * KNOB["hub"])), c, KNOB["hub_d"]))
            .fuse(lobes(face + s * KNOB["hub"], face + s * KNOB["L"], c, KNOB["D"])).clean())
    return [("nut", nut),
            ("washer_pa", ring("x", shell_out, shell_out + s * W_IN["t"], c, W_IN["d"], 4.3)),
            ("washer", ring("x", yoke_out, face, c, W_OUT["d"], 4.3)),
            ("knob", knob)]


def cap_screw(s):
    """Top (s = +1) or bottom (-1) cap screw and its press nut, as (name, solid)."""
    c = {"x": 0, "z": S.Z_NUT}
    rim_in = s * (S.CAP_W2 - S.SH_T)
    out = s * S.W2
    nut = (cyl("y", *sorted((rim_in, rim_in + s * NUT_M3["shank"])), c, NUT_M3["shank_d"])
           .fuse(cyl("y", *sorted((rim_in, rim_in - s * NUT_M3["head"])), c, NUT_M3["head_d"])).clean()
           .cut(cyl("y", -60, 60, c, M3_SCREW["d"])))
    screw = (cyl("y", *sorted((out, out - s * M3_SCREW["L"])), c, M3_SCREW["d"])
             .fuse(cyl("y", *sorted((out, out + s * M3_SCREW["head"])), c, M3_SCREW["head_d"])).clean())
    return [("nut", nut), ("m3", screw)]


def back_nut(x, y):
    """A PEM S-M3-2 in the cap's back face: shank in the sheet, head on the inside, flush outside where the box sits."""
    c, inner = {"x": x, "y": y}, S.ZB + S.SH_T
    return (cyl("z", inner - NUT_M3["shank"], inner, c, NUT_M3["shank_d"])
            .fuse(cyl("z", inner, inner + NUT_M3["head"], c, NUT_M3["head_d"])).clean()
            .cut(cyl("z", inner - 5, inner + 5, c, M3_SCREW["d"])))


def button_screw(x, y, top, length):
    """ISO 7380 M3 button head along z, its head on the face at z = top."""
    c = {"x": x, "y": y}
    return cyl("z", top - length, top, c, M3_SCREW["d"]).fuse(cyl("z", top, top + M3_SCREW["head"], c, M3_SCREW["head_d"])).clean()


def stack_hardware():
    """The three tie rods with what goes on them behind the stack, and the driver's screws, as (name, solid)."""
    out = []
    for a in S.ANG:
        x, y = S.polar(11, a)
        c = {"x": x, "y": y}
        bore = cyl("z", Z_STANDOFF - 1, S.STACK_BACK + 1, c, STUD["d"])
        out += [("stud", cyl("z", STUD["front"] - STUD["L"], STUD["front"], c, STUD["d"])),
                ("washer3", ring("z", Z_WASHER, S.STACK_BACK, c, WASHER_M3["d"], 3.2)),
                ("nut3", S.hexbar(x, y, Z_NUT3, Z_WASHER, HEXNUT_M3["af"]).cut(bore)),
                ("nylon", S.hexbar(x, y, Z_STANDOFF, Z_NUT3, STANDOFF["af"]).cut(bore)),
                ("nyscrew", cyl("z", DRV_Z, DRV_Z + DRV_SCREW["L"], c, DRV_SCREW["d"])
                 .fuse(cyl("z", DRV_Z - DRV_SCREW["head"], DRV_Z, c, DRV_SCREW["head_d"])).clean())]
    return out


def front_screws():
    """The LED screws (through hood, carrier and LED board into the plate) and the shell screws (shell face to plate)."""
    out = [("screw", button_screw(*S.polar(19, a), R2.HF, LED_SCREW_L)) for a in R6.ANG6]
    out += [("corner", button_screw(sx * S.CORNER, sy * S.CORNER, S.ZF, SHELL_SCREW_L)) for sx in (-1, 1) for sy in (-1, 1)]
    return out


def hardware():
    """Round 6's boards, lenses and door pins, with every fastener of the pivot, cap and heat stack as its real part."""
    base = R6.hardware()
    hw = [h for h in base if h[0] not in ("knob", "nylon", "steel", "screw", "corner", "drv")]
    hw.append(("drv", next(s for n, s in base if n == "drv").translate(V(0, 0, DRV_Z - S.DRV_Z))))
    hw += stack_hardware() + front_screws()
    for s in (-1, 1):
        hw += pivot(s) + cap_screw(s)
    hw += [("nut_back", back_nut(x, y)) for x, y in BACK_NUTS]
    return hw


doors = R6.doors
lamp = R6.lamp

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    parts = build()
    for name in ("shell", "cap", "yoke", "plate", "fin", "spacer"):
        s = parts[name]
        cq.exporters.export(cq.Workplane().add(s), os.path.join(OUT, f"rgb-spotlight-r7-{name}.step"))
        print(f"{name:6s} valid {s.isValid()} solids {len(s.Solids())} vol {s.Volume() / 1000:.3f} cm3")
    print(f"nut hole to the rims' edge {CAP_FRONT - S.Z_NUT:.1f} mm (PEM minimum M4 {EDGE_MIN['M4']}, M3 {EDGE_MIN['M3']})")
