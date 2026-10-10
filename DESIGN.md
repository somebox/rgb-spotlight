# RGB Spotlight — design notes

Chainable, WS2811-addressed RGB spotlight: three 3 W LEDs, each on its own PT4115 constant-current buck, run from a 12 V chain. Two boards in an aluminium cylinder:
- an **aluminium LED board** (50 mm, 1 layer) carrying only the LEDs;
- an **FR4 driver / interface board** (50 mm, 2 layers) 4–6 cm behind it, with the drivers, logic and connectors. KiCad 10, built with the Konnect MCP workflow from `~/Documents/Projects/rp2354-messages-sign/docs/PCB-WORKFLOW.md`.

**Status (2026-10-05):**
- **Schematics:** both generated. Driver: ERC 0/0, 63 topology checks pass. LED: ERC shows only 3 benign warnings (§4).
- **LED board:** fully generated and routed, DRC clean.
- **Driver board:** fully routed by script. DRC: 0 violations, 0 unconnected, parity clean.
- **Before ordering:** the v1 bench tests in §5 and the open items in §6.

| Path | What |
|---|---|
| `boards/driver/` | Driver / interface board (FR4). Schematic from `scripts/sch_driver.py`; board from `scripts/make_driver_pcb.sh` |
| `boards/led/` | LED board (aluminium). Schematic from `scripts/sch_led.py`; board from `scripts/make_led_pcb.sh` (placement and routing) |
| `lib/` | Project symbols (`PT4115`, `LED_HD2525`, 3-unit `LED_PORT`), footprints (`LED_XINGLIGHT_HD2525`, `WirePad_2.2x3.5mm`) and the 3D model, all written by `scripts/make_lib.py` |
| `scripts/` | Generators and checks. `builder.py`, `kmcp.py`, `jlc_search.py`, `drcsum.py`, `plot_print.py`, `silk_place.py` and `blank.kicad_pcb` come from the message-sign repo |
| `archive/v1-easyeda/` | v1 EasyEDA exports, the KiCad import of the v1 board, its as-built netlist, the v1 BOM doc and the bodge image |
| `docs/previews/<board>/` | Schematic PDF, front/back PNGs, 3D renders, printable PDF (`scripts/make_previews.sh`); driver `placement-ratsnest.png` (`scripts/ratsnest.py`) |
| `docs/BOM_driver.md`, `docs/BOM_led.md` | bomi BOMs. Each board folder has its own `.bomi/project.yaml` |
| `docs/datasheets/` | PDFs (git-ignored) plus bomi summaries |

```sh
python3 scripts/make_lib.py                         # project symbols + footprints
python3 scripts/sch_driver.py && python3 scripts/sch_led.py   # rebuild both schematics (Konnect); overwrites them
pcbkit erc boards/driver/driver.kicad_sch           # ERC summary (same for boards/led)
python3 scripts/netcheck.py                         # driver topology assertions (exit 1 on failure)
scripts/make_led_pcb.sh                             # LED board: placement, routing, islands, DRC (fully generated)
scripts/make_driver_pcb.sh --force --route          # driver board: placement + routing (about 6 min) + DRC; refuses hand-edited boards without --force
scripts/make_previews.sh [driver|led|all]           # docs/previews/<board>/
<KiCad python> scripts/set_outline.py <driver|led|all> <disc50|disc55|disc60|tabs3>   # change the board edge in place (§7.3)
bomi --project boards/driver list --check           # stock check; same for boards/led
```

---

## 1. v1 post-mortem (EasyEDA, ordered Mar 2026)

Sources: the EasyEDA schematic and PCB exports (2026-10-05), the as-built netlist taken from the PCB pads (`archive/v1-easyeda/v1-netlist.txt`), a copper connectivity trace of the KiCad import (`v1-easyeda.kicad_pcb`), and the bench measurements in the Cursor review transcript.

