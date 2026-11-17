"""RGB Spotlight housing: a printable knob for the yoke pivot, in place of the bought one (DESIGN D30).

uv run --python 3.12 --with cadquery python knob.py print

The bought knob is an Elesa VC.692/25 p-M4x10: five lobes, D 25, L 20, hub 12 x 6, a steel M4 stud 10 mm long. This one
keeps those sizes (round7.py's KNOB), so it fits wherever check7.py placed that one, and holds an ordinary M4 x 20
hex-head bolt (ISO 4017) as its stud:

  knob   printed hub down, no supports: the hub stands on the bed and the grip's underside is a 45 degree cone. A hex
         pocket from the top takes the bolt's head; 10 mm of solid plastic under the head, through the cone and the hub,
         leaves 10 mm of thread below the hub's face.
  plug   a hex prism that fills the pocket above the bolt's head, glued in. It keeps the bolt from sliding back when
         the thread is started, and closes the top.

The head bears on 27 mm2 of plastic around the bolt (the hex less the hole), the hub on 97 mm2. By D30's estimate
about 50 N a side holds the lamp level; at 150 N the seat carries about 6 N/mm2. D30's 0.5 N m finger turn (about
600 N) would load it to 23 N/mm2: ASA and PCTG yield near 40 to 50 (typical figures, not from a datasheet), so the seat
holds but creeps if left that tight. Tighten until the lamp stays, not further. The knob sits outside the housing on
the yoke, away from the heat: PCTG or ASA. Not printed or tried yet.
"""
import math
import os
import sys

import cadquery as cq

D, L, HUB_D, HUB_H, STUD = 25.0, 20.0, 12.0, 6.0, 10.0     # round7.py KNOB: the bought knob's sizes
BOLT_L, HEAD_AF, HEAD_K = 20.0, 7.0, 2.8                   # ISO 4017 M4 x 20: 7 mm across flats, head 2.8 high
HOLE, POCKET_AF = 4.5, 7.2                                 # printed clearances: the bolt's shank, the head's flats
SCALLOP_R, SCALLOP_AT, CORNER = 7.0, 17.0, 2.0             # five scallops between the lobes; the lobes' corner radius
TOP_CH, FOOT_CH = 1.0, 0.4                                 # top edge; the hub's foot, against a spread first layer
PLUG_AF, PLUG_GAP = 7.0, 0.1                               # the plug: a sliding fit in the pocket, its top 0.1 under

FLOOR = BOLT_L - STUD                                      # plastic under the bolt's head: 10
CONE_TOP = HUB_H + (D - HUB_D) / 2                         # where the 45 degree cone reaches the full diameter: 12.5
ROOT = SCALLOP_AT - SCALLOP_R                              # the grip's radius between two lobes: 10


def hexagon(af, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).polygon(6, af / math.cos(math.radians(30))).extrude(z1 - z0).val()


def knob():
    r, rh = D / 2, HUB_D / 2
    outline = (cq.Sketch().circle(r).parray(SCALLOP_AT, 36, 360, 5).circle(SCALLOP_R, mode="s")
               .reset().vertices().fillet(CORNER))
    grip = cq.Workplane("XY").placeSketch(outline).extrude(L).val()
    envelope = (cq.Workplane("XZ")
                .polyline([(0, 0), (rh - FOOT_CH, 0), (rh, FOOT_CH), (rh, HUB_H), (r, CONE_TOP), (r, L - TOP_CH),
                           (r - TOP_CH, L), (0, L)]).close().revolve(360, (0, 0, 0), (0, 1, 0)).val())
    hole = cq.Solid.makeCylinder(HOLE / 2, FLOOR + 2, cq.Vector(0, 0, -1))
    return grip.intersect(envelope).cut(hole).cut(hexagon(POCKET_AF, FLOOR, L + 1)).clean()


def plug():
    h = L - FLOOR - HEAD_K - PLUG_GAP
    return cq.Workplane("XY").add(hexagon(PLUG_AF, 0, h)).faces(">Z").edges().chamfer(0.4).val()


def bolt():
    """The M4 x 20 as it sits in the knob, for pictures and checks; not exported."""
    return hexagon(HEAD_AF, FLOOR, FLOOR + HEAD_K).fuse(cq.Solid.makeCylinder(2.0, BOLT_L, cq.Vector(0, 0, FLOOR - BOLT_L)))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "print"
    os.makedirs(out, exist_ok=True)
    k, p, b = knob(), plug(), bolt()
    for name, s in (("knob", k), ("knob-plug", p)):
        cq.exporters.export(cq.Workplane().add(s), os.path.join(out, f"rgb-spotlight-{name}.step"))
        bb = s.BoundingBox()
        print(f"{name:9s} valid {s.isValid()} solids {len(s.Solids())} vol {s.Volume() / 1000:.2f} cm3 "
              f"box {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
    seat = math.sqrt(3) / 2 * HEAD_AF ** 2 - math.pi / 4 * HOLE ** 2
    hub = math.pi / 4 * (HUB_D ** 2 - HOLE ** 2)
    print(f"stud below the hub {BOLT_L - FLOOR:.1f} mm (bought knob {STUD}); plastic under the head {FLOOR:.1f} mm")
    print(f"wall round the pocket {ROOT - POCKET_AF / math.sqrt(3):.1f} mm at the lobes' roots; "
          f"plug {p.BoundingBox().zlen:.1f} mm high")
    print(f"bearing: head {seat:.0f} mm2, hub {hub:.0f} mm2; at 150 N {150 / seat:.1f} N/mm2, at 600 N {600 / seat:.1f} N/mm2")
    print(f"bolt against the knob: overlap {k.intersect(b).Volume():.3f} mm3 (0 = it fits)")
