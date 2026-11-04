"""tryIt for lesson 13.
1. Fixed pipeline, cosmic-ray cleaning OFF: what happens to frame 17 (a seeded hit inside the aperture)?
2. Shipped (unfixed) flat, but flats exposed 5x brighter (30 000 e-): does the bug go away?
"""
import importlib.util
from pathlib import Path

import calibrate
import camera

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("calibrate_fixed", HERE / "solution" / "calibrate.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)

if __name__ == "__main__":
    rel, s, _ = fixed.run(clean=False, log_path=None)
    print(f"1. no cleaning: frame 17 relative flux {rel[17]:.4f}; plain rms {s['rms_percent']}%, "
          f"robust rms {s['robust_rms_percent']}%, variable={s['variable']}")
    camera.FLAT_E = 30_000.0
    rel, s, flat = calibrate.run(log_path=None)
    print(f"2. shipped flat, 30k e- flats: robust rms {s['robust_rms_percent']}%, variable={s['variable']}, "
          f"flat min {flat.min():.4f} (fixed pipeline gives 0.813 at 6k e-)")
