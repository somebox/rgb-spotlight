# Production

Status (2026-11-16): the driver released as v2.2 (D5, a clamp on the data input, DESIGN D28, and R11, which takes D5's current off the +5V rail, D29) and the LED board as v2.0 (`releases/`). The first order, [2026-11-16-v2-first](production/orders/2026-11-16-v2-first/ORDER.md), pins driver v2.2 and is in the JLC cart, unpaid, still with driver v2.1 (Y174) beside v2.0's (Y173): both are to go, v2.2 to come in, before paying. The housing moved to round 7 (DESIGN D30): the cart's round-6 shell, cap and yoke are to be replaced by `mech/housing/order7/`'s and quoted again. 2 of each board assembled, and the round-6 housing (sheet metal and optic carriers) for 5 lamps. The LED polarity is settled (diode test on v1, below).

How to order, what it costs, and a dated log of quotes and orders (newest first).

## Order files

Orders go through pcb-kit's release flow, set up in `pcbkit.toml`:

1. `pcbkit release --dry-run`, then `pcbkit release`.
   - It checks each board (ERC, DRC with parity, nothing unconnected). A board that changed since its last release gets the next version (v2.0, then v2.0.1), stamped into its title block, its root schematic and its silkscreen label ("RGB Spotlight driver v2.0", "RGB LED v2.0").
   - It writes `releases/<board>/v<version>/`, which is committed and never rewritten.
   - KiCad must have the boards closed.
2. Create an order, `production/orders/<date>-<what>/order.toml`, pinning each board's version and recording events: draft, submitted, shipped, received, problem.
3. `pcbkit production` writes the order's ORDER.md and `upload/` folder, and the overview at the end of this page. Upload from `upload/`.

Each release folder holds:
- `GERBER-<board>-v<version>.zip`;
- the JLC BOM and CPL (`-front`, `-back`, `-both`), with the "JLCPCB Part #" column and rotation corrections from pcb-kit's table;
- `PLACEMENT-<board>-jlcpcb.md`, the checklist for JLC's placement preview (below);
- `schematic.pdf`, `board.pdf` and `MANIFEST.txt`.

`scripts/make_fab.sh <driver|led>` still writes unversioned files into `build/fab/<board>/` (git-ignored), to look at before releasing.

| Board | PCB | Assembly |
| --- | --- | --- |
| **driver** | FR4, 2 layers, 1.6 mm, 1 oz, 50 mm round (`disc50`) | Top side: 33 placements, 19 BOM lines. J1/J2 (JST XH, back) and J3 (JST PH 6, front) are through-hole: JLC THT assembly, or hand-solder. R9 is DNP (no LCSC number, out of the BOM) |
| **led** | **aluminium**, 1 layer, 1.6 mm, 1 W/mK (2 W/mK if offered cheaply), 50 mm round | Top side: 3 placements (the LEDs) |

The LED board's Gerber zip also holds empty back layers; on a 1-layer aluminium order JLC uses only F.Cu, F.Mask, F.Silkscreen, Edge.Cuts and the drill files.

## Order checklist

The things that went wrong before, or could:

- **LED polarity (LED board).** Pad 1 = cathode, at −x of the footprint (DESIGN.md §6.1).
  - Settled 2026-11-16: a diode test on v1's LED1 (C49237857, the same red part) lit it with + on pad 2 (the L1 side) and − on pad 1. All three datasheets (SURC/UGC/UBC) agree: pad ① cathode, pad ② anode, the package dot by pad ②.
  - In JLC's placement preview, read each LED's own pink + and − against the silk "+" (D19), colour by colour. On 2026-11-16 JLC drew the green and blue (C49237859, C49237860) a half turn from the red on the same footprint, and they were turned by hand; pcb-kit's table now does it (branch `jlc-rotations-spotlight`).
  - Order remark: "LED1–LED3 (HD2525): cathode = pad 1, the side away from the package dot. The + on the silk marks the anode."
- **Schottky D1–D3 (SOD-123).** The cathode band faces the 12 V side (Rs / VIN). Inverted, the diode shorts SW to 12 V.
- **TVS D4 (SMA).** The cathode band goes to +12V. Inverted, it conducts the moment 12 V is applied.
- **Clamp D5 (SOD-323, from driver v2.1).** The cathode band (pad 1) goes to +5V, towards the board edge; the anode joins R7/R10. Inverted, it holds the data input high and the light gets no data. No rotation rule covers `D_SOD-323`, so the CPL has KiCad's angle (270°). On 2026-11-16 (Y174) the preview showed it right: the band and JLC's − on the pad hovering at (−13.83, 19.15), pad 1 at (−13.80, 19.00), towards the board edge; the + on pad 2 at (−13.83, 16.83). Check it again on each order: with no rule, nothing in pcb-kit records the check.
- **Placement checklist first.** On 2026-11-16 the preview showed:
  - `^SOT-89` +180° right for U2–U4 (PT4115, SOT-89-5) and U5 (78L05, SOT-89-3);
  - `^SOT-353` +180° a quarter turn out for U7 (74AHCT1G125): turned +90 by hand. pcb-kit's rule is now −90.
  The v2.0 release's CPLs and driver v2.1's and v2.2's (released before the kit's fix was merged) carry the old angles for U7 and LED2/LED3, so check those three by hand on every order from them. On Y174 (driver v2.1) U7 came out as on v2.0 (pin 1 at −8.94, 18.04) and was turned +90 by hand (pin 1 then at −10.58, 17.26).
