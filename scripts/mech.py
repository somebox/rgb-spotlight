"""Mechanical outline options, shared by both board generators, the driver router and scripts/set_outline.py.

Every part and every track lives inside the CORE_D keep-in disc (50 mm). The board edge around it is chosen
separately, as a named preset, so the housing decision can wait:

  disc50   50 mm disc (the core itself); inner M3 holes                         <- default
  disc55   55 mm disc; inner M3 holes
  disc60   60 mm disc; M3 holes in the rim at r = 27.5 mm; no inner holes
  tabs3    50 mm disc + three screw tabs (M3 at r = 28.5 mm, 9 mm wide); no inner holes

Pick one with MECH=<preset> on the make scripts, or change an existing board (routed, even hand-edited) with
  <KiCad python> scripts/set_outline.py <driver|led|all> <preset>
which only replaces the edge, the mounting holes, their copper keep-outs, the edge GND stitching and the GND pour
outlines. Parts and tracks are not touched.

Holes outside the core get a copper keep-out (screw head + margin) on every copper layer, so the screws touch no
circuit copper (chassis stays isolated). Inner holes keep the placement-time clearance only.
"""
import math, os, sys
import pcbnew
try:
    import pcbkit  # noqa: F401
except ImportError:  # an interpreter pcbkit is not linked into: use the checkout
    sys.path.insert(0, os.path.expanduser(os.environ.get("PCBKIT_ROOT", "~/src/pcb-kit")))

CORE_D = 50.0
CORE_R = CORE_D / 2
DEFAULT = os.environ.get("MECH", "disc50")
ANGLES = (30, 150, 270)                       # between the LED islands / driver cells on both boards
SCREW_HEAD_R = 3.0                            # M3 pan head (5.5 mm dia) + 0.25 mm: copper keep-out radius
INNER = {"driver": (11.0, ANGLES, 3.2), "led": (19.0, ANGLES, 3.2)}   # (r, angles, drill) inside the core

PRESETS = {
    "disc50": dict(d=50.0, inner=True),
    "disc55": dict(d=55.0, inner=True),
    "disc60": dict(d=60.0, inner=False, rim=(27.5, ANGLES, 3.2)),
    "tabs3": dict(d=CORE_D, inner=False, tabs=dict(angles=ANGLES, r_hole=28.5, width=9.0, drill=3.2)),
}

mm = pcbnew.FromMM
polar = lambda r, a: (r * math.cos(math.radians(a)), -r * math.sin(math.radians(a)))


def preset(name=None):
    name = name or DEFAULT
    if name not in PRESETS:
        raise SystemExit(f"unknown outline preset {name!r}; choose one of {', '.join(PRESETS)}")
    return name, PRESETS[name]


def extent(p):
    """Largest radius of the board edge."""
    if "tabs" in p:
        t = p["tabs"]
        return t["r_hole"] + t["width"] / 2
    return p["d"] / 2


def holes(board, p):
    """[(x, y, drill, outside_core)] mounting holes, board-centre coordinates."""
    out = []
    if p.get("inner"):
        r, angs, d = INNER[board]
        out += [(*polar(r, a), d, False) for a in angs]
    if "rim" in p:
        r, angs, d = p["rim"]
        out += [(*polar(r, a), d, True) for a in angs]
    if "tabs" in p:
        t = p["tabs"]
        out += [(*polar(t["r_hole"], a), t["drill"], True) for a in t["angles"]]
    return out


def inside(p, x, y, margin=0.0):
    """True if (x, y) is on the board at least `margin` from the edge (holes ignored)."""
    r = math.hypot(x, y)
    if r <= p["d"] / 2 - margin:
        return True
    if "tabs" in p:
        t = p["tabs"]
        for a in t["angles"]:
            ux, uy = polar(1, a); tx, ty = -uy, ux
            along, across = x * ux + y * uy, x * tx + y * ty
            if abs(across) <= t["width"] / 2 - margin and along <= t["r_hole"]:
                return along > 0
            if math.hypot(along - t["r_hole"], across) <= t["width"] / 2 - margin:
                return True
    return False


