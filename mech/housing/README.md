# Housing (sheet metal, round 7)

The square sheet-metal lamp: round 7 is the design of record (DESIGN.md D21–D24, D30). It is round 6, which was quoted on
2026-11-16 (PRODUCTION.md, Orders), with the yoke pivot built from real parts: the shell, cap and yoke changed, nothing
else. These are the scripts that build it and the files to order it from.

| Part | Shop | Material, finish | Per lamp |
| --- | --- | --- | --- |
| shell, cap, hood | JLCCNC sheet metal | Al 5052 1.5 mm, black powder coat | 1 each |
| door | JLCCNC sheet metal | Al 5052 1.0 mm, black powder coat | 4 |
| yoke | JLCCNC sheet metal | Al 5052 3 mm, black powder coat | 1 |
| plate, fin, spacer | JLCCNC sheet metal | Al 5052 3 mm, bare | 1, 4, 8 |
| carrier (+0.5, +1.0 mm for the focus test) | JLC3DP | MJF PA12, dyed black | 1 |

`order6/` holds one STEP per part (`rgb-spotlight-r6-<part>.step`) and the two drawings JLCCNC needs with them:
`rgb-spotlight-plate-threads.pdf` (10 × M3 threads in the plate) and `rgb-spotlight-cap-press-nuts.pdf` (round 6's cap).
`order7/` holds what round 7 changes, to be ordered in place of round 6's: `rgb-spotlight-r7-shell.step`,
`rgb-spotlight-r7-cap.step`, `rgb-spotlight-r7-yoke.step` and the cap's drawing (8 press nuts: 2 × M3 and 2 × M4 in the
rims, 4 × M3 in the back face). The other
parts, and the plate's drawing, stay in `order6/`.

**The yoke pivot (round 7, D30),** on each side from the outside in. Bought parts, 2 of each per lamp:

| Part | What | Size |
| --- | --- | --- |
| knob | Elesa VC.692/25 p-M4x10 (code 166132), glass-fibre polyamide, zinc-plated steel stud | five-lobe Ø25, 20 high, hub Ø12, M4 × 10 |
| washer | DIN 9021, steel, under the knob's hub | 4.3 × 12 × 1.0 |
| yoke | 3 mm arm | hole Ø4.5 |
| washer | DIN 125-A, polyamide: the friction face, in the 1.0 mm gap between yoke and shell | 4.3 × 9 × 0.8 |
| shell | 1.5 mm wall | hole Ø4.5 |
| press nut | PEM S-M4-2 in the cap's side rim, head inside (fitted by JLCCNC) | hole Ø5.41, head Ø7.87 × 2.0 |

The cap's top and bottom screws: ISO 7380 M3 × 6 into PEM S-M3-2 (hole Ø4.22, head Ø6.35 × 1.5), 2 per lamp. Sizes are
from PEM's bulletin CL (2022, page CL-5) and Elesa's VC.692 sheet. Round 6 drew the pivot as a hex placeholder over a
Ø7.14 cap hole: PEM's M5 nut (SS-M5) takes Ø6.35, and both its and the M4's minimum distance to the sheet's edge (7.1 and
6.9 mm) were more than the cap's rims gave (6.0). Round 7's rims run 1.5 mm further forward, to 7.5 mm.

**A box on the back (D31).** The cap's back face takes 4 × PEM S-M3-2 on a 46 × 46 mm square, centred, heads inside and
flush outside, for a box with a controller and power supply. They sit 6.2 mm from the cable cut-outs (PEM's minimum
4.8), the heads 1.8 mm short of the bends, and 8 mm or more from the driver's parts; nothing lies behind them for
20 mm, so the screw length doesn't matter. A box up to 64 × 64 mm (the yoke's arms are 67 mm apart) and 40 mm deep
never meets the yoke (`check7.py`); at 50 mm deep it stops the tilt at about 50° the other way too. The J1/J2 cut-outs
open into the box, so its cables can plug straight into the driver. M4 doesn't fit as a square here: it needs 6.9 mm
from the cut-outs.

Rebuild them (CadQuery under uv; the boards' STEPs go in `../out`, centred on the board):

```bash
kicad-cli pcb export step --subst-models --no-dnp --user-origin 150x100mm -o ../out/driver.step ../../boards/driver/driver.kicad_pcb
kicad-cli pcb export step --subst-models --user-origin 150x100mm -o ../out/led.step ../../boards/led/led.kicad_pcb
ROT=45 uv run --python 3.12 --with cadquery python order6.py order6
ROT=45 uv run --python 3.12 --with cadquery python round7.py order7
python3 drawings_sheet.py order6 plate && python3 drawings_sheet.py order7 cap
(cd order6 && for f in *.svg; do rsvg-convert -f pdf -o "${f%.svg}.pdf" "$f"; done)
(cd order7 && for f in *.svg; do rsvg-convert -f pdf -o "${f%.svg}.pdf" "$f"; done)
```

- `sheet.py`: the shared geometry (bends at JLCCNC's radii, the stack, the cap); `round2.py`–`round7.py` each change
  the round before; `order6.py` exports round 6's order set, `round7.py` the parts round 7 changes.
- `check6.py`, `check7.py`: interference and clearance checks; `check7.py` adds the pivot's and cap screws' parts, their
  clearance to the driver board, and PEM's edge distances. `leaks.py`, `spill_rays.py`, `door5.js`, `beam6.js`:
  the light-leak and beam studies behind D21–D23. `thermal_sheet.py`: the heat budget.
- Renders, review pages and earlier rounds' STEPs stay in `build/heatsink/housing/sheet/` (git-ignored).