- **PT4115 U2–U4 (SOT-89-5).** Pin 1 is SW. The tab must sit on the wide GND pad, not rotated 180°.
- **U1 (SOIC-8), U6 (SOIC-14).** The SOIC rule (+270°) was checked on 2026-10-26 and right here on 2026-11-16. Still check the pin-1 dots; v1 used EasyEDA footprints, these are KiCad's.
- **J1/J2 (JST XH, back).** They are in the `-back` BOM/CPL and the `-both` files. For a top-only order, hand-solder them (through-hole).
- **BOM matching.** JLC must say "Your BOM: JLCPCB Part #". With an `LCSC` header it matches by value instead (pcb-kit lesson).
- **Order number:** JLC no longer offers "specify position": choose Remove Mark, with a PCB remark that the `JLCJLCJLCJLC` on the driver's back silk is an old placeholder to leave off.
- **Stock:** `bomi --project boards/driver list --check` and the same for `boards/led`. On 2026-11-16 the LEDs had 2,570 red, 2,475 green and 3,102 blue, and the scarcest driver part was U7 at 13,391.
- **Assembly options at JLC (2026-11-16):** aluminium boards get Standard PCBA only, with JLC's 5 mm edge rails on a board under 70 mm; the driver gets Economic. JLC's quote page now defaults to OSP: choose HASL with lead. JLC flags the blue LED (C49237860) "difficult to process" and leaves it unticked: tick it.

## After the boards arrive

- **LED harness:** six 24 AWG wires with thin high-temperature insulation, at most 1.5 mm across (fluoropolymer, such as Alpha Wire ThermoThin 2924), about 8 cm, twisted per colour (D24).
  - Not silicone: 24 AWG silicone wire is 1.5–2.0 mm across, too thick for the contact's insulation crimp (0.8–1.5 mm), and six of them leave no room for the sleeve in the 6.4 mm hole.
  - Solder them to the LED board's pads (R+ R− G+ G− B+ B−) and pass them through the centre hole.
  - Crimp them into a JST PHR-6 housing (C157952) with SPH-002T-P0.5S contacts (C111515) in the same order, pin 1 = R+.
  - Or buy ready-made PH 6-pin leads with loose ends (often 26 AWG, enough at 0.45 A per LED): pass the loose ends forward through the stack and the hole, and solder them to the LED board last.
  - Aluminium boards pull heat away fast, so use a hot iron or preheat.
- **Chain cables:** JST XH 3-pin, wired pin 1 to pin 1 (D4). Up to 5 lights per 12 V feed, up to 3 m apart on 22 AWG, with a 3 A fuse at the supply end (D14, D15). Between groups, leave pin 1 open.
- **Assembly:** nylon washers or screws on the driver; a sleeve or grommet on the harness through the LED board's hole (D20).
- **Bring-up:**
  - 12 V with a current-limited supply at 0.6 A for one light: 0.42 A expected at full white.
  - Check 5 V at U1 pin 8, then the DIM pins with data.
  - Listen for the 4 kHz singing noted in DESIGN.md §2.7.

