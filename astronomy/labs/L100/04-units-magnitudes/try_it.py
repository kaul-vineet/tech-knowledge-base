"""tryIt experiments for lesson 4 (run: python try_it.py)."""
import units

# 1. Two stars of magnitude 6.0 (naked-eye limit) side by side. Predict: combined magnitude 3.0? 5.5? 6.0?
combined = 6.0 + units.mag_difference(2.0, 1.0)
print(f"two m=6.0 stars together: m = {combined:.2f}")

# 2. Gaia-like parallax 1.000 mas +/- 0.100 mas. Predict: is the distance error symmetric?
for p_mas in (0.9, 1.0, 1.1):
    d = units.parallax_distance_pc(p_mas / 1000)
    print(f"parallax {p_mas:.1f} mas -> {d:7.1f} pc, distance modulus {units.distance_modulus(d):.3f}")
