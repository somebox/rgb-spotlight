"""Maze router and routing helpers, copied from the rp2354-messages-sign repo (scripts/route_strip.py).

rgb-spotlight uses Copper, Grid, complete_nets and tie_pads (scripts/route_driver.py). Local change: `outline` may
be a circle (cx, cy, r) as well as a rectangle (x0, y0, x1, y1). The original module docstring follows.

Scripted routing for the character-module driver strip (called from gen_char_module.py).

Column fan-in, all on F.Cu with no vias. The TM5020A (QSOP-24 at -90 deg) has OUT0-7 along its top edge
(right to left) and OUT8-15 along its bottom edge (left to right); its control pins sit at the right end, and the
bottom pads are ~0.3 mm from the board edge, so they're only reachable from under the body. Walking the chip's
reachable perimeter counter-clockwise from the control end gives OUT0..OUT15, so mapping each driver's columns
right-to-left onto OUT0, OUT1, ... is planar:
  - right group (up to 8 columns): column -> down to a lane in the band above the chip -> left/right to its
    top pin -> down onto the pad;
  - left group: column -> lane -> to a bundle just left of the chip -> down to a lane in the corridor between
    the pad rows -> right to its bottom pin -> down onto the pad's inner end.
Lane depths come from a constraint graph (a route whose vertical passes through another's horizontal span must
turn above it). A cycle, or more lanes than the band holds, is an error rather than a silent DRC failure.
The same column -> output mapping (col_to_out) is used by the schematic generator and the firmware LUT.
"""
import pcbnew

OUT_PIN = {o: 5 + o for o in range(16)}          # TM5020A: OUT0..15 = pins 5..20


def chamfer(pts, c):
    """Replace each 90-degree corner of an orthogonal polyline with a 45-degree segment of leg c (capped at
    0.45 x the shorter neighbouring segment, so nested routes keep their clearance)."""
    if c <= 0 or len(pts) < 3:
        return pts
    seg = lambda a, z: ((z[0] - a[0]) ** 2 + (z[1] - a[1]) ** 2) ** 0.5
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, m, z = pts[i - 1], pts[i], pts[i + 1]
        la, lz = seg(a, m), seg(m, z)
        if la < 1e-9 or lz < 1e-9 or abs((m[0] - a[0]) * (z[0] - m[0]) + (m[1] - a[1]) * (z[1] - m[1])) > 1e-9:
            out.append(m)                                  # not a right angle: keep
            continue
        k = min(c, 0.45 * la, 0.45 * lz)
        out.append((m[0] - (m[0] - a[0]) / la * k, m[1] - (m[1] - a[1]) / la * k))
        out.append((m[0] + (z[0] - m[0]) / lz * k, m[1] + (z[1] - m[1]) / lz * k))
    out.append(pts[-1])
    return out


def lane_depths(routes, near=0.0):
    """routes: {key: dict(x0=start x, x1=end x of the horizontal)} -> {key: depth}, 0 = shallowest lane.
    Each route comes down at x0 to its lane, runs to x1, then goes on down. If b's start vertical lies inside a's
    span, b must turn above a; if b's end vertical lies inside a's span, a must be above b."""
    keys = list(routes)
    above = {k: set() for k in keys}             # above[k] = routes that must be shallower than k
    # "inside" includes verticals closer than one lane pitch (near) to either end: side-by-side verticals clash too
    inside = lambda v, r: min(r["x0"], r["x1"]) - near < v < max(r["x0"], r["x1"]) + near
    for a in keys:
        for b in keys:
            if a == b:
                continue
            if inside(routes[b]["x0"], routes[a]):
                above[a].add(b)
            if inside(routes[b]["x1"], routes[a]):
                above[b].add(a)
    depth, state = {}, {}

    def visit(k):
        if state.get(k) == 1:
            raise RuntimeError(f"fan-in lanes are not planar around {k}")
        if k not in depth:
            state[k] = 1
            depth[k] = 1 + max((visit(b) for b in above[k]), default=-1)
            state[k] = 2
        return depth[k]
    for k in keys:
        visit(k)
    return depth


