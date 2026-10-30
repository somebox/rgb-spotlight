"""Driver / interface board (FR4, 2 layers) from its netlist: footprints, placement, outline, rules, planes, silk.
No routing yet.

  scripts/make_driver_pcb.sh [--force]      (netlist export -> this script -> DRC)
  <KiCad python> scripts/gen_driver_pcb.py <netlist.net> <out.kicad_pcb> [--force]

Sits 4-6 cm behind the LED board in the housing. Board centre = origin, KiCad coordinates (y down), angles
counter-clockwise from +x.
- Front (faces the LED board): every SMD part and J3, the LED harness socket (JST PH 6 vertical), at the centre.
- Back (faces the housing's back): J1 IN and J2 OUT (JST XH 3 vertical, through-hole), reachable through the back
  cap or by pigtails to panel connectors. Everything else is SMD on the front: one-sided SMT plus 3 THT parts.
- Each PT4115 channel is one "cell", drawn for red at the top (90 deg) and rotated +-120 deg for green and blue:
  Rs and L innermost (their LED-side pads face J3), then D, then the PT4115 with Cin beside it, so the switching loop
  SW -> D -> VIN/Cin -> GND tab stays a few mm across.
- Gaps between the cells: 150 deg = J1 + input protection (TVS, bulk) + level shifter; 30 deg = J2 + 78L05;
  270 deg = WS2811 + 74HC04. M3 holes at r = 11 mm in the three gaps.
- GND pour on both layers.
- Everything stays inside the 50 mm core (mech.CORE_D). The board edge and mounting holes come from an outline preset
  (MECH=disc50|disc55|disc60|tabs3, default disc50; see scripts/mech.py); scripts/set_outline.py changes it later.
Refuses to overwrite a board that already has footprints, unless --force. Hand edits come after this.
"""
import math, os, re, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pcbkit.kicad import data_path
from pcbkit.silk import BB, Placer, set_size
import mech

args = [a for a in sys.argv[1:] if not a.startswith("--")]
NET, OUT = args[0], args[1]
if os.path.exists(OUT) and "(footprint " in open(OUT).read() and "--force" not in sys.argv:
    raise SystemExit(f"{OUT} already has footprints (hand-edited?); not overwriting without --force")
KFP = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
PLIB = os.path.join(HERE, "..", "lib", "rgb-spotlight.pretty")
libdir = lambda lib: PLIB if lib == "rgb-spotlight" else KFP + lib + ".pretty"
mm = pcbnew.FromMM
X0, Y0 = 150.0, 100.0
R_BOARD = mech.CORE_R                       # parts, tracks and silk stay inside this; the edge comes from the preset
R_CONN = 19.5                               # J1 / J2 pin-row radius (back side)
V = lambda x, y: pcbnew.VECTOR2I_MM(X0 + x, Y0 + y)
# footprint -> (lib/3dmodels file, offset xyz mm, rotation xyz deg). SOT-89-5: LCSC's model (easyeda2kicad C347356);
# LCSC's footprint is KiCad's rotated 180 deg and its model carries a 180 deg rotation, so none is needed here.
MODELS = {"SOT-89-5": ("SOT-89-5_LCSC.step", (0, 0, 0), (0, 0, 0))}

# ---- netlist ---------------------------------------------------------------------------------------------
t = open(NET).read()
comps = {}
for blk in re.split(r'\n\t\t\(comp\n', t.split("(libparts")[0].split("(nets")[0])[1:]:
    g = lambda pat: (re.search(pat, blk, re.S) or [None, None])[1]
    comps[g(r'\(ref "([^"]+)"\)')] = dict(
        value=g(r'\(value "([^"]*)"\)'), fp=g(r'\(footprint "([^"]+)"\)'),
        sheet=g(r'\(sheetpath\s*\(names "[^"]*"\)\s*\(tstamps "([^"]+)"\)'), ts=g(r'\n\t\t\t\(tstamps "([^"]+)"'),
        fields=dict(re.findall(r'\(field\s*\(name "([^"]+)"\)(?:\s*"([^"]*)")?\s*\)', blk)),
        no_bom='(name "exclude_from_bom")' in blk, dnp='(name "dnp")' in blk,
        desc=g(r'\(description "([^"]*)"\)'))
pinnet, netnames = {}, []
for blk in re.split(r'\n\t\t\(net\n', t[t.index("(nets"):])[1:]:
    name = re.search(r'\(name "([^"]*)"\)', blk).group(1)
    netnames.append(name)
    for r, pn in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk):
        pinnet[(r, pn)] = name

