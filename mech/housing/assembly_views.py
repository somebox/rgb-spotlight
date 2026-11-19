"""The assembly guide's pictures (docs/assembly/img/), drawn from round 7's model.

ROT=45 uv run --python 3.12 --with cadquery --with pillow python assembly_views.py ../../docs/assembly/img [NAME ...]

Each picture is one scene: solids from round7.py and the two boards' STEPs (../out, see README.md), tessellated, drawn
off-screen with VTK through a parallel camera, and numbered with PIL. With names after the folder, only those scenes are
drawn; PNG=1 writes PNGs beside the WebPs.

- A step's picture shows what is already fitted in pale grey and the parts the step adds in colour, pulled out along
  the line they go on by (the thin grey lines).
- The numbers are the guide's part numbers: PART below, the same list as the parts table in docs/assembly/index.html.
- A number's leader ends on a point of its part that the camera sees: the candidates are tested against the depth
  buffer, so a leader never points at a part through another one.
- The colours are a key, not the parts' finish: bare aluminium grey, powder-coated parts dark, steel fasteners orange,
  polyamide blue, boards green. The three "lamp" pictures use colours nearer the real ones.
- Not in the model, and drawn in here from their sizes: the LED leads and their plugs (wire(), PLUG), and the door pins
  as separate screws and nuts (the model fuses each pin with its nut). Where the leads' slack lies is a guess.
"""
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "views"
ONLY = sys.argv[2:]
sys.argv = sys.argv[:1] + ["/dev/null"]             # the round scripts read argv[1] as their output folder on import
import cadquery as cq  # noqa: E402
import numpy as np  # noqa: E402
import vtk  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from vtk.util import numpy_support as ns  # noqa: E402

import round3 as R3  # noqa: E402
import round4 as R4  # noqa: E402
import round7 as R7  # noqa: E402
import sheet as S  # noqa: E402

# part number -> (name, per lamp)
PART = {1: ("shell", 1), 2: ("cap, with its 8 press nuts", 1), 3: ("hood", 1), 4: ("door", 4), 5: ("yoke", 1),
        6: ("plate", 1), 7: ("fin", 4), 8: ("spacer", 8), 9: ("carrier", 1), 10: ("LED board", 1),
        11: ("driver board", 1), 12: ("lens", 3), 13: ("LED lead: XH 2-pin plug on two wires", 3),
        14: ("XH 3-pin header (J1, J2)", 2), 15: ("tie stud M3 x 45", 3), 16: ("washer M3, steel", 3),
        17: ("nut M3, steel", 3), 18: ("standoff M3 x 12, polyamide", 3), 19: ("driver screw M3 x 6, polyamide", 3),
        20: ("screw ISO 7380 M3 x 6 (shell 4, cap 2)", 6), 21: ("LED screw ISO 7380 M3 x 20, black", 3),
        22: ("door pin ISO 7380 M3 x 8", 8), 23: ("nylock nut M3", 8), 24: ("knob M4 x 10", 2),
        25: ("washer M4, steel, 12 mm", 2), 26: ("washer M4, polyamide, 9 mm", 2)}

BG = (0.984, 0.988, 0.976)                          # the page's panel colour, #fbfcf9
INK = (23, 33, 28)
GHOST, GHOST_EDGE = (0.93, 0.94, 0.93), (0.70, 0.72, 0.71)
KEY = {"alu": (0.63, 0.68, 0.75), "coat": (0.21, 0.22, 0.24), "steel": (0.93, 0.45, 0.12), "pa": (0.20, 0.52, 0.86),
       "pcb": (0.17, 0.43, 0.31), "chip": (0.17, 0.17, 0.18), "xh": (0.93, 0.90, 0.80), "mask": (0.93, 0.93, 0.90),
       "led": (0.99, 0.93, 0.62), "lens": (0.66, 0.83, 0.92), "print": (0.33, 0.31, 0.30), "knob": (0.13, 0.13, 0.14),
       "fixed": (0.60, 0.62, 0.65)}
REAL = dict(KEY, steel=(0.72, 0.73, 0.75), pa=(0.92, 0.90, 0.84), print=(0.14, 0.14, 0.15))
KIND = {"shell": "coat", "cap": "coat", "hood": "coat", "door": "coat", "yoke": "coat", "plate": "alu", "fin": "alu",
        "spacer": "alu", "carrier": "print", "lens": "lens", "stud": "steel", "washer3": "steel", "nut3": "steel",
        "screw": "steel", "corner": "steel", "m3": "steel", "pin": "steel", "pinnut": "steel", "washer": "steel",
        "nylon": "pa", "nyscrew": "pa", "washer_pa": "pa", "knob": "knob", "capnuts": "fixed", "drv_pcb": "pcb",
        "drv_parts": "chip", "drv_front": "xh", "drv_back": "xh", "led_pcb": "mask", "led_parts": "led", "plug": "xh"}
WIRE = {"R": (0.80, 0.20, 0.15), "G": (0.15, 0.55, 0.28), "B": (0.16, 0.36, 0.72)}
DIST, DEPTH = 900.0, 320.0                          # camera distance; the depth range kept either side of the focus
PLUG = (7.4, 5.75, 9.8)                             # JST XHP-2: width, depth, length along the wires
# where each LED's wire pair leaves the LED board (the pads' middle, board frame turned by ROT) and its socket's
# middle on the driver's front (J3 red, J4 green, J5 blue: the sockets' bodies in the driver's STEP)
PADS = {c: S.polar(6.2, a + R7.R6.ROT) for c, a in (("R", 90), ("G", 212), ("B", 328))}
SOCKET = {"R": (1.6, 5.0), "G": (-5.2, -1.1), "B": (3.5, -3.9)}


