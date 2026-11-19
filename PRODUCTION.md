# Production

Status (2026-11-18): the driver released as v2.4 (D5, a clamp on the data input, DESIGN D28; R11, which takes D5's current off the +5V rail, D29; three JST XH 2-pin LED sockets, D33; R10 rated 200 mW for a feed voltage held on the data pin, D34) and the LED board as v2.0 (`releases/`); the LED board for 3.5 mm LEDs, `led35` v1.0, released on 2026-11-18 to be bought bare (D35; 10 in the JLC cart, Y202, and its LEDs in the LCSC cart). The first order, [2026-11-16-v2-first](production/orders/2026-11-16-v2-first/ORDER.md), pins driver v2.4 and is in the JLC cart, unpaid. In the cart: driver v2.4 (Y200, re-saved on 2026-11-18 from Y185, which replaced v2.3's Y180 on 2026-11-17), LED board v2.0 (Y198, re-saved from Y181), 10 bare led35 boards (Y202), and the round-7 shell, cap, yoke, plate, fins and spacers (DESIGN D30–D33, `mech/housing/order7/`) in place of round 6's, $385.90 with DHL before JLCCNC prices the threads and press nuts. All 5 of each board assembled (decided 2026-11-17), and the housing (round 7 with round 6's hood and doors) and optic carriers for 5 lamps. The LED polarity is settled (diode test on v1, below).

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
| **driver** | FR4, 2 layers, 1.6 mm, 1 oz, 50 mm round (`disc50`) | Top side: 37 placements, 21 BOM lines (v2.4). J1/J2 (JST XH 3, back) and J3–J5 (JST XH 2, front) are through-hole: JLC THT assembly, or hand-solder. R9 is DNP (no LCSC number, out of the BOM) |
| **led** | **aluminium**, 1 layer, 1.6 mm, 1 W/mK (2 W/mK if offered cheaply), 50 mm round | Top side: 3 placements (the LEDs) |
| **led35** | as the LED board | None: bought bare, its release holds Gerbers only (`assembly = false` in `pcbkit.toml`). The LEDs are soldered by hand (After the boards arrive) |

The LED board's Gerber zip also holds empty back layers; on a 1-layer aluminium order JLC uses only F.Cu, F.Mask, F.Silkscreen, Edge.Cuts and the drill files.

## Order checklist

The things that went wrong before, or could:

- **LED polarity (LED board).** Pad 1 = cathode, at −x of the footprint (DESIGN.md §6.1).
  - Settled 2026-11-16: a diode test on v1's LED1 (C49237857, the same red part) lit it with + on pad 2 (the L1 side) and − on pad 1. All three datasheets (SURC/UGC/UBC) agree: pad ① cathode, pad ② anode, the package dot by pad ②.
  - In JLC's placement preview, read each LED's own pink + and − against the silk "+" (D19), colour by colour. On 2026-11-16 JLC drew the green and blue (C49237859, C49237860) a half turn from the red on the same footprint, and they were turned by hand; pcb-kit's table now does it (branch `jlc-rotations-spotlight`).
  - Order remark: "LED1–LED3 (HD2525): cathode = pad 1, the side away from the package dot. The + on the silk marks the anode."
