"""Thread and press-nut drawings for JLC's "Threads and Tapped Holes" upload (A4 landscape, mm).

python3 drawings_sheet.py OUTDIR [plate|cap]  ->  rgb-spotlight-plate-threads.svg, rgb-spotlight-cap-press-nuts.svg
(rsvg-convert -f pdf to make the PDFs). Both are round 7's: the cap with M4 nuts on the sides, rims to 16.1 and four
M3 nuts in its back (DESIGN D30, D31), the plate with a 12 mm middle hole (D33). Round 6's drawings are in order6/.
"""
import math
import os
import sys

OUT = sys.argv[1]
ONLY = sys.argv[2] if len(sys.argv) > 2 else None
L = 'stroke="#000" fill="none" stroke-width="0.35"'
T = 'stroke="#000" fill="none" stroke-width="0.18"'
C = 'stroke="#000" fill="none" stroke-width="0.15" stroke-dasharray="6 1.5 1 1.5"'
HID = 'stroke="#000" fill="none" stroke-width="0.18" stroke-dasharray="1.5 1"'


class Sheet:
    def __init__(self):
        self.el = []

    def text(self, x, y, s, size=2.8, anchor="start", weight="normal"):
        self.el.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" '
                       f'font-family="Helvetica, Arial, sans-serif">{s}</text>')

    def line(self, x1, y1, x2, y2, st=T):
        self.el.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" {st}/>')

    def circle(self, cx, cy, r, st=L):
        self.el.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" {st}/>')

    def rect(self, x, y, w, h, rx=0, st=L):
        self.el.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx:.2f}" {st}/>')

    def thread(self, cx, cy, s, d=3.0, drill=2.5):
        self.circle(cx, cy, drill / 2 * s)
        q = math.pi * d * s
        self.el.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{d / 2 * s:.2f}" stroke="#000" fill="none" '
                       f'stroke-width="0.18" stroke-dasharray="{0.75 * q / 4:.2f} {0.25 * q / 4:.2f}"/>')

    def leader(self, x1, y1, x2, y2, label, anchor="start", size=2.6):
        self.el.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" {T} marker-start="url(#dot)"/>')
        self.text(x2 + (1 if anchor == "start" else -1), y2 + 0.9, label, size, anchor)

    def dim(self, x1, y1, x2, y2, label, ox=0, oy=-1.2):
        self.el.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" {T} marker-start="url(#a)" marker-end="url(#a)"/>')
        self.text((x1 + x2) / 2 + ox, (y1 + y2) / 2 + oy, label, 2.6, "middle")

    def notes(self, x, y, lines):
        for i, (n, b) in enumerate(lines):
            self.text(x, y + i * 4.6, n, 3.2 if b else 2.8, "start", "bold" if b else "normal")

    def title(self, name, part, material, qty, mass):
        tx, ty, tw, th = 192, 168, 98, 34
        self.rect(tx, ty, tw, th)
        for yy in (ty + 10, ty + 17, ty + 24):
            self.line(tx, yy, tx + tw, yy)
        self.line(tx + 49, ty + 10, tx + 49, ty + th)
        self.text(tx + 3, ty + 6.8, name, 4.2, "start", "bold")
        self.text(tx + 3, ty + 15, f"Part: {part}", 2.6)
        self.text(tx + 52, ty + 15, f"Qty per lamp: {qty}", 2.6)
        self.text(tx + 3, ty + 22, f"Material: {material}", 2.6)
        self.text(tx + 52, ty + 22, "Units: mm   Scale: as noted", 2.6)
        self.text(tx + 3, ty + 29.5, "Date: 2026-11-16", 2.6)
        self.text(tx + 52, ty + 29.5, f"Mass ≈ {mass}", 2.6)

    def save(self, fname):
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210">
<defs>
<marker id="a" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="#000"/></marker>
<marker id="dot" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="2.5" markerHeight="2.5"><circle cx="5" cy="5" r="4" fill="#000"/></marker>
</defs>
<rect x="0" y="0" width="297" height="210" fill="#fff"/>
<rect x="6" y="6" width="285" height="198" {L}/>
{chr(10).join(self.el)}
</svg>'''
        p = os.path.join(OUT, fname)
        open(p, "w").write(svg)
        print("wrote", p)


def polar(r, a):
    return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))


# ------------------------------------------------------------------ plate: 10 x M3
def plate():
    d = Sheet()
    s, cx, cy, W = 2.0, 80, 100, 58.5
    d.rect(cx - W / 2 * s, cy - W / 2 * s, W * s, W * s, 2 * s)
    d.circle(cx, cy, 6 * s)                    # the harness bore, 12 mm in round 7 (D33)
    d.line(cx - 34 * s, cy, cx + 34 * s, cy, C); d.line(cx, cy - 34 * s, cx, cy + 34 * s, C)
    LED_ANG = (75, 195, 315)                   # round 6: the LED board turned 45 deg (D23)
    TIE_ANG = (30, 150, 270)
    for r, angs in ((19, LED_ANG), (11, TIE_ANG)):
        d.circle(cx, cy, r * s, C)
        for a in angs:
            x, y = polar(r, a)
            d.thread(cx + x * s, cy - y * s, s)
    for sx in (-1, 1):
        for sy in (-1, 1):
            d.thread(cx + sx * 24 * s, cy - sy * 24 * s, s)
    d.text(cx, cy - W / 2 * s - 9, "PLATE (round 7), front view (LED board side), 2 : 1", 3.4, "middle", "bold")
    d.dim(cx - W / 2 * s, cy + W / 2 * s + 6, cx + W / 2 * s, cy + W / 2 * s + 6, "58.5", 0, 3.6)
    d.dim(cx + W / 2 * s + 6, cy - W / 2 * s, cx + W / 2 * s + 6, cy + W / 2 * s, "", 0, 0)
    d.text(cx + W / 2 * s + 7.5, cy - 3, "58.5", 2.6)
    d.dim(cx - 24 * s, cy + W / 2 * s + 12, cx + 24 * s, cy + W / 2 * s + 12, "48", 0, 3.6)
    x, y = polar(19, 75)
    d.leader(cx + x * s, cy - y * s, cx + 72, cy - 45, "3× M3×0.5 THRU, PCD 38 at 75°, 195°, 315° (LED board)")
    x, y = polar(11, 150)
    d.leader(cx + x * s, cy - y * s, cx + 72, cy - 36, "3× M3×0.5 THRU, PCD 22 at 30°, 150°, 270° (tie rods)", "start")
    d.leader(cx + 24 * s, cy - 24 * s, cx + 72, cy - 54, "4× M3×0.5 THRU at (±24, ±24) (shell screws)")
    d.leader(cx + 6 * s * 0.7, cy + 6 * s * 0.7, cx + 72, cy + 30, "Ø12 THRU (no thread)")
    d.notes(200, 118, [("NOTES", True),
                      ("1. Al 5052, 3 mm sheet, laser cut. No finish.", False),
                      ("2. Threads: 10× M3×0.5 through the 3 mm sheet.", False),
                      ("    The model has Ø2.5 holes at these places.", False),
                      ("3. Front face (LED board side) carries the", False),
                      ("    LED board and the shell: keep it flat and", False),
                      ("    free of burrs. Deburr all holes.", False),
                      ("4. General tolerances ISO 2768-m.", False)])
    d.title("RGB Spotlight stack plate", "rgb-spotlight-plate", "Al 5052, 3 mm", 1, "27 g")
    d.save("rgb-spotlight-plate-threads.svg")


# ------------------------------------------------------------------ cap: 2 x M3 and 2 x M4 press nuts (round 7)
def cap():
    d = Sheet()
    s, cx, cy, W = 1.5, 70, 95, 61.4
    D = 16.1                                    # cap depth: face 1.5 + rims to 16.1 (round 7: 1.5 longer, D30)
    d.rect(cx - W / 2 * s, cy - W / 2 * s, W * s, W * s, 2.75 * s)
    d.rect(cx - (W / 2 - 1.5) * s, cy - (W / 2 - 1.5) * s, (W - 3) * s, (W - 3) * s, 1.25 * s, HID)
    for x, y in ((16.45, 9.5), (-16.45, 9.5)):     # seen from the back: x mirrored
        d.rect(cx + (-x - 7) * s, cy - (y + 7.5) * s, 14 * s, 15 * s, 2 * s)
    for x, y in ((23, 23), (-23, 23), (23, -23), (-23, -23)):   # 4 x M3 for a box on the back (D31)
        d.circle(cx + x * s, cy - y * s, 4.22 / 2 * s)
        d.circle(cx + x * s, cy - y * s, 6.35 / 2 * s, HID)
    d.dim(cx + W / 2 * s + 6, cy - 23 * s, cx + W / 2 * s + 6, cy + 23 * s, "", 0, 0)
    d.text(cx + W / 2 * s + 7.5, cy + 1, "46", 2.6)
    d.leader(cx - 23 * s - 1.5, cy + 23 * s + 1.5, cx - W / 2 * s + 4, cy + W / 2 * s + 16,
             "4× PRESS NUT M3 (PEM S-M3-2 or equal), hole Ø4.22, back face, on a 46 × 46 square,")
    d.text(cx - W / 2 * s + 5, cy + W / 2 * s + 20.2, "centred; head on the INSIDE, flush outside: a box mounts there", 2.6)
    d.line(cx - 36 * s, cy, cx + 36 * s, cy, C); d.line(cx, cy - 36 * s, cx, cy + 36 * s, C)
    d.text(cx, cy - W / 2 * s - D * s - 13, "BACK CAP (round 7), seen from the back (outside), 1.5 : 1", 3.4, "middle", "bold")
    d.dim(cx - W / 2 * s, cy + W / 2 * s + 6, cx + W / 2 * s, cy + W / 2 * s + 6, "61.4", 0, 3.6)
    # top view of the top rim above the back view: rim depth D, nut hole 8.6 from the back face
    ty0 = cy - W / 2 * s - D * s - 5                # the top rim's view, its back face 5 above the back view
    d.rect(cx - W / 2 * s, ty0, W * s, D * s, 0)
    d.circle(cx, ty0 + (D - 8.6) * s, 4.22 / 2 * s)
    d.circle(cx, ty0 + (D - 8.6) * s, 6.35 / 2 * s, HID)
    d.text(cx - W / 2 * s - 2, ty0 + 3, "TOP", 2.6, "end")
    d.leader(cx + 2.2 * s, ty0 + (D - 8.6) * s, cx + 62, ty0 - 2, "2× PRESS NUT M3 (PEM S-M3-2 or equal), hole Ø4.22,")
    d.text(cx + 63, ty0 + 2.2, "top and bottom rims, centred; head on the INSIDE", 2.6)
    d.dim(cx - W / 2 * s - 5, ty0 + D * s, cx - W / 2 * s - 5, ty0 + (D - 8.6) * s, "", 0, 0)
    d.text(cx - W / 2 * s - 6, ty0 + (D - 4.3) * s + 1, "8.6", 2.4, "end")
    # side view of the right rim to the right of the back view
    sx0 = cx + W / 2 * s + 18
    d.rect(sx0, cy - W / 2 * s, D * s, W * s, 0)
    d.circle(sx0 + 8.6 * s, cy, 5.41 / 2 * s)
    d.circle(sx0 + 8.6 * s, cy, 7.87 / 2 * s, HID)
    d.text(sx0 + D * s / 2, cy + W / 2 * s + 5, "SIDE (both)", 2.6, "middle")
    d.leader(sx0 + 8.6 * s + 2.7 * s * 0.7, cy + 2.7 * s * 0.7, sx0 + D * s + 8, cy + 18, "2× PRESS NUT M4 (PEM S-M4-2 or equal),")
    d.text(sx0 + D * s + 9, cy + 22.2, "hole Ø5.41, side rims, centred;", 2.6)
    d.text(sx0 + D * s + 9, cy + 26.4, "head on the INSIDE", 2.6)
    d.dim(sx0, cy - W / 2 * s - 4, sx0 + D * s, cy - W / 2 * s - 4, "16.1", 0, -1.2)
    d.dim(sx0, cy - W / 2 * s - 10, sx0 + 8.6 * s, cy - W / 2 * s - 10, "8.6", 0, -1.2)
    d.text(cx, cy + W / 2 * s + 28, "Back face is at the left/bottom edge of the rim views; rims point into the lamp.", 2.4, "middle")
    d.notes(200, 22, [("NOTES", True),
                      ("1. Al 5052, 1.5 mm, bent. Finish: black powder coat.", False),
                      ("2. Press nuts after powder coating, heads on the inside", False),
                      ("    of the cap, flush on the outside: the rims slide", False),
                      ("    into the lamp's shell and must stay flat outside.", False),
                      ("3. 8 nuts: 2× M3 in the top and bottom rims and 2× M4", False),
                      ("    in the side rims, 7.5 from the rims' front edge", False),
                      ("    (PEM: M4 6.9 min); 4× M3 in the back face, 6.2 from", False),
                      ("    the cut-outs (PEM: 4.8 min).", False),
                      ("4. Two 14 × 15 cut-outs R2 for the cables.", False),
                      ("5. General tolerances ISO 2768-m.", False)])
    d.title("RGB Spotlight back cap", "rgb-spotlight-cap", "Al 5052, 1.5 mm", 1, "26 g")
    d.save("rgb-spotlight-cap-press-nuts.svg")


if ONLY in (None, "plate"):
    plate()
if ONLY in (None, "cap"):
    cap()