def fanin(b, fps, col_top, drivers, YS, p, track):
    """col_top: {col: (x, y)} last cathode of each column; drivers: [(ref, [cols left to right])]."""
    mm = pcbnew.ToMM
    W, CL = p["FANIN_W"], p["CLEARANCE"]
    pitch = W + CL
    band_top = YS + p["FANIN_BAND_TOP"]
    report = []
    for ref, cols in drivers:
        fp = fps[ref]
        pad = {int(q.GetNumber()): q for q in fp.Pads()}
        pxy = {n: (mm(q.GetPosition().x), mm(q.GetPosition().y)) for n, q in pad.items()}
        half = lambda n: mm(pad[n].GetBoundingBox().GetHeight()) / 2
        yc = mm(fp.GetPosition().y)
        assert pxy[1][0] > pxy[12][0] and pxy[5][1] < yc < pxy[13][1], f"{ref}: expected control end right, OUT0-7 on top"
        top_outer = min(pxy[n][1] - half(n) for n in range(5, 13))          # top pads' upper ends
        top_inner = max(pxy[n][1] + half(n) for n in range(5, 13))
        bot_inner = min(pxy[n][1] - half(n) for n in range(13, 21))
        left_end = min(mm(pad[n].GetBoundingBox().GetLeft()) for n in (12, 13))
        n = len(cols)
        routes = {}
        for j, c in enumerate(cols, 1):
            from char_variants import col_to_out   # message-sign only
            o = col_to_out(j, n)
            x = col_top[c][0]
            if o < 8:
                routes[c] = dict(out=o, x0=x, x1=pxy[OUT_PIN[o]][0])
            else:                                                            # bundle: OUT8 outermost
                routes[c] = dict(out=o, x0=x, x1=left_end - CL - W / 2 - 0.05 - (15 - o) * pitch)
        depth = lane_depths(routes, near=pitch - 1e-6)
        max_d = max(depth.values())
        lane_y = lambda d: band_top + d * pitch
        assert lane_y(max_d) + W / 2 + CL <= top_outer + 1e-6, \
            f"{ref}: fan-in needs {max_d + 1} lanes, band holds {int((top_outer - CL - W / 2 - band_top) / pitch) + 1}"
        c_lo, c_hi = top_inner + CL + W / 2, bot_inner - CL - W / 2           # corridor between the pad rows
        n_bot = sum(1 for r in routes.values() if r["out"] >= 8)
        assert n_bot == 0 or c_lo + (n_bot - 1) * pitch <= c_hi + 1e-6, f"{ref}: corridor too narrow"
        for c, r in routes.items():
            x, y = col_top[c]
            net = pad[OUT_PIN[r["out"]]].GetNet()
            yl = lane_y(depth[c])
            pts = [(x, y), (x, yl), (r["x1"], yl)]
            px, py = pxy[OUT_PIN[r["out"]]]
            if r["out"] < 8:
                pts.append((px, py))                                           # onto the top pad
            else:                                                              # OUT8 lowest corridor lane
                yk = c_hi - (r["out"] - 8) * pitch
                pts += [(r["x1"], yk), (px, yk), (px, py)]
            pts = [q for i, q in enumerate(pts) if i == 0 or q != pts[i - 1]]
            pts = chamfer(pts, p["FANIN_CHAMFER"])
            for a, z in zip(pts, pts[1:]):
                track(a, z, W, pcbnew.F_Cu, net)
        report.append(f"{ref}: {n} cols, {max_d + 1} lanes")
    return report


# ---- GND stitching ----------------------------------------------------------------------------------------
def _seg_dist(p, a, z):
    ax, ay = a; zx, zy = z; px, py = p
    dx, dy = zx - ax, zy - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return ((px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2) ** 0.5


def _seg_seg(a, z, c, d):
    """Distance between segments az and cd (0 if they cross)."""
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2, o3, o4 = orient(a, z, c), orient(a, z, d), orient(c, d, a), orient(c, d, z)
    if (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0) and 0 not in (o1, o2, o3, o4):
        return 0.0
    return min(_seg_dist(a, c, d), _seg_dist(z, c, d), _seg_dist(c, a, z), _seg_dist(d, a, z))


def _seg_rect(a, z, r):
    """Exact distance between segment az and axis-aligned rectangle r (0 if they touch)."""
    x0, y0, x1, y1 = r
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in (a, z)):
        return 0.0
    edges = list(zip(corners, corners[1:] + corners[:1]))
    return min(min(_seg_seg(a, z, c, d) for c, d in edges), _rect_dist(a, r), _rect_dist(z, r))


def _rect_dist(p, r):
    x0, y0, x1, y1 = r
    dx = max(x0 - p[0], 0, p[0] - x1); dy = max(y0 - p[1], 0, p[1] - y1)
    return (dx * dx + dy * dy) ** 0.5


