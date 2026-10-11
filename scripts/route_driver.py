"""Driver board: scripted routing on the placed board (boards/driver/driver.kicad_pcb). 2 layers; GND pours on both.

  <KiCad python> scripts/route_driver.py [--force]          (scripts/make_driver_pcb.sh --route runs it)

Stages:
0. Driver cells, scripted: the cells are identical (red rotated +-120 deg), so their short links are drawn once in
   red-cell coordinates and rotated: the SW node (U.SW - D.A - L.2, 0.8 mm), the 12 V cluster (U.VIN - D.K - Rs.1, Cin.1,
   0.8 mm, with a via for the trunk on B.Cu), the Rs -> CSN sense line (0.25 mm, round the outside of Cin) and two
   GND vias at the PT4115 tab. Each piece is checked for clearance first; anything that doesn't fit is left to the router.
1. Cell links to J3 (maze router, route_strip.complete_nets): LEDK_x and CSN_x (the LED current, 455 mA).
2. +12V: first the J1.1 -> J2.1 pass-through alone at 1.5 mm (up to 3 A for a chain), preferring B.Cu, then every
   other +12V pad joins it at 0.8 mm.
3. GND: a via to the back plane beside every front SMD GND pad (nearest clear spot, short stub). Each PT4115's tab
   (pad 2, the IC's heat path) gets three.
4. Logic: +5V at 0.4 mm, then the signals at 0.25 mm, on both layers.
5. Anything left: tie_pads to the nearest via of its net, then an audit of track ends. DRC runs after (make script).
Refuses to run on a board that already has tracks (hand routing), unless --force, which clears them first.
"""
import math, os, re, sys, time
T0 = time.time()
stamp = lambda: f"[{time.time() - T0:5.1f} s]"
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from route_strip import Copper, complete_nets, net_components, tie_pads
import mech

F = os.path.join(HERE, "..", "boards", "driver", "driver.kicad_pcb")
b = pcbnew.LoadBoard(F)
tracks = list(b.GetTracks())
if tracks and "--force" not in sys.argv:
    raise SystemExit(f"{len(tracks)} tracks already on the board (hand routing?); not routing without --force")
for t in tracks:
    b.Remove(t)
mm, T = pcbnew.FromMM, pcbnew.ToMM
X0, Y0, R_BOARD = 150.0, 100.0, mech.CORE_R           # route inside the core, whatever the outline
OUT = (X0, Y0, R_BOARD)                                     # circular outline for the router's edge check
AREA = (X0 - R_BOARD + 0.2, Y0 - R_BOARD + 0.2, X0 + R_BOARD - 0.2, Y0 + R_BOARD - 0.2)
P = dict(CLEARANCE=0.2, EDGE_CLR=0.4, VIA=(0.6, 0.3), VIA_PAD_CLR=0.15, IN1_COST=20.0, AXIAL_PADS=True,
         QUICK=True, HWEIGHT=1.6)
F_, B_ = pcbnew.F_Cu, pcbnew.B_Cu
inside = lambda c, margin: math.hypot(c[0] - X0, c[1] - Y0) <= R_BOARD - margin


def track(a, z, w, layer, net):
    t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I_MM(*a)); t.SetEnd(pcbnew.VECTOR2I_MM(*z))
    t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(net); b.Add(t)


def via(xy, net, size=None):
    d, dr = size or P["VIA"]
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I_MM(*xy)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(F_, B_); v.SetWidth(mm(d)); v.SetDrill(mm(dr)); v.SetNet(net); b.Add(v)


route = lambda plan, exclude=frozenset(): complete_nets(b, P, AREA, plan, track, via, exclude=exclude, outline=OUT)
pads_of = lambda net: [(f.GetReference(), q.GetNumber()) for f in b.GetFootprints() for q in f.Pads() if q.GetNetname() == net]

# ---- 0. driver cells, scripted --------------------------------------------------------------------------------
def rot(x, y, a):
    c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
    return x * c + y * s_, -x * s_ + y * c