- **Schottky D1–D3 (SOD-123).** The cathode band faces the 12 V side (Rs / VIN). Inverted, the diode shorts SW to 12 V.
- **TVS D4 (SMA).** The cathode band goes to +12V. Inverted, it conducts the moment 12 V is applied.
- **Clamp D5 (SOD-323, from driver v2.1).** The cathode band (pad 1) goes to +5V, towards the board edge; the anode joins R7/R10. Inverted, it holds the data input high and the light gets no data. No rotation rule covers `D_SOD-323`, so the CPL has KiCad's angle (270°). On 2026-11-16 (Y174) the preview showed it right: the band and JLC's − on the pad hovering at (−13.83, 19.15), pad 1 at (−13.80, 19.00), towards the board edge; the + on pad 2 at (−13.83, 16.83). The same on Y179 (v2.3) and Y185 (v2.4): − at (−13.8, 19.1). Check it again on each order: with no rule, nothing in pcb-kit records the check.
- **LED sockets J3–J5 (JST XH 2, C158012, from driver v2.3).** Pin 1, the square pad, is the LED's + (D33). The plug is keyed to the socket's body, so a socket turned half a turn puts the plug's + on pad 2 and reverses that LED. No rotation rule covers `JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical`, so the CPL has KiCad's angle. On 2026-11-16 (Y179) JLC drew all three half a turn from KiCad's footprint: the body reached 3.4 mm from the pins on the side where KiCad's reaches 2.35, the wall slots faced the other way, and J4 and J5 lay over L2's and L3's outlines. Turned 180 by hand (Rotate Left twice): then each body filled its silkscreen outline, by the pin-1 corner mark. The same on Y180 and Y185 (v2.4). Check them on every order until pcb-kit has a rule for the footprint.
- **Placement checklist first.** On 2026-11-16 the preview showed:
  - `^SOT-89` +180° right for U2–U4 (PT4115, SOT-89-5) and U5 (78L05, SOT-89-3);
  - `^SOT-353` +180° a quarter turn out for U7 (74AHCT1G125): turned +90 by hand. pcb-kit's rule is now −90.
  The v2.0 release's CPLs and driver v2.1's, v2.2's, v2.3's and v2.4's (released before the kit's fix was merged; v2.4's CPL is v2.3's) carry the old angles for U7 and LED2/LED3, so check those three by hand on every order from them. On Y174 (driver v2.1) U7 came out as on v2.0 (pin 1 at −8.94, 18.04) and was turned +90 by hand (pin 1 then at −10.58, 17.26). On Y179 (driver v2.3) the same: after the turn pin 1 at (−10.57, 17.27), against the checklist's (−10.438, 17.250). On Y185 (driver v2.4) the same again.
- **PT4115 U2–U4 (SOT-89-5).** Pin 1 is SW. The tab must sit on the wide GND pad, not rotated 180°.
- **U1 (SOIC-8), U6 (SOIC-14).** The SOIC rule (+270°) was checked on 2026-10-26 and right here on 2026-11-16. Still check the pin-1 dots; v1 used EasyEDA footprints, these are KiCad's.
- **J1/J2 (JST XH, back).** They are in the `-back` BOM/CPL and the `-both` files. For a top-only order, hand-solder them (through-hole).
- **BOM matching.** JLC must say "Your BOM: JLCPCB Part #". With an `LCSC` header it matches by value instead (pcb-kit lesson).
- **Order number:** JLC no longer offers "specify position": choose Remove Mark, with a PCB remark that the `JLCJLCJLCJLC` on the driver's back silk is an old placeholder to leave off.
- **Stock:** `bomi --project boards/driver list --check` and the same for `boards/led`. On 2026-11-16 the LEDs had 2,570 red, 2,475 green and 3,102 blue, and the scarcest driver part was U7 at 13,391. On 2026-11-17, live at JLC: U7 (C350557) 1,086 in stock, 846 to order; R10's new part (C427241) 14,393; every other driver part above 59,000.
- **Assembly options at JLC (2026-11-16):** aluminium boards get Standard PCBA only, with JLC's 5 mm edge rails on a board under 70 mm; the driver gets Economic. JLC's quote page now defaults to OSP: choose HASL with lead. JLC flags the blue LED (C49237860) "difficult to process" and leaves it unticked: tick it.

## After the boards arrive

- **LED harness:** six 24 AWG wires with thin high-temperature insulation, at most 1.5 mm across (fluoropolymer, such as Alpha Wire ThermoThin 2924), about 8 cm, twisted per colour (D24), a pair per LED with its own JST XH 2-pin plug (D33).
  - Not silicone: 24 AWG silicone wire is 1.5–2.0 mm across, and six of them leave no room for the sleeve in the LED board's 6.4 mm hole. (The XH contact itself takes insulation up to 1.9 mm.)
  - Crimp each pair into a JST XHP-2 housing (C144401) with SXH-001T-P0.6 contacts (C140573), pin 1 = +. Red goes to J3, green to J4, blue to J5.
  - Or buy ready-made XH 2-pin leads with loose ends (26 AWG is enough at 0.45 A per LED).
  - Pass the loose ends through the LED board's centre hole from behind and solder them to its pads (R+ R− G+ G− B+ B−). The plugs then go back through the heat stack's 12 mm bore one at a time.
  - Aluminium boards pull heat away fast, so use a hot iron or preheat.
