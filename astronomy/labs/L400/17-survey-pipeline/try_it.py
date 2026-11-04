"""tryIt for lesson 17 (fixed pipeline, option A only).
1. Lower the detection threshold from 5 to 3 sigma: completeness up - and purity?
2. Coarser background mesh: 64 x 64 boxes instead of 32 x 32 against the moonlight gradient.
"""
import importlib.util
from pathlib import Path

import survey_sim as sim

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("survey_fixed", HERE / "solution" / "survey.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)

if __name__ == "__main__":
    raws, bias, flat, truth = sim.night()
    for label, nsigma, box in (("1. 3 sigma, 32 px mesh", 3.0, 32), ("2. 5 sigma, 64 px mesh", 5.0, 64)):
        fixed.NSIGMA, fixed.BOX = nsigma, box
        rows, _, _ = fixed.run("A", raws, bias, flat)
        comp, pur = fixed.score(rows, truth)
        print(f"{label}: {len(rows)} detections, completeness {comp}, purity {pur}")