def font(size, bold=True):
    for p, i in (("/System/Library/Fonts/Helvetica.ttc", 1 if bold else 0),
                 ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0)):
        if os.path.exists(p):
            return ImageFont.truetype(p, size, index=i)
    return ImageFont.load_default()


# ---------------------------------------------------------------- meshes
def mesh(solids, tol=0.03, ang=0.2):
    """One triangle mesh (points, triangles) of a solid or a list of solids."""
    vs, ts, n = [], [], 0
    for s in solids if isinstance(solids, (list, tuple)) else [solids]:
        v, t = s.tessellate(tol, ang)
        vs.append(np.array([(p.x, p.y, p.z) for p in v], float).reshape(-1, 3))
        ts.append(np.array(t, np.int64).reshape(-1, 3) + n)
        n += len(v)
    return np.vstack(vs), np.vstack(ts)


def moved(m, by):
    return m[0] + np.array(by, float), m[1]


def polydata(m):
    pts = vtk.vtkPoints()
    pts.SetData(ns.numpy_to_vtk(np.ascontiguousarray(m[0]), deep=True))
    cells = vtk.vtkCellArray()
    cells.SetData(ns.numpy_to_vtkIdTypeArray(np.arange(0, 3 * len(m[1]) + 1, 3, dtype=np.int64), deep=True),
                  ns.numpy_to_vtkIdTypeArray(np.ascontiguousarray(m[1], dtype=np.int64).ravel(), deep=True))
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetPolys(cells)
    clean = vtk.vtkCleanPolyData()                  # the faces' meshes share no points until merged
    clean.SetInputData(pd)
    clean.SetTolerance(1e-5)
    clean.Update()
    return clean.GetOutput()


def group(items):
    out = {}
    for n, s in items:
        out.setdefault(n, []).append(s)
    return out


def board(compound):
    """A board's STEP split into its PCB, its XH sockets (in front of the PCB, behind it) and its other parts."""
    pcb, xh_f, xh_b, rest = [], [], [], []
    solids = compound.Solids()
    zc = max(solids, key=lambda q: q.BoundingBox().xlen).BoundingBox().center.z
    for q in solids:
        b = q.BoundingBox()
        if b.xlen > 40:
            pcb.append(q)
        elif b.zlen > 9:
            (xh_f if b.center.z > zc + 1 else xh_b).append(q)
        else:
            rest.append(q)
    return pcb, xh_f, xh_b, rest


def half(s, side=1):
    """The solid with everything on the camera's side of the plane x = 0 cut away (side +1: x > 0)."""
    lo, hi = sorted((0.0, side * 200.0))
    return s.cut(S.bx((lo, hi), (-200, 200), (-200, 200)))


def door_pins():
    """Each door's two pins as a screw and a nut apiece: [(screw, nut, outward x/y unit vector)], doors in the order
    top, bottom, left, right. Sizes and places as round3.pins(), which fuses them."""
    lug_out, ear_in = R4.WH + R3.LUG_GAP + 1.5, R4.WH - 1.0
    c = {"y": R4.P, "z": R4.ZP}
    top = []
    for sg in (-1, 1):
        screw = (S.cyl("x", *sorted((sg * lug_out, sg * (lug_out - R3.SCREW_L))), c, 3.0)
                 .fuse(S.cyl("x", *sorted((sg * lug_out, sg * (lug_out + R3.HEAD_H))), c, R3.HEAD_D)).clean())
        x0 = min(sg * ear_in, sg * (ear_in - R3.NUT_H))
        nut = (cq.Workplane("YZ").workplane(offset=x0).center(R4.P, R4.ZP).polygon(6, R3.NUT_D).extrude(R3.NUT_H).val()
               .cut(S.cyl("x", x0 - 1, x0 + R3.NUT_H + 1, c, 3.0)))
        top.append((screw, nut, np.array((sg, 0.0, 0.0))))
    out = []
    for deg in (0, 180, 90, 270):
        a = math.radians(deg)
        rot = np.array(((math.cos(a), -math.sin(a), 0), (math.sin(a), math.cos(a), 0), (0, 0, 1)))
        out += [(R4.turn(s, deg), R4.turn(n, deg), rot @ d) for s, n, d in top]
    return out


print("building the model ...", flush=True)
parts = R7.build()
LAMP, HW = group(R7.lamp(parts, 90, 90)), group(R7.hardware())
zc = lambda s: s.BoundingBox().center.z                       # noqa: E731
LAMP["fin"].sort(key=zc, reverse=True)                        # front to back
LAMP["spacer"].sort(key=zc, reverse=True)
SOLID = {n: LAMP[n][0] for n in ("shell", "cap", "hood", "yoke", "plate", "carrier")}
SOLID.update({n: LAMP[n] for n in ("fin", "spacer", "door")})
SOLID.update({n: HW[n] for n in ("lens", "stud", "washer3", "nut3", "nylon", "nyscrew", "screw", "corner", "m3", "knob",
                                 "washer", "washer_pa")})