**Measured on the board (transcript):** 12 V and 5 V present on the IC pins; 400 kHz data present on DIN and on DIN_5V (5–6 V p-p); WS2811 VDD = 5 V; WS2811 OUTR/G/B silent (DIM_x_RAW sits at 5 V); a 2 kΩ pull-up on DIM_G did nothing; the same ESP32 output drives a WS2812 panel fine.

### F1 — PT4115 power stage wired as the wrong kind of buck (all three channels) — would never light

v1 wired each channel like a conventional buck with a *high-side* switch:

```
v1:   12V ─ Rs ─ CSN            (Rs carries no LED current: only the 8 µA CSN pin current)
      SW ─┬─ L ─ LED(A→K) ─ GND
          └─ D (K on SW, A on GND)
```

The PT4115 is a **low-side** switch (SW is the drain of an internal NMOS to GND) with **high-side** current sense. The datasheet (§8, application figure 1) puts the LED and inductor between the sense resistor and SW:

```
v2:   12V ─ Rs ─┬─ CSN
                └─ LED(A→K) ─ L ─ SW      D: A on SW, K on 12V (VIN)
```

With the v1 wiring no LED current can flow:

- with the switch on, SW is at 0 V and so is everything on the LED's side;
- with it off, nothing sources current.

Rs sees 0 mV, so the comparator holds the switch on permanently. Forcing DIM high would not have lit anything either. The v1 BOM doc's connection tables (`archive/v1-easyeda/rgb-spotlight-bom-v1.md`) and the Cursor review ("PT4115 buck topology is correct … Schottky anode to GND, cathode to SW … LED cathode to GND") both describe this same wrong topology.

### F2 — 74HC04 VCC on its own net

The schematic used two power names, `+5V` and `5V`. U6 pin 14 and C2 sat on `+5V`, which connects only to C2 (copper trace confirms: U6.14 → C2.2 only). The inverter was unpowered or back-fed through its input clamps, so the DIM pins were undefined. This is probably one of the "miswirings" fixed by hand. v2 has one `+5V` net, and `netcheck.py` asserts every logic VCC is on it.

### F3 — WS2811 receives data but its outputs never change (open)

Copper was checked pad by pad on the import:

- J1.2 → U7.2 (A), and U7.4 (Y) → U1.6 (DIN). **U7's A and Y are not swapped.**
- U1.8 → 5 V and U1.4 → GND are both connected, and the U1 footprint pin order matches the datasheet.

So the board connects correctly. The candidates left, with the tests in §5:

1. **Latch (reset) time.** The Worldsemi V2.2 datasheet needs **≥ 280 µs low** before outputs update. Older WS2812 parts latch after 50 µs, and some drivers only leave about 50 µs between frames. If frames arrive back to back, the WS2811 shifts data but never latches. That matches the symptom: outputs stuck off while data is present.
2. **Data rate.** The V2.2 part is specified at 800 kbit/s only (T0H 220–380 ns, T1H 580 ns–1 µs). The 400 kHz "WS2811 mode" (T0H ≈ 500 ns, T1H ≈ 1.2 µs) is outside its spec. Test at 800 kHz, which is FastLED's plain `WS2811` (not `WS2811_400`).
3. **Pin 7.** V2.2 calls it NC, but older WS2811 datasheets and clones use it as SET (400/800 kHz select). v1 left it floating. v2 adds a do-not-fit 0 Ω strap (R9) to +5V.
4. **Placement or damage.** U1 may have been placed rotated (check the pin-1 dot against the silkscreen) or damaged during the earlier miswiring.

### Checked and correct in v1

- 78L05G-AB3-R pinout on the PCB: 1 OUT, 2 GND, 3 IN, per the UTC ordering table "O G I". The *v1 BOM doc table* listing pins as GND/VIN/VOUT was wrong, but the schematic and PCB were right.
- WS2811, 74HC04 and 74AHCT1G125 pin maps.
- LED pads (EasyEDA symbol: pad 1 = K, pad 2 = A). Physical orientation is still to be verified (§6).

