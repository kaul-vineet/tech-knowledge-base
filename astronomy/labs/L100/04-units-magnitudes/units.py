"""L100 Units and scales: AU, light-year, parsec, magnitudes <-> flux, distance modulus.

python units.py
"""
import math

C = 299_792_458.0                 # speed of light, m/s (exact, SI)
AU = 149_597_870_700.0            # astronomical unit, m (exact, IAU 2012 Resolution B2)
JULIAN_YEAR = 365.25 * 86_400.0   # s (IAU: the light-year uses the Julian year)
LY = C * JULIAN_YEAR              # light-year, m
PC = AU * 648_000.0 / math.pi     # parsec: distance at which 1 AU subtends 1 arcsecond (IAU 2015 Resolution B2)


def flux_ratio(m1, m2):
    """F1/F2 for magnitudes m1, m2 (Pogson: 5 magnitudes = factor 100; brighter = smaller magnitude)."""
    return 10 ** (-0.4 * (m1 - m2))


def mag_difference(f1, f2):
    return -2.5 * math.log10(f1 / f2)


def distance_modulus(d_pc):
    return 5.0 * math.log10(d_pc / 10.0)  # m - M: how much fainter a star looks than at 10 pc


def distance_from_modulus(mu):
    return 10.0 ** (mu / 5.0 + 1.0)


def parallax_distance_pc(parallax_arcsec):
    return 1.0 / parallax_arcsec  # small-angle definition of the parsec


def main():
    print(f"1 AU = {AU:.0f} m | 1 ly = {LY:.0f} m | 1 pc = {PC:.6e} m")
    print(f"1 pc = {PC / AU:.3f} AU = {PC / LY:.4f} ly | light from 1 AU takes {AU / C:.3f} s")
    print(f"5 mag brighter = x{flux_ratio(0, 5):.1f} flux | 1 mag = x{flux_ratio(0, 1):.4f}")
    print(f"flux x2 -> {mag_difference(2, 1):+.4f} mag")
    for d in (10, 100, 1000):
        print(f"star with M = 4.83 at {d:>4} pc: m = {4.83 + distance_modulus(d):6.2f} (distance modulus {distance_modulus(d):5.2f})")
    print(f"same star at 1 AU (the Sun): m = {4.83 + distance_modulus(AU / PC):.2f}")
    print(f"parallax 0.1 arcsec -> {parallax_distance_pc(0.1):.1f} pc; modulus 5.00 -> {distance_from_modulus(5.0):.1f} pc")


if __name__ == "__main__":
    main()
