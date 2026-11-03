#!/usr/bin/env python3
"""Worst-case numbers for the failure review (docs/reviews/2026-10-30-v2.md): LED current spread, the Schottky's
temperature, the chain current per feed against the JST XH rating, the 78L05's dissipation, DIM drive level, a 5 V feed.
Datasheet limits, not typicals, where the datasheet gives them. Usage: python3 sim/worst_case.py
(prints a table; the review copies it to sim/results/worst_case.txt).
"""

# PT4115 (UMW, Jul 2025, §7): VIN - VCSN = 95 / 100 / 105 mV; hysteresis ±15 %; R_SW 0.6 Ω at 12 V
VCSN = (0.095, 0.100, 0.105)
RS, RS_TOL, RS_PPM = 0.22, 0.01, 300          # FRL1206FR220TS: 1 %, 300 ppm/°C (DESIGN §3)
DCR = 0.376                                   # FNR6045S680MT, JLC cache: 376 mΩ, Isat 1.1 A, Irms 1.3 A
ISAT = 1.1
VF_D = (0.40, 0.45, 0.70)                     # B5819W at ~0.5 A: 0.45 typ (sim fit to 0.60 V at 1 A); 0.70 max,
                                              # scaled from 0.90 V max at 1 A (inferred, no max curve)
LED_VF = {"red": (1.9, 2.2, 2.6), "green": (2.6, 3.0, 3.4), "blue": (2.6, 3.0, 3.4)}  # HD2525 @ 700 mA bins
RJA_D = (160, 250, 300)                       # B5819W θJA: 160 °C/W on 5 × 5 cm copper; SOD-123 pads: estimate
XH_RATING = 3.0                               # JST XH, A per contact (D9)
WIRE_R = 2 * 0.053                            # 1 m of 22 AWG, both conductors, Ω


def led_current(corner, dT=40):
    v = VCSN[corner]
    rs = RS * (1 + (RS_TOL if corner == 0 else -RS_TOL if corner == 2 else 0)) * (1 + RS_PPM * 1e-6 * dT)
    return v / rs


def channel(colour, i, vin, vfd, vfl):
    """Steady-state buck: duty from the volt-second balance; losses; input power."""
    v_on = vin - vfl - i * (DCR + 0.6)              # across L with the switch on (Rs drop ignored: 0.1 V)
    v_off = vfl + vfd + i * DCR                     # across L with the switch off
    d = v_off / (v_on + v_off)
    p_led = vfl * i
    p_d = vfd * i * (1 - d)
    p_loss = p_d + i * i * (DCR + RS) + i * i * 0.6 * d
    return d, p_led, p_d, p_led + p_loss


print("== LED current, worst corners (VCSN spread, Rs 1 %, +40 °C on Rs)")
lo, nom, hi = (led_current(c) for c in range(3))
print(f"  I_LED min {lo*1e3:.0f} mA  nom {nom*1e3:.0f} mA  max {hi*1e3:.0f} mA; LED abs max 1000 mA")
ipk = hi * 1.15 + 0.03                              # +15 % hysteresis + comparator-delay overshoot (sim: ±18 %)
print(f"  inductor peak ≈ {ipk*1e3:.0f} mA against Isat {ISAT*1e3:.0f} mA: margin x{ISAT/ipk:.1f}")

print("\n== Schottky D1-D3 at the high-current corner, VF at ~0.5 A (typ; inferred max)")
for colour in ("red", "green"):
    for vfd, rja in ((VF_D[1], RJA_D[1]), (VF_D[2], RJA_D[2])):
        d, p_led, p_d, p_in = channel(colour, hi, 12.0, vfd, LED_VF[colour][0])
        for amb in (40, 55):
            print(f"  {colour:5s} VF_d {vfd:.2f} V, θJA {rja} °C/W: P_D {p_d*1e3:3.0f} mW, Tj ≈ {amb + p_d*rja:3.0f} °C at {amb} °C"
                  f"  (Tj max 125 °C; P_D derates to 0 at 125 °C)")

