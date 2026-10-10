# rgb-spotlight-driver

RGB Spotlight v2 driver board (FR4), WS2811 + 3x PT4115, LEDs on the aluminium LED board

**19 line items (19 unique parts), ~$2.18 estimated (qty 1)**

## BOM

| Ref | Qty | LCSC | Package | Note | Stock | Price |
| --- | --- | --- | --- | --- | --- | --- |
| [C1-C4](#c1525) | 4 | C1525 | 0402 | 100nF X7R bypass: C1 WS2811, C2 74HC04, C3 74AHCT1G125, C4 78L05 out | 22.16m | $0.0045 |
| [C5](#c15850) | 1 | C15850 | 0805 | 10uF 25V 0805, 78L05 input | 4.92m | $0.0651 |
| [C6-C8](#c13585) | 3 | C13585 | 1206 | 10uF 50V X5R 1206, PT4115 VIN bypass (>=4.7uF after DC bias at 12V) | 2.38m | $0.2655 |
| [C9](#c12891) | 1 | C12891 | 1206 | 22uF 25V X5R 1206, 12V input bulk | 1.08m | $0.0494 |
| [D1-D3](#c64885) | 3 | C64885 | SOD-123 | B5819W 40V/1A Schottky freewheeling diode | 933k | $0.0194 |
| [D4](#c19077535) | 1 | C19077535 | DO-214AC(SMA) | SMAJ15A TVS on +12V (hot-plugged chain cables) | 109k | $0.0371 |
| [J1-J2](#c144394) | 2 | C144394 | Plugin,P=2.5mm | JST XH 3P vertical THT (3 A), IN/OUT on the back: 1=12V 2=DATA 3=GND | 175k | $0.0542 |
| [J3](#c131342) | 1 | C131342 | Plugin,P=2mm | JST PH 6P vertical THT, LED harness: R+ R- G+ G- B+ B- | 74k | $0.0722 |
| [L1-L3](#c168091) | 3 | C168091 | SMD,6x6mm | 68uH FNR6045S680MT, Isat 1.1A; PT4115 table 47-68uH for 0.4-0.8A | 34k | $0.0695 |
| [R1-R3](#c2907349) | 3 | C2907349 | 1206 | 0.22R 1% 1206 300ppm, current sense: 0.1V/0.22R = 455mA | 43k | $0.0071 |
| [R4-R6](#c25900) | 3 | C25900 | 0402 | 4.7k pull-up for WS2811 open-drain outputs | 15.44m | $0.0027 |
| [R7](#c25744) | 1 | C25744 | 0402 | 10k DIN pull-down (defined low when unplugged) | 21.68m | $0.0034 |
| [R8](#c25105) | 1 | C25105 | 0402 | 33R series on DOUT (cable source termination) | 1.82m | $0.0012 |
| [R10](#c25076) | 1 | C25076 | 0402 | 100R series on DIN | 2.87m | $0.0008 |
| [U1](#c114581) | 1 | C114581 | SOP-8 | WS2811 pixel controller, SET pin floated for 800kHz | 111k | $0.0413 |
| [U2-U4](#c347356) | 3 | C347356 | SOT-89-5 | PT4115 buck LED driver, one per RGB channel | 100k | $0.1104 |
| [U5](#c71136) | 1 | C71136 | SOT-89-3 | 78L05 5V regulator, basic part | 226k | $0.0893 |
| [U6](#c5590) | 1 | C5590 | SOIC-14 | 74HC04 hex inverter, WS2811 open-drain inversion | 39k | $0.1290 |
| [U7](#c350557) | 1 | C350557 | SC-70-5 | SN74AHCT1G125 3.3V-to-5V level shifter on DIN | 17k | $0.1418 |

## Details

<a id="c1525"></a>
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
| **Notes** | 100nF X7R bypass: C1 WS2811, C2 74HC04, C3 74AHCT1G125, C4 78L05 out |
| **Stock** | 22,162,126 |
| **Pricing** | $0.0045 (≥1), $0.0034 (≥1000), $0.0029 (≥3000), $0.0025 (≥10000), $0.0024 (≥50000), $0.0023 (≥100000) |
| **Capacitance** | 100nF |
| **Temperature Coefficient** | X7R |
| **Tolerance** | ±10% |
| **Voltage Rating** | 16V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL05B104KO5NNNC_C1525.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/1877-CL05B104KO5NNNC/C1525 |

<a id="c15850"></a>
### C15850

| | |
|---|---|
| **Designator** | C5 |
| **Part** | CL21A106KAYNNNE |
| **LCSC** | C15850 |
| **Manufacturer** | Samsung Electro-Mechanics |
| **Package** | 0805 |
| **Type** | Basic (no extra fee) |
| **Quantity** | 1 |
| **Description** | 10uF 25V X5R ±10% 0805 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS |
| **Notes** | 10uF 25V 0805, 78L05 input |
| **Stock** | 4,918,817 |
| **Pricing** | $0.0651 (≥1), $0.0472 (≥200), $0.0381 (≥600), $0.0304 (≥2000), $0.0278 (≥10000), $0.0261 (≥20000) |
| **Capacitance** | 10uF |
| **Temperature Coefficient** | X5R |
| **Tolerance** | ±10% |
| **Voltage Rating** | 25V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL21A106KAYNNNE_C15850.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/16532-CL21A106KAYNNNE/C15850 |

<a id="c13585"></a>
### C13585

| | |
|---|---|
| **Designator** | C6-C8 |
| **Part** | CL31A106KBHNNNE |
| **LCSC** | C13585 |
| **Manufacturer** | Samsung Electro-Mechanics |
| **Package** | 1206 |
| **Type** | Basic (no extra fee) |
| **Quantity** | 3 |
| **Description** | 10uF 50V X5R ±10% 1206 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS |
| **Notes** | 10uF 50V X5R 1206, PT4115 VIN bypass (>=4.7uF after DC bias at 12V) |
| **Stock** | 2,382,882 |
| **Pricing** | $0.2655 (≥1), $0.2028 (≥100), $0.1722 (≥300), $0.1449 (≥2000), $0.1374 (≥4000), $0.1329 (≥10000) |
| **Capacitance** | 10uF |
| **Temperature Coefficient** | X5R |
| **Tolerance** | ±10% |
| **Voltage Rating** | 50V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL31A106KBHNNNE_C13585.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/14236-CL31A106KBHNNNE/C13585 |

<a id="c12891"></a>
### C12891

| | |
|---|---|
| **Designator** | C9 |
| **Part** | CL31A226KAHNNNE |
| **LCSC** | C12891 |
| **Manufacturer** | Samsung Electro-Mechanics |
| **Package** | 1206 |
| **Type** | Basic (no extra fee) |
| **Quantity** | 1 |
| **Description** | 22uF 25V X5R ±10% 1206 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS |
| **Notes** | 22uF 25V X5R 1206, 12V input bulk |
| **Stock** | 1,082,676 |
| **Pricing** | $0.0494 (≥1), $0.0405 (≥200), $0.0361 (≥600), $0.0323 (≥2000), $0.0310 (≥10000), $0.0301 (≥20000) |
| **Capacitance** | 22uF |
| **Temperature Coefficient** | X5R |
| **Tolerance** | ±10% |
| **Voltage Rating** | 25V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL31A226KAHNNNE_C12891.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/13537-CL31A226KAHNNNE/C12891 |

<a id="c64885"></a>
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
| **Description** | -55℃~+125℃ 1.5A 1mA@40V 25A 40V 600mV@1A Standalone SOD-123 Schottky Diodes ROHS |
| **Notes** | B5819W 40V/1A Schottky freewheeling diode |
| **Stock** | 933,876 |
| **Pricing** | $0.0194 (≥1), $0.0163 (≥500), $0.0108 (≥3000), $0.0097 (≥6000), $0.0093 (≥24000), $0.0090 (≥51000) |
| **Current - Rectified** | 1.5A |
| **Diode Configuration** | Standalone |
| **Non-Repetitive Peak Forward Surge Current** | 25A |
| **Operating Junction Temperature Range** | -55℃~+125℃ |
| **Power Dissipation** | - |
| **Reverse Leakage Current (Ir)** | 1mA@40V |
| **Voltage - DC Reverse(Vr)** | 40V |
| **Voltage - Forward(Vf@If)** | 600mV@1A |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2407291648_MDD-Microdiode-Semiconductor-B5819W_C64885.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/MDD_Microdiode_Semiconductor-B5819W/C64885 |

<a id="c19077535"></a>
### C19077535

| | |
|---|---|
| **Designator** | D4 |
| **Part** | SMAJ15A |
| **LCSC** | C19077535 |
| **Manufacturer** | hongjiacheng |
| **Package** | DO-214AC(SMA) |
| **Type** | Extended |
| **Quantity** | 1 |
| **Description** | -55℃~+150℃ 1 15V 16.4A@10/1000us 18.5V 1uA 24.4V 400W@10/1000us IEC 61000-4-2 TVS Unidirectional DO-214AC(SMA) ESD and Surge Protection (TVS/ESD) ROHS |
| **Notes** | SMAJ15A TVS on +12V (hot-plugged chain cables) |
| **Stock** | 109,695 |
| **Pricing** | $0.0371 (≥1), $0.0290 (≥200), $0.0244 (≥600), $0.0210 (≥5000), $0.0186 (≥10000), $0.0174 (≥20000) |
| **Clamping Voltage** | 24.4V |
| **Junction Capacitance** | - |
| **Number of Channels** | 1 |
| **Operating Temperature** | -55℃~+150℃ |
| **Peak Pulse Current (Ipp)** | 16.4A@10/1000us |
| **Peak Pulse Power Dissipation (Ppp)** | 400W@10/1000us |
| **Polarity** | Unidirectional |
| **Reverse Leakage Current (Ir)** | 1uA |
| **Reverse Stand-Off Voltage (Vrwm)** | 15V |
| **Type** | TVS |
| **Voltage - Breakdown** | 18.5V |
| **level of protection** | IEC 61000-4-2 |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2411041728_hongjiacheng-SMAJ15A_C19077535.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/hongjiacheng-SMAJ15A/C19077535 |

<a id="c144394"></a>
### C144394

| | |
|---|---|
| **Designator** | J1-J2 |
| **Part** | B3B-XH-A(LF)(SN) |
| **LCSC** | C144394 |
| **Manufacturer** | JST |
| **Package** | Plugin,P=2.5mm |
| **Type** | Extended |
| **Quantity** | 2 |
| **Description** | -25℃~+85℃ 1 1x3P 2.5mm 250V 3 3A 3P 5.75mm 7mm 9.9mm Brass K Pin PA66 Through Hole Tin UL94V-0 White XH 插件,P=2.5mm Wire To Board Connector ROHS |
| **Notes** | JST XH 3P vertical THT (3 A), IN/OUT on the back: 1=12V 2=DATA 3=GND |
| **Stock** | 175,004 |
| **Pricing** | $0.0542 (≥1), $0.0446 (≥100), $0.0396 (≥300), $0.0352 (≥1000), $0.0337 (≥5000), $0.0327 (≥10000) |
| **Color** | White |
| **Contact Material** | Brass |
| **Contact Plating** | Tin |
| **Current Rating** | 3A |
| **Flame Retardant Rating** | UL94V-0 |
| **Mounting Type** | Through Hole |
| **Number of PINs Per Row** | 3 |
| **Number of Pins** | 3P |
| **Number of Rows** | 1 |
| **Operating Temperature** | -25℃~+85℃ |
| **Pins Structure** | 1x3P |
| **Pitch** | 2.5mm |
| **Plastic Material** | PA66 |
| **Reference Series** | XH |
| **Row Spacing** | - |
| **Supplementary Features** | K Pin |
| **Voltage Rating** | 250V |
| **X-Length of Bottom Edge on Board (Spacing Line)** | 9.9mm |
| **Y-Width of Bottom Edge on Board** | 5.75mm |
| **Z-Height of the Board** | 7mm |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_JST-B3B-XH-A-LF-SN_C144394.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/JST-B3B_XH_A_LF_SN/C144394 |

<a id="c131342"></a>
### C131342

| | |
|---|---|
| **Designator** | J3 |
| **Part** | B6B-PH-K-S(LF)(SN) |
| **LCSC** | C131342 |
| **Manufacturer** | JST |
| **Package** | Plugin,P=2mm |
| **Type** | Extended |
| **Quantity** | 1 |
| **Description** | -25℃~+85℃ 1 100V 13.9mm 1x6P 2A 2mm 4.5mm 6 6P 6mm Brass K Pin PA66 PH Through Hole Tin UL94V-0 White 插件,P=2mm Wire To Board Connector ROHS |
| **Notes** | JST PH 6P vertical THT, LED harness: R+ R- G+ G- B+ B- |
| **Stock** | 74,983 |
| **Pricing** | $0.0722 (≥1), $0.0589 (≥100), $0.0522 (≥300), $0.0474 (≥1000), $0.0433 (≥5000), $0.0413 (≥10000) |
| **Color** | White |
| **Contact Material** | Brass |
| **Contact Plating** | Tin |
| **Current Rating** | 2A |
| **Flame Retardant Rating** | UL94V-0 |
| **Mounting Type** | Through Hole |
| **Number of PINs Per Row** | 6 |
| **Number of Pins** | 6P |
| **Number of Rows** | 1 |
| **Operating Temperature** | -25℃~+85℃ |
| **Pins Structure** | 1x6P |
| **Pitch** | 2mm |
| **Plastic Material** | PA66 |
| **Reference Series** | PH |
| **Row Spacing** | - |
| **Supplementary Features** | K Pin |
| **Voltage Rating** | 100V |
| **X-Length of Bottom Edge on Board (Spacing Line)** | 13.9mm |
| **Y-Width of Bottom Edge on Board** | 4.5mm |
| **Z-Height of the Board** | 6mm |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_1811151524_JST-B6B-PH-K-S-LF-SN_C131342.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/JST-B6B_PH_K_S_LF_SN/C131342 |

<a id="c168091"></a>
### C168091

| | |
|---|---|
| **Designator** | L1-L3 |
| **Part** | FNR6045S680MT |
| **LCSC** | C168091 |
| **Manufacturer** | cjiang (Changjiang Microelectronics Tech) |
| **Package** | SMD,6x6mm |
| **Type** | Extended |
| **Quantity** | 3 |
| **Description** | 1.1A 1.3A 376mΩ 68uH Magnetic Shielded Inductor ±20% SMD,6x6mm Power Inductors ROHS |
| **Notes** | 68uH FNR6045S680MT, Isat 1.1A; PT4115 table 47-68uH for 0.4-0.8A |
| **Stock** | 34,298 |
| **Pricing** | $0.0695 (≥1), $0.0550 (≥100), $0.0478 (≥300), $0.0387 (≥1500), $0.0345 (≥4500), $0.0322 (≥10500) |
| **Current - Saturation(Isat)** | 1.3A |
| **Current Rating** | 1.1A |
| **DC Resistance(DCR)** | 376mΩ |
| **Inductance** | 68uH |
| **Tolerance** | ±20% |
| **Type** | Magnetic Shielded Inductor |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_cjiang--Changjiang-Microelectronics-Tech-FNR6045S680MT_C168091.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/179474-FNR6045S680MT/C168091 |

<a id="c2907349"></a>
### C2907349

| | |
|---|---|
| **Designator** | R1-R3 |
| **Part** | FRL1206FR220TS |
| **LCSC** | C2907349 |
| **Manufacturer** | FOJAN |
| **Package** | 1206 |
| **Type** | Extended |
| **Quantity** | 3 |
| **Description** | -55℃~+155℃ 220mΩ 250mW 500V Thick Film Resistor ±1% ±300ppm/℃ 1206 Chip Resistor - Surface Mount ROHS |
| **Notes** | 0.22R 1% 1206 300ppm, current sense: 0.1V/0.22R = 455mA |
| **Stock** | 43,689 |
| **Pricing** | $0.0071 (≥1), $0.0058 (≥1000), $0.0047 (≥5000), $0.0043 (≥10000), $0.0039 (≥50000), $0.0037 (≥100000) |
| **Operating Temperature** | -55℃~+155℃ |
| **Power(Watts)** | 250mW |
| **Resistance** | 220mΩ |
| **Temperature Coefficient** | ±300ppm/℃ |
| **Tolerance** | ±1% |
| **Type** | Thick Film Resistor |
| **Voltage-Supply(Max)** | 500V |
| **Datasheet** | https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2308241947_FOJAN-FRL1206FR220TS_C2907349.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/FOJAN-FRL1206FR220TS/C2907349 |

<a id="c25900"></a>
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
| **Stock** | 15,438,980 |
| **Pricing** | $0.0027 (≥1), $0.0021 (≥1000), $0.0017 (≥3000), $0.0016 (≥10000), $0.0013 (≥50000), $0.0013 (≥50200) |
| **Operating Temperature** | -55℃~+155℃ |
| **Power(Watts)** | 62.5mW |
| **Resistance** | 4.7kΩ |
| **Temperature Coefficient** | ±100ppm/℃ |
| **Tolerance** | ±1% |
| **Type** | Thick Film Resistor |
| **Voltage-Supply(Max)** | 50V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2206010045_UNI-ROYAL-Uniroyal-Elec-0402WGF4701TCE_C25900.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/26643-0402WGF4701TCE/C25900 |

<a id="c25744"></a>
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
| **Notes** | 10k DIN pull-down (defined low when unplugged) |
| **Stock** | 21,677,422 |
| **Pricing** | $0.0034 (≥1), $0.0027 (≥1000), $0.0023 (≥3000), $0.0021 (≥10000), $0.0017 (≥50000), $0.0017 (≥50200) |
| **Operating Temperature** | -55℃~+155℃ |
| **Power(Watts)** | 62.5mW |
| **Resistance** | 10kΩ |
| **Temperature Coefficient** | ±100ppm/℃ |
| **Tolerance** | ±1% |
| **Type** | Thick Film Resistor |
| **Voltage-Supply(Max)** | 50V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2411221126_UNI-ROYAL-Uniroyal-Elec-0402WGF1002TCE_C25744.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/26487-0402WGF1002TCE/C25744 |

<a id="c25105"></a>
### C25105

| | |
|---|---|
| **Designator** | R8 |
| **Part** | 0402WGF330JTCE |
| **LCSC** | C25105 |
| **Manufacturer** | UNI-ROYAL(Uniroyal Elec) |
| **Package** | 0402 |
| **Type** | Basic (no extra fee) |
| **Quantity** | 1 |
| **Description** | -55℃~+155℃ 33Ω 50V 62.5mW Thick Film Resistor ±1% ±100ppm/℃ 0402 Chip Resistor - Surface Mount ROHS |
| **Notes** | 33R series on DOUT (cable source termination) |
| **Stock** | 1,815,221 |
| **Pricing** | $0.0012 (≥1), $0.0009 (≥1000), $0.0007 (≥3000), $0.0007 (≥10000), $0.0006 (≥50000), $0.0006 (≥50200) |
| **Operating Temperature** | -55℃~+155℃ |
| **Power(Watts)** | 62.5mW |
| **Resistance** | 33Ω |
| **Temperature Coefficient** | ±100ppm/℃ |
| **Tolerance** | ±1% |
| **Type** | Thick Film Resistor |
| **Voltage-Supply(Max)** | 50V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2205311900_UNI-ROYAL-Uniroyal-Elec-0402WGF330JTCE_C25105.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/25848-0402WGF330JTCE/C25105 |

<a id="c25076"></a>
### C25076

| | |
|---|---|
| **Designator** | R10 |
| **Part** | 0402WGF1000TCE |
| **LCSC** | C25076 |
| **Manufacturer** | UNI-ROYAL(Uniroyal Elec) |
| **Package** | 0402 |
| **Type** | Basic (no extra fee) |
| **Quantity** | 1 |
| **Description** | -55℃~+155℃ 100Ω 50V 62.5mW Thick Film Resistor ±1% ±100ppm/℃ 0402 Chip Resistor - Surface Mount ROHS |
| **Notes** | 100R series on DIN |
| **Stock** | 2,868,420 |
| **Pricing** | $0.0008 (≥1), $0.0006 (≥1000), $0.0006 (≥3000), $0.0005 (≥10000), $0.0005 (≥50000), $0.0005 (≥50200) |
| **Operating Temperature** | -55℃~+155℃ |
| **Power(Watts)** | 62.5mW |
| **Resistance** | 100Ω |
| **Temperature Coefficient** | ±100ppm/℃ |
| **Tolerance** | ±1% |
| **Type** | Thick Film Resistor |
| **Voltage-Supply(Max)** | 50V |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2205311900_UNI-ROYAL-Uniroyal-Elec-0402WGF1000TCE_C25076.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/25819-0402WGF1000TCE/C25076 |

<a id="c114581"></a>
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
| **Stock** | 111,712 |
| **Pricing** | $0.0413 (≥1), $0.0329 (≥200), $0.0283 (≥600), $0.0217 (≥4000), $0.0192 (≥8000), $0.0179 (≥20000) |
| **Constant Current Accuracy** | - |
| **Dimming** | PWM |
| **Features** | Over Voltage Protection |
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

<a id="c347356"></a>
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
| **Stock** | 100,444 |
| **Pricing** | $0.1104 (≥1), $0.0869 (≥50), $0.0747 (≥150), $0.0610 (≥1000), $0.0574 (≥2000), $0.0550 (≥5000) |
| **Constant Current Accuracy** | 5% |
| **Dimming** | Analog、PWM |
| **Features** | Over-Temperature Protection (OTP)、Built-in soft-start |
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

<a id="c71136"></a>
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
| **Stock** | 226,961 |
| **Pricing** | $0.0893 (≥1), $0.0716 (≥50), $0.0626 (≥150), $0.0560 (≥500), $0.0483 (≥2500), $0.0457 (≥4000) |
| **Features** | Over Current Protection、Short Circuit Protection、Thermal shutdown |
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

<a id="c5590"></a>
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
| **Stock** | 39,344 |
| **Pricing** | $0.1290 (≥1), $0.1028 (≥50), $0.0893 (≥150), $0.0782 (≥500), $0.0743 (≥2500), $0.0717 (≥5000) |
| **Current - Output High(IOH)** | 5.2mA |
| **Current - Output Low(IOL)** | 5.2mA |
| **Features** | - |
| **Input Logic Level - High** | 1.5V~4.2V |
| **Input Logic Level -Low** | 500mV~1.8V |
| **Input Type** | StandardCMOS |
| **Number of Circuits** | 6 |
| **Operating Temperature** | -40℃~+125℃ |
| **Output Logic Level - High** | 1.9V、3.7V、5.2V |
| **Output Logic Level - Low** | 100mV、400mV、400mV |
| **Propagation Delay** | 14ns@6V,50pF |
| **Quiescent Current(Iq)** | 2uA |
| **Series** | 74HC |
| **Voltage - Supply** | 2V~6V |
| **output type** | Push-pull |
| **Datasheet** | https://www.lcsc.com/datasheet/lcsc_datasheet_2407241044_Nexperia-74HC04D-653_C5590.pdf |
| **JLCPCB** | https://jlcpcb.com/partdetail/Nexperia-74HC04D653/C5590 |

<a id="c350557"></a>
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
| **Stock** | 17,039 |
| **Pricing** | $0.1418 (≥1), $0.1121 (≥50), $0.0973 (≥150), $0.0860 (≥500), $0.0773 (≥3000), $0.0727 (≥6000) |
| **Channel Type** | Unidirectional |
| **Current - Output High(IOH)** | 8mA |
| **Current - Output Low(IOL)** | 8mA |
| **Features** | Edge rate controllable、Output enable、Level shifting |
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

