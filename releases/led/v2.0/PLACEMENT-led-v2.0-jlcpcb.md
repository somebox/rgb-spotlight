# Placement check: led

Parts to check in JLC's placement preview before paying: 3 of the 3 parts JLC places on both sides (3 top, 0 bottom). Two-pad parts drawn symmetrically are left out (0). For a front-only order, only the top ones; for a back-only order, only the bottom ones.

For each one, zoom in until single pads show:
- every leg sits on its pad, and the body lies the way KiCad's footprint has it;
- the pink pin-1 dot sits on pad 1, by the silkscreen's pin-1 or cathode mark;
- in the 2D view, the hover reading over pad 1 matches *Pad 1 at* below.

Positions are in mm from the board's drill/place origin with Y up: the frame of the Gerbers and the CPL, the one JLC places parts in, and the one its preview's hover reading counts in. Bottom parts are in it as seen from the top, as in the CPL. The board outline runs from (125.000, -125.000) to (175.000, -75.000). KiCad's status bar shows the same numbers with Preferences, PCB Editor, Origins & Axes set to the drill/place file origin and the Y axis increasing up.

*CPL* is KiCad's angle (on the bottom, 180 minus KiCad's) plus *Corr.*, the correction from pcbkit's rotation table (data/jlc/corrections.csv). *Rule* is the table's row: a pattern and the field it matched, or an LCSC number and the package rule it stands in for. *Checked* is the last time that row was seen right in JLC's preview; it was right for the parts checked then, and JLC's footprint for another part in the same package can still differ (SOT-23-5 comes both ways). **never**: no check on record, look at these first.

## By part

One line for each part and rule: at least one of each, and the **never** lines first.

| Side | LCSC | Footprint | Parts | Corr. | Rule | Checked |
|---|---|---|---|--:|---|---|
| top | C49237857 | LED_XINGLIGHT_HD2525 | LED1 |  |  |  |
| top | C49237859 | LED_XINGLIGHT_HD2525 | LED2 |  |  |  |
| top | C49237860 | LED_XINGLIGHT_HD2525 | LED3 |  |  |  |

## Top (3)

| Ref | LCSC | Footprint | KiCad | Corr. | CPL | Rule | Checked | Pad 1 at | Centre |
|---|---|---|--:|--:|--:|---|---|---|---|
| LED1 | C49237857 | LED_XINGLIGHT_HD2525 | 0 |  | 0 |  |  | 1: 148.925, -88.000 | 150.000, -88.000 |
| LED2 | C49237859 | LED_XINGLIGHT_HD2525 | 120 |  | 120 |  |  | 1: 140.145, -106.931 | 139.608, -106.000 |
| LED3 | C49237860 | LED_XINGLIGHT_HD2525 | 240 |  | 240 |  |  | 1: 160.930, -105.069 | 160.392, -106.000 |
