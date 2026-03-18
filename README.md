# RGB Spotlight

25mm circular chainable RGB spotlight pixel for LED installations.

![PCB render](media/v1-render.png)

## Overview

- **Input:** 12V / DIN / GND (3-wire JST PH chain)
- **Controller:** WS2811 (NeoPixel-compatible, 800kHz)
- **LED drivers:** 3x PT4115 constant-current buck converters at 454mA/channel
- **LEDs:** XINGLIGHT HD2525 series — Red (625nm), Green (525nm), Blue (455nm)
- **Power:** ~4.73W per pixel at full white
- **Level shifter:** SN74AHCT1G125 on DIN for 3.3V controller compatibility
- **Inverter:** 74HC04 corrects WS2811 open-drain / PT4115 active-high DIM polarity

## PCB

- 50mm diameter, 2-layer, 1.6mm FR4
- Top: 3x LEDs in triangle, JST PH connectors at edges
- Bottom: PT4115 groups at 120 degree spacing, WS2811 + 74HC04 center

![PCB layout](media/v1-pcb.png)

## BOM

16 line items, ~$2.26/unit at qty 1 pricing. 10 extended parts = $30 one-time setup fee.

View the full BOM with `jlcpcb bom` or see [rgb-spotlight-bom.md](rgb-spotlight-bom.md) for component selection rationale and connection tables.

```
jlcpcb status           # overview
jlcpcb bom              # full BOM table
jlcpcb bom --check      # refresh stock/prices from JLCPCB API
jlcpcb bom --format csv # export for ordering
```

## Design Decisions

See [rgb-spotlight-bom.md](rgb-spotlight-bom.md) for detailed rationale on every component choice, including the WS2811 inversion problem and why the 74HC04 is worth $0.17/unit.
