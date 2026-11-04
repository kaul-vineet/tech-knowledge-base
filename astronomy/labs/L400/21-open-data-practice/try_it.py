"""tryIt for lesson 21 (fixed release_licence()).
1. Add a ShareAlike input (a CC BY-SA 4.0 table of variable-star types): which licence must the release carry?
2. Drop the Gaia input (TESS + own photometry only): what licence, and does check() pass?
"""
import importlib.util
import tempfile
from pathlib import Path

import inputs

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("release_fixed", HERE / "solution" / "release.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)

if __name__ == "__main__":
    sa = {"name": "variable_types_table", "licence": "CC-BY-SA-4.0", "family": "BY-SA", "credit": "Types table (BY-SA)."}
    try:
        print("1. + BY-SA input ->", fixed.release_licence(inputs.INPUTS + [sa]))
    except ValueError as e:
        print("1. + BY-SA input -> ValueError:", e)
    inputs.INPUTS[:] = [i for i in inputs.INPUTS if i["name"] != "gaia_dr3_astrometry"]
    with tempfile.TemporaryDirectory() as tmp:
        d = fixed.build(Path(tmp) / "r")
        print("2. without Gaia ->", (d / "LICENSE.txt").read_text(encoding="utf-8").strip(), "| problems:", fixed.check(d))