# ---- placement plan: ref -> (x, y, rotation); BACK = refs on the back ------------------------------------------
def rot(x, y, a):
    """Rotate (x, y) counter-clockwise on screen by a degrees about the board centre."""
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return x * c + y * s, -x * s + y * c

polar = lambda r, a: (r * math.cos(math.radians(a)), -r * math.sin(math.radians(a)))
tangent = lambda a: (-math.sin(math.radians(a)), -math.cos(math.radians(a)))      # counter-clockwise unit vector

# red cell at the top; {n}: channel 1-3. Rs pad 2 (CSN = LED +) and L pad 1 (LED -) face J3 at the centre.
CELL = {"R{n}": (-4.0, -12.0, 270),          # Rs: pad 1 (+12V) outer, pad 2 (CSN, LED anode) inner
        "L{n}": (3.4, -12.0, 90),            # pad 1 (LED K) inner, pad 2 (SW) outer
        "D{n}": (0.0, -16.7, 0),             # K (pad 1, +12V) left, A (pad 2, SW) right
        "U{u}": (0.0, -20.5, 180),           # VIN lower-left, SW lower-right, CSN upper-left, DIM upper-right
        "C{c}": (-5.0, -20.0, 90)}           # Cin: pad 1 (+12V) inner, pad 2 (GND) outer
CH_ANGLE = {1: 0, 2: 120, 3: -120}           # rotation of the red cell: R top, G lower-left, B lower-right
P, BACK = {}, {"J1", "J2"}
for n, a in CH_ANGLE.items():
    for tmpl, (x, y, r) in CELL.items():
        P[tmpl.format(n=n, u=n + 1, c=n + 5)] = (*rot(x, y, a), (r + a) % 360)
P["J3"] = (0.0, -5.0, 270)                   # PH 6 vertical: pin 1 at the top (towards the red cell), pins downwards
P.update({
    # 150 deg gap: J1 (back) + input protection and level shifter (front)
    "D4": (*polar(16.4, 150), 60), "C9": (*polar(22.3, 150), 60),
    "U7": (-9.6, -16.6, 0), "C3": (-9.6, -19.0, 0), "R7": (-12.2, -17.4, 90), "R10": (-12.2, -15.2, 90),
    # 30 deg gap: J2 (back) + 78L05 (front)
    "U5": (6.8, -19.5, 0), "C5": (10.6, -18.0, 90), "C4": (9.9, -21.3, 90),
    # 270 deg gap: WS2811 + 74HC04 with pull-ups between, decoupling at the ends
    "U6": (-5.0, 18.5, 270), "C2": (-10.9, 17.7, 90), "R4": (0.7, 16.3, 90), "R5": (0.7, 18.5, 90), "R6": (0.7, 20.7, 90),
    "U1": (4.5, 18.5, 90), "C1": (8.8, 16.9, 90), "R8": (8.8, 19.3, 90), "R9": (8.8, 21.6, 90),
})
CONN = {"J1": 150, "J2": 30}                 # placed separately (back, pin row tangential at R_CONN)
missing = sorted(set(comps) - set(P) - set(CONN))
assert not missing, f"no placement for {missing}"

# ---- board --------------------------------------------------------------------------------------------
b = pcbnew.LoadBoard(data_path("templates", "blank.kicad_pcb"))
b.SetCopperLayerCount(2)
ds = b.GetDesignSettings()
ds.m_CopperEdgeClearance = mm(0.3); ds.m_MinClearance = mm(0.15); ds.m_TrackMinWidth = mm(0.15)
ds.m_ViasMinSize = mm(0.5); ds.m_MinThroughDrill = mm(0.3); ds.m_HoleToHoleMin = mm(0.25)
ds.m_MinSilkTextHeight = mm(0.8); ds.m_MinSilkTextThickness = mm(0.15)
ns = ds.m_NetSettings
dc = ns.GetDefaultNetclass()
dc.SetTrackWidth(mm(0.25)); dc.SetClearance(mm(0.2)); dc.SetViaDiameter(mm(0.6)); dc.SetViaDrill(mm(0.3))
# 0.2 mm clearance throughout (12 V needs nothing more; scripts/route_driver.py routes to 0.2 mm)
# PWR is the taps' width: the 1.5 mm J1 -> J2 pass-through ring is drawn explicitly by scripts/route_driver.py
for name, w, clr, vd, vdr, pats in (("PWR", 0.8, 0.2, 0.8, 0.4, ["+12V", "GND"]),
                                    ("LED", 0.6, 0.2, 0.8, 0.4, ["/CSN_*", "/LEDK_*", "/SW_*"]),
                                    ("LOGIC_PWR", 0.4, 0.2, 0.6, 0.3, ["+5V"])):
    k = pcbnew.NETCLASS(name); k.SetTrackWidth(mm(w)); k.SetClearance(mm(clr)); k.SetViaDiameter(mm(vd)); k.SetViaDrill(mm(vdr))
    ns.SetNetclass(name, k)
    for pt in pats:
        ns.SetNetclassPatternAssignment(pt, name)