## Costs

| Date | Board | Qty | Item | Cost |
| --- | --- | --- | --- | --- |
| 2026-11-16 | all | — | One JLC cart with driver v2.1 (Y174) and without v2.0's (Y173): boards 87.24 + sheet metal 156.95 + carriers 26.65 = 270.84; DHL 98.36 (5.23 kg), coupon −6.00. Threads and press nuts still to be priced by JLCCNC | $363.20 |
| 2026-11-16 | driver v2.1 | 5 PCBs / 2 assembled | Y174: PCB 4.00 (HASL with lead) + Economic PCBA SMT026111664196 35.60 (setup 8.24, stencil 1.55, parts 4.70 for 20 lines, Extended 15.45 for 5 types: D5 (C7502691) is listed Extended but added no fee, SMT 0.54, placement check 0.45, J3 hand-soldering 3.61 + manual 0.20, nitrogen 0.86). Same options as Y173 | $39.60 |
| 2026-11-16 | boards | — | The two boards alone with driver v2.1: 87.24 + DHL 26.97 − coupon 6.00 (0.62 kg) | $108.21 |
| 2026-11-16 | all | — | The same cart with driver v2.0 (Y173), before v2.1: boards 86.90, total 270.50 + DHL 98.36 − 6.00 | $362.86 |
| 2026-11-16 | carriers | 7 | JLC3DP MJF PA12-HP dyed black: 5 standard 18.65, +0.5 mm 3.91, +1.0 mm 4.09 (D2026111615500272, -280, -287) | $26.65 |
| 2026-11-16 | housing | 5 lamps | JLCCNC sheet metal, Al 5052, round 6 (SMS2611163003158 … 3204); by part below | $156.95 |
| 2026-11-16 | driver v2.0 | 5 PCBs / 2 assembled | Y173, still in the cart for the user to remove: PCB 4.00 (HASL with lead) + Economic PCBA 35.26 (setup 8.24, stencil 1.55, parts 4.43, Extended 15.45 for 5 types, SMT 0.47, placement check 0.45, J3 hand-soldering 3.61 + manual 0.20, nitrogen 0.86) | $39.26 |
| 2026-11-16 | led | 5 PCBs / 2 assembled | Y172: PCB 4.00 (aluminium, 1 W/mK, HASL with lead) + Standard PCBA 43.64 (setup 25.75, stencil 8.27, parts 3.94, feeder loading 4.65, SMT 0.08, placement check 0.45, packaging 0.50) | $47.64 |
| 2026-11-16 | boards | — | The two boards alone with driver v2.0: 86.90 + DHL 26.97 − coupon 6.00 (0.62 kg) | $107.87 |
| 2026-11-14 | driver | 1 | BOM, bomi qty-1 pricing, after D17/D18 (prices refreshed) | ≈ $1.70 plus the Extended-part fees listed in docs/BOM_driver.md |
| 2026-11-14 | led | 1 | BOM, bomi qty-1 pricing | ≈ $0.79 (3 Extended LEDs) |
| 2026-10-05 | driver | 1 | BOM, bomi qty-1 pricing | ≈ $2.18 plus the Extended-part fees listed in docs/BOM_driver.md |
| 2026-10-05 | led | 1 | BOM, bomi qty-1 pricing | ≈ $0.77 (3 Extended LEDs) |

**Housing quote (JLCCNC, 2026-11-16), 5 lamps.** Black matte powder coat (D25) except the bare stack parts; files in `mech/housing/order6/`. The review's estimates matched to the cent except the doors.

| Part | Qty | Finish | JLCCNC | Review estimate |
| --- | --: | --- | --: | --: |
| shell (1.5 mm) | 5 | powder coat | 31.40 | 31.40 |
| cap (1.5 mm), 2 × M3 + 2 × M5 press nuts by drawing | 5 | powder coat | 12.00 + nuts after review | 12.00 |
| hood, 78 mm (1.5 mm) | 5 | powder coat | 19.55 | ≈ 19.55 |
| door (1.0 mm) | 20 | powder coat | 44.00 | ≈ 32.80 |
| yoke (3 mm) | 5 | powder coat | 13.30 | 13.30 |
| plate (3 mm), 10 × M3 threads by drawing | 5 | bare | 5.70 + threads after review | |
| fin (3 mm) | 20 | bare | 15.40 | 36.70 for plate, fins and spacers |
| spacer (3 mm) | 40 | bare | 15.60 | |
| **Sheet metal** | | | **156.95** | ≈ 145.75 |