fp = {f.GetReference(): f for f in b.GetFootprints()}
pad = lambda ref, num: fp[ref].FindPadByNumber(num)
pc = lambda ref, num: (T(pad(ref, num).GetPosition().x), T(pad(ref, num).GetPosition().y))
class Exact:
    """Clearance against KiCad's own shapes (pads exactly, not as bounding boxes: the PT4115 tab is a thin bar and the
    rotated cells' pads have bounding boxes much larger than the copper)."""
    def __init__(self):
        self.items = []                                      # (layer, netcode, shape, is_hole)
        for f in b.GetFootprints():
            for q in f.Pads():
                for L in (F_, B_):
                    if q.IsOnLayer(L):
                        self.items.append((L, q.GetNetCode(), q.GetEffectiveShape(L), False))
                if q.GetDrillSize().x > 0:
                    self.items.append((None, q.GetNetCode(), q.GetEffectiveHoleShape(), True))
        for t in b.GetTracks():
            ls = [F_, B_] if t.Type() == pcbnew.PCB_VIA_T else [t.GetLayer()]
            for L in ls:
                self.items.append((L, t.GetNetCode(), t.GetEffectiveShape(L), False))
            if t.Type() == pcbnew.PCB_VIA_T:
                self.items.append((None, t.GetNetCode(), t.GetEffectiveHoleShape(), True))
        self.keep = []
    def ok(self, obj, layers, net, clr, via=False):
        for L in layers:
            sh = obj.GetEffectiveShape(L)
            for IL, n, other, hole in self.items:
                if hole:
                    if other.Collide(sh, mm(0.3 if not via else 0.25)) and (n != net or via):
                        return False
                    continue
                if IL != L:
                    continue
                if n != net and other.Collide(sh, mm(clr)):
                    return False
                if via and n == net and other.Collide(sh, mm(P["VIA_PAD_CLR"])) and isinstance(other, pcbnew.SHAPE):
                    if obj.Type() == pcbnew.PCB_VIA_T and n == net and any(q.GetNetCode() == net and q.HitTest(obj.GetPosition())
                                                                            for f in b.GetFootprints() for q in f.Pads()):
                        return False
        return True
    def add(self, obj, layers):
        self.keep.append(obj)
        for L in layers:
            self.items.append((L, obj.GetNetCode(), obj.GetEffectiveShape(L), False))
        if obj.Type() == pcbnew.PCB_VIA_T:
            self.items.append((None, obj.GetNetCode(), obj.GetEffectiveHoleShape(), True))
ex = Exact()
skipped = []
def try_track(pts, w, net, layer=F_):
    objs = []
    for a, z in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I_MM(*a)); t.SetEnd(pcbnew.VECTOR2I_MM(*z))
        t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(net); objs.append(t)
    if all(inside(a, 0.4 + w / 2) for a in pts) and all(ex.ok(t, [layer], net.GetNetCode(), P["CLEARANCE"]) for t in objs):
        for t in objs:
            b.Add(t); ex.add(t, [layer])
        return True
    skipped.append(f"{net.GetNetname()} {len(objs)} seg"); return False
def try_via(c, net):
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I_MM(*c)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(F_, B_); v.SetWidth(mm(P["VIA"][0])); v.SetDrill(mm(P["VIA"][1])); v.SetNet(net)
    if inside(c, 0.8) and ex.ok(v, [F_, B_], net.GetNetCode(), P["CLEARANCE"], via=True):
        b.Add(v); ex.add(v, [F_, B_]); return True
    skipped.append(f"{net.GetNetname()} via"); return False
for n, a in ((1, 0), (2, 120), (3, -120)):
    U, R, L, D, C = f"U{n + 1}", f"R{n}", f"L{n}", f"D{n}", f"C{n + 5}"
    loc = lambda x, y: (lambda q: (X0 + q[0], Y0 + q[1]))(rot(x, y, a))     # red-cell coordinates -> board
    sw, v12, csn, gnd = pad(U, "1").GetNet(), pad(U, "5").GetNet(), pad(U, "4").GetNet(), pad(U, "2").GetNet()
    try_track([pc(U, "1"), pc(D, "2")], 0.8, sw)                            # SW node, front only
    try_track([pc(D, "2"), pc(L, "2")], 0.8, sw)
    try_track([pc(D, "1"), pc(U, "5")], 0.8, v12)                           # 12 V cluster
    try_track([pc(C, "1"), pc(U, "5")], 0.8, v12)
    if try_via(loc(-2.9, -15.0), v12):                                      # trunk via between Rs.1 and D.K
        try_track([pc(R, "1"), loc(-2.9, -15.0), pc(D, "1")], 0.8, v12)
    try_track([pc(R, "2"), loc(-6.6, -11.4), loc(-6.6, -23.0), loc(-2.6, -23.0), pc(U, "4")], 0.25, csn)   # Kelvin sense
    if try_via(loc(3.4, -21.6), pad(U, "3").GetNet()):                      # DIM escape to B.Cu (the pin is boxed in on F)
        try_track([pc(U, "3"), loc(3.4, -21.6)], 0.3, pad(U, "3").GetNet())
    for x in (-3.3, 3.3):                                                   # tab -> back plane
        if try_via(loc(x, -20.5), gnd):
            try_track([loc(x * 2.6 / 3.3, -20.5), loc(x, -20.5)], 0.6, gnd)
