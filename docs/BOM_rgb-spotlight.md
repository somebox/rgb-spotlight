# rgb-spotlight

25mm circular chainable RGB spotlight pixel, WS2811 + 3x PT4115

**16 line items (16 unique parts), ~$2.24 estimated (qty 1)**

## BOM

| Ref | Qty | LCSC | Package | Note | Stock | Price |
| --- | --- | --- | --- | --- | --- | --- |
| [C1-C4](#c1525) | 4 | C1525 | 0402 | 100nF X7R bypass caps | 26.31m | $0.0013 |
| [C5-C8](#c15850) | 4 | C15850 | 0805 | 10uF X5R 25V input bulk caps | 5.10m | $0.0203 |
| [D1-D3](#c64885) | 3 | C64885 | SOD-123 | B5819W 40V/1A Schottky freewheeling diode | 1.02m | $0.0165 |
| [J1-J2](#c265101) | 2 | C265101 | SMD,P=2mm,Surface Mount，Right Angle | JST PH 2.0mm 3P SMT RA, in/out connectors | 19k | $0.2516 |
| [L1-L3](#c168095) | 3 | C168095 | SMD,6x6mm | 100uH 1A shielded inductor | 226k | $0.0676 |
| [LED1](#c49237857) | 1 | C49237857 | SMD | HD2525 Red 625nm | 1,100 | $0.2641 |
| [LED2](#c49237859) | 1 | C49237859 | SMD | HD2525 Green 525nm | 2,085 | $0.2858 |
| [LED3](#c49237860) | 1 | C49237860 | SMD | HD2525 Blue 455nm | 2,001 | $0.2033 |
| [R1-R3](#c247160) | 3 | C247160 | 0805 | 0.22R current sense, 454mA per channel | 43k | $0.0044 |
| [R4-R6](#c25900) | 3 | C25900 | 0402 | 4.7k pull-up for WS2811 open-drain outputs | 4.75m | $0.0008 |
| [R7](#c25744) | 1 | C25744 | 0402 | 10k pull-down, U7 OE enable | 6.15m | $0.0008 |
| [U1](#c114581) | 1 | C114581 | SOP-8 | WS2811 pixel controller, SET pin floated for 800kHz | 273k | $0.0325 |
| [U2-U4](#c347356) | 3 | C347356 | SOT-89-5 | PT4115 buck LED driver, one per RGB channel | 177k | $0.0899 |
| [U5](#c71136) | 1 | C71136 | SOT-89-3 | 78L05 5V regulator, basic part | 72k | $0.0719 |
| [U6](#c5590) | 1 | C5590 | SOIC-14 | 74HC04 hex inverter, WS2811 open-drain inversion | 81k | $0.1571 |
| [U7](#c350557) | 1 | C350557 | SC-70-5 | SN74AHCT1G125 3.3V-to-5V level shifter on DIN | 2,837 | $0.0980 |

## Details

### C1525

| | |
|---|---|
| **Designator** | C1-C4 |
| **Part** | CL05B104KO5NNNC |
| **LCSC** | C1525 |
| **Manufacturer** | Samsung Electro-Mechanics |
| **Package** | 0402 |
| **Type** | Basic (no extra fee) |
| **Quantity** | 4 |
| **Description** | 100nF 16V X7R ±10% 0402 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS |
| **Notes** | 100nF X7R bypass caps |
| **Stock** | 26,311,185 |
| **Pricing** | $0.0013 (≥1), $0.0010 (≥1000), $0.0009 (≥3000), $0.0008 (≥10000), $0.0007 (≥50000), $0.0007 (≥50200) |
| **Capacitance** | 100nF |
| **Temperature Coefficient** | X7R |
| **Tolerance** | ±10% |
| **Voltage Rating** | 16V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL05B104KO5NNNC_C1525.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/1877-CL05B104KO5NNNC/C1525 |

### C15850

| | |
|---|---|
| **Designator** | C5-C8 |
| **Part** | CL21A106KAYNNNE |
| **LCSC** | C15850 |
| **Manufacturer** | Samsung Electro-Mechanics |
| **Package** | 0805 |
| **Type** | Basic (no extra fee) |
| **Quantity** | 4 |
| **Description** | 10uF 25V X5R ±10% 0805 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS |
| **Notes** | 10uF X5R 25V input bulk caps |
| **Stock** | 5,098,638 |
| **Pricing** | $0.0203 (≥1), $0.0156 (≥200), $0.0135 (≥600), $0.0119 (≥2000), $0.0113 (≥10000), $0.0108 (≥20000) |
| **Capacitance** | 10uF |
| **Temperature Coefficient** | X5R |
| **Tolerance** | ±10% |
| **Voltage Rating** | 25V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL21A106KAYNNNE_C15850.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/16532-CL21A106KAYNNNE/C15850 |

### C64885

| | |
|---|---|
| **Designator** | D1-D3 |
| **Part** | B5819W |
| **LCSC** | C64885 |
| **Manufacturer** | MDD(Microdiode Semiconductor) |
| **Package** | SOD-123 |
| **Type** | Extended |
| **Quantity** | 3 |
| **Description** | -55℃~+125℃ 1A 1mA@40V 25A 40V 600mV@1A Independent SOD-123 Schottky Diodes ROHS |
| **Notes** | B5819W 40V/1A Schottky freewheeling diode |
| **Stock** | 1,024,982 |
| **Pricing** | $0.0165 (≥1), $0.0136 (≥500), $0.0092 (≥3000), $0.0083 (≥6000), $0.0079 (≥24000), $0.0076 (≥51000) |
| **Current - Rectified** | 1A |
| **Diode Configuration** | Independent |
| **Non-Repetitive Peak Forward Surge Current** | 25A |
| **Operating Junction Temperature Range** | -55℃~+125℃ |
| **Reverse Leakage Current (Ir)** | 1mA@40V |
| **Voltage - DC Reverse(Vr)** | 40V |
| **Voltage - Forward(Vf@If)** | 600mV@1A |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2407291648_MDD-Microdiode-Semiconductor-B5819W_C64885.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/MDD_Microdiode_Semiconductor-B5819W/C64885 |

### C265101

| | |
|---|---|
| **Designator** | J1-J2 |
| **Part** | S3B-PH-SM4-TB(LF)(SN) |
| **LCSC** | C265101 |
| **Manufacturer** | JST |
| **Package** | SMD,P=2mm,Surface Mount，Right Angle |
| **Type** | Extended |
| **Quantity** | 2 |
| **Description** | -25℃~+85℃ 1 100V 1x3P 2A 2mm 3 3P 5.5mm 8.6mm 9.9mm Auxiliary Solder Pin Beige Copper alloy PA PH Surface Mount, Right Angle Tin UL94V-0 SMD,P=2mm,Surface Mount，Right Angle Wire To Board Connector ROHS |
| **Notes** | JST PH 2.0mm 3P SMT RA, in/out connectors |
| **Stock** | 19,232 |
| **Pricing** | $0.2516 (≥1), $0.2017 (≥50), $0.1804 (≥150), $0.1538 (≥1000), $0.1419 (≥2000), $0.1348 (≥5000) |
| **Color** | Beige |
| **Contact Material** | Copper alloy |
| **Contact Plating** | Tin |
| **Current Rating** | 2A |
| **Flame Retardant Rating** | UL94V-0 |
| **Mounting Type** | Surface Mount, Right Angle |
| **Number of PINs Per Row** | 3 |
| **Number of Pins** | 3P |
| **Number of Rows** | 1 |
| **Operating Temperature** | -25℃~+85℃ |
| **Pins Structure** | 1x3P |
| **Pitch** | 2mm |
| **Plastic Material** | PA |
| **Reference Series** | PH |
| **Row Spacing** | - |
| **Supplementary Features** | Auxiliary Solder Pin |
| **Voltage Rating** | 100V |
| **X-Length of Bottom Edge on Board (Spacing Line)** | 9.9mm |
| **Y-Width of Bottom Edge on Board** | 8.6mm |
| **Z-Height of the Board** | 5.5mm |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_1810261109_JST-S3B-PH-SM4-TB-LF-SN_C265101.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/JST-S3B_PH_SM4_TB_LF_SN/C265101 |

### C168095

| | |
|---|---|
| **Designator** | L1-L3 |
| **Part** | FNR6045S101MT |
| **LCSC** | C168095 |
| **Manufacturer** | cjiang (Changjiang Microelectronics Tech) |
| **Package** | SMD,6x6mm |
| **Type** | Extended |
| **Quantity** | 3 |
| **Description** | 100uH 1A 563mΩ 880mA Magnetic Shielded Inductor ±20% SMD,6x6mm Power Inductors ROHS |
| **Notes** | 100uH 1A shielded inductor |
| **Stock** | 226,797 |
| **Pricing** | $0.0676 (≥1), $0.0528 (≥100), $0.0455 (≥300), $0.0376 (≥1500), $0.0332 (≥4500), $0.0310 (≥10500) |
| **Current - Saturation(Isat)** | 1A |
| **Current Rating** | 880mA |
| **DC Resistance(DCR)** | 563mΩ |
| **Inductance** | 100uH |
| **Tolerance** | ±20% |
| **Type** | Magnetic Shielded Inductor |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_cjiang--Changjiang-Microelectronics-Tech-FNR6045S101MT_C168095.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/179478-FNR6045S101MT/C168095 |

### C49237857

| | |
|---|---|
| **Designator** | LED1 |
| **Part** | XL-HD2525SURC-A4 |
| **LCSC** | C49237857 |
| **Manufacturer** | XINGLIGHT |
| **Package** | SMD |
| **Type** | Extended |
| **Quantity** | 1 |
| **Description** | -40℃~+135℃ 120° 2.4V 3W 620nm 625nm 700mA Discrete Diode Red Water Clear SMD LED Indication - Discrete ROHS |
| **Notes** | HD2525 Red 625nm |
| **Stock** | 1,100 |
| **Pricing** | $0.2641 (≥1), $0.2071 (≥50), $0.1826 (≥150), $0.1521 (≥500), $0.1384 (≥2500), $0.1303 (≥5000) |
| **Diode Configuration** | Discrete Diode |
| **Forward Current** | 700mA |
| **Illumination Color** | Red |
| **Lens Color** | Water Clear |
| **Operating Temperature** | -40℃~+135℃ |
| **Peak Wavelength** | 625nm |
| **Power(Watts)** | 3W |
| **Viewing Angle** | 120° |
| **Voltage - Forward(Vf)** | 2.4V |
| **Wavelength - Dominant** | 620nm |
| **JLCPCB** | https://jlcpcb.com/partdetail/XINGLIGHT-XL_HD2525SURCA4/C49237857 |

### C49237859

| | |
|---|---|
| **Designator** | LED2 |
| **Part** | XL-HD2525UGC-A4 |
| **LCSC** | C49237859 |
| **Manufacturer** | XINGLIGHT |
| **Package** | SMD |
| **Type** | Extended |
| **Quantity** | 1 |
| **Description** | -40℃~+135℃ 120° 3.4V 3W 525nm 525nm 700mA Discrete Diode Green Water Clear SMD LED Indication - Discrete ROHS |
| **Notes** | HD2525 Green 525nm |
| **Stock** | 2,085 |
| **Pricing** | $0.2858 (≥1), $0.2240 (≥50), $0.1975 (≥150), $0.1646 (≥500), $0.1524 (≥2500), $0.1435 (≥5000) |
| **Diode Configuration** | Discrete Diode |
| **Forward Current** | 700mA |
| **Illumination Color** | Green |
| **Lens Color** | Water Clear |
| **Operating Temperature** | -40℃~+135℃ |
| **Peak Wavelength** | 525nm |
| **Power(Watts)** | 3W |
| **Viewing Angle** | 120° |
| **Voltage - Forward(Vf)** | 3.4V |
| **Wavelength - Dominant** | 525nm |
| **JLCPCB** | https://jlcpcb.com/partdetail/XINGLIGHT-XL_HD2525UGCA4/C49237859 |

### C49237860

| | |
|---|---|
| **Designator** | LED3 |
| **Part** | XL-HD2525UBC-A4 |
| **LCSC** | C49237860 |
| **Manufacturer** | XINGLIGHT |
| **Package** | SMD |
| **Type** | Extended |
| **Quantity** | 1 |
| **Description** | -40℃~+135℃ 120° 3.4V 3W 455nm 455nm Blue Discrete Diode Water Clear SMD LED Indication - Discrete ROHS |
| **Notes** | HD2525 Blue 455nm |
| **Stock** | 2,001 |
| **Pricing** | $0.2033 (≥1), $0.1594 (≥50), $0.1405 (≥150), $0.1170 (≥500), $0.1066 (≥2000), $0.1004 (≥4000) |
| **Diode Configuration** | Discrete Diode |
| **Illumination Color** | Blue |
| **Lens Color** | Water Clear |
| **Operating Temperature** | -40℃~+135℃ |
| **Peak Wavelength** | 455nm |
| **Power(Watts)** | 3W |
| **Viewing Angle** | 120° |
| **Voltage - Forward(Vf)** | 3.4V |
| **Wavelength - Dominant** | 455nm |
| **JLCPCB** | https://jlcpcb.com/partdetail/XINGLIGHT-XL_HD2525UBCA4/C49237860 |

### C247160

| | |
|---|---|
| **Designator** | R1-R3 |
| **Part** | 0805W8F220LT5E |
| **LCSC** | C247160 |
| **Manufacturer** | UNI-ROYAL(Uniroyal Elec) |
| **Package** | 0805 |
| **Type** | Extended |
| **Quantity** | 3 |
| **Description** | -55℃~+155℃ 125mW 150V 220mΩ Thick Film Resistor ±1% ±800ppm/℃ 0805 Chip Resistor - Surface Mount ROHS |
| **Notes** | 0.22R current sense, 454mA per channel |
| **Stock** | 43,401 |
| **Pricing** | $0.0044 (≥1), $0.0035 (≥1000), $0.0027 (≥5000), $0.0025 (≥10000), $0.0022 (≥50000), $0.0022 (≥50200) |
| **Operating Temperature** | -55℃~+155℃ |
| **Power(Watts)** | 125mW |
| **Resistance** | 220mΩ |
| **Temperature Coefficient** | ±800ppm/℃ |
| **Tolerance** | ±1% |
| **Type** | Thick Film Resistor |
| **Voltage-Supply(Max)** | 150V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2205311916_UNI-ROYAL-Uniroyal-Elec-0805W8F220LT5E_C247160.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/244368-0805W8F220LT5E/C247160 |

### C25900

| | |
|---|---|
| **Designator** | R4-R6 |
| **Part** | 0402WGF4701TCE |
| **LCSC** | C25900 |
| **Manufacturer** | UNI-ROYAL(Uniroyal Elec) |
| **Package** | 0402 |
| **Type** | Basic (no extra fee) |
| **Quantity** | 3 |
| **Description** | -55℃~+155℃ 4.7kΩ 50V 62.5mW Thick Film Resistor ±1% ±100ppm/℃ 0402 Chip Resistor - Surface Mount ROHS |
| **Notes** | 4.7k pull-up for WS2811 open-drain outputs |
| **Stock** | 4,750,163 |
| **Pricing** | $0.0008 (≥1), $0.0007 (≥1000), $0.0006 (≥3000), $0.0005 (≥10000), $0.0005 (≥50000), $0.0005 (≥50200) |
| **Operating Temperature** | -55℃~+155℃ |
| **Power(Watts)** | 62.5mW |
| **Resistance** | 4.7kΩ |
| **Temperature Coefficient** | ±100ppm/℃ |
| **Tolerance** | ±1% |
| **Type** | Thick Film Resistor |
| **Voltage-Supply(Max)** | 50V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2206010045_UNI-ROYAL-Uniroyal-Elec-0402WGF4701TCE_C25900.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/26643-0402WGF4701TCE/C25900 |

### C25744

| | |
|---|---|
| **Designator** | R7 |
| **Part** | 0402WGF1002TCE |
| **LCSC** | C25744 |
| **Manufacturer** | UNI-ROYAL(Uniroyal Elec) |
| **Package** | 0402 |
| **Type** | Basic (no extra fee) |
| **Quantity** | 1 |
| **Description** | -55℃~+155℃ 10kΩ 50V 62.5mW Thick Film Resistor ±1% ±100ppm/℃ 0402 Chip Resistor - Surface Mount ROHS |
| **Notes** | 10k pull-down, U7 OE enable |
| **Stock** | 6,154,117 |
| **Pricing** | $0.0008 (≥1), $0.0007 (≥1000), $0.0006 (≥3000), $0.0006 (≥10000), $0.0005 (≥50000), $0.0005 (≥50200) |
| **Operating Temperature** | -55℃~+155℃ |
| **Power(Watts)** | 62.5mW |
| **Resistance** | 10kΩ |
| **Temperature Coefficient** | ±100ppm/℃ |
| **Tolerance** | ±1% |
| **Type** | Thick Film Resistor |
| **Voltage-Supply(Max)** | 50V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2411221126_UNI-ROYAL-Uniroyal-Elec-0402WGF1002TCE_C25744.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/26487-0402WGF1002TCE/C25744 |

### C114581

| | |
|---|---|
| **Designator** | U1 |
| **Part** | WS2811 |
| **LCSC** | C114581 |
| **Manufacturer** | Worldsemi |
| **Package** | SOP-8 |
| **Type** | Extended |
| **Quantity** | 1 |
| **Description** | -25℃~+85℃ 16.5mA 20V 3 5V~24V 800kHz Over Voltage Protection、Short-Circuit  Protection PWM SOP-8 LED Drivers ROHS |
| **Notes** | WS2811 pixel controller, SET pin floated for 800kHz |
| **Stock** | 273,223 |
| **Pricing** | $0.0325 (≥1), $0.0257 (≥200), $0.0219 (≥600), $0.0167 (≥4000), $0.0147 (≥8000), $0.0136 (≥20000) |
| **Constant Current Accuracy** | - |
| **Dimming** | PWM |
| **Features** | Over Voltage Protection、Short-Circuit  Protection |
| **Frequency - Switching** | 800kHz |
| **Number of Channels** | 3 |
| **Operating temperature** | -25℃~+85℃ |
| **Output Current** | 16.5mA |
| **Output Voltage** | 20V |
| **Switch Tube (Built-In/External)** | - |
| **Topology** | - |
| **Type** | - |
| **Voltage - Input(AC)** | - |
| **Voltage - Input(DC)** | 5V~24V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_1810081420_Worldsemi-WS2811_C114581.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/Worldsemi-WS2811/C114581 |

### C347356

| | |
|---|---|
| **Designator** | U2-U4 |
| **Part** | PT4115 |
| **LCSC** | C347356 |
| **Manufacturer** | UMW(Youtai Semiconductor Co., Ltd.) |
| **Package** | SOT-89-5 |
| **Type** | Extended |
| **Quantity** | 3 |
| **Description** | -25℃~+85℃ 1.2A 1MHz 5% 6V~30V Analog、PWM Buck Built-in DC-DC Over-Temperature Protection (OTP) SOT-89-5 LED Drivers ROHS |
| **Notes** | PT4115 buck LED driver, one per RGB channel |
| **Stock** | 177,910 |
| **Pricing** | $0.0899 (≥1), $0.0714 (≥50), $0.0619 (≥150), $0.0512 (≥1000), $0.0486 (≥2000), $0.0467 (≥5000) |
| **Constant Current Accuracy** | 5% |
| **Dimming** | Analog、PWM |
| **Features** | Over-Temperature Protection (OTP) |
| **Frequency - Switching** | 1MHz |
| **Number of Channels** | - |
| **Operating temperature** | -25℃~+85℃ |
| **Output Current** | 1.2A |
| **Output Voltage** | - |
| **Switch Tube (Built-In/External)** | Built-in |
| **Topology** | Buck |
| **Type** | DC-DC |
| **Voltage - Input(AC)** | - |
| **Voltage - Input(DC)** | 6V~30V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_1912111437_UMW-Youtai-Semiconductor-Co---Ltd--PT4115_C347356.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/324016-PT4115/C347356 |

### C71136

| | |
|---|---|
| **Designator** | U5 |
| **Part** | 78L05G-AB3-R |
| **LCSC** | C71136 |
| **Manufacturer** | UTC(Unisonic Tech) |
| **Package** | SOT-89-3 |
| **Type** | Basic (no extra fee) |
| **Quantity** | 1 |
| **Description** | -40℃~+85℃ 1 1.7V@(40mA) 100mA 2mA 30V 40uV 5V 80dB@(120Hz) Fixed Over Current Protection、Short Circuit Protection、Thermal Shutdown Positive SOT-89-3 Voltage Regulators - Linear, Low Drop Out (LDO) Regulators ROHS |
| **Notes** | 78L05 5V regulator, basic part |
| **Stock** | 72,112 |
| **Pricing** | $0.0719 (≥1), $0.0581 (≥50), $0.0509 (≥150), $0.0452 (≥500), $0.0417 (≥2500), $0.0405 (≥4000) |
| **Features** | Over Current Protection、Short Circuit Protection、Thermal Shutdown |
| **Noise** | 40uV |
| **Number of Outputs** | 1 |
| **Operating Temperature** | -40℃~+85℃ |
| **Output Configuration** | Positive |
| **Output Current** | 100mA |
| **Output Type** | Fixed |
| **Output Voltage** | 5V |
| **Power Supply Rejection Ratio (PSRR)** | 80dB@(120Hz) |
| **Voltage - Supply** | 30V |
| **Voltage Dropout** | 1.7V@(40mA) |
| **standby current** | 2mA |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_UTC-Unisonic-Tech-78L05G-AB3-R_C71136.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/UTC_Unisonic_Tech-78L05G_AB3R/C71136 |

### C5590

| | |
|---|---|
| **Designator** | U6 |
| **Part** | 74HC04D,653 |
| **LCSC** | C5590 |
| **Manufacturer** | Nexperia |
| **Package** | SOIC-14 |
| **Type** | Extended |
| **Quantity** | 1 |
| **Description** | -40℃~+125℃ 1 1.5V~4.2V 1.9V、3.7V、5.2V 100mV、400mV、400mV 14ns@6V,50pF 2V~6V 2uA 5.2mA 5.2mA 500mV~1.8V 6 74HC SOIC-14 Inverters ROHS |
| **Notes** | 74HC04 hex inverter, WS2811 open-drain inversion |
| **Stock** | 81,287 |
| **Pricing** | $0.1571 (≥1), $0.1231 (≥50), $0.1064 (≥150), $0.0915 (≥500), $0.0874 (≥2500), $0.0850 (≥5000) |
| **Current - Output High(IOH)** | 5.2mA |
| **Current - Output Low(IOL)** | 5.2mA |
| **Input Logic Level - High** | 1.5V~4.2V |
| **Input Logic Level -Low** | 500mV~1.8V |
| **Input Type** | - |
| **Number of Circuits** | 6 |
| **Number of Inputs** | 1 |
| **Operating Temperature** | -40℃~+125℃ |
| **Output Logic Level - High** | 1.9V、3.7V、5.2V |
| **Output Logic Level - Low** | 100mV、400mV、400mV |
| **Propagation Delay** | 14ns@6V,50pF |
| **Quiescent Current(Iq)** | 2uA |
| **Series** | 74HC |
| **Voltage - Supply** | 2V~6V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2407241044_Nexperia-74HC04D-653_C5590.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/Nexperia-74HC04D653/C5590 |

### C350557

| | |
|---|---|
| **Designator** | U7 |
| **Part** | SN74AHCT1G125DCKR |
| **LCSC** | C350557 |
| **Manufacturer** | Texas Instruments |
| **Package** | SC-70-5 |
| **Type** | Extended |
| **Quantity** | 1 |
| **Description** | -40℃~+125℃ 1 1 10uA 4.5V~5.5V 5.5ns@5V,15pF 74AHCT 8mA 8mA Tri-State Unidirectional SC-70-5 Buffers, Drivers, Receivers, Transceivers ROHS |
| **Notes** | SN74AHCT1G125 3.3V-to-5V level shifter on DIN |
| **Stock** | 2,837 |
| **Pricing** | $0.0980 (≥1), $0.0772 (≥50), $0.0669 (≥150), $0.0592 (≥500), $0.0530 (≥3000), $0.0498 (≥6000) |
| **Channel Type** | Unidirectional |
| **Current - Output High(IOH)** | 8mA |
| **Current - Output Low(IOL)** | 8mA |
| **Input type** | - |
| **Logic Family** | 74AHCT |
| **Number of Bits per Element** | 1 |
| **Number of Elements** | 1 |
| **Operating Temperature** | -40℃~+125℃ |
| **Propagation Delay** | 5.5ns@5V,15pF |
| **Quiescent Current** | 10uA |
| **Voltage - Supply** | 4.5V~5.5V |
| **output type** | Tri-State |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_1912111437_Texas-Instruments-SN74AHCT1G125DCKR_C350557.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/TexasInstruments-SN74AHCT1G125DCKR/C350557 |

