# RGB Spotlight

Chainable, addressable 3 x 3 W RGB spotlight for 12 V installations: an aluminium LED board and an FR4 driver board in an aluminium cylinder.

![v2 boards: LED board (aluminium) and driver board](docs/previews/v2-boards.png)

> **Status (2026-10-05):** v1 (EasyEDA, one FR4 board) was built but never lit: the PT4115 stages were wired as the wrong kind of buck, and the 74HC04 was unpowered.
>
> **v2 is a KiCad restart with two boards:**
> - **LED board:** routed, DRC clean.
> - **Driver board:** fully routed by script, DRC clean.
>
> See [DESIGN.md](DESIGN.md) for the v1 post-mortem, the v2 design, the thermal estimate and the open items.

## What it does

A high-power, addressable RGB pixel for spotlights and creative lighting. It speaks the WS2811 protocol, so it daisy-chains and works with FastLED, WLED and other WS2811-compatible software.

- **LED board** (aluminium, 1 layer, 50 mm):
  - three XINGLIGHT HD2525 3 W LEDs (R/G/B), spread on a 12 mm-radius ring;
  - each LED on its own heat-spreading copper island;
  - six wire pads around a centre hole for the harness.
- **Driver board** (FR4, 2 layers, 50 mm), mounted 4–6 cm behind the LED board:
  - WS2811 pixel controller;
  - three PT4115 constant-current bucks (455 mA each);
  - level shifter on DIN; inverter for the PWM polarity;
  - 78L05 logic rail; TVS on the 12 V input.

## Electrical specs

- **Supply:** 12 V (the PT4115 regulates down to about 6 V at the end of a chain)
- **Data:** WS2811 protocol, 800 kHz, single wire; 3.3 V or 5 V at DIN
- **LED current:** about 455 mA per channel (`I = 0.1 V / 0.22 Ω`); LEDs rated 1 A / 3 W
- **Full white:** about 4.5 W, 0.38 A at 12 V per light
- **Chaining:** JST XH connectors (3 A) pass 12 V/GND through, so about 7 lights per power feed. Inject power again after that.
- **Heat:** about 2.7 W in the LED board, which needs a heatsink: the housing's heat plate. About 0.9 W in the driver. See DESIGN.md §2.6.

## Connections

| Connector | Where | Pins |
| --- | --- | --- |
| J1 IN | driver, back (JST XH 3, vertical) | 1 `12V`, 2 `DATA`, 3 `GND` |
| J2 OUT | driver, back (JST XH 3, vertical) | 1 `12V`, 2 `DATA`, 3 `GND` |
| J3 LED | driver, front (JST PH 6, vertical) | 1 `R+`, 2 `R-`, 3 `G+`, 4 `G-`, 5 `B+`, 6 `B-` |
| TP1–TP6 | LED board, around the centre hole | same order as J3; solder the wires here |

J1 and J2 share one pin order, so chain with pin-1-to-pin-1 cables. v1 had J2 mirrored.

1. Connect the controller's data to J1 pin 2 of the first light, and +12 V / GND to pins 1 / 3. Keep controller and power grounds common.
2. Chain J2 of one light to J1 of the next.
3. Twist each colour's LED pair in the harness.

## Project layout

- `boards/led/`, `boards/driver/`: KiCad 10 projects. Schematics come from `scripts/sch_led.py` / `scripts/sch_driver.py`; boards from `scripts/make_led_pcb.sh` / `scripts/make_driver_pcb.sh`.
- `lib/`: project symbols, footprints and 3D models (`scripts/make_lib.py`).
- `scripts/`: generators and checks (`netcheck.py`, `ratsnest.py`, `make_previews.sh`). The shared parts (schematic builder, silkscreen placer, DRC/ERC summaries, previews, JLC fab files) come from [pcb-kit](https://github.com/somebox/pcb-kit): `uv tool install -e ~/src/pcb-kit && pcbkit link`.
- `docs/previews/<board>/`: schematic PDF, board PNGs, 3D renders. `docs/previews/outline-presets.png` compares the board outline options.
- **Board outline:** everything sits in a 50 mm core. The edge is a preset, `disc50` (current), `disc55`, `disc60` or `tabs3` (screw tabs). Change it with `scripts/set_outline.py`; see DESIGN.md §7.3.
- `archive/v1-easyeda/`: the v1 EasyEDA exports, a KiCad import of the v1 board, its as-built netlist and the bodge guide.

```bash
python3 scripts/sch_driver.py && python3 scripts/sch_led.py
pcbkit erc boards/driver/driver.kicad_sch && python3 scripts/netcheck.py
scripts/make_led_pcb.sh && scripts/make_driver_pcb.sh --force --route
scripts/make_previews.sh all
```

## BOM

- Driver: 19 lines, about $2.18 at qty 1. LED board: 3 lines, about $0.77 (bomi, 2026-10-05).
- Each board has its own bomi project:

```bash
bomi --project boards/driver list --check
bomi --project boards/driver list --format markdown > docs/BOM_driver.md
bomi --project boards/led list --format markdown > docs/BOM_led.md
```

See [docs/BOM_driver.md](docs/BOM_driver.md), [docs/BOM_led.md](docs/BOM_led.md) and DESIGN.md §3. The v1 rationale doc is in `archive/v1-easyeda/rgb-spotlight-bom-v1.md`; its PT4115 connection tables are wrong.

## v1 (for reference)

![v1 PCB render](media/v1-render.png)
