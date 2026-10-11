#!/usr/bin/env python3
"""One PT4115 LED channel in ngspice: power handling at full brightness, and what the WS2811's PWM does to it.

Questions (DESIGN.md §2.7):
  Q1  At full brightness, what LED current, ripple and switching frequency do we get per colour, where do the watts
      go (LED, Rs, switch, diode, inductor), and how hot do the PT4115 and the Schottky run?
  Q2  With the WS2811's ~4 kHz PWM on DIM, how linear is brightness against the PWM duty, and where does the
      bottom of the range stop following?
  Q3  What does a channel's PWM do to the 12 V input (current steps, board ripple through 1 m of cable)?

    python3 sim/channel.py                       # tables -> sim/results/channel.txt
    uv run --with numpy --with matplotlib python sim/channel.py --plot   # + sim/results/*.png

Model: the PT4115 has no SPICE model; it is built from its datasheet as a hysteretic switch.
  - Sense: V(VIN) - V(CSN) across Rs. The switch turns on below 85 mV and off above 115 mV (100 mV +-15 %).
  - Switch: 0.6 ohm on-resistance (datasheet at 12 V), behind COMP_DELAY of comparator delay (an assumption; the
    datasheet gives none).
  - DIM: below 0.3 V off, above 2.5 V on. The IC's own start-up delay after DIM rises is not modelled; the datasheet's
    minimum PWM duty implies about 2 us (DESIGN.md §2.1).
  - Board parts: the real L (68 uH, DCR 0.33 ohm), Rs 0.22 ohm, the B5819W (0.6 V at 1 A typ, fitted), and Cin
    10 uF 1206 50 V at about 6 uF under 12 V bias.
  - Supply: 12 V through 1 m of 22 AWG pair (0.1 ohm, 1 uH) and C9 (22 uF 1206 25 V, about 8 uF at 12 V).
  - LEDs: knee voltage + 0.55 ohm, matched to the HD2525 datasheet VF at 455 mA: R 2.1 V, G 3.0 V, B 3.1 V.
Left out: temperature (VF falls and DCR rises as things warm), inductor saturation (Isat 1.1 A, peak here < 0.6 A),
parasitic capacitance at SW, and the WS2811's channel-to-channel PWM phase (all three start each period together).
"""
import os
import sys

try:
    import pcbkit  # noqa: F401
except ImportError:  # an interpreter pcbkit is not linked into: use the checkout
    sys.path.insert(0, os.path.expanduser(os.environ.get("PCBKIT_ROOT", "~/src/pcb-kit")))
from pcbkit.spice import run

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
F_PWM = 4000.0               # WS2811 PWM ("scan frequency 4 kHz", datasheet)
COMP_DELAY = 150e-9          # comparator + gate delay, assumed
LEDS = {"red": 2.10, "green": 3.00, "blue": 3.10}   # VF at 455 mA
R_LED = 0.55

DECK = """* PT4115 channel, behavioural
.param vknee={vknee} rled={rled}
VSUP sup 0 12
RCAB sup cab 0.1
LCAB cab vb 1u
VMIN vb vin 0
C9 vin c9e 8u
RC9 c9e 0 5m
CIN vin cine 6u
RCIN cine 0 5m
* sense resistor and LED (anode at CSN, cathode at K)
RS vin csn 0.22
VMLED csn la 0
DLED la lk DIDEAL
VKNEE lk lr {{vknee}}
RLED lr k {{rled}}
* inductor with DCR, to SW
LL k lxa 68u
RDCR lxa lx 0.33
* Schottky: anode SW, cathode VIN
VMD lx da 0
DS da vin B5819W
* PT4115: hysteretic switch on SW, gated by DIM
VMSW lx swi 0
SW1 swi 0 ctl 0 SWM
BCTL ctlr 0 V = u(V(dim) - 2.5) * (0.1 - (V(vin) - V(csn)) + 1) - 1
RDL ctlr ctl 1k
CDL ctl 0 {cdl}
.model SWM SW(VT=0 VH=0.015 RON=0.6 ROFF=1e7)
.model DIDEAL D(IS=1e-12 N=0.05)
.model B5819W D(IS=2e-6 N=1.2 RS=0.15 CJO=110p M=0.35 BV=40 IBV=1m)
{dim}
.tran {step} {tstop} 0 {step}
.control
run
{meas}
{wr}
quit
.endc
.end
"""


