"""Checks for round 8 (round8.py): the hood against JLCCNC's bending limits, and the carriers' walls against JLC3DP's.

ROT=45 uv run --python 3.12 --with cadquery --with trimesh --with rtree python check8.py OUTDIR

1. Round 6's hood and round 8's, measured on the solids, against JLCCNC's limits for 1.5 mm (round8.JLC_15): each lug's
   window along its bend line, the window's end to the outside of the wall beside it, the lugs and walls as flanges
   (outside, at the lug's edge and its middle), the pin hole to the face's outside.
2. What the wider windows open onto: their nearest point to the lamp's axis against the carrier's skirt and the shell's
   window, and to the lens windows and LED screw heads.
3. The ordered carriers (order6/rgb-spotlight-r6-carrier*.step): wall thickness by rays cast inward from points spread
   over the surface, the share under JLC3DP's 1.0 mm and 2.0 mm, and where the thin walls are.
The fit of the new hood with everything else (doors at every position, the tilt, the hardware) is check7.py on round 8:
ROT=45 ROUND=round8 uv run --python 3.12 --with cadquery python check7.py OUTDIR
"""
import json
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "out/r8"
sys.argv = sys.argv[:1] + ["/dev/null"]
import cadquery as cq  # noqa: E402
from cadquery import Vector as V  # noqa: E402

import round2 as R2  # noqa: E402
import round6 as R6  # noqa: E402
import round8 as R8  # noqa: E402
import sheet as S  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
t = R2.H_T
ZM = (R2.HB + R2.HF) / 2                         # mid-plane of the hood's face
STEP = 0.02


def solid_at(s, a, b, z, axis_a):
    p = {axis_a: a, ("y" if axis_a == "x" else "x"): b, "z": z}
    return s.isInside(V(p["x"], p["y"], p["z"]), 1e-4)


def runs(s, axis_a, a, sb, z, lo, hi):
    """Open (empty) intervals along b from lo to hi (b >= 0 side, times sb) at a, z."""
    out, start, n = [], None, int(round((hi - lo) / STEP))
    for i in range(n + 1):
        b = lo + i * STEP
        empty = not solid_at(s, a, sb * b, z, axis_a)
        if empty and start is None:
            start = b
        if not empty and start is not None:
            out.append((start, b)); start = None
    if start is not None:
        out.append((start, hi))
    return out


def hood_dfm(s, w2):
    L, flat_len, P, KN, ZP = R8.lug_frame()
    a_win = L - 4.0                               # inside the window, clear of the standing lug and its bend
    a_lug = L - RIN_T - t / 2                     # the lug's mid-plane
    res = []
    for axis_a in ("x", "y"):
        for sa in (-1, 1):
            for sb in (-1, 1):
                gaps = [g for g in runs(s, axis_a, sa * a_win, sb, ZM, 0.0, w2 + 0.5) if g[0] < P < g[1]]
                lo, hi = gaps[0]
                tops = []
                for db in (-(KN - 0.05), 0.0, KN - 0.05):    # the lug's top, scanned down from above its knuckle
                    z = ZP + KN + 1.0
                    while not solid_at(s, sa * a_lug, sb * (P + db), z, axis_a):
                        z -= STEP
                    tops.append(z)
                res.append({"lug": f"{axis_a}{'+' if sa > 0 else '-'} {'+' if sb > 0 else '-'}",
                            "window": hi - lo, "window from": lo, "window to": hi,
                            "window to wall outside": w2 - hi, "window to wall inside": w2 - t - hi,
                            "lug flange at its edges": min(tops[0], tops[2]) - R2.HB,
                            "lug flange in its middle": tops[1] - R2.HB})
    return res


