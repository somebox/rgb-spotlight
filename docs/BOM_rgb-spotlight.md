# RGB Spotlight BOM Snapshot

Refreshed with `bomi` on 2026-03-28 using:

```bash
bomi fetch --all --force
bomi list --check
bomi list --format markdown
```

## Summary

- 16 line items (16 unique LCSC parts)
- Estimated unit cost (qty 1): ~$2.24
- Extended parts: 10 unique (~$30 one-time setup fee at JLCPCB)

## BOM

| Ref | Qty | LCSC | Package | Note | Stock | Price |
| --- | --- | --- | --- | --- | --- | --- |
| C1-C4 | 4 | C1525 | 0402 | 100nF X7R bypass caps | 45,027,993 | $0.0013 |
| C5-C8 | 4 | C15850 | 0805 | 10uF X5R 25V input bulk caps | 3,784,382 | $0.0212 |
| D1-D3 | 3 | C64885 | SOD-123 | B5819W 40V/1A Schottky freewheeling diode | 973,161 | $0.0165 |
| J1-J2 | 2 | C265101 | SMD,P=2mm,Surface Mount, Right Angle | JST PH 2.0mm 3P SMT RA, in/out connectors | 18,394 | $0.2506 |
| L1-L3 | 3 | C168095 | SMD,6x6mm | 100uH 1A shielded inductor | 218,996 | $0.0673 |
| LED1 | 1 | C49237857 | SMD | HD2525 Red 625nm | 1,100 | $0.2631 |
| LED2 | 1 | C49237859 | SMD | HD2525 Green 525nm | 2,045 | $0.2848 |
| LED3 | 1 | C49237860 | SMD | HD2525 Blue 455nm | 2,001 | $0.2025 |
| R1-R3 | 3 | C247160 | 0805 | 0.22R current sense, 454mA per channel | 42,731 | $0.0044 |
| R4-R6 | 3 | C25900 | 0402 | 4.7k pull-up for WS2811 open-drain outputs | 4,423,363 | $0.0008 |
| R7 | 1 | C25744 | 0402 | 10k pull-down, U7 OE enable | 2,415,244 | $0.0008 |
| U1 | 1 | C114581 | SOP-8 | WS2811 pixel controller, SET pin floated for 800kHz | 261,017 | $0.0324 |
| U2-U4 | 3 | C347356 | SOT-89-5 | PT4115 buck LED driver, one per RGB channel | 171,387 | $0.0935 |
| U5 | 1 | C71136 | SOT-89-3 | 78L05 5V regulator, basic part | 87,009 | $0.0692 |
| U6 | 1 | C5590 | SOIC-14 | 74HC04 hex inverter, WS2811 open-drain inversion | 95,947 | $0.1575 |
| U7 | 1 | C350557 | SC-70-5 | SN74AHCT1G125 3.3V-to-5V level shifter on DIN | 1,985 | $0.0931 |

## Notes

- Stock and pricing values are live snapshots and can change daily.
- For current values, re-run:

```bash
bomi fetch --all --force
bomi list --check
```
