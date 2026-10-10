#!/bin/sh
# Regenerate review previews for one board (or all) into docs/previews/<board>/ with `pcbkit previews`:
# schematic.pdf, pcb-front/back.png, assembly-back.png, board.pdf (1:1), render-top/bottom.png (skip with NO_RENDER=1).
# Usage: scripts/make_previews.sh [driver|led|all]   (default all)
set -e
cd "$(dirname "$0")/.."
boards=${1:-all}
[ "$boards" = all ] && boards="driver led"
for b in $boards; do
  pcbkit previews "boards/$b/$b.kicad_pcb" "docs/previews/$b" --zoom 1.0 --render-size 1600x1600 ${NO_RENDER:+--no-render}
done