SOLID["capnuts"] = HW["nut"] + HW["nut_back"]                 # fitted by JLCCNC: drawn with the cap
drv_pcb, drv_front, drv_back, drv_parts = board(HW["drv"][0])
led_pcb, _, _, led_parts = board(HW["led"][0])
SOLID.update({"drv_pcb": drv_pcb, "drv_front": drv_front, "drv_back": drv_back, "drv_parts": drv_parts,
              "led_pcb": led_pcb, "led_parts": led_parts})
PINS = door_pins()
SOLID["pin"], SOLID["pinnut"] = [p[0] for p in PINS], [p[1] for p in PINS]
SOLID["plug"] = S.bx((-PLUG[0] / 2, PLUG[0] / 2), (-PLUG[1] / 2, PLUG[1] / 2), (0, PLUG[2]))
_MESH = {}


def M(name, i=None, cutaway=0):
    """The mesh of a named part (its i-th copy), whole or cut away at x = 0."""
    key = (name, i, cutaway)
    if key not in _MESH:
        s = SOLID[name]
        if i is not None:
            s = s[i]
        elif isinstance(s, list) and name not in ("capnuts", "drv_pcb", "drv_front", "drv_back", "drv_parts", "led_pcb",
                                                  "led_parts"):
            raise KeyError(f"{name} needs an index")
        if cutaway and name in BOARD_LISTS and not name.endswith("pcb"):
            s = [q for q in s if q.BoundingBox().center.x * cutaway < 0.5]      # a board's parts: whole, or left out
        elif cutaway:
            s = [half(q, cutaway) for q in s] if isinstance(s, list) else half(s, cutaway)
        _MESH[key] = mesh(s)
    return _MESH[key]


# ---------------------------------------------------------------- a scene
class Item:
    def __init__(self, m, colour, ghost, alpha):
        self.m, self.colour, self.ghost, self.alpha = m, colour, ghost, alpha


