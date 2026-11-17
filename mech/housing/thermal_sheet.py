"""Rough still-air estimate for the square sheet-metal lamp (sheet.py). Order of magnitude only.

Heat leaves the LED board's plate two ways:
  channels: the fin gaps, vented through the slots in the walls (a chimney when the lamp points sideways)
  housing:  plate -> shell face (greased contact outside the window) -> the four walls, bent from the face
Inner wall surfaces, the back cap and the driver's 0.9 W are left out.
"""
import math

k_air, nu, Pr, g = 0.0271, 1.70e-5, 0.705, 9.81
dT, Tm = 25.0, 313.0
h_rad1 = 4 * 5.67e-8 * ((Tm + 298) / 2) ** 3          # W/m2K per unit emissivity, about 6.7


def h_channel(s, L):                                    # Bar-Cohen & Rohsenow, vertical parallel plates
    Ra = g / Tm * dT * s ** 3 / nu ** 2 * Pr
    El = Ra * s / L
    return (576 / El ** 2 + 2.873 / El ** 0.5) ** -0.5 * k_air / s


def h_vert(L):                                          # vertical plate, laminar
    return 1.42 * (dT / L) ** 0.25


def fin_eff(h, t, L, k=138.0):                          # 5052: k about 138 W/mK
    m = math.sqrt(h / (k * t)); return math.tanh(m * L) / (m * L)


FIN, PLATE, SPACER, BORE, WINDOW = 61.0, 58.5, 30.0, 8.0, 52.0
face = FIN ** 2 - math.pi / 4 * SPACER ** 2 - 3 * math.pi / 4 * 3.2 ** 2 - 4 * 3 ** 2 * (1 - math.pi / 4)
contact = PLATE ** 2 - math.pi / 4 * WINDOW ** 2                     # plate against the shell's face, mm2
R_c = 0.05 * 632 / contact                                           # greased, scaled from the spacer joints
A_walls = 4 * 0.065 * 0.071
A_front = (65 ** 2 - math.pi / 4 * WINDOW ** 2) * 1e-6

for orient, ch_derate, walls_h, front_h in (("sideways", 0.55, 0.8 * h_vert(0.065), 4.0),
                                            ("pointing down", 0.15, h_vert(0.071), 2.0)):
    G_ch = 4 * 2 * face * 1e-6 * h_channel(0.006, FIN / 1000) * ch_derate
    for finish, eps in (("bare", 0.08), ("black anodized", 0.85)):
        h_o = walls_h + eps * h_rad1
        G_w = A_walls * h_o * fin_eff(h_o, 0.0015, 0.071)
        G_f = A_front * (front_h + 0.6 * eps * h_rad1)              # the frame shades the face
        G_h = 1 / (R_c + 1 / (G_w + G_f))
        G = G_ch + G_h
        print(f"{orient:13s} {finish:15s}: channels {G_ch:.3f} + housing {G_h:.3f} W/K -> {1 / G:.1f} K/W, "
              f"+{2.7 / G:.0f} C at 2.7 W, +{3.6 / G:.0f} C at 3.6 W")
print(f"contact {contact:.0f} mm2 -> {R_c:.3f} K/W; channel h {h_channel(0.006, FIN / 1000):.1f} W/m2K before derating;"
      f" wall h {h_vert(0.065):.1f}; radiation {h_rad1:.1f} x eps")