ds.SetAuxOrigin(V(0, 0)); ds.SetGridOrigin(V(0, 0))
tb = b.GetTitleBlock(); tb.SetTitle("RGB Spotlight - driver board"); tb.SetRevision("2.0"); tb.SetDate("2026-10-05")
tb.SetComment(0, "placement by scripts/gen_driver_pcb.py; FR4 2 layers; J1/J2 on the back")
for nm in netnames:
    if b.FindNet(nm) is None:
        b.Add(pcbnew.NETINFO_ITEM(b, nm))


def pad_xy(fp, num):
    p = fp.FindPadByNumber(num).GetPosition()
    return pcbnew.ToMM(p.x) - X0, pcbnew.ToMM(p.y) - Y0

for ref, c in comps.items():
    lib, name = c["fp"].split(":")
    fp = pcbnew.FootprintLoad(libdir(lib), name)
    assert fp, c["fp"]
    fp.SetFPID(pcbnew.LIB_ID(lib, name)); fp.SetReference(ref); fp.SetValue(c["value"])
    fp.SetPath(pcbnew.KIID_PATH(c["sheet"] + c["ts"]))
    fp.SetSheetname("/"); fp.SetSheetfile("driver.kicad_sch")
    for key, v in c["fields"].items():
        if key in ("Footprint", "Reference", "Value"):
            continue
        if not fp.HasField(key):
            fp.Add(pcbnew.PCB_FIELD(fp, fp.GetNextFieldOrdinal(), key))
        fp.GetField(key).SetText(v or ""); fp.GetField(key).SetVisible(False)
    if c["desc"] is not None and fp.HasField("Description"):
        fp.GetField("Description").SetText(c["desc"])
    fp.SetExcludedFromBOM(c["no_bom"]); fp.SetDNP(c["dnp"])
    if name in MODELS:                       # KiCad 10 ships no model for these footprints
        fp.Models().clear()
        m = pcbnew.FP_3DMODEL(); m.m_Filename = "${KIPRJMOD}/../../lib/3dmodels/" + MODELS[name][0]
        m.m_Offset = pcbnew.VECTOR3D(*MODELS[name][1]); m.m_Rotation = pcbnew.VECTOR3D(*MODELS[name][2])
        fp.Models().push_back(m)
    b.Add(fp)
    for pad in fp.Pads():
        n = pinnet.get((ref, pad.GetNumber()))
        if n:
            pad.SetNet(b.FindNet(n))
    if ref in CONN:
        # back side; pin row tangential at R_CONN, centred on pin 2, body towards the board centre
        a = CONN[ref]; fp.SetPosition(V(0, 0)); fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        tx, ty = tangent(a); best = None
        for deg in range(0, 360, 15):
            fp.SetOrientationDegrees(deg)
            (x1, y1), (x3, y3) = pad_xy(fp, "1"), pad_xy(fp, "3")
            if abs((x3 - x1) * tx + (y3 - y1) * ty) < 4.9:
                continue                      # not tangential
            fp.SetPosition(V(0, 0)); px, py = pad_xy(fp, "2"); cx, cy = polar(R_CONN, a)
            fp.SetPosition(V(cx - px, cy - py))
            bb = fp.GetCourtyard(pcbnew.B_CrtYd).BBox(); r = math.hypot(pcbnew.ToMM(bb.Centre().x) - X0, pcbnew.ToMM(bb.Centre().y) - Y0)
            if best is None or r < best[0]:
                best = (r, deg)
        fp.SetOrientationDegrees(best[1]); fp.SetPosition(V(0, 0)); px, py = pad_xy(fp, "2"); cx, cy = polar(R_CONN, a)
        fp.SetPosition(V(cx - px, cy - py))
        continue
    x, y, r = P[ref]
    fp.SetPosition(V(x, y)); fp.SetOrientationDegrees(r)
    if ref == "J3":                          # centre the 6-pin row on the board centre
        (x1, y1), (x6, y6) = pad_xy(fp, "1"), pad_xy(fp, "6")
        fp.SetPosition(V(x - (x1 + x6) / 2, y - 5.0 - (y1 + y6) / 2 + 5.0))