### Convention, not a fault: connector pin order

v1 used J1 = 12V/DIN/GND and J2 = GND/DOUT/12V, so the chain depends on a reversed (pin 1 ↔ pin 3) cable. A pin-1-to-pin-1 cable would put 12 V on the next board's GND. v2 gives both connectors the same order (1 = 12V, 2 = data, 3 = GND) for pin-1-to-pin-1 cables. **Check which kind of JST PH cable you have.** If yours are reversed, swap J2's pins 1 and 3 in `sch_main.py`.

---

## 2. v2 circuit

### 2.1 LED channels (×3, PT4115)
- Topology per datasheet: 12 V → Rs → (CSN, LED anode); LED cathode → L → SW; Schottky anode on SW, cathode on 12 V; 10 µF across VIN–GND at the pin.
- **I_LED = 0.1 V / Rs = 0.1 / 0.22 = 455 mA.** Datasheet limits: Rs ≥ 0.082 Ω, LED max 1 A / 3 W. Rs dissipation is 45 mW (1206, 250 mW).
- **Inductor 68 µH** (FNR6045S680MT, Isat 1.1 A, DCR 0.38 Ω). The datasheet table gives 47–68 µH for 0.4–0.8 A, and Isat ≥ 1.3–1.5 × I_out. v1 used 100 µH, the value for I ≤ 0.4 A.
- **Switching frequency** (hysteresis ±15 % → ΔI ≈ 136 mA; R_SW 0.6 Ω at 12 V):
  - red, VF ≈ 2.2 V: t_on ≈ 1.0 µs, t_off ≈ 3.2 µs, so ≈ 240 kHz;
  - green/blue, VF ≈ 3.2 V: t_on ≈ 1.15 µs, t_off ≈ 2.3 µs, so ≈ 290 kHz.

  Both are under the 1 MHz limit.
- **Input cap** 10 µF 50 V X5R 1206. The datasheet asks for at least 4.7 µF; v1's 0805 25 V part keeps only about 3–4 µF at 12 V bias.
- **DIM:** 0 V = off, > 2.5 V = full, internal 200 kΩ pull-up to 5 V, abs max 6 V. It is driven by 74HC04 outputs at 5 V.
  - WS2811 PWM runs at about 4 kHz. The PT4115 holds its 0.02 % minimum duty at 100 Hz but needs 4 % at 20 kHz. Expect roughly the bottom 1 % (2–3 of 255 levels) to be dark or non-linear.

### 2.2 Data path
- **J1.2 → R10 100 Ω → (R7 10k to GND) → 74AHCT1G125 → WS2811 DIN.** R10 limits current into the buffer input when a hot-plugged cable rings.
  - AHCT input VIH = 2.0 V, so 3.3 V or 5 V controllers both work; WS2811 VIH is 0.55·VDD = 2.75 V.
  - R7 holds the line low when unplugged, which also keeps the WS2811 in reset.
  - OE is tied straight to GND. v1's R7 pull-down on OE did the same job; that resistor now goes to DIN.
- **WS2811 DO → R8 33 Ω → J2.2:** source termination for the cable. Each WS2811 regenerates the signal at 5 V.
- **R9 (0 Ω, not fitted):** pin 7 (SET) to +5V. Fit it only if bring-up shows the part needs it (§1 F3).

### 2.3 Inversion (unchanged idea, now powered)
WS2811 outputs are 20 V-tolerant constant-current sinks (≈ 16 mA) and sink when a channel is on.
- R4–R6 (4.7 kΩ to 5 V) limit that to 1.06 mA, so the outputs pull fully low.
- The 74HC04 inverts, so DIM is high when the channel is on: 0xFF → full on, 0x00 → off, with standard NeoPixel software.
- Gates 4–6: inputs to GND, outputs open.

