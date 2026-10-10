#!/bin/bash
# LED board (aluminium) from its schematic: netlist -> scripts/gen_led_pcb.py (placement, routing, islands) -> DRC.
# Fully generated: rerun freely while it has no hand edits.
set -eo pipefail
cd "$(dirname "$0")/.."
K=/Applications/KiCad/KiCad.app/Contents
NET=$(mktemp -t led).net
"$K/MacOS/kicad-cli" sch export netlist --format kicadsexpr -o "$NET" boards/led/led.kicad_sch >/dev/null
PY="$K/Frameworks/Python.framework/Versions/3.9/bin/python3"
"$PY" scripts/gen_led_pcb.py "$NET" boards/led/led.kicad_pcb 2>&1 | { grep -v -e wxApp -e swig/python -e Fontconfig || true; }
pcbkit drc boards/led/led.kicad_pcb