class Scene:
    """Parallel camera with the projection worked out by hand, so numbers can be placed on the picture."""

    def __init__(self, name, size, focal, eye, scale, up=(0, 1, 0), palette=KEY):
        self.name, (self.W, self.H), self.palette = name, size, palette
        self.f = np.array(focal, float)
        e = np.array(eye, float) / np.linalg.norm(eye)
        self.d = -e
        u = np.array(up, float)
        u = u - u.dot(self.d) * self.d
        self.u = u / np.linalg.norm(u)
        self.r = np.cross(self.d, self.u)
        self.pos = self.f + e * DIST
        self.scale = scale                          # half the picture's height, in mm
        self.items, self.lines, self.tubes, self.calls, self.texts = [], [], [], [], []

    # -- projection
    def px(self, p):
        q = np.asarray(p, float) - self.f
        k = (self.H / 2) / self.scale
        return np.stack([self.W / 2 + q @ self.r * k, self.H / 2 - q @ self.u * k], axis=-1)

    def at(self, u, v, w=0.0):
        """The point u mm right of, v mm above and w mm nearer than the focus, as the camera sees it."""
        return self.f + u * self.r + v * self.u - w * self.d

    # -- content
    def add(self, name, i=None, move=(0, 0, 0), ghost=False, alpha=1.0, cutaway=0, colour=None):
        m = name if isinstance(name, tuple) else M(name, i, cutaway)
        kind = None if isinstance(name, tuple) else KIND[name]
        col = colour or (self.palette[kind] if kind else GHOST)
        if kind == "lens":
            alpha = min(alpha, 0.45)
        it = Item(moved(m, move), col, ghost, alpha)
        self.items.append(it)
        return it

    def each(self, name, move=(0, 0, 0), **kw):
        return [self.add(name, i, move, **kw) for i in range(len(SOLID[name]))]

    def boards(self, which, move=(0, 0, 0), ghost=False, back=True, cutaway=0):
        names = ("drv_pcb", "drv_parts", "drv_front") + (("drv_back",) if back else ()) if which == "drv" else \
            ("led_pcb", "led_parts")
        return [self.add(n, move=move, ghost=ghost, cutaway=cutaway) for n in names]

    def line(self, p0, p1):
        self.lines.append((np.array(p0, float), np.array(p1, float)))

    def wire(self, pts, colour, r=1.1):
        self.tubes.append((np.array(pts, float), colour, r))

    def call(self, n, targets, off=(70, -70), near=None):
        self.calls.append((n, targets if isinstance(targets, list) else [targets], off, near))

    def text(self, s, at, off=(0, 0), size=26):
        self.texts.append((s, np.array(at, float), off, size))

    # -- drawing
    def _actor(self, it):
        pd = polydata(it.m)
        nrm = vtk.vtkPolyDataNormals()
        nrm.SetInputData(pd)
        nrm.SetFeatureAngle(35)
        nrm.SplittingOn()
        mp = vtk.vtkPolyDataMapper()
        mp.SetInputConnection(nrm.GetOutputPort())
        a = vtk.vtkActor()
        a.SetMapper(mp)
        p = a.GetProperty()
        p.SetColor(*(GHOST if it.ghost else it.colour))
        p.SetAmbient(0.62 if it.ghost else 0.42)
        p.SetDiffuse(0.42 if it.ghost else 0.66)
        p.SetSpecular(0.03 if it.ghost else 0.16)
        p.SetSpecularPower(25)
        p.SetOpacity(it.alpha)
        fe = vtk.vtkFeatureEdges()
        fe.SetInputData(pd)
        fe.BoundaryEdgesOn()
        fe.FeatureEdgesOn()
        fe.ManifoldEdgesOff()
        fe.NonManifoldEdgesOff()
        fe.SetFeatureAngle(32)
        fe.ColoringOff()
        sil = vtk.vtkPolyDataSilhouette()
        sil.SetInputData(pd)
        sil.SetDirectionToSpecifiedVector()
        sil.SetVector(*self.d)
        sil.BorderEdgesOff()
        both = vtk.vtkAppendPolyData()
        both.AddInputConnection(fe.GetOutputPort())
        both.AddInputConnection(sil.GetOutputPort())
        em = vtk.vtkPolyDataMapper()
        em.SetInputConnection(both.GetOutputPort())
        em.ScalarVisibilityOff()
        e = vtk.vtkActor()
        e.SetMapper(em)
        q = e.GetProperty()
        q.SetColor(*(GHOST_EDGE if it.ghost else tuple(0.42 * c for c in it.colour)))
        q.SetLineWidth(1.6 if it.ghost else 2.0)
        q.SetAmbient(1.0)
        q.SetDiffuse(0.0)
        q.SetOpacity(1.0 if it.alpha == 1.0 else 0.7)
        return a, e

    def _tube(self, p0, p1=None, pts=None, colour=(0.45, 0.47, 0.50), r=0.13, flat=True):
        if pts is None:
            src = vtk.vtkLineSource()
            src.SetPoint1(*p0)
            src.SetPoint2(*p1)
        else:
            vp = vtk.vtkPoints()
            for p in pts:
                vp.InsertNextPoint(*p)
            sp = vtk.vtkParametricSpline()
            sp.SetPoints(vp)
            src = vtk.vtkParametricFunctionSource()
            src.SetParametricFunction(sp)
            src.SetUResolution(120)
        tf = vtk.vtkTubeFilter()
        tf.SetInputConnection(src.GetOutputPort())
        tf.SetRadius(r)
        tf.SetNumberOfSides(14)
        tf.CappingOn()
        mp = vtk.vtkPolyDataMapper()
        mp.SetInputConnection(tf.GetOutputPort())
        a = vtk.vtkActor()
        a.SetMapper(mp)
        a.GetProperty().SetColor(*colour)
        if flat:
            a.GetProperty().SetAmbient(1.0)
            a.GetProperty().SetDiffuse(0.0)
        else:
            a.GetProperty().SetAmbient(0.45)
            a.GetProperty().SetDiffuse(0.65)
        return a

    def render(self):
        ren = vtk.vtkRenderer()
        ren.SetBackground(*BG)
        for it in self.items:
            for a in self._actor(it):
                ren.AddActor(a)
        for p0, p1 in self.lines:
            ren.AddActor(self._tube(p0, p1))
        for pts, colour, r in self.tubes:
            ren.AddActor(self._tube(None, pts=pts, colour=colour, r=r, flat=False))
        kit = vtk.vtkLightKit()
        kit.SetKeyLightIntensity(0.95)
        for warmth in (kit.SetKeyLightWarmth, kit.SetFillLightWarmth, kit.SetHeadLightWarmth, kit.SetBackLightWarmth):
            warmth(0.5)                             # neutral: the kit's default tints pale parts yellow
        kit.AddLightsToRenderer(ren)
        win = vtk.vtkRenderWindow()
        win.SetOffScreenRendering(1)
        win.AddRenderer(ren)
        win.SetSize(self.W, self.H)
        win.SetMultiSamples(8)
        cam = ren.GetActiveCamera()
        cam.SetFocalPoint(*self.f)
        cam.SetPosition(*self.pos)
        cam.SetViewUp(*self.u)
        cam.SetParallelProjection(1)
        cam.SetParallelScale(self.scale)
        cam.SetClippingRange(DIST - DEPTH, DIST + DEPTH)
        win.Render()
        w2i = vtk.vtkWindowToImageFilter()
        w2i.SetInput(win)
        w2i.Update()
        im = w2i.GetOutput()
        rgb = ns.vtk_to_numpy(im.GetPointData().GetScalars()).reshape(self.H, self.W, -1)[::-1, :, :3]
        zb = vtk.vtkFloatArray()
        win.GetZbufferData(0, 0, self.W - 1, self.H - 1, zb)
        self.zbuf = (DIST - DEPTH) + ns.vtk_to_numpy(zb).reshape(self.H, self.W)[::-1] * 2 * DEPTH
        return Image.fromarray(np.ascontiguousarray(rgb))

    def seen(self, pts):
        """Which of the points the camera sees: nothing drawn lies in front of them."""
        xy = np.rint(self.px(pts)).astype(int)
        ok = (xy[:, 0] >= 0) & (xy[:, 0] < self.W) & (xy[:, 1] >= 0) & (xy[:, 1] < self.H)
        depth = (pts - self.pos) @ self.d
        vis = np.zeros(len(pts), bool)
        vis[ok] = np.abs(self.zbuf[xy[ok, 1], xy[ok, 0]] - depth[ok]) < 0.5
        return vis

    def anchor(self, targets, near):
        """A point of the targets that the camera sees: the one nearest `near`, or the middle of what shows."""
        cand = np.vstack([it.m[0][it.m[1]].mean(axis=1) for it in targets])
        if all(it.alpha < 1 for it in targets):               # see-through parts leave no depth: take their near side
            depth = (cand - self.pos) @ self.d
            vis = depth < np.percentile(depth, 25)
        else:
            vis = self.seen(cand)
        if not vis.any():
            print(f"  {self.name}: nothing of a callout's part shows; its leader ends on the part's middle")
            return cand.mean(axis=0)
        cand = cand[vis]
        want = self.px(near) if near is not None else np.median(self.px(cand), axis=0)
        return cand[np.argmin(((self.px(cand) - want) ** 2).sum(axis=1))]

    def save(self):
        img = self.render()
        d = ImageDraw.Draw(img)
        for s, at, off, size in self.texts:
            x, y = self.px(at)
            d.text((x + off[0], y + off[1]), s, fill=INK, font=font(size), anchor="mm", stroke_width=5,
                   stroke_fill=tuple(int(255 * c) for c in BG))
        placed = []
        for n, targets, off, near in self.calls:
            ax, ay = self.px(self.anchor(targets, near))
            placed.append((n, ax, ay, ax + off[0], ay + off[1]))
        for _, ax, ay, lx, ly in placed:
            d.line([(ax, ay), (lx, ly)], fill=INK, width=3)
            d.ellipse([ax - 5, ay - 5, ax + 5, ay + 5], fill=INK)
        for n, _, _, lx, ly in placed:                        # the numbers last, over every leader
            badge(d, n, lx, ly)
        for (x, y, n, qty) in getattr(self, "badges", []):
            badge(d, n, x, y, qty)
        os.makedirs(OUT, exist_ok=True)
        path = os.path.join(OUT, self.name + ".webp")
        img.save(path, quality=84, method=6)
        if os.environ.get("PNG"):
            img.save(os.path.join(OUT, self.name + ".png"))
        print(f"  {self.name}.webp {img.size[0]} x {img.size[1]}, {os.path.getsize(path) // 1000} kB", flush=True)

    # -- a parts sheet: parts laid out side by side, all at the picture's one scale
    def lay(self, n, what, u, v, qty=None):
        """Draw a part (a list of (mesh, kind)) with its middle u mm right of and v mm above the picture's middle, and
        its number and count below it."""
        allv = np.vstack([m[0] for m, _ in what])
        shift = self.at(u, v) - (allv.min(axis=0) + allv.max(axis=0)) / 2
        its = [self.add(m, move=shift, colour=self.palette[k], alpha=0.45 if k == "lens" else 1.0) for m, k in what]
        xy = self.px(np.vstack([it.m[0] for it in its]))
        self.badges = getattr(self, "badges", [])
        self.badges.append((xy[:, 0].min() + 20, xy[:, 1].max() + 36, n, PART[n][1] if qty is None else qty))
        return its