### 2.4 Logic supply and 12 V input
78L05 (SOT-89, O-G-I) from 12 V, with 10 µF in and 100 nF out. Load is about 5 mA: WS2811 0.3 mA, 3 × 1.06 mA pull-ups, R7 up to 0.5 mA, gate quiescent. That dissipates ≈ 35 mW. Each logic IC has its own 100 nF.

**12 V input:** an SMAJ15A TVS (breakdown ≥ 16.7 V, clamps 24.4 V) and a 22 µF 1206 at J1. Hot-plugging a cable onto ceramic-only inputs can ring to about 2 × 12 V; the PT4115 is rated to 35 V and the caps to 25/50 V.
- J1 → J2 carry +12V and GND straight through; JST XH is rated 3 A.
- At ≈ 0.38 A per light (full white), one feed powers **up to 7 lights**.
- 1 m of 22 AWG between lights drops about 0.85 V over 6 lights. The PT4115 runs down to about 6 V, so voltage is not the limit; connector current is. Inject power again after about 7 lights.

### 2.5 Mechanical: two boards in an aluminium cylinder (2026-10-05)
- **LED board** (aluminium, 1 layer, 50 mm):
  - LEDs on a ring at r = 12 mm (R 90°, G 210°, B 330°). They are spread apart on purpose: the colours stay separate.
  - Each LED sits on its own large copper island (`HEAT_R/G/B`), never joined. That makes the slug-isolation question moot, and the dielectric isolates the islands from the aluminium.
  - A 6.4 mm centre hole passes the wires. The six wire pads around it are soldered on the front; the wires go straight through the hole.
  - Three M3 holes at r = 19 mm (30° / 150° / 270°) bolt it to the housing's heat plate with thermal paste or a pad.
- **Harness:** six 24 AWG wires, twisted per colour, soldered to the LED board and crimped into a JST PH 6 housing. Pin order: R+ R− G+ G− B+ B−.
  - The LED pins are not the switching node (that is SW, between L and the PT4115 on the driver board). The wires carry DC with about ±15 % ripple at 240–290 kHz, so 4–6 cm is no problem.
- **Driver board** (FR4, 2 layers, 50 mm, about 1 W):
  - Front faces the LED board: all SMD parts, plus J3 (PH 6 vertical) at the centre.
  - Back faces the housing's back: J1 IN and J2 OUT (XH 3 vertical, through-hole). They are reachable through cut-outs in the back cap, or by short pigtails to panel connectors.
  - Three M3 holes at r = 11 mm for standoffs.
- **Power per light at full white:**
  - LEDs ≈ 0.455 A × (2.1 + 3.0 + 3.1 V) ≈ 3.7 W;
  - driver losses ≈ 0.9 W;
  - total **≈ 4.5 W in, ≈ 0.38 A at 12 V.**

### 2.6 Thermal estimate (2026-10-05)

Full white at 455 mA. Assumptions:
- LED wall-plug efficiency ≈ 30 % red, 20 % green, 35 % blue;
- LED junction-to-slug ≈ 10 °C/W (the datasheet gives only Tj max = 125 °C);
- still air h ≈ 10–12 W/m²K, counting both faces.

| | Value |
|---|---|
| Heat in LEDs | R 0.67 W, G 1.09 W, B 0.92 W, so **2.7 W**, all within about 7 mm of the centre |
| Heat in drivers | ≈ 0.3 W per channel (diode, switch, DCR, Rs), so **0.9 W** |
| One 50 mm FR4 disc, free-standing | 21–25 °C/W to air, even with ideal spreading, so **+77–92 °C** (board ≈ 100–115 °C, LEDs at or past Tj max). **Needs a heatsink** |
| FR4 + via array (0.3 mm via ≈ 190 °C/W each, 10 vias ≈ 19 °C/W) onto a heatsink | Tj(green) ≈ T_heatsink + 33 °C: 78 °C at a 45 °C heatsink |
| Aluminium MCPCB (≈ 1.5 W/mK, 0.1 mm dielectric, ≈ 3 °C/W) | Tj(green) ≈ T_heatsink + 14 °C: 59 °C at a 45 °C heatsink |
| Heatsink for a 45 °C base at 25 °C ambient | ≈ 5.5 °C/W for 3.6 W |