**Round 7 (D30), not yet quoted.** The yoke pivot as real parts: the shell and yoke get Ø4.5 holes (were 5.5), and the cap 2 × PEM S-M4-2 nuts (hole 5.41) in rims 1.5 mm longer, instead of M5 nuts in 7.14 mm holes 6.0 mm from the edge, which PEM's M5 nut (SS-M5: hole 6.35, 7.1 mm from the edge) can't meet. Files: `mech/housing/order7/` (shell, cap, yoke and the cap's drawing); the rest stays round 6's. Bought for the pivot, per lamp: 2 × Elesa VC.692/25 p-M4x10 knob, 2 × DIN 9021 and 2 × DIN 125 polyamide M4 washers, and 2 × ISO 7380 M3 × 6 for the cap (the order's extras).

Hand-soldered on each assembled driver: J1 and J2 (JST B3B-XH-A, C144394, on the back). JLC solders J3.

## Overview

<!-- pcbkit:production:begin -->
<!-- generated by pcbkit production from the boards' releases.toml, production/orders/*/order.toml and production/stock.toml: edit those, then run it again -->

### In production

| order | PCB | version | house | PCBs / assembled | status | order no. | price | last note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [2026-11-16-v2-first](production/orders/2026-11-16-v2-first/ORDER.md) | driver | v2.2 | JLCPCB | 5 / 2 | draft 2026-11-16 |  | 39.60 USD |  |
| [2026-11-16-v2-first](production/orders/2026-11-16-v2-first/ORDER.md) | led | v2.0 | JLCPCB | 5 / 2 | draft 2026-11-16 |  | 47.64 USD |  |

### Boards

| PCB | in KiCad | released | state | parts a board (USD) | latest order | in stock | parts on hand build |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [driver](boards/driver) | v2.2 | v2.2 2026-11-16 | released | 1.83, 7 ext. | 2026-11-16-v2-first: draft |  |  |
| [led](boards/led) | v2.0 | v2.0 2026-11-16 | released | 0.79, 3 ext. | 2026-11-16-v2-first: draft |  |  |

Parts costs: placed parts at unit prices from konnect's JLC parts cache of 2026-11-03; Extended parts add a setup fee each per order.

### Parts for the open orders

To finish every board of the open orders by hand: the assembled ones, or every PCB of a bare order (with the parts the assembler would have placed), as the versions they pin need; and the orders' extras.

| part | needed | on hand | to buy | where |
| --- | --- | --- | --- | --- |
| B3B-XH-A(LF)(SN) (JST), 3-pin XH vertical | 4 | 0 | 4 | LCSC C144394 |
| Elesa VC.692/25 p-M4x10 (code 166132), five-lobe knob D25, M4 x 10 zinc-plated steel stud | 10 | 0 | 10 | Elesa or a distributor |
| Housing sheet metal for 5 lamps (round 7) | 1 | 0 | 1 | JLCCNC, in the JLC cart (SMS2611163003158 ... SMS2611163003204, round 6: the shell, cap and yoke to be replaced by round 7's) |
| Optic carrier, MJF PA12 dyed black | 7 | 0 | 7 | JLC3DP, in the JLC cart (D2026111615500272, -280, -287) |
| Screw ISO 7380 M3 x 6, button head | 10 | 0 | 10 | any |
| Washer DIN 125-A 4.3 (M4), polyamide, 4.3 x 9 x 0.8 | 10 | 0 | 10 | any |
| Washer DIN 9021 4.3 (M4), steel, 4.3 x 12 x 1.0 | 10 | 0 | 10 | any |

### Orders

| order | what | status | last event |
| --- | --- | --- | --- |
| [2026-11-16-v2-first](production/orders/2026-11-16-v2-first/ORDER.md) | driver v2.2 and LED board v2.0, 2 of each assembled, with the round-7 housing for 5 lamps | draft | 2026-11-16 |

### Problems

_none_

<!-- pcbkit:production:end -->
