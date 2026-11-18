#!/bin/sh
# Regenerate review previews for one board (or all) into docs/previews/<board>/ with `pcbkit previews`:
# schematic.pdf, pcb-front/back.png, assembly-back.png, board.pdf (1:1), render-top/bottom.png (skip with NO_RENDER=1).
# Usage: scripts/make_previews.sh [driver|led|led35|all]   (default all)
set -e
cd "$(dirname "$0")/.."
boards=${1:-all}
[ "$boards" = all ] && boards="driver led led35"
for b in $boards; do
  pcbkit previews "boards/$b/$b.kicad_pcb" "docs/previews/$b" --zoom 1.0 --render-size 1600x1600 ${NO_RENDER:+--no-render}
  # The LED boards are aluminium: render them again in their own stackup colours (aluminium core, bare back), which
  # `pcbkit previews` doesn't use. The back gets a bottom light, or bare aluminium renders nearly black.
  if [ "${b#led}" != "$b" ] && [ -z "$NO_RENDER" ]; then
    KC=$(python3 -c 'import pcbkit.kicad as k; print(k.KICAD_CLI)')
    "$KC" pcb render --side top -w 1600 -h 1600 --use-board-stackup-colors \
      -o "docs/previews/$b/render-top.png" "boards/$b/$b.kicad_pcb" >/dev/null
    "$KC" pcb render --side bottom -w 1600 -h 1600 --use-board-stackup-colors --light-bottom 1 --light-camera 0.8 \
      -o "docs/previews/$b/render-bottom.png" "boards/$b/$b.kicad_pcb" >/dev/null
  fi
done