BOARD_LISTS = ("capnuts", "drv_pcb", "drv_front", "drv_back", "drv_parts", "led_pcb", "led_parts")


def badge(d, n, x, y, qty=None):
    r = 23
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255), outline=INK, width=3)
    d.text((x, y + 1), str(n), fill=INK, font=font(25), anchor="mm")
    if qty is not None and qty > 1:
        d.text((x + r + 8, y + 1), f"× {qty}", fill=INK, font=font(24, bold=False), anchor="lm")


# ---------------------------------------------------------------- what the scenes share
RODS = [S.polar(11, a) for a in S.ANG]                        # the three tie rods
LEDSCREW = [S.polar(19, a) for a in R7.R6.ANG6]               # the three LED screws
CORNERS = [(sx * S.CORNER, sy * S.CORNER) for sx in (-1, 1) for sy in (-1, 1)]
STACK = ("fin", "spacer", "stud", "washer3", "nut3", "nylon")


def fitted(sc, names, ghost=True, move=(0, 0, 0), cutaway=0, skip=()):
    """Add whole groups of parts where they sit in the lamp."""
    out = {}
    for n in names:
        if n in ("drv", "led"):
            out[n] = sc.boards(n, move, ghost, cutaway=cutaway)
        elif isinstance(SOLID[n], list) and n not in BOARD_LISTS:
            out[n] = [sc.add(n, i, move, ghost=ghost, cutaway=cutaway if n in CUT else 0)
                      for i in range(len(SOLID[n])) if (n, i) not in skip and
                      not (cutaway and n not in CUT and SOLID[n][i].BoundingBox().center.x * cutaway > 0.5)]
        else:
            out[n] = [sc.add(n, None, move, ghost=ghost, cutaway=cutaway if n in CUT else 0)]
    return out


# what a cutaway cuts at x = 0, with the boards' PCBs; fasteners and other loose parts in front of the plane are left
# out, those on it or behind it are drawn whole
CUT = ("shell", "cap", "hood", "plate", "fin", "spacer", "carrier", "yoke", "lens")


def lead(sc, c, pts, plug_at):
    """An LED lead drawn in: its wire pair as one tube through pts, and its plug with its wire end at plug_at, its
    length running back (-z) from there, towards the driver."""
    sc.wire(pts, WIRE[c])
    m = M("plug")
    return sc.add((m[0] * np.array((1, 1, -1.0)) + np.array(plug_at, float), m[1]), colour=sc.palette["xh"])