print(stamp(), f"0. cells scripted; skipped (left to the router): {skipped or 'none'}")
if os.environ.get("ROUTE_STAGE0_ONLY"):                    # debug: save just the scripted cells elsewhere
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(os.environ["ROUTE_STAGE0_ONLY"], b); raise SystemExit(0)

# ---- 1. cell links to J3 ---------------------------------------------------------------------------------------
n1, f1 = route([(r"/SW_[RGB]", [F_], 0.8), (r"/LEDK_[RGB]", [F_, B_], 0.8), (r"/CSN_[RGB]", [F_, B_], 0.6)])
print(stamp(), f"1. cells: {n1} connections, failed {sorted(set(f1)) or 'none'}")

# ---- 2. +12V ------------------------------------------------------------------------------------------------
# The trunk is scripted: a 1.5 mm ring on B.Cu at R_RING, outside every cell (their tab vias end at r ~ 21.1), with
# radial stubs out from J1.1 and J2.1. It carries the chain's pass-through current (up to ~3 A). The router then
# only adds the short taps (cells, 78L05, TVS, bulk cap) at 0.8 mm.
R_RING, W_RING = 23.3, 1.5
v12 = b.FindNet("+12V")
ring = [(X0 + R_RING * math.cos(math.radians(k)), Y0 - R_RING * math.sin(math.radians(k))) for k in range(0, 361, 6)]
# open at 270 deg (the logic side, no taps there) so the trunk is a C, not a closed loop (pcbkit check flags loops)
n_ring = sum(try_track([p_, q_], W_RING, v12, B_) for k, (p_, q_) in enumerate(zip(ring, ring[1:])) if k * 6 != 270)
for j in ("J1", "J2"):
    x, y = pc(j, "1"); r = math.hypot(x - X0, y - Y0)
    try_track([(x, y), (X0 + (x - X0) * R_RING / r, Y0 + (y - Y0) * R_RING / r)], W_RING, v12, B_)
n2b, f2b = route([(r"\+12V", [F_, B_], 0.8)])
f2a = []
print(stamp(), f"2. +12V: ring {n_ring}/{len(ring) - 2} segments + J1/J2 stubs (skipped {skipped or 'none'}), taps {n2b} (failed {sorted(set(f2b)) or 'none'})")

# ---- 3. GND vias ----------------------------------------------------------------------------------------------
def plane_vias(net_name, size, per_pad=lambda ref, q: 1, radius=3.0, step=0.2):
    """A via beside every front SMD pad of the net: nearest clear spot, straight stub on F.Cu."""
    cu = Copper(b); cu.via_pad_clr = P["VIA_PAD_CLR"]
    vr, clr, netobj = size[0] / 2, P["CLEARANCE"], b.FindNet(net_name)
    placed, failed = 0, []
    pads = [(f.GetReference(), q) for f in b.GetFootprints() for q in f.Pads()
            if q.GetNetname() == net_name and q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and q.IsOnLayer(F_)]
    for ref, q in pads:
        c0 = (T(q.GetPosition().x), T(q.GetPosition().y))
        sw = min(0.5, T(min(q.GetSize(F_).x, q.GetSize(F_).y)))
        k = int(radius / step)
        cands = sorted((math.hypot(ix * step, iy * step), (c0[0] + ix * step, c0[1] + iy * step))
                       for ix in range(-k, k + 1) for iy in range(-k, k + 1) if 0.4 <= math.hypot(ix, iy) * step <= radius)
        got = 0
        for d, c in cands:
            if not inside(c, 0.8):
                continue
            if cu.clear(("disc", (c, vr)), "all", net_name, clr) and cu.clear(("seg", (c0, c, sw / 2)), {F_}, net_name, clr):
                via(c, netobj, size); track(c0, c, sw, F_, netobj)
                cu.add_via(c, vr, net_name); cu.add_track(c0, c, sw / 2, F_, net_name)
                got += 1
                if got >= per_pad(ref, q):
                    break
        placed += got
        if not got:
            failed.append(f"{ref}.{q.GetNumber()}")
    return placed, failed

