#!/usr/bin/env python3
"""Assert the intended topology of the driver board netlist (ERC only proves the wiring is legal).

Each check targets a v1 failure mode (DESIGN.md §1): the PT4115 current loop (now through the LED harness J3),
the 74HC04 supply, and the J1/J2 pinout. Usage: python3 scripts/netcheck.py   (exports the netlist; exit 1 on failure)
Parsing and the expect/same helpers come from pcb-kit (pcbkit.checks.netlist).
"""
import os, sys
try:
    import pcbkit  # noqa: F401
except ImportError:  # an interpreter pcbkit is not linked into: use the checkout
    sys.path.insert(0, os.path.expanduser(os.environ.get("PCBKIT_ROOT", "~/src/pcb-kit")))
from pcbkit.checks.netlist import Netlist

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nl = Netlist(os.path.join(ROOT, "boards/driver/driver.kicad_sch"))

for i, ch in enumerate("RGB"):
    n = i + 1; U = f"U{n + 1}"; R = f"R{n}"; L = f"L{n}"; D = f"D{n}"
    A, K = ("J3", str(2 * n - 1)), ("J3", str(2 * n))      # LED harness: anode, cathode of this channel's LED
    print(f"-- channel {ch}: {U} {R} {L} {D}, LED on J3.{A[1]} (+) / J3.{K[1]} (-)")
    nl.same((U, "5"), (R, "1"), "Rs from VIN")
    nl.same((R, "1"), (D, "1"), "Schottky cathode on VIN")
    nl.expect(nl.pin[(U, "5")] == "+12V", "VIN on +12V")
    nl.same((R, "2"), (U, "4"), "Rs to CSN")
    nl.same((R, "2"), A, "LED anode (J3 +) on CSN node (LED current flows through Rs)")
    nl.same(K, (L, "1"), "LED cathode (J3 -) to inductor")
    nl.same((L, "2"), (U, "1"), "inductor to SW")
    nl.same((D, "2"), (U, "1"), "Schottky anode on SW")
    nl.expect(len(nl.nets[nl.pin[(R, "2")]]) == 3, f"CSN node has only Rs, CSN, J3 +: {sorted(nl.nets[nl.pin[(R, '2')]])}")
    nl.expect(len(nl.nets[nl.pin[K]]) == 2, f"LED cathode node has only J3 - and L: {sorted(nl.nets[nl.pin[K]])}")
    nl.expect(len(nl.nets[nl.pin[(U, "1")]]) == 3, f"SW node has only SW, L, D: {sorted(nl.nets[nl.pin[(U, '1')]])}")
    nl.expect(nl.pin[(U, "2")] == "GND", "PT4115 GND")
    nl.expect(nl.pin[(U, "3")] == f"DIM_{ch}" and ("U6", {"R": "2", "G": "4", "B": "6"}[ch]) in nl.nets[f"DIM_{ch}"], "DIM driven by a 74HC04 output")

print("-- logic")
for p in [("U1", "8"), ("U6", "14"), ("U7", "5"), ("U5", "1")]:
    nl.expect(nl.pin[p] == "+5V", f"{p} on +5V (v1 had U6 VCC on a separate '+5V' net)")
nl.expect(nl.pin[("U5", "3")] == "+12V" and nl.pin[("U5", "2")] == "GND", "78L05 SOT-89 pinout O-G-I")
for a, y in [("1", "2"), ("3", "4"), ("5", "6")]:
    nl.expect(len(nl.nets[nl.pin[("U6", a)]]) == 3, f"74HC04 input {a}: WS2811 out + pull-up + gate {sorted(nl.nets[nl.pin[('U6', a)]])}")
for a in ["9", "11", "13"]:
    nl.expect(nl.pin[("U6", a)] == "GND", f"unused 74HC04 input {a} tied to GND")
nl.expect(nl.pin[("U1", "6")] == nl.pin[("U7", "4")], "WS2811 DIN from the level shifter")
nl.expect(nl.pin[("U7", "1")] == "GND", "74AHCT1G125 OE enabled")
nl.expect(nl.nets.get("SET") == {("U1", "7"), ("R9", "2")} and nl.pin[("R9", "1")] == "+5V", "WS2811 SET (pin 7) on the DNP strap R9 to +5V")
print("-- connectors (one pinout for J1 and J2)")
for j in ("J1", "J2"):
    nl.expect(nl.pin[(j, "1")] == "+12V" and nl.pin[(j, "3")] == "GND", f"{j}: 1 = +12V, 3 = GND")
nl.expect(nl.pin[("J1", "2")] == "DIN" and nl.pin[("R10", "1")] == "DIN", "J1.2 -> R10")
nl.same(("R10", "2"), ("U7", "2"), "R10 -> level shifter input"); nl.same(("R7", "1"), ("U7", "2"), "R7 pull-down at the shifter input")
nl.expect(nl.pin[("R7", "2")] == "GND", "R7 to GND")
nl.expect(nl.pin[("D4", "1")] == "+12V" and nl.pin[("D4", "2")] == "GND", "TVS D4 cathode on +12V, anode on GND")
nl.expect(nl.pin[("C9", "1")] == "+12V" and nl.pin[("C9", "2")] == "GND", "bulk C9 across +12V")
nl.same(("J2", "2"), ("R8", "2"), "J2.2 through R8 from WS2811 DO")
nl.no_single_node_nets()
nl.finish()