# ---------------------------------------------------------------- the scenes
def lamp_views():
    dm = [mesh(s) for _, s in R7.doors(parts["door"], 118, 118)]
    for name, eye, focal, scale in (("lamp-front", (0.80, 0.42, 1.0), (0, -8, -8), 82),
                                    ("lamp-back", (0.85, 0.48, -1.0), (0, 2, -6), 96)):
        if ONLY and name not in ONLY:
            continue
        sc = Scene(name, (1500, 1150), focal, eye, scale, palette=REAL)
        fitted(sc, ("shell", "cap", "capnuts", "hood", "yoke", "plate", "fin", "spacer", "carrier", "lens", "led", "drv",
                    "stud", "washer3", "nut3", "nylon", "nyscrew", "corner", "m3", "knob", "washer", "washer_pa"),
               ghost=False)
        for i in range(3):
            sc.add("screw", i, colour=(0.12, 0.12, 0.13))
        for screw, nut, _ in PINS:
            sc.add(mesh([screw, nut]), colour=REAL["steel"])
        for m in dm:
            sc.add(m, colour=REAL["coat"])
        sc.save()


def lamp_section():
    """The lamp without its doors and yoke, cut through the middle and seen from the right."""
    sc = Scene("lamp-section", (1500, 1080), (0, -1, -20), (1.0, 0.30, 0.42), 58)
    p = fitted(sc, ("shell", "cap", "hood", "plate", "fin", "spacer", "carrier", "lens", "led", "drv", "stud", "washer3",
                    "nut3", "nylon", "nyscrew", "screw", "corner", "m3"), ghost=False, cutaway=1)
    sc.add("capnuts", cutaway=1)
    leads = []
    for c in "RGB":
        x, y = PADS[c]
        sx, sy = SOCKET[c]
        leads.append(lead(sc, c, [(x, y, 4.9), (0.55 * x, 0.55 * y, 6.2), (0.22 * x, 0.22 * y, 3.5),
                                  (0.22 * x, 0.22 * y, -20), (0.3 * sx, 0.3 * sy, -37), (1.5 * sx, 1.5 * sy, -40.5),
                                  (sx, sy, -40.9)], (sx, sy, -41.0)))
    sc.call(3, p["hood"], (-70, -80), near=(0, 38, 10))
    sc.call(1, p["shell"], (-30, -90), near=(0, 31.7, -25))
    sc.call(2, p["cap"], (90, -70), near=(0, 30, -62))
    sc.call(12, p["lens"], (-150, -60), near=(-8, 14, 15))
    sc.call(9, p["carrier"], (-150, 30), near=(0, -22, 12))
    sc.call(10, p["led"], (-150, 120), near=(0, -22, 3.8))
    sc.call(6, p["plate"], (-90, 130), near=(0, -27, 1.5))
    sc.call(7, p["fin"], (-30, 130), near=(0, -29, -16.5))
    sc.call(8, p["spacer"], (30, 150), near=(0, -14, -22.5))
    sc.call(15, p["stud"], (110, 170), near=(0, -11, -30))
    sc.call(18, p["nylon"], (150, 130), near=(0, -11, -45))
    sc.call(11, p["drv"], (170, 60), near=(0, -22, -51.7))
    sc.call(13, leads, (190, -50))
    sc.save()


def step_01():
    sc = Scene("step-01", (1400, 900), (0, 3, -60), (0.50, -0.66, -0.66), 31, up=(0, 0, -1))
    b = sc.boards("drv", back=False)
    j = sc.add("drv_back", move=(0, 0, -14))
    for name, x in (("J2 OUT", 16.45), ("J1 IN", -16.45)):
        sc.line((x, 9.5, -53), (x, 9.5, -74))
        sc.text(name, (x, 9.5, -74), (0, -62), size=30)
    sc.call(11, b[:1], (-150, 70), near=(-8, -19, -52.5))
    sc.call(14, [j], (130, 30), near=(21, 9.5, -70))
    sc.save()


def step_05():
    sc = Scene("step-05", (1400, 900), (0, 0, -20), (0.62, -0.55, -0.62), 46, up=(0, 0, -1))
    p = sc.add("plate")
    st = sc.each("stud", (0, 0, -24))
    for x, y in RODS:
        sc.line((x, y, 0), (x, y, -70))
    sc.call(6, p, (150, 60), near=(20, -8, 0))
    sc.call(15, st, (120, -60), near=(RODS[0][0], RODS[0][1], -50))
    sc.save()


def step_06():
    sc = Scene("step-06", (1200, 1700), (0, 0, -98), (0.66, -0.60, -0.24), 118, up=(0, 0, -1))
    fitted(sc, ("plate", "stud"))
    sp, fn = [], []
    for i in range(4):                                        # two spacers, then a fin, four times
        sp.append(sc.add("spacer", 2 * i, (0, 0, -(8 + 33 * i))))
        sp.append(sc.add("spacer", 2 * i + 1, (0, 0, -(16 + 33 * i))))
        fn.append(sc.add("fin", i, (0, 0, -(25 + 33 * i))))
    w = sc.each("washer3", (0, 0, -134))
    n = sc.each("nut3", (0, 0, -143))
    so = sc.each("nylon", (0, 0, -155))
    for x, y in RODS:
        sc.line((x, y, -42), (x, y, S.STACK_BACK - 172))
    sc.call(8, sp[:1], (-190, 10))
    sc.call(8, sp[1:2], (-190, 10))
    sc.call(7, fn[:1], (190, -40), near=(26, -26, -34))
    sc.call(16, w, (150, 20))
    sc.call(17, n, (150, 0))
    sc.call(18, so, (150, -20))
    sc.save()