**Conclusion:** a heatsink is needed either way. Aluminium keeps the LEDs about 20 °C cooler than FR4 with vias. Without a heatsink, run about 200–300 mA (Rs = 0.47 / 0.33 Ω).

**Decision (2026-10-05):** LEDs go on an aluminium board bolted to the housing's heat plate, and the driver goes on its own FR4 board (§2.5).
- The 2.7 W of LED heat goes into the aluminium cylinder, which has passive vents.
- The driver's 0.9 W is spread over its own disc.
- Spreading the LEDs to r = 12 mm also spreads their heat.

## 3. Parts (bomi: `docs/BOM_driver.md` 19 lines ≈ $2.18; `docs/BOM_led.md` 3 lines ≈ $0.77, qty 1)

| Board | Ref | Part | LCSC | Note / change from v1 |
|---|---|---|---|---|
| LED | LED1–3 | XL-HD2525 SURC / UGC / UBC | C49237857 / 859 / 860 | **green stock low** (bomi check: 325) |
| LED | TP1–TP6 | wire pads 2.2 × 3.5 mm | — | not in the BOM; hand-soldered wires |
| driver | U1 | WS2811 SOP-8 | C114581 | |
| driver | U2–U4 | PT4115 SOT-89-5 | C347356 | stock KiCad `SOT-89-5` footprint (pad 2 = tab = GND) |
| driver | U5 | 78L05G-AB3-R | C71136 | Basic |
| driver | U6 | 74HC04D | C5590 | |
| driver | U7 | SN74AHCT1G125DCKR | C350557 | |
| driver | L1–L3 | FNR6045S680MT 68 µH | C168091 | was 100 µH C168095 |
| driver | D1–D3 | B5819W | C64885 | now SW → 12 V |
| driver | D4 | SMAJ15A TVS | C19077535 | new (Preferred) |
| driver | R1–R3 | 0.22 Ω 1 % 1206, 300 ppm | C2907349 | was 0805, 800 ppm (C247160) |
| driver | R4–R6 | 4.7 kΩ 0402 | C25900 | |
| driver | R7 | 10 kΩ 0402 | C25744 | now the DIN pull-down |
| driver | R8 | 33 Ω 0402 | C25105 | new: DOUT series |
| driver | R9 | 0 Ω 0402 | — | new, **DNP**: SET strap |
| driver | R10 | 100 Ω 0402 | C25076 | new: DIN series |
| driver | C1–C4 | 100 nF 0402 | C1525 | |
| driver | C5 | 10 µF 25 V 0805 | C15850 | |
| driver | C6–C8 | 10 µF 50 V 1206 | C13585 | was 0805 25 V |
| driver | C9 | 22 µF 25 V 1206 | C12891 | new: 12 V input bulk |
| driver | J1, J2 | JST B3B-XH-A, vertical THT, back side | C144394 | was PH SMD right-angle; 3 A for chaining |
| driver | J3 | JST B6B-PH-K-S, vertical THT | C131342 | new: LED harness |

## 4. Verification

- **Driver ERC:** 0 errors, 0 warnings (`scripts/erc.py`).
- **LED ERC:** 3 warnings, `isolated_pin_label` on HEAT_R/G/B. They are benign: each island is meant to connect to one pad only.
- **`scripts/netcheck.py`** (63 assertions, driver) checks the v1 failure points directly:
  - each channel's 12 V → Rs → CSN / J3 x+ … J3 x− → L → SW, and D from SW to 12 V;
  - the CSN, LED-cathode and SW nodes hold nothing else;
  - DIM comes from a 74HC04 output;
  - every logic VCC is on +5V; the 78L05 pinout; the TVS orientation; R10/R7; the connector pinout; no single-node nets.
- **DRC with schematic parity:** both boards clean (the driver is unrouted).

