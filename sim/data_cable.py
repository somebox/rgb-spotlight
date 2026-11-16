#!/usr/bin/env python3
"""Data link between two lights in ngspice: does the signal reach the next U7 intact over a long chain cable, with
R10 at 100 ohm or 1 k and R8 at 33 or 82 ohm, and does it need another repeater? (docs/reviews/2026-10-30-v2.md, R6 and "Power and data".)
And with D5 (D28) clamping U7's input to +5V: what 12 V on the data pin leaves at U7.

Pass: a T0H pulse (250 ns, FastLED) crosses U7's input with one clean edge each way, width inside 220-380 ns, and
stays under U7's 7 V abs max. Below -0.5 V U7's clamp conducts, so the model (which has no clamp) overstates the
undershoot; the table gives the most that R10 lets through. Usage: python3 sim/data_cable.py

Model: WS2811 DO as a 5 V source behind 40 ohm (Idout 10 mA at 0.4 V, so at most 40 ohm low; the high side is assumed
the same) with 20 ns edges (assumed), R8, a lossless line (pessimistic), Z0 120 ohm, 4.8 ns/m (three loose wires,
assumed), R10, R7 10 k, 10 pF at U7 (input + pad), and D5 to a 5.0 V rail: a Schottky fitted to RB751V-40's 0.37 V at
1 mA, with 2 pF (the RB751 family; 10 pF changes T0H by 2 ns). AHCT switches near 1.5 V.
"""
import os
import sys

try:
    import pcbkit  # noqa: F401
except ImportError:
    sys.exit("pcbkit not found: uv tool install -e ~/src/pcb-kit")
from pcbkit.spice import run

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results", "data_cable.txt")


def deck(metres, r8, r10, fault=False):
    td = metres * 4.8e-9
    src = "VDO src 0 DC 12" if fault else "VDO src 0 PULSE(0 5 100n 20n 20n 250n 1250n)"
    return f"""* data link {metres} m R8 {r8} R10 {r10}
{src}
RO src do 40
R8 do line {r8}
T1 line 0 far 0 Z0=120 TD={td:.4g}
R10 far in {r10}
R7 in 0 10k
CU7 in 0 10p
V5 vcc 0 DC 5.0
D5 in vcc RB751
.model RB751 D(IS=2e-8 N=1.05 RS=8 CJO=2p M=0.4 VJ=0.4 BV=40)
.tran 0.2n 1.2u
.control
run
meas tran vmax MAX v(in)
meas tran vmin MIN v(in)
meas tran id5 MAX i(V5)
meas tran t_up WHEN v(in)=1.5 RISE=1
meas tran t_dn WHEN v(in)=1.5 FALL=1
meas tran rises WHEN v(in)=1.5 RISE=2
.endc
.end
"""


lines = ["T0H 250 ns from WS2811 DO through R8, a chain cable and R10, at U7's input with D5 to +5V (1.5 V threshold, U7's own clamp not modelled)",
         "cable  R8  R10    Vin max  Vin min  clamp mA  T0H at U7  edges  pass"]
for metres in (1, 2, 4, 8):
    for r8, r10 in ((33, 100), (33, 1000), (82, 1000)):
        m = run(deck(metres, r8, r10), sim_dir=HERE, timeout=60).meas
        width = (m["t_dn"] - m["t_up"]) * 1e9
        false_edge = m.get("rises") is not None
        clamp = max(0.0, -m["vmin"] - 0.5) / r10 * 1e3
        ok = 220 <= width <= 380 and m["vmax"] < 7.0 and not false_edge and clamp < 1.0
        lines.append(f"{metres:3d} m  {r8:2d}  {r10:4d}  {m['vmax']:6.2f}  {m['vmin']:6.2f}  {clamp:7.2f}  {width:6.0f} ns  "
                     f"{'false' if false_edge else 'clean'}  {'yes' if ok else 'NO'}")
m = run(deck(1, 33, 1000, fault=True), sim_dir=HERE, timeout=60).meas
lines.append(f"12 V on the data pin (a mis-crimped cable, review R6), 1 m, R8 33, R10 1k: U7 input {m['vmax']:.2f} V, "
             f"{abs(m['id5']) * 1e3:.1f} mA through D5 into +5V (U7 abs max 7 V; without D5, 12 V x 10k/11k = 10.9 V)")
text = "\n".join(lines) + "\n"
print(text)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(text)