def step_07():
    sc = Scene("step-07", (1500, 950), (0, -2, -56), (0.95, 0.50, 0.62), 76)
    back = -82.0
    p = fitted(sc, ("plate",) + STACK, move=(0, 0, back))
    sh = sc.add("shell")
    cs = sc.each("corner", (0, 0, 26))
    for x, y in CORNERS:
        sc.line((x, y, S.ZF + 34), (x, y, S.ZF + 2))
    sc.call(1, sh, (-60, -150), near=(20, 32.5, -30))
    sc.call(20, cs[1:2], (-10, -100))
    sc.call(6, p["plate"], (90, 120), near=(26, -26, back + 3))
    sc.save()


def step_08():
    lift = 25.0
    sc = Scene("step-08", (1300, 1250), (0, 0, -22), (1.0, -0.18, 0.40), 62, up=(0, 0, 1))
    fitted(sc, ("shell", "plate") + STACK + ("corner",), cutaway=1)
    b = sc.boards("led", (0, 0, lift))
    zb = S.T + 1.6 + lift
    plugs = {}
    for c, (bottom, bend) in {"R": (-47.5, 0.0), "G": (-21.0, 7.0), "B": (7.0, 15.0)}.items():
        x, y = PADS[c]
        hx, hy = 0.25 * x, 0.25 * y
        pts = [(x, y, zb + 0.3), (0.6 * x, 0.6 * y, zb + 2.2), (hx, hy, zb - 1.0)]
        if bend:                                              # slack between the board and the plate
            pts += [(hx + bend * 0.5, hy - bend, zb - 9), (hx - bend * 0.3, hy + bend * 0.4, bottom + PLUG[2] + 9)]
        pts += [(hx, hy, bottom + PLUG[2] + 3), (hx, hy, bottom + PLUG[2])]
        plugs[c] = lead(sc, c, pts, (hx, hy, bottom + PLUG[2]))
    sc.line((0, 0, zb - 2), (0, 0, 4))
    sc.call(10, b[:1], (150, -60), near=(0, 22, zb))
    sc.call(13, [plugs["G"]], (190, 10))
    sc.save()


def step_09():
    sc = Scene("step-09", (1300, 1600), (0, 0, 62), (0.55, -0.72, 0.34), 96, up=(0, 0, 1))
    fitted(sc, ("shell", "plate", "led", "corner"))
    ca = sc.add("carrier", move=(0, 0, 26))
    le = sc.each("lens", (0, 0, 58))
    ho = sc.add("hood", move=(0, 0, 88))
    scr = sc.each("screw", (0, 0, 128))
    for x, y in LEDSCREW:
        sc.line((x, y, 5), (x, y, 150))
    sc.call(9, ca, (-190, 30), near=(-24, -8, 26 + 10))
    sc.call(12, le, (190, 10))
    sc.call(3, ho, (-150, 70), near=(-38, -30, 88 + 10))
    sc.call(21, scr[2:], (150, -20))
    sc.save()


def step_10():
    pull = 30.0
    sc = Scene("step-10", (1300, 1250), (0, 0, -66), (1.0, 0.20, -0.46), 58, up=(0, 0, -1))
    p = fitted(sc, ("shell", "plate") + STACK, cutaway=1)
    b = sc.boards("drv", (0, 0, -pull))
    ns_ = sc.each("nyscrew", (0, 0, -pull - 20))
    plugs = {}
    for c in "RGB":
        sx, sy = SOCKET[c]
        hx, hy = 0.22 * PADS[c][0], 0.22 * PADS[c][1]
        top = R7.Z_STANDOFF - pull + R7.XH_PLUG["mated"] + 5.5          # the plug's wire end, 5.5 mm short of mated
        plugs[c] = lead(sc, c, [(hx, hy, -30), (hx, hy, -38), (0.6 * sx, 0.6 * sy, top + 14), (sx, sy, top + 4),
                                (sx, sy, top)], (sx, sy, top))
    for x, y in RODS:
        sc.line((x, y, R7.Z_STANDOFF), (x, y, R7.Z_STANDOFF - pull - 32))
    sc.call(11, b[:1], (170, 40), near=(0, -22, R7.Z_STANDOFF - 1.6 - pull))
    sc.call(14, b[3:], (-150, -70))
    sc.call(13, [plugs["R"]], (-190, 10))
    sc.call(18, p["nylon"], (-190, 60))
    sc.call(19, ns_, (-170, -50))
    sc.save()


def step_11():
    sc = Scene("step-11", (1500, 1050), (0, 16, 30), (0.62, 0.66, 1.0), 62)
    fitted(sc, ("shell", "hood", "carrier", "lens", "screw"))
    d0 = sc.add("door", 0, (0, 0, 26))
    got = []
    for screw, nut, dirn in PINS[:2]:                         # the top door's two pins
        got.append((sc.add(mesh(screw), move=dirn * 15, colour=KEY["steel"]),
                    sc.add(mesh(nut), move=-dirn * 10, colour=KEY["steel"])))
        sc.line((dirn[0] * 46, R4.P, R4.ZP), (dirn[0] * 6, R4.P, R4.ZP))
    sc.call(4, d0, (-150, 40), near=(-20, 30, 26 + 45))
    sc.call(22, got[1][0], (90, -70))
    sc.call(23, got[1][1], (-30, -130))
    sc.call(3, [sc.items[1]], (150, 110), near=(36, -20, 17.4))
    sc.save()


