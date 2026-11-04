"""tryIt for lesson 19 (fixed index, 1 million sources, 100 cones each).
1. Very fine zones (h = 0.01 deg): faster or slower than h = 1.0?
2. Big cones (radius 5 deg): how much faster than brute force is the index then?
"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("catalog_fixed", HERE / "solution" / "catalog.py")
cat_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cat_mod)

if __name__ == "__main__":
    cat = cat_mod.make_catalogue()
    cones = cat_mod.test_cones()[100:200]
    brute = cat_mod.Brute(cat)
    ref, ms_a, _ = cat_mod.measure(brute, cones)
    for h in (0.01, 1.0):
        _, ms, wrong = cat_mod.measure(cat_mod.Zones(cat, h=h), cones, ref)
        print(f"1. zones h={h}: {ms:.3f} ms/query (brute {ms_a:.2f}), wrong cones {wrong}")
    big = [(ra, dec, 5.0) for ra, dec, _ in cones]
    ref, ms_a, _ = cat_mod.measure(brute, big)
    _, ms_c, wrong = cat_mod.measure(cat_mod.CoarseZones(cat), big, ref)
    print(f"2. radius 5 deg: brute {ms_a:.2f} ms, zones h=1.0 {ms_c:.2f} ms -> {ms_a / ms_c:.0f}x, wrong {wrong}")