## 5. Bench tests on the v1 boards (before ordering v2)

### Data path (F3)
Hold the scope or DMM ground on J1.3.

1. **Is the WS2811 decoding?** Configure ≥ 2 pixels in firmware and scope **J2.2 (DOUT)**. A decoding WS2811 forwards everything after the first 24 bits.
   - **Bits on DOUT:** the chip receives and decodes. Go to step 2.
   - **DOUT silent:** go to step 3.
2. **Latch:** add a gap after each frame (e.g. `FastLED.show(); delayMicroseconds(500);`) or send one frame and stop, at **800 kHz** (FastLED `WS2811`, not `WS2811_400`). Expected: DIM_x_RAW drops to ≈ 0 V for full white.
3. **If DOUT is silent:**
   - check U1's pin-1 dot against the silkscreen;
   - try pin 7 tied to 5 V, then to GND;
   - otherwise swap the WS2811.

### Power stage (F1): bodge one channel
Red channel, marked up in `archive/v1-easyeda/bodge-red-channel.png`. It drives an **external** LED. The on-board LED can't be reused: its cathode pad sits under the body and is wired to GND.

1. **Remove LED1.** Photograph its orientation first. Once it's off:
   - diode-test it to settle §6 item 1 (in v1 the pad nearer the board centre was the GND/cathode pad);
   - wick its pads flat.
2. **Cut the DIM_R trace** where it leaves U2 pin 3 (top-left pin of U2 in the image).
   - With DIM disconnected, the PT4115's internal pull-up turns the channel on.
   - This takes the 74HC04 and WS2811 out of the test.
3. **Add a Schottky** (1N5819, SS14, or any ≥ 1 A / ≥ 20 V part):
   - anode on D1's left pad (the SW node, also U2 pin 1);
   - banded cathode on C6's upper pad (+12 V).
   - Keep the leads short: this is the switching loop.
   - Leave D1 in place: in the new circuit it is always reverse-biased.
4. **Wire R1's left pad** (the end that beeps to U2 pin 4, **not** 12 V) to the external LED's **+**.
5. **Wire LED1's former outer pad** (the one toward L1, joined to L1 by the trapezoid copper) to the external LED's **−**.
   - Scraping the mask on the trapezoid gives a bigger target.
   - This wire must **not** beep to GND: shorting it to GND would put the LED straight across 12 V through R1.

**Resulting loop:** 12 V → R1 → LED+ … LED− → L1 → SW (U2) → GND, freewheeling through the new Schottky back to 12 V.

**External LED:** a 3 W "star" LED on a heatsink, since the channel runs 455 mA with R1 = 0.22 Ω. For a gentler first try, swap R1 (0805) for 0.47 Ω (≈ 210 mA).

**Power-up:** bench supply at 12 V with the current limit at about 0.25 A. Expect:
- about 0.1–0.15 A drawn;
- about **100 mV across R1** (= 455 mA);
- a 0 ↔ 12.4 V square wave at roughly 150–250 kHz on D1's left pad (with v1's 100 µH).

If the supply hits its current limit, power off and check the new diode's direction and wire 5.

**Afterwards:** bridge the DIM cut with solder and go back to the data-path tests above. Once the WS2811 decodes, red = 255 should light this LED.

## 6. Open items (before ordering v2)

1. **LED orientation.** The datasheet top view puts the dot at pad ② (anode). The LCSC/EasyEDA footprint (which JLC uses) puts its dot at pad 1 (cathode).
   - Our footprint has pad 1 = cathode at −x, with silk closing that side.
   - Check on a v1 board: diode-test LED1, red probe on the L1-side pad (v1 pad 2), black on GND (pad 1). It should glow faintly.
   - Then confirm polarity in JLC's DFM preview.
