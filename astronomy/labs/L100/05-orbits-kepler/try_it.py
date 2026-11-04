"""tryIt experiments for lesson 5 (run: python try_it.py)."""
import math
from datetime import datetime, timezone

import kepler

# 1. Fixed-point iteration E = M + e sin E vs Newton. Predict: how many steps for e = 0.9?
for e in (0.1, 0.9):
    M, E, n = 1.0, 1.0, 0
    while abs(E - e * math.sin(E) - M) > 1e-12 and n < 10_000:
        E, n = M + e * math.sin(E), n + 1
    print(f"e={e}: fixed-point needs {n} iterations; Newton gives the same E = {kepler.solve_kepler(M, e):.9f}")

# 2. Mars-Earth distance over 2026-2028. Predict: when is Mars closest (opposition)?
best = min((math.dist(kepler.heliocentric("Mars", jd + 0.5), kepler.heliocentric("EM Bary", jd + 0.5)), jd + 0.5)
           for jd in range(2461041, 2461771))  # one sample per day at 0h, 2026-01-01 .. 2027-12-31
print(f"closest Mars-Earth distance 2026-2027: {best[0]:.4f} au at JD {best[1]} ({datetime.fromtimestamp((best[1] - 2440587.5) * 86400, timezone.utc):%Y-%m-%d})")
