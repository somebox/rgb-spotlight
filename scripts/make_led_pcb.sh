#!/bin/bash
# An LED board (aluminium) from its schematic: netlist -> scripts/gen_led_pcb.py (placement, routing, islands) -> DRC.
# Usage: scripts/make_led_pcb.sh [led|led35]   (default led; led35 is the same board for 3.5 mm LEDs, D35)
# Fully generated: rerun freely while the board has no hand edits. A released board is not regenerated: change it in place.
set -eo pipefail
cd "$(dirname "$0")/.."
B=${1:-led}
K=/Applications/KiCad/KiCad.app/Contents
NET=$(mktemp -t "$B").net
"$K/MacOS/kicad-cli" sch export netlist --format kicadsexpr -o "$NET" "boards/$B/$B.kicad_sch" >/dev/null
PY="$K/Frameworks/Python.framework/Versions/3.9/bin/python3"
"$PY" scripts/gen_led_pcb.py "$NET" "boards/$B/$B.kicad_pcb" 2>&1 | { grep -v -e wxApp -e swig/python -e Fontconfig || true; }
pcbkit drc "boards/$B/$B.kicad_pcb"