- **The bare boards for 3.5 mm LEDs (`led35`, D35):** any 3535 LED with two side pads and a centre slug fits; R, G and B on the board name the driver's channels, whatever colour is fitted.
  - Soldering: paste on the three pads, then a hot plate or hot air from below. The slug pad can't be reached with an iron, and the aluminium takes an iron's heat away. The side pads stand 0.15 mm out from the body, for a probe or a touch-up.
  - Polarity: pad 2, by the silkscreen "+", is the anode. The makers mark it differently (the columns below), so diode-test one of each type before soldering.
  - Current: the driver gives about 455 mA (Rs 0.22 Ω). Every part below takes that. A part limited to 350 mA (XINGLIGHT's XL-HD3535 family) needs Rs 0.33 Ω on its channel, about 303 mA.
  - Height: 1.67–2.25 mm against the HD2525's 2.1, all inside the lens's cavity. Whether the focus moves with another dome hasn't been tried: the +0.5 and +1.0 mm carriers are there for that.
  - Datasheets read at LCSC on 2026-11-18, stock and prices from LCSC the same day:

  | Colour | Part | LCSC | Max. current | Vf at 350 mA | Height | Polarity mark | USD each, smallest lot | Stock |
  | --- | --- | --- | --: | --: | --: | --- | --: | --: |
  | deep red, 665 nm | Hongli HL-C3535F15R3GA-ZW | C5445086 | 800 mA | 2.5 V (listing) | 2.15 | dot by the anode; + on the left in the top view | 0.53 | 5,401 |
  | far red, 730–740 nm | JNJ LTHI0113W120 | C19185882 | 1000 mA | 1.8 V | 2.1 | ① cathode, + and a dot by ② | 0.73 | 128 |
  | amber, 590 nm | Silverlight M3535O1YG6G12 | C22466168 | 700 mA typical, 1000 max | 2.0–3.6 V | 2.25 | − left, + right in the top view | 0.41 | 750 |
  | warm white, 2870–3220 K | Hongli HL-C3535F77W1KA(Ra1)-FC | C19184447 | 1000 mA peak; 700 mA with the solder point under 85 °C | 2.85 V (listing) | 2.25 | + on the left in the top view | 0.33 | 985 |
  | neutral white, 3710–4260 K | Hongli HL-C3535F77W1KA(Ra1)-FC | C19184448 | as the warm white | 3.15 V (listing) | 2.25 | as the warm white | 0.31 | 520 |
  | cool white, 5500–6500 K | JNJ LTJW0115T140 | C19185883 | 1500 mA | 3.2 V | 2.1 | ① cathode | 0.57 | 2,415 |
  | green, 525–530 nm | JNJ LEHG0113W120 | C19185875 | 1000 mA | 3.2 V | 1.67 | ① cathode, a corner mark by ① | 0.32 | 610 |
  | red, 620–630 nm | JNJ LEHR0111W120 | C19185876 | 700 mA | 2.0 V | 1.67 | ① cathode, a corner mark by ① | 0.21 | 985 |
  | blue, 455 nm | JNJ 3535AW120C-45045-S-G1 | C25170647 | 1000 mA | 3.0 V | 2.1 | ① cathode, + and a dot by ② | 1.03 | 704 |

  - Left out: the 30° parts (JNJ LTJB0115W30, C19185864, and its like) are 4.09 mm tall and number the anode ①; XINGLIGHT's warm white (C3646954) had no stock, and its red (C3646952) is limited to 350 mA. Ultraviolet and infrared parts fit the pads too, but behind a collimating lens they are an eye hazard.
- **Chain cables:** JST XH 3-pin, wired pin 1 to pin 1 (D4). Up to 5 lights per 12 V feed, up to 3 m apart on 22 AWG, with a 3 A fuse at the supply end (D14, D15). Between groups, leave pin 1 open.
- **Assembly:** the housing's fasteners and the order to fit them are in [mech/housing/README.md](mech/housing/README.md) (D30, D32): the driver sits on polyamide standoffs with polyamide screws (D20). A sleeve or grommet on the harness through the LED board's hole (D20).
- **Bring-up:**
  - 12 V with a current-limited supply at 0.6 A for one light: 0.42 A expected at full white.
  - Check 5 V at U1 pin 8, then the DIM pins with data.
  - Listen for the 4 kHz singing noted in DESIGN.md §2.7.

## Costs

| Date | Board | Qty | Item | Cost |
| --- | --- | --- | --- | --- |
| 2026-11-18 | all | — | The JLC cart with 10 bare led35 boards added: boards 102.31 (driver Y200 49.66, LED board Y198 47.65, led35 Y202 5.00) + sheet metal 157.95 + carriers 26.65 = 286.91; DHL 104.99 (5.51 kg), coupon −6.00; ships about 2026-11-24. Threads and press nuts still to be priced by JLCCNC | $385.90 |
| 2026-11-18 | led35 | 10 PCBs / bare | Y202: aluminium, 1 layer, 1 W/mK, 3000 V, white mask, black silkscreen, HASL with lead, no assembly | $5.00 |
| 2026-11-18 | driver v2.4, led | 5 / 5 each | Re-saved by another session on 2026-11-18, in place of Y185 and Y181: driver Y200 (PCB 4.00 + Economic PCBA SMT026111864042 45.66) and LED board Y198 (PCB 4.00 + Standard PCBA SMT026111864021 43.65) | $97.31 |
| 2026-11-18 | boards | — | The three boards alone: 102.31 + DHL 26.97 − coupon 6.00 (0.90 kg) | $123.28 |
| 2026-11-18 | parts | 60 | LCSC cart "nov-2026 message sign": 5 of each of the nine 3535 LEDs for led35 (22.19) and 5 spare HD2525 of each colour for the LED board (3.99), 12 lines | $26.18 |
| 2026-11-17 | all | — | The JLC cart with driver v2.4 (Y185) in place of v2.3, LED board Y181, both fully assembled, and the round-7 housing: boards 97.30 + sheet metal 157.95 + carriers 26.65 = 281.90; DHL 98.36 (5.30 kg), coupon −6.00; ships about 2026-11-23. $4.11 more than with v2.3. Threads and press nuts still to be priced by JLCCNC | $374.26 |
| 2026-11-17 | driver v2.4 | 5 PCBs / 5 assembled | Y185: PCB 4.00 (HASL with lead) + Economic PCBA SMT026111765268 45.66 (setup 8.24, stencil 1.55, parts 10.72 for 21 lines, Extended 18.54: R10 (C427241) adds 3.09, SMT 1.11, placement check 0.45, J3–J5 hand-soldering 3.61 + manual 0.53, nitrogen 0.91). Same options as Y180 | $49.66 |
| 2026-11-17 | boards | — | The two boards alone with driver v2.4: 97.30 + DHL 26.97 − coupon 6.00 (0.69 kg) | $118.27 |
| 2026-11-17 | all | — | The JLC cart with both boards fully assembled, driver v2.3 Y180 (replaced by v2.4) and LED board Y181, and the round-7 housing: boards 93.19 + sheet metal 157.95 + carriers 26.65 = 277.79; DHL 98.36 (5.30 kg), coupon −6.00; ships about 2026-11-23. $5.78 more than 2 of each. Threads and press nuts still to be priced by JLCCNC | $370.15 |
| 2026-11-17 | driver v2.3 | 5 PCBs / 5 assembled | Y180, replaced by v2.4 (Y185) on 2026-11-17: PCB 4.00 (HASL with lead) + Economic PCBA SMT026111666618 41.55 (setup 8.24, stencil 1.55, parts 9.75 for 21 lines, Extended 15.45, SMT 1.06, placement check 0.45, J3–J5 hand-soldering 3.61 + manual 0.53, nitrogen 0.91). Same options as Y179 | $45.55 |
| 2026-11-17 | led | 5 PCBs / 5 assembled | Y181: PCB 4.00 (aluminium, 1 W/mK, HASL with lead) + Standard PCBA SMT026111666632 43.64 (setup 25.75, stencil 8.27, parts 3.94, feeder loading 4.65, SMT 0.08, placement check 0.45, packaging 0.50): the same as 2 assembled, as JLC buys 5 of each LED either way. Same options as Y172 | $47.64 |
| 2026-11-17 | boards | — | The two boards alone, fully assembled, with driver v2.3: 93.19 + DHL 26.97 − coupon 6.00 (0.69 kg) | $114.16 |
| 2026-11-16 | all | — | The JLC cart with driver v2.3 (Y179) and the round-7 housing, 2 of each board assembled, the old drivers and round-6 parts removed: boards 87.41 + sheet metal 157.95 + carriers 26.65 = 272.01; DHL 98.36 (5.22 kg), coupon −6.00; ships about 2026-11-22. Threads and press nuts still to be priced by JLCCNC | $364.37 |
| 2026-11-16 | driver v2.3 | 5 PCBs / 2 assembled | Y179, replaced by Y180 (5 assembled) on 2026-11-17: PCB 4.00 (HASL with lead) + Economic PCBA SMT026111666453 35.77 (setup 8.24, stencil 1.55, parts 4.83 for 21 lines, Extended 15.45, SMT 0.55, placement check 0.45, J3–J5 hand-soldering 3.61 + manual 0.23, nitrogen 0.86). Same options as Y174 | $39.77 |
| 2026-11-16 | boards | — | The two boards alone with driver v2.3: 87.41 + DHL 26.97 − coupon 6.00 (0.62 kg) | $108.38 |
| 2026-11-16 | housing | 5 lamps | JLCCNC sheet metal, Al 5052: round 7's shell, cap, yoke, plate, fins and spacers (SMS2611173001134 … 1162, 94.40) with round 6's hood and doors (63.55); by part below | $157.95 |
| 2026-11-16 | all | — | The cart with driver v2.1 (Y174) and round 6, before v2.3 and round 7: boards 87.24 + sheet metal 156.95 + carriers 26.65 = 270.84; DHL 98.36 (5.23 kg), coupon −6.00 | $363.20 |
| 2026-11-16 | driver v2.1 | 5 PCBs / 2 assembled | Y174, removed from the cart for v2.3: PCB 4.00 (HASL with lead) + Economic PCBA SMT026111664196 35.60 (setup 8.24, stencil 1.55, parts 4.70 for 20 lines, Extended 15.45 for 5 types: D5 (C7502691) is listed Extended but added no fee, SMT 0.54, placement check 0.45, J3 hand-soldering 3.61 + manual 0.20, nitrogen 0.86). Same options as Y173 | $39.60 |
| 2026-11-16 | boards | — | The two boards alone with driver v2.1: 87.24 + DHL 26.97 − coupon 6.00 (0.62 kg) | $108.21 |
| 2026-11-16 | all | — | The same cart with driver v2.0 (Y173), before v2.1: boards 86.90, total 270.50 + DHL 98.36 − 6.00 | $362.86 |
| 2026-11-16 | carriers | 7 | JLC3DP MJF PA12-HP dyed black: 5 standard 18.65, +0.5 mm 3.91, +1.0 mm 4.09 (D2026111615500272, -280, -287) | $26.65 |
| 2026-11-16 | housing | 5 lamps | JLCCNC sheet metal, Al 5052, round 6 (SMS2611163003158 … 3204); by part below. Its shell, cap, yoke, plate, fins and spacers were replaced by round 7's | $156.95 |
| 2026-11-16 | driver v2.0 | 5 PCBs / 2 assembled | Y173, removed from the cart for v2.3: PCB 4.00 (HASL with lead) + Economic PCBA 35.26 (setup 8.24, stencil 1.55, parts 4.43, Extended 15.45 for 5 types, SMT 0.47, placement check 0.45, J3 hand-soldering 3.61 + manual 0.20, nitrogen 0.86) | $39.26 |
| 2026-11-16 | led | 5 PCBs / 2 assembled | Y172, replaced by Y181 (5 assembled) on 2026-11-17: PCB 4.00 (aluminium, 1 W/mK, HASL with lead) + Standard PCBA 43.64 (setup 25.75, stencil 8.27, parts 3.94, feeder loading 4.65, SMT 0.08, placement check 0.45, packaging 0.50) | $47.64 |
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

**Round 7 (D30–D33), quoted 2026-11-16 and in the cart** in place of round 6's six parts, with the same material, finishes and quantities. The cap goes with `order7/rgb-spotlight-cap-press-nuts.pdf` and a remark for its 8 nuts, the plate with `order7/rgb-spotlight-plate-threads.pdf` and a remark for its 10 threads; JLCCNC prices both in its review.

| Part | Qty | Finish | JLCCNC | Cart no. | Round 6 |
| --- | --: | --- | --: | --- | --: |
| shell (1.5 mm) | 5 | powder coat | 31.40 | SMS2611173001162 | 31.40 |
| cap (1.5 mm), 6 × M3 + 2 × M4 press nuts by drawing | 5 | powder coat | 12.50 + nuts after review | SMS2611173001134 | 12.00 |
| yoke (3 mm) | 5 | powder coat | 13.30 | SMS2611173001139 | 13.30 |
| plate (3 mm), 10 × M3 threads by drawing | 5 | bare | 5.80 + threads after review | SMS2611173001149 | 5.70 |
| fin (3 mm) | 20 | bare | 15.80 | SMS2611173001150 | 15.40 |
| spacer (3 mm) | 40 | bare | 15.60 | SMS2611173001160 | 15.60 |
| hood and doors, round 6's | 5 + 20 | powder coat | 63.55 | SMS2611163003204, …3181 | 63.55 |
| **Sheet metal** | | | **157.95** | | 156.95 |

The yoke pivot as real parts: the shell and yoke get Ø4.5 holes (were 5.5), and the cap 2 × PEM S-M4-2 nuts (hole 5.41) in rims 1.5 mm longer, instead of M5 nuts in 7.14 mm holes 6.0 mm from the edge, which PEM's M5 nut (SS-M5: hole 6.35, 7.1 mm from the edge) can't meet. The cap's back face also takes 4 × S-M3-2 for a box (D31): 8 press nuts a cap. The plate, fins and spacers get a Ø12 middle hole (was 8) for the LED plugs (D33). Files: `mech/housing/order7/` (shell, cap, yoke, plate, fin, spacer and both drawings); the hood, doors and carriers stay round 6's. Bought for the pivot, per lamp: 2 × Elesa VC.692/25 p-M4x10 knob, 2 × DIN 9021 and 2 × DIN 125 polyamide M4 washers, and 2 × ISO 7380 M3 × 6 for the cap (the order's extras).

Hand-soldered on each assembled driver: J1 and J2 (JST B3B-XH-A, C144394, on the back). JLC solders J3–J5 (JST B2B-XH-A, C158012).

**Other quantities, quoted 2026-11-16/17; decided 2026-11-17: the order stays at 5 lamps with 5 of each board assembled.** Fresh quotes with the cart lines' options, not saved to the cart; USD, before DHL and the coupon.

| | 2 | 5 (in cart) | 10 |
| --- | --: | --: | --: |
| driver v2.3, that many assembled (5 PCBs for 2 and 5, 10 for 10) | 39.77 | 45.55 | 56.15 |
| LED board v2.0, that many assembled (5 PCBs for 2 and 5, 10 for 10) | 47.64 | 47.64 | 52.67 |
| **both boards** | **87.41** | **93.19** | **108.82** |
| shell | 15.98 | 31.40 | 53.00 |
| cap | 8.40 | 12.50 | 19.40 |
| yoke | 8.16 | 13.30 | 21.80 |
| hood | 12.42 | 19.55 | 29.50 |
| doors, 4 a lamp | 18.80 | 44.00 | 86.00 |
| plate | 3.50 | 5.80 | 9.40 |
| fins, 4 a lamp | 7.68 | 15.80 | 29.60 |
| spacers, 8 a lamp | 7.68 | 15.60 | 28.80 |
| **sheet metal for that many lamps** | **82.62** | **157.95** | **277.50** |
| sheet metal a lamp | 41.31 | 31.59 | 27.75 |

- The doors have no volume break: about $2.15 each at every quantity.
- The cap's press nuts and the plate's threads are in none of these prices.
- DHL was read only for the cart as it stands: $26.97 for the boards alone (0.69 kg) and $98.36 with the housing for 5 lamps (5.30 kg), so about $15.5 per kg and 0.9 kg a lamp. From that, 10 of each board would add about $8 of DHL to its $15.63, and 2 lamps instead of 5 would save about $43 of DHL besides $75.33 of sheet metal. Estimates, not quotes.
- The bought hardware (the order's extras) is not quoted. Estimate for 5 lamps: about $84, with the knobs near $2 each, the fasteners in 100-packs about $47 whatever the lamp count, and paste and thread-lock about $15.

## Overview

<!-- pcbkit:production:begin -->
<!-- generated by pcbkit production from the boards' releases.toml, production/orders/*/order.toml and production/stock.toml: edit those, then run it again -->

### In production

| order | PCB | version | house | PCBs / assembled | status | order no. | price | last note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [2026-11-16-v2-first](production/orders/2026-11-16-v2-first/ORDER.md) | driver | v2.4 | JLCPCB | 5 / 5 | draft 2026-11-18 |  | 49.66 USD |  |
| [2026-11-16-v2-first](production/orders/2026-11-16-v2-first/ORDER.md) | led | v2.0 | JLCPCB | 5 / 5 | draft 2026-11-18 |  | 47.65 USD |  |
| [2026-11-16-v2-first](production/orders/2026-11-16-v2-first/ORDER.md) | led35 | v1.0 | JLCPCB | 10 / 0 | draft 2026-11-18 |  | 5.00 USD |  |

### Boards

| PCB | in KiCad | released | state | parts a board (USD) | latest order | in stock | parts on hand build |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [driver](boards/driver) | v2.4 | v2.4 2026-11-17 | changed | 1.93, 8 ext. | 2026-11-16-v2-first: draft |  |  |
| [led](boards/led) | v2.0 | v2.0 2026-11-16 | changed | 0.79, 3 ext. | 2026-11-16-v2-first: draft |  |  |
| [led35](boards/led35) | v1.0 | v1.0 2026-11-18 | released |  | 2026-11-16-v2-first: draft |  |  |

Parts costs: placed parts at unit prices from konnect's JLC parts cache of 2026-11-03; Extended parts add a setup fee each per order.

### Parts for the open orders

To finish every board of the open orders by hand: the assembled ones, or every PCB of a bare order (with the parts the assembler would have placed), as the versions they pin need; and the orders' extras.

| part | needed | on hand | to buy | where |
| --- | --- | --- | --- | --- |
| 20 mm PMMA TIR lens without holder, 30 degrees, smooth face (listed as 20 x 10.8 mm) | 20 | 0 | 20 | AliExpress, A Global Optics Store, item 1005002662759375: '30 degrees / Smooth surface / 10pcs' x 2, in the cart |
| 20 mm PMMA TIR lens without holder, to compare: 15 degrees smooth, 45 degrees smooth, 30 degrees bead face, 30 degrees frosted | 20 | 0 | 20 | AliExpress, the same item, four lines of '5pcs', in the cart |
| B3B-XH-A(LF)(SN) (JST), 3-pin XH vertical | 10 | 0 | 10 | LCSC C144394 |
| Elesa VC.692/25 p-M4x10 (code 166132), five-lobe knob D25, M4 x 10 zinc-plated steel stud | 10 | 0 | 10 | Elesa or a distributor |
| Hex standoff M3 x 12, female-female, polyamide | 15 | 0 | 15 | any |
| Hongli HL-C3535F15R3GA-ZW, 3535 LED, deep red 665 nm | 5 | 0 | 5 | LCSC C5445086, in the cart 'nov-2026 message sign' |
| Hongli HL-C3535F77W1KA(Ra1)-FC, 3535 LED, neutral white 3710-4260 K | 5 | 0 | 5 | LCSC C19184448, in the cart 'nov-2026 message sign' |
| Hongli HL-C3535F77W1KA(Ra1)-FC, 3535 LED, warm white 2870-3220 K | 5 | 0 | 5 | LCSC C19184447, in the cart 'nov-2026 message sign' |
| Housing sheet metal for 5 lamps (round 7) | 1 | 0 | 1 | JLCCNC, in the JLC cart: round 7's shell, cap, yoke, plate, fins and spacers (SMS2611173001134 ... SMS2611173001162), round 6's hood and doors (SMS2611163003204, SMS2611163003181) |
| JNJ 3535AW120C-45045-S-G1, 3535 LED, blue 455 nm | 5 | 0 | 5 | LCSC C25170647, in the cart 'nov-2026 message sign' |
| JNJ LEHG0113W120, 3535 LED, green 525-530 nm | 5 | 0 | 5 | LCSC C19185875, in the cart 'nov-2026 message sign' |
| JNJ LEHR0111W120, 3535 LED, red 620-630 nm | 5 | 0 | 5 | LCSC C19185876, in the cart 'nov-2026 message sign' |
| JNJ LTHI0113W120, 3535 LED, far red 730-740 nm | 5 | 0 | 5 | LCSC C19185882, in the cart 'nov-2026 message sign' |
| JNJ LTJW0115T140, 3535 LED, cool white 5500-6500 K | 5 | 0 | 5 | LCSC C19185883, in the cart 'nov-2026 message sign' |
| Kafuter K-704B, black RTV silicone, 45 g | 1 | 0 | 1 | AliExpress, YaoTool Store, item 1005006906337621: '704B--Black', in the cart |
| Nut ISO 4032 M3, steel | 15 | 0 | 15 | any |
| Optic carrier, MJF PA12 dyed black | 7 | 0 | 7 | JLC3DP, in the JLC cart (D2026111615500272, -280, -287) |
| SXH-001T-P0.6 (JST), XH crimp contact, 22-28 AWG | 30 | 0 | 30 | LCSC C140573 |
| Screw ISO 7380 M3 x 20, button head, black | 15 | 0 | 15 | any |
| Screw ISO 7380 M3 x 6, button head | 30 | 0 | 30 | any |
| Screw ISO 7380 M3 x 8, button head, with nut M3 nylock (DIN 985) | 40 | 0 | 40 | any |
| Screw M3 x 6, pan head, polyamide | 15 | 0 | 15 | any |
| Silicone-coated fibreglass sleeve, black, 200 C, 2 m with 4 mm inner diameter and 2 m with 5 mm | 2 | 0 | 2 | AliExpress item 1005012524001363: 'black / 4mm / 2M' and 'black / 5mm / 2M', in the cart |
| Silverlight M3535O1YG6G12, 3535 LED, amber 590 nm | 5 | 0 | 5 | LCSC C22466168, in the cart 'nov-2026 message sign' |
| Threaded rod M3 (DIN 976-1), cut to 45 mm | 15 | 0 | 15 | any; 1 m of rod gives 20 |
| Washer DIN 125-A 3.2 (M3), steel | 15 | 0 | 15 | any |
| Washer DIN 125-A 4.3 (M4), polyamide, 4.3 x 9 x 0.8 | 10 | 0 | 10 | any |
| Washer DIN 9021 4.3 (M4), steel, 4.3 x 12 x 1.0 | 10 | 0 | 10 | any |
| XHP-2 (JST), XH 2-pin plug housing | 15 | 0 | 15 | LCSC C144401 |
| XINGLIGHT XL-HD2525SURC-A4, red (LED1) | 5 | 0 | 5 | LCSC C49237857, in the cart 'nov-2026 message sign' |
| XINGLIGHT XL-HD2525UBC-A4, blue (LED3) | 5 | 0 | 5 | LCSC C49237860, in the cart 'nov-2026 message sign' |
| XINGLIGHT XL-HD2525UGC-A4, green (LED2) | 5 | 0 | 5 | LCSC C49237859, in the cart 'nov-2026 message sign' |

### Orders

| order | what | status | last event |
| --- | --- | --- | --- |
| [2026-11-16-v2-first](production/orders/2026-11-16-v2-first/ORDER.md) | driver v2.4 and LED board v2.0, all 5 of each assembled, with the round-7 housing for 5 lamps, and 10 bare led35 v1.0 boards | draft | 2026-11-18 |

### Problems

- boards/driver/driver.kicad_pcb: changed since v2.4: run pcbkit release
- boards/led/led.kicad_pcb: changed since v2.0: run pcbkit release

<!-- pcbkit:production:end -->