2. **WS2811 behaviour (F3)** from §5. If it stays unexplained, consider another 12 V WS2811-protocol controller.
3. **Chain cables:** J1/J2 now share one pinout, so use pin-1-to-pin-1 XH cables or pigtails.
4. **Green LED stock:** 325 at the last check. Order early, or find an alternate.
5. **Housing fit:** pick the outline preset once the housing is known (§7.3): `disc50` (current) / `disc55` / `disc60` / `tabs3`, or add one to `scripts/mech.py`.
   - Check the back-cap cut-outs over J1/J2 at r = 19.5 mm, 30° / 150°.
6. **Aluminium board order:** 1 layer, 1.6 mm, 1–2 W/mK. JLC assembles the LEDs.

## 7. PCBs

### 7.1 LED board (`scripts/make_led_pcb.sh`, fully generated, DRC clean)
- Parameters at the top of `gen_led_pcb.py`:
  - `R_BOARD` 25;
  - `R_LED` 12 (LED ring);
  - `R_PAD` 6.2 / `PAD_SPREAD` 23° (wire pads);
  - `D_WIRE_HOLE` 6.4;
  - `R_HOLE` 19 (M3);
  - islands r 8.6–22 mm, ±46°;
  - LED tracks 1.2 mm.
- Each LED pad leaves at pad width (0.45 mm) for 2.1 mm, to stay 0.3 mm off the centre thermal pad. It then widens to 1.2 mm and runs straight to its wire pad.
- The wire hole is a plain Edge.Cuts circle. A mounting-hole footprint would bring a screw-head courtyard over the pads.
- Only F.Cu is used: order it as a 1-layer aluminium board.

### 7.2 Driver board (`scripts/make_driver_pcb.sh --force --route`; routed, DRC clean)
- 50 mm disc, 2 layers, GND pour on both.
- Rules: 0.2 mm clearance everywhere (the router routes to 0.2 mm; 12 V needs no more). Net classes:
  - PWR 1.5 mm (+12V / GND);
  - LED 0.6 mm;
  - +5V 0.4 mm;
  - default 0.25 mm.

**Placement** (board centre = origin):

| Where | What |
|---|---|
| centre, front | J3 LED harness (PH 6 vertical); pin 1 at the top, towards the red cell; legend R+ … B− beside it |
| driver cells at 90° / 210° / 330° | identical (red rotated ±120°): Rs and L innermost (their LED-side pads face J3), then D, then the PT4115 with Cin |
| 150° gap | J1 IN on the **back** (pin row tangential at r = 19.5 mm); TVS D4 + C9, level shifter U7 + R7/R10/C3 on the front |
| 30° gap | J2 OUT on the **back**; 78L05 U5 + C4/C5 on the front |
| 270° gap | U6 74HC04 and U1 WS2811 side by side, pull-ups R4–R6 between them; C1/C2, R8/R9 |
| r = 11 mm, 30° / 150° / 270° | M3 standoff holes |

**Routing** (`scripts/route_driver.py`, built on the message-sign maze router `route_strip.py`, extended for round outlines). 328 segments, 69 vias.

0. **Cells, scripted** in red-cell coordinates and rotated ±120°. Each piece is checked against KiCad's exact pad shapes (not bounding boxes) before it is added:
   - SW node U.SW → D.A → L.2 at 0.8 mm, front only: the hot loop is about 5 × 4 mm;
   - 12 V cluster D.K → U.VIN, Cin.1 → U.VIN, Rs.1 → via → D.K at 0.8 mm;
   - Rs.2 → CSN Kelvin sense at 0.25 mm, round the outside of Cin;
   - a DIM escape via beside each PT4115;
   - two GND vias at each tab.
