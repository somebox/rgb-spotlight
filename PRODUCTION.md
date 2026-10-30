# Production

Status (2026-10-29): both boards pass `pcbkit release --dry-run` (ERC, DRC with parity, nothing unconnected) and would be released as v2.0; nothing released or ordered for v2 yet. Before ordering: DESIGN.md §5 (v1 bench tests) and §6 (open items), and the housing decision (outline preset, LAYOUT.md).

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
| **driver** | FR4, 2 layers, 1.6 mm, 1 oz, 50 mm round (`disc50`) | Top side: 33 placements, 18 BOM lines. J1/J2 (JST XH, back) and J3 (JST PH 6, front) are through-hole: JLC THT assembly, or hand-solder. R9 is DNP (no LCSC number, out of the BOM) |
| **led** | **aluminium**, 1 layer, 1.6 mm, 1 W/mK (2 W/mK if offered cheaply), 50 mm round | Top side: 3 placements (the LEDs) |

The LED board's Gerber zip also holds empty back layers; on a 1-layer aluminium order JLC uses only F.Cu, F.Mask, F.Silkscreen, Edge.Cuts and the drill files.

## Order checklist

The things that went wrong before, or could:

- **LED polarity (LED board).** Pad 1 = cathode, at −x of the footprint (DESIGN.md §6.1).
  - The datasheet's top view puts the package dot at the anode; LCSC's footprint puts it at pad 1.
  - Before paying, check JLC's placement preview: each LED's cathode must be on the pad wired to "x−".
  - Diode-test a v1 LED first if that's still open.
- **Schottky D1–D3 (SOD-123).** The cathode band faces the 12 V side (Rs / VIN). Inverted, the diode shorts SW to 12 V.
- **TVS D4 (SMA).** The cathode band goes to +12V. Inverted, it conducts the moment 12 V is applied.
- **Placement checklist first.** Its **never** rows have rotation rules that have never been checked in JLC's preview:
  - `^SOT-89` +180°: U2–U4 (PT4115, SOT-89-5) and U5 (78L05, SOT-89-3);
  - `^SOT-353` +180°: U7 (74AHCT1G125).
  For each one, the pin-1 dot must sit on pad 1 at the position the checklist gives. Afterwards, record the result in pcb-kit's `data/jlc/corrections.csv`, so the next board inherits it.
- **PT4115 U2–U4 (SOT-89-5).** Pin 1 is SW. The tab must sit on the wide GND pad, not rotated 180°.
- **U1 (SOIC-8), U6 (SOIC-14).** The SOIC rule (+270°) was checked on 2026-10-26. Still check the pin-1 dots; v1 used EasyEDA footprints, these are KiCad's.
- **J1/J2 (JST XH, back).** They are in the `-back` BOM/CPL and the `-both` files. For a top-only order, hand-solder them (through-hole).
- **BOM matching.** JLC must say "Your BOM: JLCPCB Part #". With an `LCSC` header it matches by value instead (pcb-kit lesson).
- **Order number:** choose "specify position" (`JLCJLCJLCJLC` on the driver's back silk).
- **Stock:** `bomi --project boards/driver list --check` and the same for `boards/led`. Green LED C49237859 had 325 left on 2026-10-05.

## After the boards arrive

- **LED harness:** six 24 AWG silicone wires, about 8 cm, twisted per colour.
  - Solder them to the LED board's pads (R+ R− G+ G− B+ B−) and pass them through the centre hole.
  - Crimp them into a JST PHR-6 housing (SPH-002T contacts) in the same order, pin 1 = R+.
  - Aluminium boards pull heat away fast, so use a hot iron or preheat.
- **Chain cables:** JST XH 3-pin, wired pin 1 to pin 1 (D4). Up to 6 lights per 12 V feed (D13).
- **Bring-up:**
  - 12 V with a current-limited supply at 0.6 A for one light: 0.42 A expected at full white.
  - Check 5 V at U1 pin 8, then the DIM pins with data.
  - Listen for the 4 kHz singing noted in DESIGN.md §2.7.

## Costs

| Date | Board | Qty | Item | Cost |
| --- | --- | --- | --- | --- |
| 2026-10-05 | driver | 1 | BOM, bomi qty-1 pricing | ≈ $2.18 plus the Extended-part fees listed in docs/BOM_driver.md |
| 2026-10-05 | led | 1 | BOM, bomi qty-1 pricing | ≈ $0.77 (3 Extended LEDs) |

No quotes or orders for v2 yet.

## Overview

<!-- pcbkit:production:begin -->
<!-- generated by pcbkit production from the boards' releases.toml, production/orders/*/order.toml and production/stock.toml: edit those, then run it again -->

### In production

_none_

### Boards

| PCB | in KiCad | released | state | parts a board (USD) | latest order | in stock | parts on hand build |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [driver](boards/driver) | 2.0 |  | not checked | 2.32, 7 ext. |  |  |  |
| [led](boards/led) | 2.0 |  | not checked | 0.77, 3 ext. |  |  |  |

Parts costs: placed parts at unit prices from konnect's JLC parts cache of 2026-09-29; Extended parts add a setup fee each per order.

### Parts for the open orders

To finish every board of the open orders by hand: the assembled ones, or every PCB of a bare order (with the parts the assembler would have placed), as the versions they pin need; and the orders' extras.

_none_

### Orders

_none_

### Problems

_none_

<!-- pcbkit:production:end -->