tab = lambda ref, q: 3 if ref in ("U2", "U3", "U4") and q.GetNumber() == "2" else 1
ng, fg = plane_vias("GND", P["VIA"], per_pad=tab)
print(stamp(), f"3. GND vias: {ng} (failed {fg or 'none'})")

# ---- 4. logic ------------------------------------------------------------------------------------------------
# escape vias first for the pins of the long cross-board nets (their pads sit in crowded corners): the nearest clear
# spot within 3 mm, checked against exact shapes, with a short F.Cu stub. The back, inside the ring, is then open.
ex = Exact(); skipped = []
def escape(ref, num, radius=3.0, step=0.2):
    q = pad(ref, num); c0 = pc(ref, num); net = q.GetNet()
    k = int(radius / step)
    for d, c in sorted((math.hypot(i * step, j * step), (c0[0] + i * step, c0[1] + j * step))
                       for i in range(-k, k + 1) for j in range(-k, k + 1) if 0.8 <= math.hypot(i, j) * step <= radius):
        if not inside(c, 0.8):
            continue
        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I_MM(*c)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(F_, B_); v.SetWidth(mm(P["VIA"][0])); v.SetDrill(mm(P["VIA"][1])); v.SetNet(net)
        t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I_MM(*c0)); t.SetEnd(pcbnew.VECTOR2I_MM(*c))
        t.SetWidth(mm(0.25)); t.SetLayer(F_); t.SetNet(net)
        if ex.ok(v, [F_, B_], net.GetNetCode(), P["CLEARANCE"], via=True) and ex.ok(t, [F_], net.GetNetCode(), P["CLEARANCE"]):
            b.Add(v); ex.add(v, [F_, B_]); b.Add(t); ex.add(t, [F_])
            return True
    skipped.append(f"{ref}.{num}"); return False
ESC = [("U7", "4"), ("U1", "6"), ("R8", "2"), ("U6", "2"), ("U6", "4"), ("U6", "6"), ("U1", "1")]
n_esc = sum(escape(r_, n_) for r_, n_ in ESC)
print(stamp(), f"4a. escape vias: {n_esc}/{len(ESC)} (failed {skipped or 'none'})")
# +5V spine for the pull-ups: their +5V pads (pin 1) alternate with OUT_x pads in one column, so feed them from a
# straight track in the gap between the column and U6's pin row
xs = (T(pad("U6", "1").GetBoundingBox().GetRight()) + T(pad("R4", "1").GetBoundingBox().GetLeft())) / 2
v5 = pad("R4", "1").GetNet()
(x4, y4), (x5, y5), (x6, y6) = pc("R4", "1"), pc("R5", "1"), pc("R6", "1")
spine = try_track([(x4, y4), (xs, y4), (xs, y6), (x6, y6)], 0.25, v5) and try_track([(xs, y5), (x5, y5)], 0.25, v5)
print(stamp(), f"4b. pull-up +5V spine: {'ok' if spine else 'blocked ' + str(skipped)}")
n4, f4 = route([(r"/OUT_[RGB]|/SET|/DIN|/DIN_IN|/DOUT_RAW", [F_, B_], 0.25),
                (r"/DIM_[RGB]|/DIN_5V|/DOUT", [B_, F_], 0.25),
                (r"\+5V", [F_, B_], 0.4)])
print(stamp(), f"4. logic: {n4} connections, failed {sorted(set(f4)) or 'none'}")

