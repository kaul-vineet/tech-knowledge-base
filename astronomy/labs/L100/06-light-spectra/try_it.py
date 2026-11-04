"""tryIt experiments for lesson 6 (run: python try_it.py)."""
import light

# 1. Double the temperature of the Sun. Predict: peak wavelength? total flux?
for T in (5772, 11544):
    print(f"T={T} K: peak {light.peak_wavelength(T) * 1e9:6.1f} nm, flux {light.total_flux(T):.3e} W/m^2")

# 2. A galaxy line at 721.9 nm that left as H-alpha. Predict: z and the two velocity estimates
z = light.redshift(721.9e-9, light.H_ALPHA)
print(f"z = {z:.4f}: cz = {light.C * z / 1000:.0f} km/s, relativistic {light.relativistic_velocity(z) / 1000:.0f} km/s")