1. **Cell links to J3** (LEDK_x, CSN_x), maze-routed.
2. **+12V trunk:** a scripted 1.5 mm ring on B.Cu at r = 23.3 mm, outside every cell, with radial stubs from J1.1 / J2.1 (the chain's pass-through, up to 3 A). Maze taps join each cell's 12 V via, the 78L05, the TVS and C9.
3. **GND:** a via beside every front SMD GND pad (27). C4.2, at the edge, joins through the front pour.
4. **Logic:**
   - escape vias for the long cross-board pins (U7.4, U1.6, U1.1, R8.2, U6.2/4/6);
   - a scripted +5V spine for the pull-ups R4–R6 (their 5 V pads alternate with OUT pads in one column);
   - then the maze: OUT/SET/DIN locally, DIM/DIN_5V/DOUT preferring the back, +5V last.
5. **Full search** (no corridor limit) for whatever the quick pass missed. Last run: +5V, DIM_R, DIN_5V and DOUT, all routed.
6. **Clean-up:** removes escape vias and stubs the router didn't use, then refills the zones.

**Known compromise:** the long logic runs (DIN_5V, DIM_R, +5V) cross the middle of the back. That splits the back GND plane into a few regions, all joined through the front pour and the stitching vias. That is fine for an 800 kHz data line and a 4 kHz PWM. A hand pass could move parts of those runs to the front.

**Regenerating:** the whole board comes from the scripts (`--force --route`, about 6 min). Stop regenerating once you edit it by hand, and use *Update PCB from Schematic* instead.

**3D:** the SOT-89-5 model comes from LCSC (`lib/3dmodels/SOT-89-5_LCSC.step`, via easyeda2kicad C347356). It needs no rotation on the KiCad footprint: LCSC's footprint is KiCad's turned 180°, and its model carries that 180°.

### 7.3 Board outline presets (`scripts/mech.py`, `scripts/set_outline.py`)
- **Parts, tracks and silk** on both boards live inside the **50 mm core** (`mech.CORE_D`). The router also keeps to it, and the driver's 12 V ring sits at r = 23.3 mm.
- **The board edge is a separate preset**, so the housing decision doesn't touch the layout. Preview: `docs/previews/outline-presets.png`.

| Preset | Edge | Mounting |
|---|---|---|
| `disc50` (current) | 50 mm disc | inner M3: LED board r = 19 mm, driver r = 11 mm (30° / 150° / 270°) |
| `disc55` | 55 mm disc | inner M3 as above |
| `disc60` | 60 mm disc | M3 in the rim at r = 27.5 mm (30° / 150° / 270°); no inner holes |
| `tabs3` | 50 mm disc + three 9 mm tabs | M3 at r = 28.5 mm on the tabs (30° / 150° / 270°); no inner holes |

- **Choosing a preset:**
  - at generation: `MECH=<preset> scripts/make_led_pcb.sh`, `MECH=<preset> scripts/make_driver_pcb.sh --force --route`;
  - later, in place, even on a hand-edited board: `<KiCad python> scripts/set_outline.py <driver|led|all> <preset>`. It replaces only the edge, the H# mounting holes, their keep-outs, the edge stitching vias and the GND pour extent. Close the board in KiCad first.
- **Holes outside the core** get a copper keep-out (r = 3.0 mm, an M3 pan head plus margin) on both layers, so the screws touch no circuit copper. Inner holes keep only their placement clearance.
- **Driver pour:** the GND pour grows with the outline. Outside the core, the back pour is stitched to the front by a via every 10° at r = 26 mm, skipping the screw keep-outs.
- **LED board:** the extra area is bare aluminium; the copper islands stay in the core.
- **Tested:** all four presets on both boards give DRC 0 / unconnected 0 / parity 0. Re-applying a preset is idempotent.
- **Adding a preset:** add an entry to `PRESETS` in `mech.py`. The fields are `d`, `inner`, `rim=(r, angles, drill)` and `tabs=dict(angles, r_hole, width, drill)`.
- **KiCad 10 Python gotcha** (found here): `BOARD.Remove()` segfaults on a board loaded together with its project, and after any `FootprintLoad` in the same run.
  - That's why `set_outline.py` strips the old outline as a plain edit of the `.kicad_pcb` text (`mech.strip_outline_file`), then loads the board to add the new one.
  - Worth adding to the message-sign playbook's pcbnew gotchas.

