#!/bin/bash
# Driver board from its schematic: netlist -> placement, planes, silk (scripts/gen_driver_pcb.py) -> DRC summary.
# Refuses to overwrite a board that has footprints (hand edits) unless --force.
#   --route   then scripts/route_driver.py: cells, +12V, GND vias, logic (several minutes)
# Usage: scripts/make_driver_pcb.sh [--force] [--route]
set -eo pipefail
cd "$(dirname "$0")/.."
K=/Applications/KiCad/KiCad.app/Contents
NET=$(mktemp -t driver).net
"$K/MacOS/kicad-cli" sch export netlist --format kicadsexpr -o "$NET" boards/driver/driver.kicad_sch >/dev/null
PY="$K/Frameworks/Python.framework/Versions/3.9/bin/python3"
FORCE=""; ROUTE=""
for a in "$@"; do case "$a" in --force) FORCE=--force;; --route) ROUTE=1;; esac; done
"$PY" scripts/gen_driver_pcb.py "$NET" boards/driver/driver.kicad_pcb $FORCE 2>&1 | { grep -v -e wxApp -e swig/python -e Fontconfig || true; }
if [ -n "$ROUTE" ]; then
  "$PY" -u scripts/route_driver.py --force 2>&1 | { grep -v -e wxApp -e swig/python -e Fontconfig || true; }
fi
pcbkit drc boards/driver/driver.kicad_pcb
