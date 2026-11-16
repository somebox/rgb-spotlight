# Housing (sheet metal, round 6)

The square sheet-metal lamp: round 6 is the design of record (DESIGN.md D21–D24). These are the scripts that build it and
the files it was quoted from on 2026-11-16 (PRODUCTION.md, Orders).

| Part | Shop | Material, finish | Per lamp |
| --- | --- | --- | --- |
| shell, cap, hood | JLCCNC sheet metal | Al 5052 1.5 mm, black powder coat | 1 each |
| door | JLCCNC sheet metal | Al 5052 1.0 mm, black powder coat | 4 |
| yoke | JLCCNC sheet metal | Al 5052 3 mm, black powder coat | 1 |
| plate, fin, spacer | JLCCNC sheet metal | Al 5052 3 mm, bare | 1, 4, 8 |
| carrier (+0.5, +1.0 mm for the focus test) | JLC3DP | MJF PA12, dyed black | 1 |

`order6/` holds one STEP per part (`rgb-spotlight-r6-<part>.step`) and the two drawings JLCCNC needs with them:
`rgb-spotlight-plate-threads.pdf` (10 × M3 threads in the plate) and `rgb-spotlight-cap-press-nuts.pdf` (2 × M3 and
2 × M5 press nuts in the cap).

Rebuild them (CadQuery under uv):

```bash
ROT=45 uv run --python 3.12 --with cadquery python order6.py order6
python3 drawings_sheet.py order6 && (cd order6 && for f in *.svg; do rsvg-convert -f pdf -o "${f%.svg}.pdf" "$f"; done)
```

- `sheet.py`: the shared geometry (bends at JLCCNC's radii, the stack, the cap); `round2.py`–`round6.py` each change
  the round before; `order6.py` exports the order set.
- `check6.py`: interference and clearance checks for round 6. `leaks.py`, `spill_rays.py`, `door5.js`, `beam6.js`:
  the light-leak and beam studies behind D21–D23. `thermal_sheet.py`: the heat budget.
- Renders, review pages and earlier rounds' STEPs stay in `build/heatsink/housing/sheet/` (git-ignored).