class Copper:
    """Just enough geometry to place a via + stub without asking DRC: pads as rectangles, tracks as capsules,
    vias as discs, per copper layer, tagged with net names; bucketed on a 1 mm grid for fast lookups."""
    B = 1.0

    def __init__(self, b, hole_pitch=0.55):
        mm = pcbnew.ToMM
        self.hole_pitch = hole_pitch                         # drill 0.25 + hole-to-hole 0.25, plus margin
        self.via_pad_clr = 0.15
        self.items, self.buckets = [], {}                    # items: (layers, kind, geometry, net)
        for fp in b.GetFootprints():
            for q in fp.Pads():
                r = q.GetBoundingBox()
                layers = {l for l in (pcbnew.F_Cu, pcbnew.B_Cu) if q.IsOnLayer(l)}
                self._add((layers, "rect", (mm(r.GetLeft()), mm(r.GetTop()), mm(r.GetRight()), mm(r.GetBottom())), q.GetNetname()))
        for t in b.GetTracks():
            if t.Type() == pcbnew.PCB_VIA_T:
                self.add_via((mm(t.GetPosition().x), mm(t.GetPosition().y)), mm(t.GetWidth(pcbnew.F_Cu)) / 2, t.GetNetname())
            else:
                self.add_track((mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y)),
                               mm(t.GetWidth()) / 2, t.GetLayer(), t.GetNetname())

    @staticmethod
    def _bbox(kind, g):
        if kind == "rect":
            return g
        if kind == "disc":
            (x, y), r = g
            return (x - r, y - r, x + r, y + r)
        (ax, ay), (zx, zy), hw = g
        return (min(ax, zx) - hw, min(ay, zy) - hw, max(ax, zx) + hw, max(ay, zy) + hw)

    def _keys(self, bb, pad=0.0):
        B = self.B
        return [(i, j) for i in range(int((bb[0] - pad) // B), int((bb[2] + pad) // B) + 1)
                for j in range(int((bb[1] - pad) // B), int((bb[3] + pad) // B) + 1)]

    def _add(self, it):
        self.items.append(it)
        for k in self._keys(self._bbox(it[1], it[2])):
            self.buckets.setdefault(k, []).append(len(self.items) - 1)

    def add_via(self, c, r, net):
        self._add(("all", "disc", (c, r), net))

    def add_track(self, a, z, hw, layer, net):
        self._add(({layer}, "seg", (a, z, hw), net))

    def near(self, kind, g, pad):
        seen = set()
        for k in self._keys(self._bbox(kind, g), pad):
            for i in self.buckets.get(k, ()):
                if i not in seen:
                    seen.add(i)
                    yield self.items[i]

    def clear(self, shape, layers, net, clr):
        """shape: ('disc', (c, r)) or ('seg', (a, z, hw)); True if clr from all other-net copper on layers."""
        kind, g = shape
        for ils, ik, ig, inet in self.near(kind, g, max(clr, self.hole_pitch) + 0.05):
            if kind == "disc" and ik == "rect" and inet == net:        # no via in or touching any pad, same net too
                if _rect_dist(g[0], ig) - g[1] < self.via_pad_clr:
                    return False
                continue
            if kind == "disc" and ik == "disc" and inet == net:        # same-net vias still need hole spacing
                if ((g[0][0] - ig[0][0]) ** 2 + (g[0][1] - ig[0][1]) ** 2) ** 0.5 < self.hole_pitch:
                    return False
                continue
            if inet == net or (ils != "all" and layers != "all" and not (ils & layers)):
                continue
            if kind == "disc":
                c, r = g
                if ik == "rect":
                    d = _rect_dist(c, ig) - r
                elif ik == "disc":
                    d = ((c[0] - ig[0][0]) ** 2 + (c[1] - ig[0][1]) ** 2) ** 0.5 - r - ig[1]
                else:
                    d = _seg_dist(c, ig[0], ig[1]) - r - ig[2]
            else:
                a, z, hw = g
                if ik == "rect":
                    d = _seg_rect(a, z, ig) - hw
                elif ik == "disc":
                    d = _seg_dist(ig[0], a, z) - hw - ig[1]
                else:
                    d = _seg_seg(a, z, ig[0], ig[1]) - hw - ig[2]
            if d < clr - 1e-6:
                return False
        return True


def stitch_gnd(b, fps, p, area, track, via, skip=lambda ref: False):
    """Give every GND pad (outside `skip`) a via to the inner GND planes: try spots around the pad, outward
    from its footprint first, and keep the first one clear of other-net copper on F/B/In2 and inside `area`."""
    mm = pcbnew.ToMM
    cu = Copper(b)
    cu.via_pad_clr = p.get("VIA_PAD_CLR", 0.15)
    vr, clr = p["VIA"][0] / 2, p["CLEARANCE"]
    stub_w = p["GND_STUB_W"]
    placed, failed = 0, []
    for ref, fp in sorted(fps.items()):
        if skip(ref):
            continue
        fx, fy = mm(fp.GetPosition().x), mm(fp.GetPosition().y)
        for q in fp.Pads():
            if q.GetNetname() != "GND":
                continue
            layer = pcbnew.B_Cu if q.IsOnLayer(pcbnew.B_Cu) else pcbnew.F_Cu
            px, py = mm(q.GetPosition().x), mm(q.GetPosition().y)
            bb = q.GetBoundingBox()
            hw, hh = mm(bb.GetWidth()) / 2, mm(bb.GetHeight()) / 2
            ox, oy = px - fx, py - fy                       # outward from the footprint centre
            n = (ox * ox + oy * oy) ** 0.5 or 1.0
            r2 = 0.5 ** 0.5
            dirs = [(ox / n, oy / n), (0, -1), (0, 1), (-1, 0), (1, 0),
                    (r2, r2), (-r2, r2), (r2, -r2), (-r2, -r2), (-ox / n, -oy / n)]
            ok = False
            for gap in (0.25, 0.5, 0.9, 1.4):
                for dx, dy in dirs:
                    reach = abs(dx) * hw + abs(dy) * hh + vr + gap
                    c = (px + dx * reach, py + dy * reach)
                    if not (area[0] + vr <= c[0] <= area[2] - vr and area[1] + vr <= c[1] <= area[3] - vr):
                        continue
                    if not cu.clear(("disc", (c, vr)), "all", "GND", clr):
                        continue
                    edge = (px + dx * (reach - vr), py + dy * (reach - vr))
                    if not cu.clear(("seg", ((px, py), c, stub_w / 2)), {layer}, "GND", clr):
                        continue
                    via(c, q.GetNet()); track((px, py), c, stub_w, layer, q.GetNet())
                    cu.add_via(c, vr, "GND"); cu.add_track((px, py), c, stub_w / 2, layer, "GND")
                    ok = True
                    break
                if ok:
                    break
            if ok:
                placed += 1
            else:
                failed.append(f"{ref}.{q.GetNumber()}")
    return placed, failed


# ---- escape vias --------------------------------------------------------------------------------------------
def escape_pins(fps, p):
    """Front pins whose net must leave the front copper (to the In2 bus or the back): [(ref, pin)].
    Drivers: data in/out, CLK, LE, OE, VDD. '595: SER, SRCLK, RCLK, VCC, ~SRCLR, row outputs.
    '245: the A inputs used, VCC, DIR; its outputs leave after the 33R (R101.. pin 2)."""
    pins = []
    for i in range(p["DRIVERS"]):
        pins += [(f"U20{i + 1}", n) for n in ("2", "3", "4", "21", "22", "24")]
    if p["ROW_SELECT"] == "595":
        pins += [("U204", n) for n in ("14", "11", "12", "16", "10")]
        pins += [("U204", n) for n in ("15", "1", "2", "3", "4", "5", "6", "7")[:p["ROWS"]]]
    n_used = sum(1 for r in range(101, 108) if f"R{r}" in fps)
    pins += [("U101", str(2 + i)) for i in range(n_used)] + [("U101", "20"), ("U101", "1")]
    pins += [(f"R{101 + i}", "2") for i in range(n_used)]
    return [(r, n) for r, n in pins if r in fps]


def back_escape_pins(fps, p):
    """Back pins whose net must reach In2 or the front: FET gates and drains, R204 (OE, +3V3), the +3V3 out of
    the ferrite, and the SIG connectors' signal pins (1 GND, 2 CLK, 3 GND, 4 DATA, 5 LE, 6 OE)."""
    pins = []
    for r in range(1, p["ROWS"] + 1):
        pins += [(f"Q20{r}", "1"), (f"Q20{r}", "3")]
    pins += [("R204", "1"), ("R204", "2"), ("FB101", "2")]
    for j in ("J101", "J102"):
        pins += [(j, n) for n in ("2", "4", "5", "6")]
    return [(r, n) for r, n in pins if r in fps]


def escape_vias(b, fps, p, area, track, via, commit=True, radius=6.0, step=0.25, pins=None, layer=None):
    """A via for every escape pin: the nearest grid spot within `radius` whose via is clear of other-net copper
    on all layers and whose straight F.Cu stub from the pad is clear. The most constrained pin goes first;
    after each placement only the neighbours' candidate lists are re-checked. Returns (placed, failed)."""
    mm = pcbnew.ToMM
    cu = Copper(b)
    cu.via_pad_clr = p.get("VIA_PAD_CLR", 0.15)
    vr, clr, sw = p["VIA"][0] / 2, p["CLEARANCE"], p["ESCAPE_W"]
    layer = pcbnew.F_Cu if layer is None else layer
    ok = lambda net, pxy, c: (cu.clear(("disc", (c, vr)), "all", net, clr)
                              and cu.clear(("seg", (pxy, c, sw / 2)), {layer}, net, clr))
    todo = []
    for ref, n in (escape_pins(fps, p) if pins is None else pins):
        q = next(q for q in fps[ref].Pads() if q.GetNumber() == n)
        if q.GetNetname() and not q.GetNetname().startswith("unconnected"):
            todo.append([ref, n, q, (mm(q.GetPosition().x), mm(q.GetPosition().y)), None])
    k = int(radius / step)
    for it in todo:
        px, py = it[3]
        cands = []
        for ix in range(-k, k + 1):
            for iy in range(-k, k + 1):
                c = (px + ix * step, py + iy * step)
                d = ((c[0] - px) ** 2 + (c[1] - py) ** 2) ** 0.5
                if 0.5 <= d <= radius and area[0] + vr <= c[0] <= area[2] - vr and area[1] + vr <= c[1] <= area[3] - vr:
                    cands.append((d, c))
        it[4] = sorted(x for x in cands if ok(it[2].GetNetname(), it[3], x[1]))
    placed, failed = {}, []
    while todo:
        todo.sort(key=lambda it: len(it[4]))
        ref, n, q, pxy, cands = todo.pop(0)
        if not cands:
            failed.append(f"{ref}.{n} ({q.GetNetname().split('/')[-1]})")
            continue
        c = cands[0][1]
        placed[(ref, n)] = c
        cu.add_via(c, vr, q.GetNetname()); cu.add_track(pxy, c, sw / 2, layer, q.GetNetname())
        if commit:
            via(c, q.GetNet()); track(pxy, c, sw, layer, q.GetNet())
        for it in todo:                                  # re-check only candidates near the new via and stub
            if abs(it[3][0] - c[0]) < 2 * radius + 1 and abs(it[3][1] - c[1]) < 2 * radius + 1:
                it[4] = [x for x in it[4] if ok(it[2].GetNetname(), it[3], x[1])]
    return placed, failed


# ---- maze router: complete nets -----------------------------------------------------------------------------
import heapq, math, os as _os, re as _re, time as _time
_VERBOSE, _T0 = bool(_os.environ.get("ROUTE_VERBOSE")), _time.time()


class Grid:
    """0.1 mm routing grid over `area` for one copper layer. Each cell keeps (net, distance) for nearby copper,
    so one raster serves every track width: a cell is blocked for (net, half-width) if other-net copper is closer
    than clearance + half-width."""
    def __init__(self, cu, layer, area, g=0.1, reach=0.8, outline=None, edge_clr=0.3):
        self.layer, self.area, self.g, self.reach = layer, area, g, reach
        self.outline, self.edge_clr = outline, edge_clr
        self.nx = int((area[2] - area[0]) / g) + 1
        self.ny = int((area[3] - area[1]) / g) + 1
        self.near = {}                                   # cell -> list[(net, dist)]
        self.keepout = []                                # (rect, allowed_net)
        for ils, ik, ig, inet in cu.items:
            if ils == "all" or layer in ils:
                self.add(ik, ig, inet)

    def xy(self, i, j):
        return (self.area[0] + i * self.g, self.area[1] + j * self.g)

    def add(self, kind, geom, net):
        x0, y0, x1, y1 = Copper._bbox(kind, geom)
        r, g, A = self.reach, self.g, self.area
        for i in range(max(0, int((x0 - r - A[0]) / g)), min(self.nx, int((x1 + r - A[0]) / g) + 2)):
            for j in range(max(0, int((y0 - r - A[1]) / g)), min(self.ny, int((y1 + r - A[1]) / g) + 2)):
                p = self.xy(i, j)
                if kind == "rect":
                    d = _rect_dist(p, geom)
                elif kind == "disc":
                    d = math.hypot(p[0] - geom[0][0], p[1] - geom[0][1]) - geom[1]
                else:
                    d = _seg_dist(p, geom[0], geom[1]) - geom[2]
                if d < r:
                    self.near.setdefault((i, j), []).append((net, d))

    def blocked(self, c, net, need, hw=0.0):
        for n, d in self.near.get(c, ()):
            if n != net and d < need:
                return True
        p = self.xy(*c)
        if self.outline:                                     # copper-to-edge: centre + half-width + clearance
            o, e = self.outline, self.edge_clr + hw
            if len(o) == 3:                                  # round board: (cx, cy, r)
                if math.hypot(p[0] - o[0], p[1] - o[1]) > o[2] - e:
                    return True
            elif p[0] < o[0] + e or p[0] > o[2] - e or p[1] < o[1] + e or p[1] > o[3] - e:
                return True
        for (x0, y0, x1, y1), allowed in self.keepout:
            if allowed != net and x0 <= p[0] <= x1 and y0 <= p[1] <= y1:
                return True
        return False

    def inside(self, c, net):
        return any(n == net and d <= 0 for n, d in self.near.get(c, ()))


DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def astar(grid, net, need, sources, targets, max_expand=400000, turn=0.6):
    """Multi-source A* on 8-connected cells; returns the cell path from a source to a target, or None."""
    tlist = list(targets)
    if not tlist:
        return None
    tx = [c[0] for c in tlist]; ty = [c[1] for c in tlist]
    bx0, bx1, by0, by1 = min(tx), max(tx), min(ty), max(ty)
    h = lambda c: hweight * math.hypot(max(bx0 - c[0], 0, c[0] - bx1), max(by0 - c[1], 0, c[1] - by1))
    openq, best, parent = [], {}, {}
    for s in sources:
        best[(s, -1)] = 0.0
        heapq.heappush(openq, (h(s), 0.0, s, -1))
    n = 0
    while openq and n < max_expand:
        f, gc, c, di = heapq.heappop(openq)
        if gc > best.get((c, di), 1e18):
            continue
        n += 1
        if c in targets:
            path = [c]
            k = (c, di)
            while k in parent:
                k = parent[k]
                path.append(k[0])
            return path[::-1]
        for d, (dx, dy) in enumerate(DIRS):
            nc = (c[0] + dx, c[1] + dy)
            if not (0 <= nc[0] < grid.nx and 0 <= nc[1] < grid.ny):
                continue
            if nc not in targets and grid.blocked(nc, net, need):
                continue
            if dx and dy and (grid.blocked((c[0] + dx, c[1]), net, need) or grid.blocked((c[0], c[1] + dy), net, need)):
                continue                                     # no corner cutting past an obstacle
            ng = gc + (1.4142 if dx and dy else 1.0) + (turn if di not in (-1, d) else 0.0)
            if ng < best.get((nc, d), 1e18):
                best[(nc, d)] = ng
                parent[(nc, d)] = (c, di)
                heapq.heappush(openq, (ng + h(nc), ng, nc, d))
    return None


def astar_ml(grids, layers, net, need, hw, sources, targets, via_ok, via_cost=6.0, layer_cost=None,
             corridor=None, max_expand=600000, turn=0.6, hweight=1.0):
    """A* over (cell, layer): 8-connected moves within a layer, or a via to another allowed layer where via_ok.
    sources/targets: sets of (cell, layer). corridor: (i0, j0, i1, j1) cell bounds. Returns [(cell, layer)]."""
    layer_cost = layer_cost or {L: 1.0 for L in layers}
    tl = list(targets)
    if not tl:
        return None
    bx0 = min(t[0][0] for t in tl); bx1 = max(t[0][0] for t in tl)
    by0 = min(t[0][1] for t in tl); by1 = max(t[0][1] for t in tl)
    h = lambda c: math.hypot(max(bx0 - c[0], 0, c[0] - bx1), max(by0 - c[1], 0, c[1] - by1))
    G0 = grids[layers[0]]
    i0, j0, i1, j1 = corridor or (0, 0, G0.nx - 1, G0.ny - 1)
    openq, best, parent = [], {}, {}
    for s_ in sources:
        best[(s_, -1)] = 0.0
        heapq.heappush(openq, (h(s_[0]), 0.0, s_, -1))
    n = 0
    while openq and n < max_expand:
        f, gc, st, di = heapq.heappop(openq)
        if gc > best.get((st, di), 1e18):
            continue
        n += 1
        if st in targets:
            path, k = [st], (st, di)
            while k in parent:
                k = parent[k]
                path.append(k[0])
            return path[::-1]
        c, L = st
        G = grids[L]
        for d, (dx, dy) in enumerate(DIRS):
            nc = (c[0] + dx, c[1] + dy)
            if not (i0 <= nc[0] <= i1 and j0 <= nc[1] <= j1):
                continue
            ns = (nc, L)
            if G.blocked(nc, net, need, hw):                 # targets too: a wide track must clear neighbours
                continue
            if dx and dy and (G.blocked((c[0] + dx, c[1]), net, need, hw) or G.blocked((c[0], c[1] + dy), net, need, hw)):
                continue
            ng = gc + (1.4142 if dx and dy else 1.0) * layer_cost[L] + (turn if di not in (-1, d) else 0.0)
            if ng < best.get((ns, d), 1e18):
                best[(ns, d)] = ng
                parent[(ns, d)] = (st, di)
                heapq.heappush(openq, (ng + h(nc), ng, ns, d))
        if via_ok(c):
            for L2 in layers:
                if L2 != L and not grids[L2].blocked(c, net, need, hw):   # the track leaving the via must clear too
                    ns = (c, L2)
                    ng = gc + via_cost
                    if ng < best.get((ns, -1), 1e18):
                        best[(ns, -1)] = ng
                        parent[(ns, -1)] = (st, di)
                        heapq.heappush(openq, (ng + h(c), ng, ns, -1))
    return None


def _route_once(Gs, layers, net, clr, width, src, tgt, via_ok, G0, p):
    """p["QUICK"]: give up early (corridors of 4 and 12 mm, 250k expansions each, no whole-board search), so a hard
    connection fails in seconds and is left for hand routing. p["HWEIGHT"] > 1 makes the A* greedier (weighted
    heuristic): far fewer expansions, paths slightly longer than optimal."""
    allc = [s_[0] for s_ in src] + [t[0] for t in tgt]
    quick = p.get("QUICK", False)
    for m in ((40, 120) if quick else (40, 120, None)):  # corridor margin in cells, widening on failure
        cor = None if m is None else (max(0, min(c[0] for c in allc) - m), max(0, min(c[1] for c in allc) - m),
                                      min(G0.nx - 1, max(c[0] for c in allc) + m), min(G0.ny - 1, max(c[1] for c in allc) + m))
        path = astar_ml(Gs, layers, net, clr + width / 2 + 0.02, width / 2, src, tgt, via_ok,
                        layer_cost={L: (p["IN1_COST"] if L == pcbnew.In1_Cu else 1 + 0.25 * k) for k, L in enumerate(layers)},
                        corridor=cor, max_expand=250000 if quick else (600000 if m else 3000000),
                        hweight=p.get("HWEIGHT", 1.0))
        if path:
            return path
    return None


def _simplify(path):
    pts = [path[0]]
    for k in range(1, len(path) - 1):
        a, m, z = pts[-1], path[k], path[k + 1]
        if (m[0] - a[0]) * (z[1] - m[1]) != (m[1] - a[1]) * (z[0] - m[0]):
            pts.append(m)
    pts.append(path[-1])
    return pts


def net_components(b, net_name, exclude):
    """Connected groups of a net's copper (pads, vias, tracks); zones ignored. Returns list of item lists."""
    mm = pcbnew.ToMM
    items = []
    for fp in b.GetFootprints():
        for q in fp.Pads():
            if q.GetNetname() == net_name and (fp.GetReference(), q.GetNumber()) not in exclude:
                r = q.GetBoundingBox()
                ls = {l for l in (pcbnew.F_Cu, pcbnew.B_Cu) if q.IsOnLayer(l)}
                items.append((ls, "rect", (mm(r.GetLeft()), mm(r.GetTop()), mm(r.GetRight()), mm(r.GetBottom()))))
    for t in b.GetTracks():
        if t.GetNetname() != net_name:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            items.append(("all", "disc", ((mm(t.GetPosition().x), mm(t.GetPosition().y)), mm(t.GetWidth(pcbnew.F_Cu)) / 2)))
        else:
            items.append(({t.GetLayer()}, "seg", ((mm(t.GetStart().x), mm(t.GetStart().y)),
                                                  (mm(t.GetEnd().x), mm(t.GetEnd().y)), mm(t.GetWidth()) / 2)))
    par = list(range(len(items)))
    find = lambda k: k if par[k] == k else find(par[k])

    def dist(a, z):
        (la, ka, ga), (lz, kz, gz) = a, z
        if la != "all" and lz != "all" and not (la & lz):
            return 1.0
        if ka == "seg" and kz == "seg":
            return _seg_seg(ga[0], ga[1], gz[0], gz[1]) - ga[2] - gz[2]
        if ka == "rect" and kz == "rect":
            return 0.0 if (ga[0] <= gz[2] and gz[0] <= ga[2] and ga[1] <= gz[3] and gz[1] <= ga[3]) else 1.0
        if kz == "rect":
            a, z = z, a; (la, ka, ga), (lz, kz, gz) = a, z
        if ka == "rect":
            return (_rect_dist(gz[0], ga) - gz[1]) if kz == "disc" else (_seg_rect(gz[0], gz[1], ga) - gz[2])
        if ka == "disc" and kz == "disc":
            return math.hypot(ga[0][0] - gz[0][0], ga[0][1] - gz[0][1]) - ga[1] - gz[1]
        if ka == "seg":
            a, z = z, a; (la, ka, ga), (lz, kz, gz) = a, z
        return _seg_dist(ga[0], gz[0], gz[1]) - ga[1] - gz[2]
    for i in range(len(items)):
        for k in range(i + 1, len(items)):
            if find(i) != find(k) and dist(items[i], items[k]) <= 1e-3:
                par[find(i)] = find(k)
    groups = {}
    for i, it in enumerate(items):
        groups.setdefault(find(i), []).append(it)
    return list(groups.values())


def complete_nets(b, p, area, plan, track, via_fn, exclude=frozenset(), keepouts=(), outline=None):
    """plan: [(net regex, [layer ids in preference order], width)]. For each matching net, join its copper groups
    one at a time: A* from the growing tree to the nearest other group, trying the layers in order.
    Returns (routed connections, [unrouted net names])."""
    cu = Copper(b)
    cu.via_pad_clr = p.get("VIA_PAD_CLR", 0.15)
    clr = p["CLEARANCE"]
    grids = {}

    def grid(layer):
        if layer not in grids:
            grids[layer] = Grid(cu, layer, area, outline=outline, edge_clr=p["EDGE_CLR"])
            for rect, allowed, lyr in keepouts:
                if lyr == layer:
                    grids[layer].keepout.append((rect, allowed))
        return grids[layer]
    names = sorted({n.GetNetname() for n in b.GetNetsByNetcode().values() if n.GetNetname()})
    done, failed = 0, []
    for pattern, layers, width in plan:
        for net in [n for n in names if _re.fullmatch(pattern, n)]:
            groups = net_components(b, net, exclude)
            if len(groups) < 2:
                continue
            netobj = b.FindNet(net)
            tree, rest = groups[0], groups[1:]
            while rest:
                routed = False
                Gs = {L: grid(L) for L in layers}
                G0 = Gs[layers[0]]
                src, tgt = set(), {}
                ax = p.get("AXIAL_PADS", False)
                for L in layers:
                    src |= {(c, L) for it in tree if it[0] == "all" or L in it[0] for c in _cells(Gs[L], it, ax)}
                    for gi, grp in enumerate(rest):
                        for it in grp:
                            if it[0] == "all" or L in it[0]:
                                for c in _cells(Gs[L], it, ax):
                                    tgt[(c, L)] = gi
                vr = p["VIA"][0] / 2
                vcache = {}

                def via_ok(c):
                    if c not in vcache:
                        xy = G0.xy(*c)
                        vcache[c] = all(not grid(L).blocked(c, net, clr + vr + 0.02, vr)
                                        for L in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu)) and \
                            cu.clear(("disc", (xy, vr)), "all", net, clr)
                    return vcache[c]
                path = None
                w_used = width
                for w_try in (width, max(0.3, round(width * 0.6, 2)), 0.2):   # neck down onto small pins
                    if w_try > width or (p.get("QUICK") and w_try not in (width, 0.2)):
                        continue
                    w_used = w_try
                    path = _route_once(Gs, layers, net, clr, w_try, src, tgt, via_ok, G0, p) if src and tgt else None
                    if path:
                        break
                        if path:
                            break
                if path:
                    def centre(items, st):                       # pad / via centre of the item holding this cell
                        xy, L = Gs[st[1]].xy(*st[0]), st[1]
                        for ls, k, g in items:
                            if ls != "all" and L not in ls:
                                continue
                            if k == "rect" and g[0] <= xy[0] <= g[2] and g[1] <= xy[1] <= g[3]:
                                return ((g[0] + g[2]) / 2, (g[1] + g[3]) / 2)
                            if k == "disc" and math.hypot(xy[0] - g[0][0], xy[1] - g[0][1]) <= g[1]:
                                return g[0]
                        return None
                    c_start = centre(tree, path[0])
                    c_end = centre(rest[tgt[path[-1]]], path[-1])
                    runs, cur = [], [path[0]]
                    for st in path[1:]:
                        if st[1] != cur[-1][1]:
                            runs.append(cur); cur = [st]
                            xy = G0.xy(*st[0])
                            via_fn(xy, netobj)
                            cu.add_via(xy, vr, net)
                            for gr in grids.values():
                                gr.add("disc", (xy, vr), net)
                            tree.append(("all", "disc", (xy, vr)))
                        else:
                            cur.append(st)
                    runs.append(cur)
                    def lay(a, z, w, L):
                        track(a, z, w, L, netobj)
                        seg = (a, z, w / 2)
                        cu.add_track(a, z, w / 2, L, net)
                        grids[L].add("seg", seg, net)
                        tree.append(({L}, "seg", seg))

                    def to_centre(a, c, L):                      # finish exactly on the pad / via centre, necked if needed
                        if not c or math.hypot(a[0] - c[0], a[1] - c[1]) < 1e-6:
                            return
                        for w in (w_used, max(0.2, round(w_used * 0.6, 2)), 0.2):
                            if cu.clear(("seg", (a, c, w / 2)), {L}, net, clr):
                                lay(a, c, w, L)
                                return
                    for ri, run in enumerate(runs):
                        L = run[0][1]
                        pts = [Gs[L].xy(*c) for c in _simplify([st[0] for st in run])]
                        pts = [q for i, q in enumerate(pts) if i == 0 or q != pts[i - 1]]
                        for a, z in zip(pts, pts[1:]):
                            lay(a, z, w_used, L)
                        if ri == 0:
                            to_centre(pts[0], c_start, L)
                        if ri == len(runs) - 1:
                            to_centre(pts[-1], c_end, L)
                    tree += rest.pop(tgt[path[-1]])
                    done += 1
                    routed = True
                if _VERBOSE:
                    print(f"   {_time.time() - _T0:6.1f}s {net}: {'ok' if routed else 'FAILED'} ({len(rest)} groups left)", flush=True)
                if not routed:                               # this tree is stuck: keep it, grow a new one
                    failed.append(net)
                    tree, rest = rest[0], rest[1:]
    return done, failed


def _cells(G, it, axial=False):
    """Grid cells lying inside an item's copper (with a small inset), for A* sources/targets.
    axial: for pads, only cells on the pad's long centre line (both lines for a square pad), so a route enters along
    the axis and its last segment to the pad centre stays inside the pad: every track then ends on the centre."""
    ls, kind, geom = it
    x0, y0, x1, y1 = Copper._bbox(kind, geom)
    out, g, A = [], G.g, G.area
    cx, cy, wx, wy = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    for i in range(max(0, int((x0 - A[0]) / g)), min(G.nx, int((x1 - A[0]) / g) + 2)):
        for j in range(max(0, int((y0 - A[1]) / g)), min(G.ny, int((y1 - A[1]) / g) + 2)):
            p = G.xy(i, j)
            if kind == "rect":
                ok = geom[0] + 0.05 <= p[0] <= geom[2] - 0.05 and geom[1] + 0.05 <= p[1] <= geom[3] - 0.05
                if ok and axial:
                    on_h = abs(p[1] - cy) <= g * 0.51 and wx >= wy * 0.9    # horizontal centre line (wide pad)
                    on_v = abs(p[0] - cx) <= g * 0.51 and wy >= wx * 0.9    # vertical centre line (tall pad)
                    ok = on_h or on_v
            elif kind == "disc":
                ok = math.hypot(p[0] - geom[0][0], p[1] - geom[0][1]) <= geom[1] - 0.05
            else:
                ok = _seg_dist(p, geom[0], geom[1]) <= geom[2] - 0.02
            if ok:
                out.append((i, j))
    return out


# ---- leftovers -------------------------------------------------------------------------------------------------
def tie_pads(b, p, area, pads, net, layers, width, track, via_fn, outline=None):
    """Route each (ref, pad) of `net` to the nearest existing via of that net (e.g. GND pads the stitcher could not
    serve): one A* per pad, from the pad to any via of the net. Returns (tied, failed)."""
    mm = pcbnew.ToMM
    cu = Copper(b)
    cu.via_pad_clr = p.get("VIA_PAD_CLR", 0.15)
    clr, vr = p["CLEARANCE"], p["VIA"][0] / 2
    Gs = {L: Grid(cu, L, area, outline=outline, edge_clr=p["EDGE_CLR"]) for L in layers}
    G0 = Gs[layers[0]]
    netobj = b.FindNet(net)
    vias = [(("all", "disc", ((mm(t.GetPosition().x), mm(t.GetPosition().y)), mm(t.GetWidth(pcbnew.F_Cu)) / 2)))
            for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == net]
    tied, failed = 0, []
    for ref, num in pads:
        q = next(q for f in b.GetFootprints() if f.GetReference() == ref for q in f.Pads() if q.GetNumber() == num)
        r = q.GetBoundingBox()
        it = ({L for L in layers if q.IsOnLayer(L)}, "rect", (mm(r.GetLeft()), mm(r.GetTop()), mm(r.GetRight()), mm(r.GetBottom())))
        src = {(c, L) for L in it[0] for c in _cells(Gs[L], it)}
        tgt = {(c, L): 0 for L in layers for v in vias for c in _cells(Gs[L], v)}
        path = _route_once(Gs, layers, net, clr, width, src, tgt, lambda c: False, G0, p) if src and tgt else None
        if not path:
            failed.append(f"{ref}.{num}"); continue
        L = path[0][1]
        pts = [Gs[L].xy(*c) for c in _simplify([st[0] for st in path])]
        pc = (mm(q.GetPosition().x), mm(q.GetPosition().y))
        end = min(vias, key=lambda v: math.hypot(v[2][0][0] - pts[-1][0], v[2][0][1] - pts[-1][1]))[2][0]
        pts = [pc] + pts + [end]
        pts = [x for i, x in enumerate(pts) if i == 0 or x != pts[i - 1]]
        for a, z in zip(pts, pts[1:]):
            track(a, z, width, L, netobj)
            cu.add_track(a, z, width / 2, L, net)
            Gs[L].add("seg", (a, z, width / 2), net)
        tied += 1
    return tied, failed
