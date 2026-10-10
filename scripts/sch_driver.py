#!/usr/bin/env python3
"""Generate boards/driver/driver.kicad_sch (single sheet) through Konnect: the FR4 driver / interface board.

The LEDs are on the aluminium LED board (scripts/sch_led.py); here they are the 3 units of J3 (LED harness socket,
JST PH 6: 1 R+, 2 R-, 3 G+, 4 G-, 5 B+, 6 B-), each drawn in its channel's current loop where the LED would be.

Rebuilds the whole sheet: `reset` blanks it (keeping its uuid), `build` places, powers and labels every pin.
Run from anywhere:  python3 scripts/sch_driver.py
Design rationale for every value is in DESIGN.md (§2 circuit, §3 parts).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import builder
from builder import *

builder.P = P = ROOT + "boards/driver/"
SHEET = "driver.kicad_sch"
XH3 = "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"
R0402 = "Resistor_SMD:R_0402_1005Metric"; C0402 = "Capacitor_SMD:C_0402_1005Metric"
R1206 = "Resistor_SMD:R_1206_3216Metric"; C0805 = "Capacitor_SMD:C_0805_2012Metric"; C1206 = "Capacitor_SMD:C_1206_3216Metric"

def r(ref, val, lcsc, x, y, p1, p2, rot=0, fp=R0402, mpn=None):
    d = dict(ref=ref, lib="Device:R", val=val, fp=fp, x=x, y=y, rot=rot, lcsc=lcsc, pins={"1": p1, "2": p2})
    if mpn: d["fields"] = {"MPN": mpn}
    return d

def c(ref, val, lcsc, x, y, p1, p2="GND", fp=C0402, mpn=None):
    d = dict(ref=ref, lib="Device:C", val=val, fp=fp, x=x, y=y, lcsc=lcsc, pins={"1": p1, "2": p2})
    if mpn: d["fields"] = {"MPN": mpn}
    return d

comps = [
    # ---- data in: J1 -> R10 100R -> (R7 10k pull-down) -> 74AHCT1G125 (3.3 V -> 5 V) -> WS2811 DIN
    dict(ref="J1", lib="Connector_Generic:Conn_01x03", val="IN 12V/DATA/GND", fp=XH3, x=30.48, y=60.96, mirror="y",
         lcsc="C144394", fields={"MPN": "B3B-XH-A(LF)(SN)"}, pins={"1": None, "2": "DIN", "3": None}),
    r("R10", "100", "C25076", 45.72, 76.2, "DIN", "DIN_IN"),
    r("R7", "10k", "C25744", 55.88, 76.2, "DIN_IN", "GND"),
    dict(ref="U7", lib="74xGxx:74AHCT1G125", val="74AHCT1G125", fp="Package_TO_SOT_SMD:SOT-353_SC-70-5",
         x=76.2, y=60.96, lcsc="C350557", fields={"MPN": "SN74AHCT1G125DCKR"},
         pins={"1": "GND", "2": "DIN_IN", "3": "GND", "4": "DIN_5V", "5": "+5V"}),
    # ---- 12 V input protection (hot-plugged chain cables): TVS + bulk
    dict(ref="D4", lib="Diode:SMAJ15A", val="SMAJ15A", fp="Diode_SMD:D_SMA", x=30.48, y=99.06, rot=90, lcsc="C19077535",
         pins={"1": "+12V", "2": "GND"}),
    c("C9", "22uF 25V", "C12891", 43.18, 99.06, "+12V", fp=C1206, mpn="CL31A226KAHNNNE"),
    # ---- WS2811: open-drain outputs, pulled up to 5 V, inverted by the 74HC04 (DESIGN.md §2.3)
    dict(ref="U1", lib="Driver_LED:WS2811", val="WS2811", fp="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
         x=111.76, y=60.96, lcsc="C114581",
         pins={"1": "OUT_R", "2": "OUT_G", "3": "OUT_B", "4": "GND", "5": "DOUT_RAW", "6": "DIN_5V", "7": "SET", "8": "+5V"}),
    r("R9", "0R DNP", "", 93.98, 76.2, "+5V", "SET"),   # SET strap, unfitted: Worldsemi V2.2 says NC, older/clone WS2811s use it for 400/800k
    r("R4", "4.7k", "C25900", 132.08, 45.72, "+5V", "OUT_R"),
    r("R5", "4.7k", "C25900", 142.24, 45.72, "+5V", "OUT_G"),
    r("R6", "4.7k", "C25900", 152.4, 45.72, "+5V", "OUT_B"),
    r("R8", "33", "C25105", 116.84, 99.06, "DOUT_RAW", None, rot=90),
    dict(ref="J2", lib="Connector_Generic:Conn_01x03", val="OUT 12V/DATA/GND", fp=XH3, x=139.7, y=99.06,
         lcsc="C144394", fields={"MPN": "B3B-XH-A(LF)(SN)"}, pins={"1": None, "2": None, "3": None}),
    # ---- 74HC04: gates 1-3 invert OUT_x -> DIM_x; gates 4-6 inputs to GND, outputs open; unit 7 = power
    dict(ref="U6", unit=1, lib="74xx:74HC04", val="74HC04", fp="Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
         x=177.8, y=50.8, lcsc="C5590", fields={"MPN": "74HC04D,653"}, pins={"1": "OUT_R", "2": "DIM_R"}),
    dict(ref="U6", unit=2, lib="74xx:74HC04", x=177.8, y=63.5, pins={"3": "OUT_G", "4": "DIM_G"}),
    dict(ref="U6", unit=3, lib="74xx:74HC04", x=177.8, y=76.2, pins={"5": "OUT_B", "6": "DIM_B"}),
    dict(ref="U6", unit=4, lib="74xx:74HC04", x=210.82, y=50.8, pins={"9": "GND", "8": "NC"}),
    dict(ref="U6", unit=5, lib="74xx:74HC04", x=210.82, y=63.5, pins={"11": "GND", "10": "NC"}),
    dict(ref="U6", unit=6, lib="74xx:74HC04", x=210.82, y=76.2, pins={"13": "GND", "12": "NC"}),
    dict(ref="U6", unit=7, lib="74xx:74HC04", x=236.22, y=63.5, pins={"14": "+5V", "7": "GND"}),
    # ---- logic decoupling (one per IC, place at the VCC pin)
    c("C1", "100nF", "C1525", 167.64, 101.6, "+5V"),   # U1 WS2811
    c("C2", "100nF", "C1525", 177.8, 101.6, "+5V"),    # U6 74HC04
    c("C3", "100nF", "C1525", 187.96, 101.6, "+5V"),   # U7 74AHCT1G125
    # ---- 5 V logic rail
    c("C5", "10uF", "C15850", 271.78, 63.5, "+12V", fp=C0805),
    dict(ref="U5", lib="Regulator_Linear:L78L05_SOT89", val="78L05", fp="Package_TO_SOT_SMD:SOT-89-3",
         x=289.56, y=55.88, lcsc="C71136", fields={"MPN": "78L05G-AB3-R"}, pins={"3": "+12V", "2": "GND", "1": "+5V"}),
    c("C4", "100nF", "C1525", 307.34, 63.5, "+5V"),
    dict(ref="#FLG01", lib="power:PWR_FLAG", x=330.2, y=50.8, pins={"1": "+12V"}),
    dict(ref="#FLG02", lib="power:PWR_FLAG", x=345.44, y=50.8, pins={"1": "GND"}),
]

# ---- three PT4115 channels, drawn as explicit wires so the current loop reads at a glance.
#      Datasheet topology (high-side sense, low-side switch):
#      +12V -> Rs -> CSN node -> J3 x+ ... LED on the LED board ... J3 x- -> L -> SW ;  Schottky A=SW, K=+12V
CH = []   # (n, ch, Ux, Uy)
for i, ch in enumerate("RGB"):
    n = i + 1; Ux = 73.66 + 127 * i; Uy = 175.26; X = Ux - 25.4
    CH.append((n, ch, Ux, Uy))
    comps += [
        r(f"R{n}", "0.22R 1%", "C2907349", X, Uy - 12.7, None, None, fp=R1206, mpn="FRL1206FR220TS"),
        dict(ref="J3", unit=n, lib="rgb-spotlight:LED_PORT", val="LED harness", x=X, y=Uy + 5.08,
             fp="Connector_JST:JST_PH_B6B-PH-K_1x06_P2.00mm_Vertical", lcsc="C131342", fields={"MPN": "B6B-PH-K-S(LF)(SN)"},
             pins={str(2 * n - 1): None, str(2 * n): None}),
        dict(ref=f"L{n}", lib="Device:L", val="68uH", fp="Inductor_SMD:L_Changjiang_FNR6045S", x=X, y=Uy + 24.13,
             lcsc="C168091", fields={"MPN": "FNR6045S680MT"}, pins={"1": None, "2": None}),
        dict(ref=f"D{n}", lib="Device:D_Schottky", val="B5819W", fp="Diode_SMD:D_SOD-123", x=Ux + 20.32, y=Uy - 7.62,
             rot=270, lcsc="C64885", pins={"1": None, "2": None}),
        dict(ref=f"U{n + 1}", lib="rgb-spotlight:PT4115", val="PT4115", x=Ux, y=Uy, lcsc="C347356",
             pins={"5": None, "4": None, "3": f"DIM_{ch}", "1": None, "2": "GND"}),
        c(f"C{n + 5}", "10uF 50V", "C13585", Ux + 33.02, Uy, None, fp=C1206, mpn="CL31A106KBHNNNE"),
    ]

def channel_wires(L):
    """Wires and junctions for each channel, computed from the real pin endpoints."""
    pt = lambda ref, p: L[(ref, p)][:2]
    W, J, PW = [], [], []
    def path(*pts):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]): W.append((x1, y1, x2, y2))
    for n, ch, Ux, Uy in CH:
        U, R, Lr, D, C = f"U{n + 1}", f"R{n}", f"L{n}", f"D{n}", f"C{n + 5}"
        rail = Uy - 20.32
        r1, r2 = pt(R, "1"), pt(R, "2"); la, lk = pt("J3", str(2 * n - 1)), pt("J3", str(2 * n))
        l1, l2 = pt(Lr, "1"), pt(Lr, "2"); dk, da = pt(D, "1"), pt(D, "2")
        vin, csn, sw = pt(U, "5"), pt(U, "4"), pt(U, "1"); c1 = pt(C, "1")
        assert r2[0] == la[0] == lk[0] == l1[0] and r2[1] < csn[1] < la[1], (r2, la, csn)
        assert dk[1] < da[1] and sw[1] > da[1] and lk[1] < l1[1], (dk, da, sw)
        xv = vin[0] - 2.54; bot = l2[1] + 5.08
        path((r1[0], rail), (c1[0], rail))                     # +12V rail
        path(r1, (r1[0], rail)); path(dk, (dk[0], rail)); path(c1, (c1[0], rail))
        path(vin, (xv, vin[1]), (xv, rail))
        J += [(xv, rail), (dk[0], rail)]
        PW.append(("+12V", r1[0], rail, 90))
        path(r2, la); path((r2[0], csn[1]), csn); J.append((r2[0], csn[1]))   # CSN node
        path(lk, l1)                                                        # LED cathode -> L
        path(l2, (l2[0], bot), (da[0], bot), da)                            # L -> SW node <- D anode
        path(sw, (da[0], sw[1])); J.append((da[0], sw[1]))
    # connectors: +12V up and GND down on short wires, clear of the data pin
    for j, dx in (("J1", 5.08), ("J2", -5.08)):
        p1, p3 = pt(j, "1"), pt(j, "3"); x = p1[0] + dx
        path(p1, (x, p1[1]), (x, p1[1] - 5.08)); PW.append(("+12V", x, p1[1] - 5.08, 90))
        path(p3, (x, p3[1]), (x, p3[1] + 5.08)); PW.append(("GND", x, p3[1] + 5.08, 270))
    path(pt("R8", "2"), pt("J2", "2"))
    return W, J, PW

if __name__ == "__main__":
    reset(SHEET)
    txt = open(P + SHEET).read()   # title block (reset() writes a bare sheet)
    open(P + SHEET, "w").write(txt.replace('\t(paper "A3")\n', '\t(paper "A3")\n\t(title_block (title "RGB Spotlight - driver board") (date "2026-10-05") (rev "2.0") '
                                         '(comment 1 "WS2811 pixel, 3x PT4115 455 mA, 12 V chain; LEDs on the aluminium LED board") (comment 2 "Generated by scripts/sch_driver.py"))\n'))
    L = build(SHEET, 0, comps, {})
    W, J, PW = channel_wires(L)
    k = Konnect(); k.load("sch_wiring", "sch_batch")
    k.call("batch_add_wire", {"schematic": P + SHEET, "wires": [dict(x1=a, y1=b, x2=c_, y2=d) for a, b, c_, d in W]})
    k.call("batch_add_junction", {"schematic": P + SHEET, "positions": [dict(x=a, y=b) for a, b in J]})
    k.call("batch_place_components", {"schematic": P + SHEET, "components": [
        {"lib_id": f"power:{net}", "reference": f"#PWR{90 + i:04d}", "x": x, "y": y, "rotation": 0} for i, (net, x, y, _) in enumerate(PW)]})
    # name the channel nets that are drawn as wires (labels sit on the wires)
    lab = []
    for n, ch, Ux, Uy in CH:
        lab += [(f"CSN_{ch}", Ux - 17.78, Uy - 2.54, 0), (f"SW_{ch}", Ux + 13.97, Uy, 0), (f"LEDK_{ch}", Ux - 25.4, Uy + 15.24, 0)]
    lab.append(("DOUT", 127.0, 99.06, 0))
    labels(SHEET, lab)
    txt = open(P + SHEET).read()   # R9 is a do-not-populate strap: mark it DNP and out of the BOM
    i = txt.index('(property "Reference" "R9"'); j = txt.rfind("(symbol\n", 0, i)
    blk = txt[j:i].replace("(in_bom yes)", "(in_bom no)").replace("(dnp no)", "(dnp yes)")
    open(P + SHEET, "w").write(txt[:j] + blk + txt[i:])
    k = Konnect(); k.load("sch_wiring", "sch_components", "sch_batch", "sch_analysis")
    notes = [
        ("DATA IN: 3.3 V or 5 V -> R10 -> 74AHCT1G125 -> 5 V. R7 holds DIN low when unplugged.", 22.86, 40.64),
        ("12 V in: SMAJ15A TVS + 22 uF for hot-plugged chain cables. J1/J2 12V and GND pass straight through (3 A).", 22.86, 116.84),
        ("WS2811 outputs sink when ON; R4-R6 pull up; 74HC04 inverts so DIM is HIGH = LED on.", 116.84, 30.48),
        ("J1 and J2 (JST XH, back of the board) share one pinout: 1 = 12V, 2 = data, 3 = GND.", 101.6, 121.92),
        ("PT4115 loop (datasheet): +12V -> Rs -> J3 x+ -> LED -> J3 x- -> L -> SW; Schottky SW -> +12V.  I_LED = 0.1 V / Rs = 455 mA", 30.48, 137.16),
        ("J3 = LED harness (JST PH 6, front of the board): 1 R+  2 R-  3 G+  4 G-  5 B+  6 B-. Twist each +/- pair.", 30.48, 142.24),
    ]
    for t, x, y in notes:
        k.call("add_schematic_text", {"schematic": P + SHEET, "text": t, "x": x, "y": y})
