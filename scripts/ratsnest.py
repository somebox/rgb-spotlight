"""Placement review image: front copper + silk + courtyards with each net's shortest-spanning ratsnest drawn over it.

  <KiCad python> scripts/ratsnest.py [driver|led]     -> docs/previews/<board>/placement-ratsnest.png
Colours: blue +12V, green +5V, magenta DIM_x / OUT_x (PWM), orange everything else. GND and HEAT are planes (not drawn).
"""
import math, os, subprocess, sys, tempfile
import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD = sys.argv[1] if len(sys.argv) > 1 else "driver"
B = os.path.join(ROOT, f"boards/{BOARD}/{BOARD}.kicad_pcb")
OUT = os.path.join(ROOT, f"docs/previews/{BOARD}/placement-ratsnest.png")
W = 2000
b = pcbnew.LoadBoard(B)
bb = b.GetBoardEdgesBoundingBox()
x0, y0, s = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), W / pcbnew.ToMM(bb.GetWidth())
nets = {}
for fp in b.GetFootprints():
    for p in fp.Pads():
        n = p.GetNetname()
        if n and not n.startswith("unconnected") and n not in ("GND", "/HEAT", "HEAT"):
            q = p.GetPosition(); nets.setdefault(n, []).append((pcbnew.ToMM(q.x), pcbnew.ToMM(q.y)))
col = lambda n: "#0070ff" if n == "+12V" else "#00a000" if n == "+5V" else "#ff00ff" if "DIM" in n or "OUT_" in n else "#ff8000"
tmp = tempfile.mkdtemp()
subprocess.run(["/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli", "pcb", "export", "svg", "--layers", "F.Cu,F.SilkS,F.CrtYd,B.CrtYd,Edge.Cuts",
                "--mode-single", "--fit-page-to-board", "--exclude-drawing-sheet", "-o", f"{tmp}/f.svg", B], capture_output=True, check=True)
subprocess.run(["rsvg-convert", "-w", str(W), "-b", "white", f"{tmp}/f.svg", "-o", f"{tmp}/f.png"], check=True)
cmd = ["magick", f"{tmp}/f.png", "-strokewidth", "4", "-fill", "none"]
for n, pts in nets.items():
    pts = list(dict.fromkeys(pts)); tree, rest = [pts[0]], pts[1:]
    while rest:
        a, c = min(((a, c) for a in tree for c in rest), key=lambda t: math.dist(*t))
        cmd += ["-stroke", col(n), "-draw", f"line {(a[0]-x0)*s},{(a[1]-y0)*s} {(c[0]-x0)*s},{(c[1]-y0)*s}"]
        tree.append(c); rest.remove(c)
subprocess.run(cmd + [OUT], check=True)
print(OUT)
