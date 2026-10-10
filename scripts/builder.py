"""Project glue for pcbkit.schematic (the sheet builder lives in pcb-kit, ~/src/pcb-kit).

sch_driver.py and sch_led.py do `import builder; from builder import *` and set `builder.P` to their board's
directory. This module configures pcbkit.schematic and then *becomes* it (sys.modules swap), so `builder.P`,
`builder.POWER` and `builder.ROOT` are the engine's own. Power symbols: GND, +5V, +12V.
"""
import os
import sys

try:
    import pcbkit  # noqa: F401
except ImportError:  # an interpreter pcbkit is not linked into: use the checkout
    sys.path.insert(0, os.path.expanduser(os.environ.get("PCBKIT_ROOT", "~/src/pcb-kit")))
from pcbkit import schematic as _m

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"   # repo root, wherever it lives
_m.configure(ROOT + "boards/driver/")
for _net in ("+3V3", "VBUS"):
    _m.POWER.pop(_net, None)
_m.ROOT = ROOT
sys.modules[__name__] = _m