def deck(vknee, dim_line, tstop, meas, wr="", step=10e-9):
    return DECK.format(vknee=vknee - 0.07, rled=R_LED, dim=dim_line, tstop=tstop, step=step, meas=meas, wr=wr,
                       cdl=COMP_DELAY / 1e3)


def full_power(colour, plot=False):
    """Q1: DIM held high; measure over 200 us of steady state."""
    t0, t1 = "1.0m", "1.2m"
    meas = f"""let pin = v(vb)*i(vmin)
let pled = (v(la)-v(k))*i(vmled)
let prs = (v(vin)-v(csn))*i(vmled)
let psw = v(swi)*i(vmsw)
let pd = (v(da)-v(vin))*i(vmd)
let pl = i(vmled)*i(vmled)*0.33
meas tran iled avg i(vmled) from={t0} to={t1}
meas tran iled_max max i(vmled) from={t0} to={t1}
meas tran iled_min min i(vmled) from={t0} to={t1}
meas tran p_in avg pin from={t0} to={t1}
meas tran p_led avg pled from={t0} to={t1}
meas tran p_rs avg prs from={t0} to={t1}
meas tran p_sw avg psw from={t0} to={t1}
meas tran p_d avg pd from={t0} to={t1}
meas tran p_l avg pl from={t0} to={t1}
meas tran ta when v(lx)=6 rise=100
meas tran tb when v(lx)=6 rise=200
meas tran vin_pp pp v(vin) from={t0} to={t1}
meas tran iin_pp pp i(vmin) from={t0} to={t1}"""
    wr = f"wrdata {colour}_full.txt i(vmled) v(lx) i(vmin)" if plot else ""
    r = run(deck(LEDS[colour], "VDIM dim 0 5", "1.2m", meas, wr), sim_dir=HERE, timeout=300, keep=RES if plot else None)
    return r


def pwm(colour, duty, plot=False):
    """Q2/Q3: DIM = 4 kHz PWM at `duty`; average over 4 periods after 4 settling periods."""
    per = 1 / F_PWM
    pw = max(duty * per, 20e-9)
    t0, t1 = 4 * per, 8 * per
    meas = f"""meas tran iled avg i(vmled) from={t0} to={t1}
meas tran iled_pk max i(vmled) from={t0} to={t1}
meas tran iin avg i(vmin) from={t0} to={t1}
meas tran iin_max max i(vmin) from={t0} to={t1}
meas tran vin_min min v(vin) from={t0} to={t1}
meas tran vin_max max v(vin) from={t0} to={t1}"""
    dim = f"VDIM dim 0 PULSE(0 5 10u 10n 10n {pw:.4g} {per:.6g})"
    tag = f"{colour}_pwm{duty * 100:g}".replace(".", "p")
    wr = f"wrdata {tag}.txt i(vmled) v(dim) i(vmin)" if plot else ""
    return run(deck(LEDS[colour], dim, f"{t1:.6g}", meas, wr, step=20e-9), sim_dir=HERE, timeout=300,
               keep=RES if plot else None)