# ---- 5. leftovers + audit -------------------------------------------------------------------------------------
failed = sorted(set(f1 + f2a + f2b + f4))
if failed:                                                   # full search (no corridor limit) for what's left
    P["QUICK"] = False
    n5, f5 = route([(re.escape(n), [B_, F_], 0.4 if n in ("+12V", "+5V") else 0.25) for n in failed])
    print(stamp(), f"5. full-search pass: {n5}, still failed {sorted(set(f5)) or 'none'}")
# scripted fallback for OUT_R (WS2811 pin 1 sits on the far row of U1 from R4 / U6.1): up between U1's pin rows,
# along the 1.3 mm gap between U1 and the R4-R6 column, into R4.2. Only if the router left it unjoined.
if len(net_components(b, "/OUT_R", frozenset())) > 1:
    ex = Exact(); skipped = []
    (ux, uy), (rx, ry) = pc("U1", "1"), pc("R4", "2")
    xg = (T(pad("R4", "2").GetBoundingBox().GetRight()) + T(pad("U1", "1").GetBoundingBox().GetLeft())) / 2
    ok = try_track([(ux, uy), (ux, uy - 1.55), (xg, uy - 1.55), (xg, ry), (rx, ry)], 0.25, pad("U1", "1").GetNet())
    print(stamp(), f"5b. OUT_R scripted fallback: {'ok' if ok else 'blocked ' + str(skipped)}")
# clean-up: drop escape vias the router didn't use, and the stubs that led to them (repeat until stable)
def touching(item_pos, net, layer, skip):
    for f in b.GetFootprints():
        for q in f.Pads():
            if q.GetNetCode() == net and q.IsOnLayer(layer) and q.HitTest(item_pos):
                return True
    for t in b.GetTracks():
        if t == skip or t.GetNetCode() != net:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            if t.HitTest(item_pos):
                return True
        elif t.GetLayer() == layer and t.HitTest(item_pos, 0):
            return True
    return False
removed = 0
while True:
    gone = []
    for t in b.GetTracks():
        if t.GetNetname() == "GND":
            continue                                         # GND vias and stubs feed the planes
        if t.Type() == pcbnew.PCB_VIA_T:
            users = [u for u in b.GetTracks() if u.Type() != pcbnew.PCB_VIA_T and u.GetNetCode() == t.GetNetCode()
                     and (t.HitTest(u.GetStart()) or t.HitTest(u.GetEnd()) or u.HitTest(t.GetPosition(), 0))]
            if len({u.GetLayer() for u in users}) < 2:       # a via joins two layers or it does nothing
                gone.append(t)
        elif not (touching(t.GetStart(), t.GetNetCode(), t.GetLayer(), t) and touching(t.GetEnd(), t.GetNetCode(), t.GetLayer(), t)):
            gone.append(t)
    if not gone:
        break
    for t in gone:
        b.Remove(t)
    removed += len(gone)
print(stamp(), f"6. clean-up: removed {removed} unused vias / stubs")
key = lambda x, y: (round(x / 2000), round(y / 2000))
ends, segs = {}, []
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        continue
    segs.append(t)
    for e in (t.GetStart(), t.GetEnd()):
        ends.setdefault((key(e.x, e.y), t.GetLayer()), []).append(t)
vias = {key(v.GetPosition().x, v.GetPosition().y) for v in b.GetTracks() if v.Type() == pcbnew.PCB_VIA_T}
pad_c = {(key(q.GetPosition().x, q.GetPosition().y), L) for f in b.GetFootprints() for q in f.Pads() for L in (F_, B_) if q.IsOnLayer(L)}
dangling = 0
for (k, L), ts in ends.items():
    if (k, L) in pad_c or k in vias or len(ts) > 1:
        continue
    x, y = k[0] * 2000, k[1] * 2000
    if any(s_ is not ts[0] and s_.GetLayer() == L and s_.GetNetname() == ts[0].GetNetname()
           and s_.HitTest(pcbnew.VECTOR2I(int(x), int(y)), 0) for s_ in segs):
        continue
    if any(q.IsOnLayer(L) and q.HitTest(pcbnew.VECTOR2I(int(x), int(y))) for f in b.GetFootprints() for q in f.Pads()):
        continue
    dangling += 1
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(F, b)
nt = sum(1 for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T); nv = sum(1 for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T)
print(stamp(), f"saved: {nt} track segments, {nv} vias, dangling track ends {dangling}")
