# Housing (sheet metal, round 7)

The square sheet-metal lamp: round 7 is the design of record (DESIGN.md D21–D24, D30–D33). It is round 6, which was quoted
on 2026-11-16 (PRODUCTION.md, Orders), with every fastener a real part, four nuts in the cap's back for a box, and a
12 mm bore down the stack for the LED plugs: the shell, cap, yoke, plate, fins and spacers changed. These are the scripts
that build it and the files to order it from.

| Part | Shop | Material, finish | Per lamp |
| --- | --- | --- | --- |
| shell, cap, hood | JLCCNC sheet metal | Al 5052 1.5 mm, black powder coat | 1 each |
| door | JLCCNC sheet metal | Al 5052 1.0 mm, black powder coat | 4 |
| yoke | JLCCNC sheet metal | Al 5052 3 mm, black powder coat | 1 |
| plate, fin, spacer | JLCCNC sheet metal | Al 5052 3 mm, bare | 1, 4, 8 |
| carrier (+0.5, +1.0 mm for the focus test) | JLC3DP | MJF PA12, dyed black | 1 |

`order6/` holds one STEP per part (`rgb-spotlight-r6-<part>.step`) and the two drawings JLCCNC needs with them:
`rgb-spotlight-plate-threads.pdf` (10 × M3 threads in the plate) and `rgb-spotlight-cap-press-nuts.pdf` (round 6's cap).
`order7/` holds what round 7 changes, to be ordered in place of round 6's: the shell, cap, yoke, plate, fin and spacer
(`rgb-spotlight-r7-<part>.step`), the cap's drawing (8 press nuts: 2 × M3 and 2 × M4 in the rims, 4 × M3 in the back
face) and the plate's (10 × M3 threads, Ø12 middle hole). Only the hood, the door and the carriers stay round 6's.

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

**The heat stack (round 7, D32).** Three tie rods at r 11 (30° / 150° / 270°) hold the plate, the eight spacers and the
four fins together and carry the driver. Bought parts, per lamp:

| Part | What | Per lamp |
| --- | --- | --: |
| tie stud | M3 threaded rod (DIN 976-1), cut to 45 mm (up to 47 fits), with medium thread-lock in the plate | 3 |
| washer | DIN 125-A 3.2, steel, 7 × 0.5 | 3 |
| nut | ISO 4032 M3, steel: this clamps the stack | 3 |
| standoff | polyamide hex, M3 female-female × 12, on the 3.3 mm of stud behind the nut | 3 |
| driver screw | polyamide pan head M3 × 6, from the back | 3 |
| LED screw | ISO 7380 M3 × 20, black: through the hood, the carrier and the LED board into the plate (75° / 195° / 315°) | 3 |
| shell screw | ISO 7380 M3 × 6: the shell's face to the plate's corner threads | 4 |
| door pin | ISO 7380 M3 × 8 with an M3 nylock nut (D27) | 8 |

Thermal paste goes under the LED board, between the plate and the shell's face, and between the plate, spacers and fins
(`thermal_sheet.py` counts on greased joints). Earlier rounds drew a 15 mm nylon standoff as the stack's nut and no driver
screws; the steel nut moves the driver 0.1 mm forward (its front face 14.9 mm behind the stack). `check7.py` prints every
thread length and what sticks out where.

Assembly order:
1. Studs into the plate's three r 11 threads from the back, with thread-lock, their ends 0.2 mm below the plate's front
   face and never above it: the LED board lies there.
2. Onto the studs with a film of paste: two spacers, a fin, four times. Washers and nuts, tightened evenly (about
   0.5 N·m), then the standoffs against the nuts.
3. The stack into the shell from the back, paste on the plate's front rim; four M3 × 6 through the shell's face.
4. LED board on the plate with paste, turned 45° (D23), its three wire pairs behind it; each pair's XH plug through the
   stack's 12 mm bore, one at a time (D33). Carrier, lenses, hood; three M3 × 20. They clamp the LED board
   through the lens flanges and the carrier, so tighten them evenly.
5. Plug red into J3, green into J4, blue into J5; seat the driver on the standoffs, three polyamide M3 × 6 from the back.
6. Door pins and nylocks; cables through the cap's cut-outs, cap in, two M3 × 6; yoke, washers and knobs.

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
python3 drawings_sheet.py order7
(cd order7 && for f in *.svg; do rsvg-convert -f pdf -o "${f%.svg}.pdf" "$f"; done)
```

- `sheet.py`: the shared geometry (bends at JLCCNC's radii, the stack, the cap); `round2.py`–`round7.py` each change
  the round before; `order6.py` exports round 6's order set, `round7.py` the parts round 7 changes.
- `check6.py`, `check7.py`: interference and clearance checks; `check7.py` adds every fastener as its real part (pivot,
  cap, back nuts, heat stack), their clearance to the driver, thread lengths, and PEM's edge distances. `leaks.py`, `spill_rays.py`, `door5.js`, `beam6.js`:
  the light-leak and beam studies behind D21–D23. `thermal_sheet.py`: the heat budget.
- Renders, review pages and earlier rounds' STEPs stay in `build/heatsink/housing/sheet/` (git-ignored).
