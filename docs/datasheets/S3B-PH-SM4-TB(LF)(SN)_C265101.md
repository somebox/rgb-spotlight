# S3B-PH-SM4-TB(LF)(SN) (C265101)

**Manufacturer:** JST  
**Package:** SMD,P=2mm,Surface Mount，Right Angle  
**Category:** Wire To Board Connector  
**Datasheet:** https://www.lcsc.com/datasheet/lcsc_datasheet_1810261109_JST-S3B-PH-SM4-TB-LF-SN_C265101.pdf  
**JLCPCB:** https://jlcpcb.com/partdetail/JST-S3B_PH_SM4_TB_LF_SN/C265101  

---

# JST S3B-PH-SM4-TB(LF)(SN) — Technical Summary

## Overview
3-circuit, 2.0mm pitch, SMT right-angle (side entry) wire-to-board shrouded header. Part of JST's PH series. Tape-and-reel packaged for automated SMT assembly.

---

## Key Specifications

| Parameter | Value |
|-----------|-------|
| Voltage Rating | 100V AC/DC |
| Current Rating | 2A AC/DC (per contact, AWG #24) |
| Temperature Range | −25°C to +85°C (including self-heating) |
| Withstanding Voltage | 800V AC/min |
| Contact Resistance | ≤10 mΩ (initial); ≤20 mΩ (post-environmental) |
| Insulation Resistance | ≥1,000 MΩ |
| Pitch | 2.0 mm |
| Number of Circuits | 3 |
| Mounting Style | SMT, Right Angle (Side Entry), SM4 type |
| Mated Height | 8.6 mm |
| Body Width | 5.5 mm |
| Body Length (B) | 9.9 mm |
| PC Board Thickness | 0.8 to 1.6 mm |
| Applicable Wire | AWG #32 to #24 |
| Housing Material | PA, UL94V-0, Beige/Natural (Ivory) |
| Contact Material | Copper alloy, tin-plated (reflow) |
| Solder Tab Material | Brass, tin-plated (reflow) |
| Flammability | UL94V-0 |
| RoHS | Compliant [(LF)(SN) labeled] |
| Packaging | Tape & Reel, 1,000 pcs/reel |

---

## Pin Descriptions

> Circuit No. 1 is marked on the connector body. Pins are numbered sequentially at 2.0 mm pitch.

| Pin No. | Description |
|---------|-------------|
| **1** | Circuit No. 1 (marked on housing) — Signal/Power |
| **2** | Circuit No. 2 — Signal/Power |
| **3** | Circuit No. 3 — Signal/Power |
| **SM4 Tabs** | Auxiliary solder retention tabs (×2, not signal-carrying) — mechanical PCB anchoring only |

> ⚠️ Pin function is application-defined; the connector provides no polarity enforcement beyond the keyed housing shroud. Circuit No. 1 is indicated by a molded marker on the housing.

---

## Mating Connector

| Component | Model |
|-----------|-------|
| Mating Housing | **PHR-3** (3-circuit, PA66, UL94V-0, natural white) |
| Crimp Contact (AWG 30–24) | **SPH-002T-P0.5S** |
| Crimp Contact (AWG 28–24, low insertion force) | **SPH-002T-P0.5L** |
| Crimp Contact (AWG 32–28) | **SPH-004T-P0.5S** |

---

## Recommended PCB Land Pattern (SMT Side Entry)

```
Signal pads (×3):
  Pitch:        2.0 mm
  Pad size:     per JST SMT footprint guideline

Retention tabs (SM4, ×2):
  Positioned at each end of connector body
  Provide mechanical solder anchoring — verify land pattern per JST datasheet

Component body:
  A (contact span) = 4.0 mm
  B (overall length) = 9.9 mm
  Height above PCB = 5.5 mm
  Depth (wire exit side) = 6.0 mm
```

> ℹ️ Use JST-provided land pattern drawing for exact pad dimensions. Tolerances are non-cumulative ±0.05 mm on all centers.

---

## Design Notes & Limitations

- **SMT reflow only** — SM4 solder tabs provide board retention during reflow; ensure solder paste is applied to tab pads.
- **Auxiliary tabs are mechanical only** — do not route signals through SM4 retention tabs.
- **Wire-side clearance** — right-angle (side entry) orientation requires adequate clearance for wire egress perpendicular to the PCB surface.
- **Maximum current per contact is 2A** — derate for elevated ambient temperatures or when all 3 circuits are simultaneously loaded.
- **Mating engagement** — fully shrouded header provides polarization; confirm Circuit No. 1 alignment with mating PHR-3 housing before assembly.
- **No gold-plating standard** — tin-plated contacts may be susceptible to fretting corrosion in high-vibration environments; contact JST for gold-plated variants.
- **Low insertion force variant** (SPH-002T-P0.5L) has reduced vibration resistance — use standard contact (SPH-002T-P0.5S) for vibration-prone applications.
- **PCB thickness** must be 0.8–1.6 mm for proper SM4 tab engagement.
- **Certifications:** UL Recognized (E60389), CSA Certified (LR20812), TÜV (R75087).