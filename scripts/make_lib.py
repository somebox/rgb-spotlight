#!/usr/bin/env python3
"""Write the project library: lib/rgb-spotlight.kicad_sym (PT4115, LED_HD2525, LED_PORT) and
lib/rgb-spotlight.pretty/ (LED_XINGLIGHT_HD2525, WirePad_2.2x3.5mm). Overwrites both; rerun after edits here.

Pinouts are from the datasheets in docs/datasheets/ (DESIGN.md §2):
  PT4115 SOT-89-5: 1 SW, 2 GND (+ tab), 3 DIM, 4 CSN, 5 VIN  -> stock Package_TO_SOT_SMD:SOT-89-5 (pad 2 = tab)
  HD2525 (XINGLIGHT): 1 cathode, 2 anode, centre pad = thermal slug (pad 3, net HEAT)
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "lib")

def prop(name, val, x=0, y=0, hide=False):
    h = " (hide yes)" if hide else ""
    return f'(property "{name}" "{val}" (at {x} {y} 0){h} (effects (font (size 1.27 1.27))))'

def pin(typ, x, y, ang, name, num, length=2.54):
    return (f'(pin {typ} line (at {x} {y} {ang}) (length {length}) '
            f'(name "{name}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))')

PT4115 = f"""(symbol "PT4115" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  {prop("Reference", "U", 0, 10.16)}
  {prop("Value", "PT4115", 0, -10.16)}
  {prop("Footprint", "Package_TO_SOT_SMD:SOT-89-5", 0, 0, True)}
  {prop("Datasheet", "https://www.lcsc.com/datasheet/lcsc_datasheet_1912111437_UMW-Youtai-Semiconductor-Co---Ltd--PT4115_C347356.pdf", 0, 0, True)}
  {prop("Description", "30V 1.2A hysteretic buck LED driver, high-side sense (I = 0.1V/Rs), DIM: PWM/analog/enable", 0, 0, True)}
  {prop("ki_keywords", "LED driver buck constant current", 0, 0, True)}
  (symbol "PT4115_0_1" (rectangle (start -7.62 7.62) (end 7.62 -7.62) (stroke (width 0.254) (type default)) (fill (type background))))
  (symbol "PT4115_1_1"
    {pin("power_in", -10.16, 5.08, 0, "VIN", "5")}
    {pin("input", -10.16, 2.54, 0, "CSN", "4")}
    {pin("input", -10.16, -2.54, 0, "DIM", "3")}
    {pin("open_collector", 10.16, 0, 180, "SW", "1")}
    {pin("power_in", 0, -10.16, 90, "GND", "2")})
  (embedded_fonts no))"""

# Device:LED body plus a third (thermal) pin at the bottom
LED = f"""(symbol "LED_HD2525" (pin_numbers (hide yes)) (pin_names (offset 1.016) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  {prop("Reference", "LED", 0, 3.81)}
  {prop("Value", "LED_HD2525", 0, -5.08)}
  {prop("Footprint", "rgb-spotlight:LED_XINGLIGHT_HD2525", 0, 0, True)}
  {prop("Datasheet", "", 0, 0, True)}
  {prop("Description", "XINGLIGHT HD2525 3W LED, 2.5x2.5mm; pad 1 K, pad 2 A, centre pad thermal (keep isolated)", 0, 0, True)}
  {prop("ki_keywords", "LED power", 0, 0, True)}
  (symbol "LED_HD2525_0_1"
    (polyline (pts (xy -3.048 -0.762) (xy -4.572 -2.286) (xy -3.81 -2.286) (xy -4.572 -2.286) (xy -4.572 -1.524)) (stroke (width 0) (type default)) (fill (type none)))
    (polyline (pts (xy -1.778 -0.762) (xy -3.302 -2.286) (xy -2.54 -2.286) (xy -3.302 -2.286) (xy -3.302 -1.524)) (stroke (width 0) (type default)) (fill (type none)))
    (polyline (pts (xy -1.27 0) (xy 1.27 0)) (stroke (width 0) (type default)) (fill (type none)))
    (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
    (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none))))
  (symbol "LED_HD2525_1_1"
    {pin("passive", -3.81, 0, 0, "K", "1")}
    {pin("passive", 3.81, 0, 180, "A", "2")}
    {pin("passive", 0, -3.81, 90, "PAD", "3", 2.54)})
  (embedded_fonts no))"""

# Driver board side of the LED harness: one 6-pin connector drawn as 3 units (one per LED, "+" on top), so each unit
# sits in its channel's current loop where the LED would be. Pins: 1 R+, 2 R-, 3 G+, 4 G-, 5 B+, 6 B-.
def port_unit(u, col):
    a, k = 2 * u - 1, 2 * u
    return (f'(symbol "LED_PORT_{u}_1" (rectangle (start -2.54 2.54) (end 2.54 -2.54) (stroke (width 0.254) (type default)) (fill (type background)))'
            f' (text "{col}" (at 0 0 0) (effects (font (size 1.27 1.27))))'
            f' {pin("passive", 0, 5.08, 270, col + "+", str(a))} {pin("passive", 0, -5.08, 90, col + "-", str(k))})')
LED_PORT = f"""(symbol "LED_PORT" (pin_names (offset 0.508) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  {prop("Reference", "J", 3.81, 1.27)}
  {prop("Value", "LED_PORT", 3.81, -1.27)}
  {prop("Footprint", "Connector_JST:JST_PH_B6B-PH-K_1x06_P2.00mm_Vertical", 0, 0, True)}
  {prop("Datasheet", "", 0, 0, True)}
  {prop("Description", "LED harness socket, 6 pins as 3 units: 1 R+, 2 R-, 3 G+, 4 G-, 5 B+, 6 B- (+ = LED anode)", 0, 0, True)}
  {port_unit(1, "R")} {port_unit(2, "G")} {port_unit(3, "B")}
  (embedded_fonts no))"""

open(os.path.join(LIB, "rgb-spotlight.kicad_sym"), "w").write(
    '(kicad_symbol_lib (version 20251024) (generator "make_lib.py") (generator_version "10.0")\n'
    + PT4115 + "\n" + LED + "\n" + LED_PORT + "\n)\n")

# Land pattern: datasheet "recommended soldering pattern" (2.6 mm overall, 0.45 / 1.0 / 0.45 mm pads),
# pad length 2.4 mm as in the LCSC/EasyEDA footprint. Pad 1 (cathode) at -x.
MODEL = "LED-SMD_3P-L2.5-W2.5_XL-HD2525SURC-A4"
FP = f"""(footprint "LED_XINGLIGHT_HD2525" (version 20250114) (generator "make_lib.py") (layer "F.Cu")
  (descr "XINGLIGHT XL-HD2525 3W LED 2.5x2.5mm, 2 pads + centre thermal slug. Pad 1 cathode, pad 2 anode")
  (tags "LED 2525 HD2525 XINGLIGHT")
  (property "Reference" "REF**" (at 0 -2.4 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (property "Value" "LED_HD2525" (at 0 2.4 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (attr smd)
  (fp_line (start -1.75 -1.45) (end 1.45 -1.45) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
  (fp_line (start -1.75 1.45) (end 1.45 1.45) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
  (fp_line (start -1.75 -1.45) (end -1.75 1.45) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))
  (fp_rect (start -1.25 -1.25) (end 1.25 1.25) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))
  (fp_line (start -0.6 -1.25) (end -0.6 1.25) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
  (fp_text user "K" (at -1.08 -1.9 0) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.08))))
  (fp_rect (start -2.0 -1.7) (end 1.7 1.7) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
  (pad "1" smd rect (at -1.075 0) (size 0.45 2.4) (layers "F.Cu" "F.Paste" "F.Mask"))
  (pad "2" smd rect (at 1.075 0) (size 0.45 2.4) (layers "F.Cu" "F.Paste" "F.Mask"))
  (pad "3" smd rect (at 0 0) (size 1.0 2.4) (layers "F.Cu" "F.Paste" "F.Mask"))
  (model "${{KIPRJMOD}}/../../lib/3dmodels/{MODEL}.wrl" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 180)))
)
"""
os.makedirs(os.path.join(LIB, "rgb-spotlight.pretty"), exist_ok=True)
open(os.path.join(LIB, "rgb-spotlight.pretty", "LED_XINGLIGHT_HD2525.kicad_mod"), "w").write(FP)
# LED board wire pad: hand-soldered 24 AWG wire, no paste (HASL-tinned), on the single copper layer of the aluminium board
WIREPAD = """(footprint "WirePad_2.2x3.5mm" (version 20250114) (generator "make_lib.py") (layer "F.Cu")
  (descr "Solder pad for a hand-soldered wire (24 AWG), no paste") (tags "wire pad solder")
  (property "Reference" "REF**" (at 0 -2.6 0) (layer "F.SilkS") (hide yes) (effects (font (size 0.8 0.8) (thickness 0.12))))
  (property "Value" "WirePad" (at 0 2.6 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (attr smd exclude_from_pos_files exclude_from_bom)
  (fp_rect (start -1.35 -2.0) (end 1.35 2.0) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))
  (pad "1" smd roundrect (at 0 0) (size 2.2 3.5) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.15))
)
"""
open(os.path.join(LIB, "rgb-spotlight.pretty", "WirePad_2.2x3.5mm.kicad_mod"), "w").write(WIREPAD)
print("wrote lib/rgb-spotlight.kicad_sym and lib/rgb-spotlight.pretty/LED_XINGLIGHT_HD2525.kicad_mod")
