"""L100 Light and spectra: blackbody (Planck, Wien, Stefan-Boltzmann), Doppler shift and redshift.

python light.py
"""
import numpy as np

H = 6.62607015e-34      # Planck constant, J s (exact, SI 2019)
C = 299_792_458.0       # m/s (exact)
K = 1.380649e-23        # Boltzmann constant, J/K (exact)
B_WIEN = 2.897771955e-3  # Wien displacement constant, m K (CODATA)
SIGMA = 5.670374419e-8   # Stefan-Boltzmann constant, W m^-2 K^-4 (CODATA)
H_ALPHA = 656.28e-9      # hydrogen-alpha rest wavelength in air, m


def planck(wavelength_m, T):
    """Spectral radiance B_lambda(T) in W m^-2 sr^-1 m^-1."""
    x = H * C / (wavelength_m * K * T)
    return 2 * H * C**2 / wavelength_m**5 / np.expm1(x)  # expm1: accurate when x is small


def peak_wavelength(T, lo=50e-9, hi=50e-6, n=200_001):
    lam = np.geomspace(lo, hi, n)
    return lam[np.argmax(planck(lam, T))]  # numerical peak, to compare with Wien's law b / T


def total_flux(T):
    lam = np.geomspace(10e-9, 1e-2, 400_001)
    return np.pi * np.trapezoid(planck(lam, T), lam)  # pi * integral of B over wavelength = sigma T^4


def doppler_velocity(observed_m, rest_m):
    return C * (observed_m - rest_m) / rest_m  # non-relativistic: v = c * dlambda / lambda (+ = moving away)


def redshift(observed_m, rest_m):
    return observed_m / rest_m - 1.0


def relativistic_velocity(z):
    s = (1 + z) ** 2
    return C * (s - 1) / (s + 1)


def main():
    for name, T in (("Sun", 5772), ("Betelgeuse-like", 3600), ("Rigel-like", 12100)):
        print(f"{name:<16} T={T:>6} K  Wien b/T = {B_WIEN / T * 1e9:7.1f} nm  numerical peak = {peak_wavelength(T) * 1e9:7.1f} nm")
    print(f"Sun: pi * integral B = {total_flux(5772):.4e} W/m^2 vs sigma T^4 = {SIGMA * 5772**4:.4e} W/m^2")
    obs = 656.50e-9
    print(f"H-alpha observed at 656.50 nm: v = {doppler_velocity(obs, H_ALPHA) / 1000:+.1f} km/s (z = {redshift(obs, H_ALPHA):.6f})")
    for z in (0.001, 0.1, 1.0):
        print(f"z = {z:<5}: cz = {C * z / 1000:9.0f} km/s  relativistic Doppler v = {relativistic_velocity(z) / 1000:9.0f} km/s")


if __name__ == "__main__":
    main()
