"""tryIt for lesson 18 (fixed broker).
1. Match the PSF but NOT the transparency (a = 1, b = 0): what do the firehose (A) and option C see?
2. The known-variable catalogue is unavailable (cross-match service down): what does V1 become?
"""
import importlib.util
from pathlib import Path

import numpy as np

import alert_sim as sim

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("alerts_fixed", HERE / "solution" / "alerts.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)

if __name__ == "__main__":
    exposures, ref = sim.nights(), sim.reference()
    full = fixed.difference

    def psf_only(new, ref_img, sigma_new):
        return new - fixed.blur(ref_img, np.sqrt(sigma_new ** 2 - sim.REF_SIGMA ** 2))

    fixed.difference = psf_only
    for option in "AC":
        s = fixed.summary(option, fixed.run(option, exposures, ref), exposures)
        print(f"1. PSF matched, flux not, option {option}: {s['alerts_per_night']} alerts/night, classes {s['classes']}")
    fixed.difference = full
    vx, vy = sim.known_variables()[0][1:]
    sim.known_variables = lambda: []
    out = fixed.run("C", exposures, ref)
    v1 = [p["class"] for _, _, p in out if np.hypot(p["candidate"]["x"] - vx, p["candidate"]["y"] - vy) < 2]
    print(f"2. no known-variable catalogue: V1 alerts classified as {v1}")