RIN_T = S.RIN[t]
L, flat_len, P, KN, ZP = R8.lug_frame()
out = {"limits (1.5 mm, outside)": R8.JLC_15}
for name, s, w2 in (("round 6", R6.hood(), R2.H_W2), ("round 8", R8.hood(), R8.H_W2)):
    m = hood_dfm(s, w2)
    worst = {k: (min if k != "window to" else max)(r[k] for r in m) for k in m[0] if k != "lug"}
    fixed = {"wall flange": R2.HF - R2.H_BACK, "pin hole to the face's outside": ZP - 1.6 - R2.HB}
    print(f"=== 1. {name}'s hood, {2 * w2:g} mm, measured on the solid (worst of the eight lugs) ===")
    rows = [("window along the bend line", worst["window"], R8.JLC_15["window"]),
            ("window's end to the wall's outside", worst["window to wall outside"], R8.JLC_15["rect hole to bend"]),
            ("  (to the wall's inside)", worst["window to wall inside"], None),
            ("lug flange at its edges", worst["lug flange at its edges"], R8.JLC_15["flange"]),
            ("lug flange in its middle", worst["lug flange in its middle"], R8.JLC_15["flange"]),
            ("wall flange", fixed["wall flange"], R8.JLC_15["flange"]),
            ("pin hole to the face's outside", fixed["pin hole to the face's outside"], R8.JLC_15["round hole to bend"])]
    for label, v, lim in rows:
        verdict = "" if lim is None else ("ok" if v >= lim - 1e-6 else "UNDER")
        print(f"   {label:38s} {v:6.2f} mm  {'' if lim is None else f'(JLCCNC {lim})':16s} {verdict}")
    print(f"   windows run {worst['window from']:.2f} .. {max(r['window to'] for r in m):.2f} from the centre")
    out[name] = {"lugs": m, "worst": worst, **fixed, "valid": s.isValid(), "size": 2 * w2,
                 "mass g": round(s.Volume() * 2.68e-3, 1)}

# 2. what the wider windows open onto
L0 = L - flat_len - 0.6                           # the window's inner end across the bend line
w_in = P + KN + R8.WIN_GAP - R8.WIN
near = math.hypot(L0, w_in)
heads = 19 + 5.7 / 2
lens = 12 + S.RET_WIN / 2
behind = {"windows' nearest point to the axis": near, "carrier's skirt outside (r)": R2.SKIRT_OUT,
          "shell's window (r)": R2.WINDOW / 2, "lens windows' outer edge (r)": lens, "LED screw heads' outer edge (r)": heads}
print("=== 2. the windows' nearest point to the lamp's axis, against what lies behind and beside them ===")
for k, v in behind.items():
    print(f"   {k:40s} {v:6.2f} mm")
out["behind the windows"] = {k: round(v, 2) for k, v in behind.items()}

# 3. the carriers' walls
import numpy as np  # noqa: E402
import trimesh  # noqa: E402

print("=== 3. the ordered carriers: wall thickness by rays cast inward (60 000 points each) ===")
out["carriers"] = {}
for tag in ("", "-plus0.5", "-plus1"):
    f = os.path.join(HERE, "order6", f"rgb-spotlight-r6-carrier{tag}.step")
    s = cq.importers.importStep(f).val()
    vs, fs = s.tessellate(0.02, 0.2)
    m = trimesh.Trimesh(np.array([(v.x, v.y, v.z) for v in vs]), np.array(fs), process=True)
    pts, fi = trimesh.sample.sample_surface_even(m, 60000, seed=1)
    n = m.face_normals[fi]
    org = pts - 1e-3 * n
    loc, ri, _ = m.ray.intersects_location(org, -n, multiple_hits=False)
    th = np.full(len(pts), np.inf)
    th[ri] = np.linalg.norm(loc - org[ri], axis=1)
    r = np.hypot(pts[:, 0], pts[:, 1]); z = pts[:, 2]
    ring = (r > 23.9) & (r < 25.4) & (z < S.BOARD + 0.6)        # the flange the skirt hangs from
    thin = th < 1.0
    other = thin & ~ring
    rec = {"under 1.0 mm, % of surface": round(thin.mean() * 100, 2),
           "under 2.0 mm, % of surface": round((th < 2.0).mean() * 100, 2),
           "skirt flange r 24..25.3 (mm)": round(float(np.median(th[ring & thin])), 2) if (ring & thin).any() else None,
           "skirt (mm)": round(float(np.median(th[(r > 25.3) & (r < 26.6) & (z < R2.LED_TOP) & (th < 2)])), 2),
           "pocket rims (mm)": round(float(np.min(th[(r > 21) & (r < 24.1) & (z > S.Z_LEDGE) & (th < 2.5)])), 2),
           "other samples under 1.0 mm": int(other.sum())}
    print(f"   carrier{tag or ' (standard)'}: " + ", ".join(f"{k} {v}" for k, v in rec.items()))
    out["carriers"][f"carrier{tag}"] = rec

os.makedirs(OUT, exist_ok=True)
json.dump(out, open(os.path.join(OUT, f"check8-rot{R6.ROT:g}.json"), "w"), indent=1, default=float)
