"""Change a board's outline preset in place: edge, mounting holes, copper keep-outs, edge stitching, GND pour extent.
Parts and tracks stay as they are, so this works on routed and hand-edited boards. Presets: scripts/mech.py.

  <KiCad python> scripts/set_outline.py <driver|led|all> <disc50|disc55|disc60|tabs3>

Close the board in KiCad first (or reload it afterwards without saving the old copy).
"""
import os, subprocess, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mech

if len(sys.argv) != 3:
    raise SystemExit(__doc__)
which, name = sys.argv[1], sys.argv[2]
mech.preset(name)                                            # validates the name
for board in (("driver", "led") if which == "all" else (which,)):
    path = os.path.join(HERE, "..", "boards", board, f"{board}.kicad_pcb")
    n = mech.strip_outline_file(path, 150.0, 100.0)            # old outline out (text edit), then the new one in
    b = pcbnew.LoadBoard(path)
    gnd = b.FindNet("GND") if board == "driver" else None
    _, n_holes, n_stitch = mech.apply_outline(b, board, name, 150.0, 100.0, stitch_net=gnd)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(path, b)
    print(f"{board}: removed {n} old outline items; outline {name} ({mech.describe(name)}), {n_holes} holes, {n_stitch} edge stitching vias")
    from pcbkit.checks.drc import run, summarise
    summarise(run(path))