print("\n== Chain current per 12 V feed (worst light: high-current corner, blue/green VF max, red VF max)")
p_light = sum(channel(c, hi, 11.0, VF_D[1], LED_VF[c][2])[3] for c in LED_VF) + 12 * 0.005   # + logic 5 mA
p_nom = sum(channel(c, nom, 12.0, VF_D[1], LED_VF[c][1])[3] for c in LED_VF) + 12 * 0.005
print(f"  per light: {p_nom:.2f} W nominal, {p_light:.2f} W worst")
for n in (4, 5, 6, 7):
    # feed at 12.0 V, 1 m of 22 AWG between lights: solve the drops by iterating
    v = [12.0] * n
    for _ in range(20):
        i_light = [p_light / vk for vk in v]
        seg = [sum(i_light[k:]) for k in range(n)]      # current in the cable into light k
        vk, v = 12.0, []
        for k in range(n):
            vk -= seg[k] * (WIRE_R if k else 0)         # the first light sits at the feed
            v.append(vk)
    flag = "OVER" if seg[0] > XH_RATING else "ok" if seg[0] < 0.85 * XH_RATING else "tight"
    print(f"  {n} lights: {seg[0]:.2f} A through the first J1/J2 ({seg[0]/XH_RATING*100:.0f} % of 3 A, {flag}); "
          f"last light at {v[-1]:.2f} V")

print("\n== 78L05 (UTC: 350 mW SOT-89 at 25 °C, Vin 7-20 V operating, 30 V abs max)")
for vin in (12.0, 13.2, 16.7, 24.4):
    p = (vin - 5.0) * 0.006 + vin * 0.0055 * 0.5      # 6 mA load (worst), Iq 5.5 mA max, half of it as a guess
    print(f"  Vin {vin:4.1f} V: {p*1e3:3.0f} mW" + ("  (TVS breakdown min)" if vin == 16.7 else "  (TVS clamp at 16 A)" if vin == 24.4 else ""))

print("\n== DIM drive (PT4115: high 2.5-5 V for full current, 6 V abs max; 74HC04 VOH ≈ VCC)")
for vcc in (4.80, 5.00, 5.20):
    print(f"  78L05 at {vcc:.2f} V -> DIM high ≈ {vcc:.2f} V: {'inside 2.5-5 V' if vcc <= 5.0 else 'above the 5 V the PWM formula assumes, under 6 V abs max'}")

print("\n== 5 V feed (PT4115: VIN 6-30 V, UVLO 5.1 V falling + 0.5 V hysteresis; 78L05: dropout 1.7 V; WS2811: VDD 3.5 V min)")
print(f"  PT4115 at 5.0 V: below 6 V and below the {5.1 + 0.5:.1f} V restart level, so it stays off")
print(f"  78L05 at 5.0 V: output ≈ {5.0 - 1.7:.1f} V, below the WS2811's 3.5 V")
i_5v = 4.07 / 0.85 / 5.0                            # another driver, 85 % assumed: LEDs 4.07 W (§2.7)
print(f"  with a 5 V LED driver instead: ≈ {i_5v:.2f} A per light, {int(XH_RATING // i_5v)} lights on a 3 A connector at nominal")

print("\n== Power for one feed, lights spaced along 22 AWG (per span both conductors plus 4 XH contacts at 20 mΩ, assumed; board trunk 0.03 Ω)")
print("   worst light 5.51 W is constant power, so current rises as the voltage falls; PT4115 needs 6 V, 78L05 7 V")
def feed(n, metres, p, vfeed=12.0):
    r = metres * WIRE_R + 4 * 0.020 + 0.03
    v = [vfeed] * n
    for _ in range(40):
        seg = [sum(p / vk for vk in v[k:]) for k in range(n)]
        vk, v = vfeed, []
        for k in range(n):
            vk -= seg[k] * (r if k else 0)
            v.append(vk)
    return seg[0], v[-1], seg[0] * vfeed, sum(seg[k] ** 2 * r for k in range(1, n))
for n in (4, 5):
    for m in (1, 2, 3):
        i, vlast, watts, loss = feed(n, m, p_light)
        ityp, vtyp, wtyp, _ = feed(n, m, 5.0)
        print(f"  {n} lights, {m} m apart: typ {ityp:.2f} A {wtyp:4.1f} W; worst {i:.2f} A {watts:4.1f} W ({i/XH_RATING*100:.0f} % of 3 A), "
              f"last light {vlast:.2f} V, {loss:.1f} W lost in cable")
for vfeed in (11.4, 13.0):
    i, vlast, watts, _ = feed(5, 3, p_light, vfeed)
    print(f"  5 lights, 3 m apart, feed {vfeed} V: {i:.2f} A, last light {vlast:.2f} V")
c_light = 22 + 3 * 10 + 10                          # C9, C6-C8, C5 in µF, nominal; about half at 12 V bias
print(f"  input capacitance {c_light} µF per light nominal, so {4 * c_light}-{5 * c_light} µF on a feed")