# ---- zones: GND on both layers -------------------------------------------------------------------------------
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.FindNet("GND")); z.SetZoneName(f"GND_{b.GetLayerName(layer)}")
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetThermalReliefGap(mm(0.3)); z.SetThermalReliefSpokeWidth(mm(0.5))
    ol = z.Outline(); ol.NewOutline()
    for i in range(72):
        x, y = polar(R_BOARD - 0.3, i * 5)
        ol.Append(mm(X0 + x), mm(Y0 + y))
    b.Add(z)
# board edge, mounting holes (+ copper keep-outs), edge stitching and pour extent: from the outline preset
OUTLINE, n_holes, n_stitch = mech.apply_outline(b, "driver", None, X0, Y0, stitch_net=b.FindNet("GND"))

# ---- silkscreen -----------------------------------------------------------------------------------------
class RoundPlacer(Placer):
    def free(self, item, s, area=None):
        x0, y0, x1, y1 = BB(item)
        if max(math.hypot(x - X0, y - Y0) for x in (x0, x1) for y in (y0, y1)) > R_BOARD - 0.5:
            return False
        return super().free(item, s, area)
pl = RoundPlacer(b, (X0 - R_BOARD, Y0 - R_BOARD, X0 + R_BOARD, Y0 + R_BOARD))
for fp in b.GetFootprints():                 # through-hole pads are obstacles on both sides
    for q in fp.Pads():
        if q.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
            pl.obst["B" if not fp.IsFlipped() else "F"].append(BB(q))
def text(s, x, y, size, layer=pcbnew.F_SilkS, angle=0):
    tx = pcbnew.PCB_TEXT(b); tx.SetText(s); tx.SetLayer(layer); set_size(tx, size)
    tx.SetTextAngleDegrees(angle); tx.SetPosition(V(x, y))
    if layer == pcbnew.B_SilkS:
        tx.SetMirrored(True)
    b.Add(tx); pl.commit(tx, "B" if layer == pcbnew.B_SilkS else "F")
    return tx
# J3 pin legend, left of the pin column
j3 = b.FindFootprintByReference("J3")
x_left = pcbnew.ToMM(j3.GetCourtyard(pcbnew.F_CrtYd).BBox().GetLeft()) - X0
for num, lab in zip("123456", ("R+", "R-", "G+", "G-", "B+", "B-")):
    _, y = pad_xy(j3, num)
    text(lab, x_left - 1.3, y, 0.8)
text("LED", x_left - 1.3, pad_xy(j3, "1")[1] - 2.0, 0.8)
# back: connector legends and board text
for ref, a, title in (("J1", 150, "IN"), ("J2", 30, "OUT")):     # beside the connector, on the side away from the cells
    text(title, *polar(R_CONN, a + (21 if a > 90 else -24)), 1.2, pcbnew.B_SilkS, (a + 90) % 360 if a > 90 else (a - 90) % 360)
text("RGB Spotlight driver v2.0", 0, 15.6, 1.2, pcbnew.B_SilkS)          # back, below J3's pins and the bottom hole
text("J1 IN / J2 OUT: 1=12V 2=DATA 3=GND", 0, 18.2, 0.9, pcbnew.B_SilkS)
text("JLCJLCJLCJLC", 0, 20.6, 1.0, pcbnew.B_SilkS)
REF_W = 0.8
todo, unplaced = [], []
for fp in b.GetFootprints():
    f = fp.Reference()
    if fp.GetReference()[0] == "H":
        continue
    side = "B" if fp.IsFlipped() else "F"
    f.SetLayer(pcbnew.B_SilkS if side == "B" else pcbnew.F_SilkS)
    pads = [BB(q) for q in fp.Pads()]
    todo.append((f, (min(q[0] for q in pads), min(q[1] for q in pads), max(q[2] for q in pads), max(q[3] for q in pads)), fp, side))
while todo:
    todo.sort(key=lambda tt: pl.try_slots(tt[0], tt[3], tt[1], 0.8, count=True, width=REF_W))
    f, anchor, fp, side = todo.pop(0)
    if not pl.try_slots(f, side, anchor, 0.8, width=REF_W):
        f.SetLayer(pcbnew.B_Fab if side == "B" else pcbnew.F_Fab); unplaced.append(fp.GetReference())
print(f"silk: {len(unplaced)} references without a free slot (moved to Fab): {unplaced}")

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(OUT, b)
print(f"driver: {len(comps)} footprints in the {mech.CORE_D:.0f} mm core (J1/J2 on the back), GND both layers; "
      f"outline {OUTLINE}: {mech.describe(OUTLINE)}, {n_holes} holes, {n_stitch} edge stitching vias")