def step_12():
    sc = Scene("step-12", (1500, 1000), (0, 0, -74), (0.85, 0.50, -1.0), 66)
    fitted(sc, ("shell", "plate", "drv", "nyscrew") + STACK)
    back = -42.0
    c = sc.add("cap", move=(0, 0, back))
    sc.add("capnuts", move=(0, 0, back))
    ms = [sc.add("m3", i, (0, (-1, 1)[i] * 20, 0)) for i in range(2)]
    for s in (-1, 1):
        sc.line((0, s * 33, S.Z_NUT), (0, s * 60, S.Z_NUT))
    sc.call(2, c, (-120, 110), near=(-10, -20, S.ZB + back))
    sc.call(20, ms[1:], (110, -40))
    sc.call(1, [sc.items[0]], (-130, -50), near=(-20, 32.5, -30))
    sc.save()


def step_13():
    sc = Scene("step-13", (1500, 1150), (0, -26, -56), (0.80, 0.42, -1.0), 90)
    fitted(sc, ("shell", "cap", "capnuts", "m3", "hood", "drv"))
    y = sc.add("yoke", move=(0, -30, 0))
    wp = [sc.add("washer_pa", i, ((-1, 1)[i] * 9, 0, 0)) for i in range(2)]
    ws = [sc.add("washer", i, ((-1, 1)[i] * 22, 0, 0)) for i in range(2)]
    kn = [sc.add("knob", i, ((-1, 1)[i] * 36, 0, 0)) for i in range(2)]
    for s in (-1, 1):
        sc.line((s * 33, 0, S.Z_NUT), (s * 96, 0, S.Z_NUT))
    sc.call(5, y, (-150, 40), near=(-36.5, -60, -58))
    sc.call(26, wp[:1], (-60, -110))
    sc.call(25, ws[:1], (-10, -130))
    sc.call(24, kn[:1], (60, -150))
    sc.save()


def P(name, i=None):
    return M(name, i), KIND[name]


def parts_housing():
    sc = Scene("parts-housing", (1600, 1280), (0, 0, 0), (0.62, 0.45, 1.0), 140)
    door = mesh(R7.doors(parts["door"], 0, 0)[0][1])          # a door as it lies closed
    for n, what, u, v in ((1, [P("shell")], -122, 88), (2, [P("cap"), P("capnuts")], -38, 88), (3, [P("hood")], 42, 88),
                          (5, [P("yoke")], 127, 88), (4, [(door, "coat")], -120, -5), (6, [P("plate")], -47, -5),
                          (7, [P("fin", 0)], 19, -5), (8, [P("spacer", 0)], 74, -5), (9, [P("carrier")], 127, -5),
                          (12, [P("lens", 0)], -99, -98), (10, [P("led_pcb"), P("led_parts")], -40, -98),
                          (11, [P("drv_pcb"), P("drv_parts"), P("drv_front")], 34, -98)):
        sc.lay(n, what, u, v)
    sc.save()


def parts_fasteners():
    sc = Scene("parts-fasteners", (1600, 800), (0, 0, 0), (0.62, 0.45, 1.0), 40)
    for n, what, u, v in ((15, [P("stud", 0)], -60, 21), (16, [P("washer3", 0)], -32, 21), (17, [P("nut3", 0)], -12, 21),
                          (18, [P("nylon", 0)], 10, 21), (19, [P("nyscrew", 0)], 34, 21), (20, [P("corner", 0)], 56, 21),
                          (21, [P("screw", 0)], -62, -12), (22, [P("pin", 1)], -40, -12), (23, [P("pinnut", 1)], -20, -12),
                          (24, [P("knob", 1)], 8, -12), (25, [P("washer", 1)], 44, -12), (26, [P("washer_pa", 1)], 62, -12)):
        sc.lay(n, what, u, v)
    sc.save()


def board_pictures():
    """The boards' top views, from KiCad's renders in docs/previews (scripts/make_previews.sh), cut to the board's edge
    so the page can lay labels over them in millimetres: 50 mm across, the centre in the middle."""
    prev = os.path.join(S.HERE, "..", "..", "docs", "previews")
    for name, src in (("board-driver-front", "driver/render-top.png"), ("board-driver-back", "driver/render-bottom.png"),
                      ("board-led-front", "led/render-top.png"), ("board-led35-front", "led35/render-top.png")):
        im = Image.open(os.path.join(prev, src)).convert("RGBA")
        a = np.array(im)
        solid = (a[:, :, 3] > 40) & (a[:, :, :3].min(axis=2) < 245)
        ys, xs = np.where(solid)
        im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).resize((1000, 1000), Image.LANCZOS)
        os.makedirs(OUT, exist_ok=True)
        path = os.path.join(OUT, name + ".webp")
        im.save(path, quality=86, method=6)
        print(f"  {name}.webp from {src}: board {xs.max() + 1 - xs.min()} x {ys.max() + 1 - ys.min()} px, "
              f"{os.path.getsize(path) // 1000} kB", flush=True)


SCENES = {"boards": board_pictures, "lamp-front": lamp_views, "lamp-back": lamp_views, "lamp-section": lamp_section,
          "parts-housing": parts_housing,
          "parts-fasteners": parts_fasteners, "step-01": step_01, "step-05": step_05, "step-06": step_06,
          "step-07": step_07, "step-08": step_08, "step-09": step_09, "step-10": step_10, "step-11": step_11,
          "step-12": step_12, "step-13": step_13}

if __name__ == "__main__":
    vtk.vtkMapper.SetResolveCoincidentTopologyToPolygonOffset()
    vtk.vtkObject.GlobalWarningDisplayOff()
    done = set()
    for name, fn in SCENES.items():
        if (not ONLY or name in ONLY) and fn not in done:
            done.add(fn)
            fn()
