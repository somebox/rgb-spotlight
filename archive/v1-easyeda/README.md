# v1 — EasyEDA design (Mar 2026), archived

Produced by JLCPCB. It never lit up; the faults are in [DESIGN.md §1](../../DESIGN.md#1-v1-post-mortem-easyeda-ordered-mar-2026).

| File | What |
|---|---|
| `SCH_rgb-discreet-leds_2026-10-05.json` | EasyEDA Std schematic export |
| `PCB_PCB_rgb-discreet-leds_2026-10-05.json` | EasyEDA Std PCB export |
| `v1-easyeda.kicad_pcb` | KiCad import of the PCB (`kicad-cli pcb import`), as-built reference only |
| `v1-netlist.txt` | as-built netlist taken from the PCB pads |
| `v1-front.png`, `v1-back-mirrored.png` | renders of the import |
| `rgb-spotlight-bom-v1.md` | v1 BOM and rationale. **Its PT4115 connection tables and 78L05 pin table are wrong** (see DESIGN.md §1) |

The KiCad import DRCs with many clearance and silk notes against KiCad's default rules. That's expected; it is not a design to fabricate from.
