#!/usr/bin/env python3
"""Data link between two lights in ngspice: does the signal reach the next U7 intact over a long chain cable, with
R10 at 100 ohm or 1 k and R8 at 33 or 82 ohm, and does it need another repeater? (docs/reviews/2026-10-30-v2.md, R6 and "Power and data".)
And with D5 (D28) clamping U7's input to +5V: what a feed voltage held on the data pin does to U7's input and to the
+5V rail, whose 78L05 can only source current, with and without R11's bleed (D29).

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


def deck(metres, r8, r10):
    td = metres * 4.8e-9
    return f"""* data link {metres} m R8 {r8} R10 {r10}
VDO src 0 PULSE(0 5 100n 20n 20n 250n 1250n)
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


def rail_deck(reg, pullups, bleed):
    """12 V (or more) held on the data pin, DC: R10, R7, D5 into a +5V rail whose 78L05 can only source current."""
    return f"""* data pin held high: +5V rail, 78L05 sourcing only
VF far 0 DC 12
R10 far in 1k
R7 in 0 10k
D5 in vcc RB751
.model RB751 D(IS=2e-8 N=1.05 RS=8 CJO=2p M=0.4 VJ=0.4 BV=40)
B78 0 vcc I = {reg} * max(0, (5.0 - v(vcc)) * 50)
IWS vcc 0 DC 0.3m
{"RP vcc 0 1567" if pullups else ""}
{f"R11 vcc 0 {bleed}" if bleed else ""}
.dc VF 11 16 0.5
.control
run
meas dc v12 FIND v(vcc) AT=12
meas dc v13 FIND v(vcc) AT=13
meas dc v15 FIND v(vcc) AT=15
meas dc u15 FIND v(in) AT=15
meas dc i15 FIND i(VF) AT=15
.endc
.end
"""


lines += ["",
          "A feed voltage held on the data pin (a mis-crimped cable, review R6): DC, R10 1k, R7 10k, D5 into +5V. The 78L05",
          "sources only (it cannot sink); +5V load: the WS2811 0.3 mA, plus R4-R6 3 x 4.7k when all three channels are on;",
          "C1-C4 don't matter at DC. The WS2811's internal zener (voltage not stated) and the ICs' own clamps are not modelled,",
          "so a rail above 5.7 V means those would conduct instead. Abs max: U6 and U7 VCC 7 V, the WS2811's VDD rated to 5.7 V.",
          "feed  channels  R11      +5V at 12 V  13 V   15 V   U7 in at 15 V  mA from the pin at 15 V"]
for reg, feed in ((1, "on "), (0, "off")):
    for pullups in (False, True):
        for bleed in (None, 470):
            m = run(rail_deck(reg, pullups, bleed), sim_dir=HERE, timeout=60).meas
            lines.append(f"{feed}   {'all on ' if pullups else 'all off'}  {str(bleed or 'none'):5s}    {m['v12']:5.2f}  "
                         f"{m['v13']:5.2f}  {m['v15']:5.2f}  {m['u15']:5.2f}          {abs(m['i15']) * 1e3:4.1f}")
lines.append("feed off: the 12 V and data wires swapped, so the 78L05 has no input and the pin's current alone holds the rail up")
text = "\n".join(lines) + "\n"
print(text)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(text)