def _edge(b, V, kind, a, z=None, mid=None, r=None):
    e = pcbnew.PCB_SHAPE(b); e.SetLayer(pcbnew.Edge_Cuts); e.SetWidth(mm(0.05))
    if kind == "circle":
        e.SetShape(pcbnew.SHAPE_T_CIRCLE); e.SetCenter(V(*a)); e.SetEnd(V(a[0] + r, a[1]))
    elif kind == "arc":
        e.SetShape(pcbnew.SHAPE_T_ARC); e.SetArcGeometry(V(*a), V(*mid), V(*z))
    else:
        e.SetShape(pcbnew.SHAPE_T_SEGMENT); e.SetStart(V(*a)); e.SetEnd(V(*z))
    b.Add(e)


def draw_outline(b, V, p):
    if "tabs" not in p:
        _edge(b, V, "circle", (0, 0), r=p["d"] / 2)
        return
    R, t = p["d"] / 2, p["tabs"]
    hw = t["width"] / 2
    da = math.degrees(math.asin(hw / R))              # half-angle where a tab side meets the core circle
    base = math.sqrt(R * R - hw * hw)
    angs = sorted(a % 360 for a in t["angles"])
    for i, a in enumerate(angs):                       # going counter-clockwise: tab at a, then core arc to the next tab
        ux, uy = polar(1, a); tx, ty = -uy, ux         # radial and counter-clockwise tangent (KiCad y down)
        p_cw = (base * ux - hw * tx, base * uy - hw * ty)          # side on the clockwise side of the tab
        p_ccw = (base * ux + hw * tx, base * uy + hw * ty)
        e_cw = (t["r_hole"] * ux - hw * tx, t["r_hole"] * uy - hw * ty)
        e_ccw = (t["r_hole"] * ux + hw * tx, t["r_hole"] * uy + hw * ty)
        tip = ((t["r_hole"] + hw) * ux, (t["r_hole"] + hw) * uy)
        _edge(b, V, "seg", p_cw, e_cw)
        _edge(b, V, "arc", e_cw, e_ccw, mid=tip)
        _edge(b, V, "seg", e_ccw, p_ccw)
        nxt = angs[(i + 1) % len(angs)] + (360 if i == len(angs) - 1 else 0)
        a0, a1 = a + da, nxt - da
        _edge(b, V, "arc", polar(R, a0), polar(R, a1), mid=polar(R, (a0 + a1) / 2))


def strip_outline_file(path, X0, Y0):
    """Remove the edge (not inner cut-outs), the board-only H# mounting holes, their MH_KEEPOUT rule areas and the GND
    vias outside the core (edge stitching), by editing the .kicad_pcb text (pcbnew's Remove() corrupts its bindings
    mid-run; see pcb-kit's CONVENTIONS). Blocks come from pcbkit.mech.top_level_blocks. Returns items removed."""
    import re
    from pcbkit.mech import top_level_blocks
    txt = open(path).read()
    num = r"(-?[0-9.]+)"
    def drop(head, it):
        if head in ("gr_line", "gr_arc", "gr_circle", "gr_rect", "gr_poly") and '(layer "Edge.Cuts")' in it:
            if head == "gr_circle":
                (cx, cy), (ex, ey) = (tuple(map(float, re.search(rf"\({k} {num} {num}\)", it).groups())) for k in ("center", "end"))
                if math.hypot(ex - cx, ey - cy) < CORE_R - 5:
                    return False                            # an inner cut-out
            return True
        if head == "footprint" and "board_only" in it and re.search(r'\(property "Reference" "H\d+"', it):
            return True
        if head == "zone" and re.search(r'\(name "MH_KEEPOUT', it):
            return True
        if head == "via" and '(net "GND")' in it:
            x, y = map(float, re.search(rf"\(at {num} {num}\)", it).groups())
            return math.hypot(x - X0, y - Y0) > CORE_R + 0.3
        return False
    gone = [(a, z) for a, z, head in top_level_blocks(txt) if drop(head, txt[a:z])]
    for a, z in reversed(gone):
        ws = a
        while ws > 0 and txt[ws - 1] in " \t\n":           # take the item's leading newline/indent with it
            ws -= 1
        txt = txt[:ws] + txt[z:]
    open(path, "w").write(txt)
    return len(gone)


