"""L500 #27 Reading seminar: check the internal arithmetic of the two readings before you critique them.

python reading_checks.py
Numbers are quoted from Hubble (1929, PNAS 15, 168) and the Gaia DR3 summary (Gaia Collaboration, Vallenari et al. 2023,
A&A 674, A1, abstract). Only the numbers are reused; read the papers themselves for the arguments.
"""
import math

AU = 149_597_870_700.0
MPC_KM = AU * 648_000.0 / math.pi * 1e6 / 1000
GYR_S = 365.25 * 86_400.0 * 1e9


def hubble_time_gyr(h0):
    return MPC_KM / h0 / GYR_S


def abs_mag(m, d_mpc):
    return m - (5 * math.log10(d_mpc * 1e6) - 5)


def main():
    k = 500.0  # "K = +500 km./sec. per million parsecs"
    print(f"Hubble 1929: K = 500 km/s/Mpc -> 1/K = {hubble_time_gyr(k):.2f} Gyr")
    d7619 = 3910 / k
    print(f"NGC 7619: v = +3910 km/s (solar-motion corrected) / K = {d7619:.2f} Mpc (paper: 7.8 x 10^6 pc)")
    print(f"NGC 7619: m = 11.8 at 7.8 Mpc -> M = {abs_mag(11.8, 7.8):.2f} (paper: -17.65)")
    print(f"22 nebulae without individual distances: 745 km/s at 1.4 Mpc -> K = {745 / 1.4:.0f} (paper: 530)")
    print(f"modern H0 = 67.4: NGC 7619 at {3910 / 67.4:.1f} Mpc; K/H0 = {k / 67.4:.2f} (the 1929 distance scale was too short by this factor)")
    print(f"Gaia DR3: >33 million radial velocities / ~1500 million sources with class probabilities = {33 / 1500:.1%}")
    print(f"Gaia DR3: 34 months of data = {34 / 12:.2f} yr")


if __name__ == "__main__":
    main()
