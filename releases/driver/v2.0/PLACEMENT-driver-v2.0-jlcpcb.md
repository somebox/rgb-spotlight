# Placement check: driver

Parts to check in JLC's placement preview before paying: 14 of the 35 parts JLC places on both sides (12 top, 2 bottom). Two-pad parts drawn symmetrically are left out (21). For a front-only order, only the top ones; for a back-only order, only the bottom ones.

For each one, zoom in until single pads show:
- every leg sits on its pad, and the body lies the way KiCad's footprint has it;
- the pink pin-1 dot sits on pad 1, by the silkscreen's pin-1 or cathode mark;
- in the 2D view, the hover reading over pad 1 matches *Pad 1 at* below.

Positions are in mm from the board's drill/place origin with Y up: the frame of the Gerbers and the CPL, the one JLC places parts in, and the one its preview's hover reading counts in. Bottom parts are in it as seen from the top, as in the CPL. The board outline runs from (-25.000, -25.000) to (25.000, 25.000). KiCad's status bar shows the same numbers with Preferences, PCB Editor, Origins & Axes set to the drill/place file origin and the Y axis increasing up.

*CPL* is KiCad's angle (on the bottom, 180 minus KiCad's) plus *Corr.*, the correction from pcbkit's rotation table (data/jlc/corrections.csv). *Rule* is the table's row: a pattern and the field it matched, or an LCSC number and the package rule it stands in for. *Checked* is the last time that row was seen right in JLC's preview; it was right for the parts checked then, and JLC's footprint for another part in the same package can still differ (SOT-23-5 comes both ways). **never**: no check on record, look at these first.

Under a rule never checked in the preview: `^SOT-89` (U2, U3, U4, U5); `^SOT-353` (U7).

## By part

One line for each part and rule: at least one of each, and the **never** lines first.

| Side | LCSC | Footprint | Parts | Corr. | Rule | Checked |
|---|---|---|---|--:|---|---|
| top | C64885 | D_SOD-123 | D1, D2, D3 |  |  |  |
| top | C19077535 | D_SMA | D4 |  |  |  |
| top | C131342 | JST_PH_B6B-PH-K_1x06_P2.00mm_Vertical | J3 |  |  |  |
| top | C114581 | SOIC-8_3.9x4.9mm_P1.27mm | U1 | +270 | `^SOIC-` (footprint) | 2026-10-26 |
| top | C347356 | SOT-89-5 | U2, U3, U4 | +180 | `^SOT-89` (footprint) | **never** |
| top | C71136 | SOT-89-3 | U5 | +180 | `^SOT-89` (footprint) | **never** |
| top | C5605 | SOIC-14_3.9x8.7mm_P1.27mm | U6 | +270 | `^SOIC-` (footprint) | 2026-10-26 |
| top | C350557 | SOT-353_SC-70-5 | U7 | +180 | `^SOT-353` (footprint) | **never** |
| bottom | C144394 | JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical | J1, J2 |  |  |  |

## Top (12)

| Ref | LCSC | Footprint | KiCad | Corr. | CPL | Rule | Checked | Pad 1 at | Centre |
|---|---|---|--:|--:|--:|---|---|---|---|
| D1 | C64885 | D_SOD-123 | 0 |  | 0 |  |  | 1: -1.650, 16.700 | 0.000, 16.700 |
| D2 | C64885 | D_SOD-123 | 120 |  | 120 |  |  | 1: -13.638, -9.779 | -14.463, -8.350 |
| D3 | C64885 | D_SOD-123 | 240 |  | 240 |  |  | 1: 15.288, -6.921 | 14.463, -8.350 |
| D4 | C19077535 | D_SMA | 60 |  | 60 |  |  | 1: -15.203, 6.468 | -14.203, 8.200 |
| J3 | C131342 | JST_PH_B6B-PH-K_1x06_P2.00mm_Vertical | 270 |  | 270 |  |  | 1: 0.000, 5.000 | 0.000, 0.000 |
| U1 | C114581 | SOIC-8_3.9x4.9mm_P1.27mm | 90 | +270 | 0 | `^SOIC-` (footprint) | 2026-10-26 | 1: 2.595, -20.975 | 4.500, -18.500 |
| U2 | C347356 | SOT-89-5 | 180 | +180 | 0 | `^SOT-89` (footprint) | **never** | 1: 1.850, 19.000 | 0.000, 20.500 |
| U3 | C347356 | SOT-89-5 | 300 | +180 | 120 | `^SOT-89` (footprint) | **never** | 1: -17.379, -7.898 | -17.754, -10.250 |
| U4 | C347356 | SOT-89-5 | 60 | +180 | 240 | `^SOT-89` (footprint) | **never** | 1: 15.529, -11.102 | 17.754, -10.250 |
| U5 | C71136 | SOT-89-3 | 0 | +180 | 180 | `^SOT-89` (footprint) | **never** | 1: 4.850, 21.000 | 6.500, 19.500 |
| U6 | C5605 | SOIC-14_3.9x8.7mm_P1.27mm | 270 | +270 | 180 | `^SOIC-` (footprint) | 2026-10-26 | 1: -1.190, -16.025 | -5.000, -18.500 |
| U7 | C350557 | SOT-353_SC-70-5 | 0 | +180 | 180 | `^SOT-353` (footprint) | **never** | 1: -10.438, 17.250 | -9.600, 16.600 |

## Bottom (2)

| Ref | LCSC | Footprint | KiCad | Corr. | CPL | Rule | Checked | Pad 1 at | Centre |
|---|---|---|--:|--:|--:|---|---|---|---|
| J1 | C144394 | JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical | 240 |  | 300 |  |  | 1: -15.637, 11.915 | -16.778, 9.860 |
| J2 | C144394 | JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical | 120 |  | 60 |  |  | 1: 18.137, 7.585 | 16.997, 9.640 |