def apply_outline(b, board, name, X0, Y0, stitch_net=None):
    """Add the board edge, mounting holes (+ keep-outs outside the core), edge stitching and the GND pour extent for
    preset `name`. The board must have no edge / H# holes yet: a fresh board, or a file run through
    strip_outline_file first. Inner cut-outs (e.g. the LED board's wire hole) are left alone."""
    name, p = preset(name)
    V = lambda x, y: pcbnew.VECTOR2I_MM(X0 + x, Y0 + y)
    T = pcbnew.ToMM
    kfp = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/MountingHole.pretty"
    hl = holes(board, p)
    new_fps = []
    for x, y, d, outer in hl:
        fpn = "MountingHole_3.2mm_M3" if abs(d - 3.2) < 0.01 else f"MountingHole_{d:.1f}mm"
        fp = pcbnew.FootprintLoad(kfp, fpn); fp.SetFPID(pcbnew.LIB_ID("MountingHole", fpn))
        new_fps.append((fp, x, y, d, outer))
    draw_outline(b, V, p)
    for i, (fp, x, y, d, outer) in enumerate(new_fps, 1):
        fp.SetReference(f"H{i}"); fp.SetValue(f"M{d - 0.2:.0f}")
        fp.SetBoardOnly(True); fp.SetExcludedFromBOM(True); fp.SetExcludedFromPosFiles(True)
        fp.Reference().SetLayer(pcbnew.F_Fab); fp.Value().SetLayer(pcbnew.F_Fab)
        b.Add(fp); fp.SetPosition(V(x, y))
        if outer:                                                # no circuit copper under the screw head
            z = pcbnew.ZONE(b); z.SetIsRuleArea(True); z.SetZoneName(f"MH_KEEPOUT_H{i}")
            ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); z.SetLayerSet(ls)
            z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
            z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
            ol = z.Outline(); ol.NewOutline()
            for k in range(36):
                cx, cy = polar(SCREW_HEAD_R, k * 10)
                ol.Append(mm(X0 + x + cx), mm(Y0 + y + cy))
            b.Add(z)
    ext = extent(p)
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.GetNetname() == "GND":
            ol = z.Outline(); ol.RemoveAllContours(); ol.NewOutline()
            for k in range(72):
                cx, cy = polar(ext - 0.3, k * 5)
                ol.Append(mm(X0 + cx), mm(Y0 + cy))
    n_st = 0
    if stitch_net is not None and ext > CORE_R + 1.5:            # tie the back pour outside the core to the front
        for k in range(0, 360, 10):
            x, y = polar(CORE_R + 1.0, k + 5)
            if inside(p, x, y, 1.0) and all(math.hypot(x - hx, y - hy) > SCREW_HEAD_R + 0.6 for hx, hy, _, _ in hl):
                v = pcbnew.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3)); v.SetNet(stitch_net)
                b.Add(v); n_st += 1
    tb = b.GetTitleBlock(); tb.SetComment(1, f"outline: {name} ({describe(name)})")
    return name, len(hl), n_st


def describe(name):
    p = PRESETS[name]
    if "tabs" in p:
        t = p["tabs"]
        return f"{p['d']:.0f} mm disc + {len(t['angles'])} tabs, M3 at r = {t['r_hole']} mm"
    s = f"{p['d']:.0f} mm disc"
    if p.get("inner"):
        s += ", inner M3 holes"
    if "rim" in p:
        s += f", M3 rim holes at r = {p['rim'][0]} mm"
    return s