def main():
    plot = "--plot" in sys.argv
    os.makedirs(RES, exist_ok=True)
    out = []
    say = lambda s="": (print(s), out.append(s))
    say("# PT4115 channel simulation (sim/channel.py, ngspice via pcbkit.spice)")
    say(f"# 12 V through 0.1 ohm + 1 uH; Rs 0.22 ohm; 68 uH / 0.33 ohm; Cin ~6 uF; comparator delay {COMP_DELAY * 1e9:.0f} ns")
    say()
    say("## Q1  full brightness (DIM high)")
    say(f"{'colour':6} {'I_LED mA':>9} {'ripple mA pp':>13} {'f_sw kHz':>9} {'P_LED W':>8} {'P_Rs':>6} {'P_sw':>6} "
        f"{'P_D':>6} {'P_L':>6} {'P_in W':>7} {'eff %':>6} {'Vin pp mV':>10} {'Iin pp mA':>10}")
    full = {}
    for c in LEDS:
        r = full_power(c, plot)
        if r.aborted:
            say(f"{c}: run aborted ({r.reason})"); continue
        m = r.meas; full[c] = m
        fsw = 100 / (m["tb"] - m["ta"])
        say(f"{c:6} {m['iled'] * 1e3:9.0f} {(m['iled_max'] - m['iled_min']) * 1e3:13.0f} {fsw / 1e3:9.0f} "
            f"{m['p_led']:8.2f} {m['p_rs']:6.3f} {m['p_sw']:6.3f} {m['p_d']:6.3f} {m['p_l']:6.3f} {m['p_in']:7.2f} "
            f"{100 * m['p_led'] / m['p_in']:6.1f} {m['vin_pp'] * 1e3:10.0f} {m['iin_pp'] * 1e3:10.0f}")
    if full:
        say()
        say("Temperature rise (datasheet RthJA; both are best-case figures with generous copper):")
        for c, m in full.items():
            say(f"  {c:6} PT4115 switch {m['p_sw'] * 45:5.1f} C (45 C/W)   B5819W {m['p_d'] * 160:5.1f} C (160 C/W)")
        tot = sum(m["p_in"] for m in full.values())
        say(f"  light at full white: {tot:.2f} W in, {tot / 12 * 1e3:.0f} mA at 12 V (three channels, logic not included)")
    say()
    say("## Q2/Q3  PWM on DIM at 4 kHz (green), brightness linearity and the 12 V input")
    say(f"{'duty %':>7} {'level/255':>9} {'I_LED avg mA':>13} {'ideal mA':>9} {'ratio':>6} {'I_in avg mA':>12} "
        f"{'I_in peak mA':>13} {'Vin dip mV':>11}")
    i_full = full.get("green", {}).get("iled", 0.455)
    for duty in (1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 4 / 255, 2 / 255, 1 / 255):
        r = pwm("green", duty, plot and duty in (0.5, 0.05, 4 / 255, 1 / 255))
        if r.aborted:
            say(f"{duty * 100:7.2f}: run aborted ({r.reason})"); continue
        m = r.meas
        ideal = duty * i_full
        say(f"{duty * 100:7.2f} {duty * 255:9.1f} {m['iled'] * 1e3:13.1f} {ideal * 1e3:9.1f} {m['iled'] / ideal:6.2f} "
            f"{m['iin'] * 1e3:12.1f} {m['iin_max'] * 1e3:13.0f} {(12 - m['vin_min']) * 1e3:11.0f}")
    with open(os.path.join(RES, "channel.txt"), "w") as f:
        f.write("\n".join(out) + "\n")
    if plot:
        make_plots()


def make_plots():
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    load = lambda n: np.loadtxt(os.path.join(RES, n))
    # full brightness: LED current and SW node, 20 us window
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2), sharey=False)
    for ax, c in zip(axes, LEDS):
        d = load(f"{c}_full.txt"); t = d[:, 0]; sel = (t > 1.0e-3) & (t < 1.02e-3)
        ax.plot((t[sel] - 1e-3) * 1e6, d[sel, 1] * 1e3, color={"red": "#d62728", "green": "#2ca02c", "blue": "#1f77b4"}[c])
        ax2 = ax.twinx(); ax2.plot((t[sel] - 1e-3) * 1e6, d[sel, 3], color="#888", lw=0.8, ls=":")
        ax.set_title(f"{c}: LED current (solid) and SW node (dotted)"); ax.set_xlabel("us"); ax.set_ylabel("mA"); ax2.set_ylabel("V")
    fig.tight_layout(); fig.savefig(os.path.join(RES, "channel_full.png"), dpi=110)
    # PWM: one period at several duties
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.2))
    for ax, (tag, title, win) in zip(axes, [("green_pwm50", "50 %", 260e-6), ("green_pwm5", "5 %", 30e-6),
                                           ("green_pwm1p56863", "4/255 = 1.6 %", 12e-6), ("green_pwm0p392157", "1/255 = 0.4 %", 12e-6)]):
        d = load(tag + ".txt"); t = d[:, 0]; per = 1 / F_PWM; t0 = 6 * per + 10e-6 - 2e-6
        sel = (t > t0) & (t < t0 + win)
        ax.plot((t[sel] - t0) * 1e6, d[sel, 1] * 1e3, color="#2ca02c", label="LED current")
        ax.plot((t[sel] - t0) * 1e6, d[sel, 3] / 5 * 455, color="#888", ls=":", label="DIM (scaled)")
        ax.set_title(f"green, PWM duty {title}"); ax.set_xlabel("us"); ax.set_ylabel("mA"); ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(RES, "channel_pwm.png"), dpi=110)
    print("wrote", os.path.join(RES, "channel_full.png"), os.path.join(RES, "channel_pwm.png"))


if __name__ == "__main__":
    main()
