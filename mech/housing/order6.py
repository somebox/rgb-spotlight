"""RGB Spotlight housing, round 6: the parts to order, one STEP each, with the extra carriers for the focus test (D2).

ROT=45 uv run --python 3.12 --with cadquery python order6.py OUTDIR

Round 6 is the design of record (DESIGN D21-D23): round 5's door (LEN 40, WID 71, CUT 90), the hood, front plate and
carrier turned 45 deg, everything else as round 4. Carriers +0.5 and +1.0 mm: the ledge and the top raised by that
much, the feet, skirt and relief where they are, so the lenses stand further from the LEDs.
"""
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "order6"
sys.argv = sys.argv[:1] + ["/dev/null"]
import cadquery as cq  # noqa: E402

import round2 as R2  # noqa: E402
import round4 as R4  # noqa: E402
import round6 as R6  # noqa: E402
import sheet as S  # noqa: E402

SHOP = {"shell": "JLCCNC sheet metal", "cap": "JLCCNC sheet metal", "hood": "JLCCNC sheet metal",
        "door": "JLCCNC sheet metal", "yoke": "JLCCNC sheet metal", "plate": "JLCCNC sheet metal (bare)",
        "fin": "JLCCNC sheet metal (bare)", "spacer": "JLCCNC sheet metal (bare)", "carrier": "JLC3DP MJF PA12"}


def taller_carrier(dz):
    z = (S.Z_LEDGE, S.Z_CAR)
    S.Z_LEDGE, S.Z_CAR = z[0] + dz, z[1] + dz
    try:
        return R6.rz(R2.carrier())
    finally:
        S.Z_LEDGE, S.Z_CAR = z


def export(name, s, tag=""):
    f = os.path.join(OUT, f"rgb-spotlight-r6-{name}{tag}.step")
    cq.exporters.export(cq.Workplane().add(s), f)
    bb = s.BoundingBox()
    t = R4.THICK.get(name, "")
    q = R4.QTY.get(name, R4.PRINTED.get(name, ""))
    print(f"{name + tag:14s} t {t!s:4s} x{q!s:2s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f}  "
          f"valid {s.isValid()} solids {len(s.Solids())}  vol {s.Volume() / 1000:6.2f} cm3  {SHOP[name]}  {os.path.basename(f)}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    parts = R6.build()
    for name in ("shell", "cap", "hood", "door", "yoke", "plate", "fin", "spacer", "carrier"):
        export(name, parts[name])
    for dz in (0.5, 1.0):
        export("carrier", taller_carrier(dz), f"-plus{dz:g}")
