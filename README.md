# RGB Spotlight

50mm circular chainable RGB spotlight pixel for 12V LED installations.

![PCB render](media/v1-render.png)

## What It Does

This module is a high-powered, addressable RGB LED pixel designed for spotlights and creative LED experimentation. It uses a WS2811 chip so it can be daisy-chained and used with FastLED, WLED, and other WS2811-compatible libraries. Arranged on a 50mm circular board with thermal heatsink pads.

- WS2811-compatible pixel input/output (`DIN` -> `DOUT`)
- Three PT4115 constant-current channels (R/G/B)
- 5V logic rail from 12V, with data level shifting and PWM polarity correction

## Electrical Specs

- **Supply input:** 12V nominal (design target)
- **Data protocol:** WS2811-compatible, 800kHz, single-wire
- **Data logic input:** 3.3V or 5V at DIN (first pixel level-shifted to 5V)
- **LED current per channel:** ~454mA (`I = 0.1V / 0.22R`)
- **LED operating margin:** 454mA vs 700mA LED max (~64%)
- **Full-white input power:** ~4.73W per pixel
- **Full-white input current:** ~0.39A per pixel at 12V
- **5V logic rail load:** ~17mA (WS2811 + 74HC04 + level shifter)

For chain power sizing at full white:

- `I_total ~= 0.39A x number_of_pixels`
- Example: 10 pixels -> about 3.9A at 12V (before wiring margin)

## Connection / Wiring

| Connector | Pin 1 | Pin 2 | Pin 3 |
| --- | --- | --- | --- |
| J1 (input) | `12V` | `DIN` | `GND` |
| J2 (output) | `GND` | `DOUT` | `12V` |

Bring-up and chain rules:

1. Connect controller data to first pixel `J1 pin 2 (DIN)`.
2. Connect supply `+12V` to `J1 pin 1` and supply ground to `J1 pin 3`.
3. Keep controller ground and power ground common.
4. Chain by wiring `J2 DOUT` of one board to `J1 DIN` of the next.
5. Power also passes through connectors (`12V` and `GND`), but inject power along long chains to limit voltage drop.

## PCB

- 50mm diameter, 2-layer, 1.6mm FR4
- Top: 3x LEDs in triangle, JST PH connectors at edges
- Bottom: PT4115 groups at 120 degree spacing, WS2811 + 74HC04 center

![PCB layout](media/v1-pcb.png)

## BOM

16 line items, ~$2.24/unit at qty 1 pricing. 10 extended parts = $30 one-time setup fee.

Use `bomi` to inspect/refresh the BOM and export files:

```bash
bomi status
bomi fetch --all --force
bomi list --check
bomi list --format markdown > docs/BOM_rgb-spotlight.md
bomi list --format csv > docs/BOM_rgb-spotlight.csv
```

See [docs/BOM_rgb-spotlight.md](docs/BOM_rgb-spotlight.md) for the latest part snapshot and [rgb-spotlight-bom.md](rgb-spotlight-bom.md) for detailed rationale and full connection tables.
