"""L100 Orbits: Kepler's laws, Kepler's equation and a planet's position from approximate elements.

Elements: JPL "Approximate Positions of the Planets" (Standish & Williams), Table 1, valid 1800-2050;
nominal error for Mars about 40 arcsec in longitude.
python kepler.py                 # 2026-10-29 0h TDB
python kepler.py --jd 2461500.5
"""
import argparse
import math

# a [au], e, I [deg], L [deg], long.peri [deg], long.node [deg]; second tuple = rates per Julian century
ELEMENTS = {
    "EM Bary": ((1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0),
                (0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0)),
    "Mars": ((1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891),
             (0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343)),
    "Jupiter": ((5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909),
                (-0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106)),
}
OBLIQUITY = math.radians(23.43928)  # J2000


def solve_kepler(M, e, tol=1e-12):
    """Solve M = E - e sin E for E (radians) with Newton's method."""
    E = M + e * math.sin(M)  # JPL's starting guess
    for _ in range(50):
        dE = (M - (E - e * math.sin(E))) / (1 - e * math.cos(E))  # Newton step on f(E) = E - e sin E - M
        E += dE
        if abs(dE) < tol:
            return E
    raise RuntimeError("Kepler's equation did not converge")


def heliocentric(name, jd_tdb):
    """Heliocentric ecliptic J2000 position (x, y, z) in au."""
    T = (jd_tdb - 2451545.0) / 36525.0
    a, e, I, L, peri, node = (v0 + rate * T for v0, rate in zip(*ELEMENTS[name]))
    w, M = math.radians(peri - node), math.radians((L - peri + 180) % 360 - 180)  # argument of perihelion, mean anomaly
    E = solve_kepler(M, e)
    xp, yp = a * (math.cos(E) - e), a * math.sqrt(1 - e * e) * math.sin(E)  # position in the orbit plane
    I, node = math.radians(I), math.radians(node)
    cw, sw, cO, sO, ci, si = math.cos(w), math.sin(w), math.cos(node), math.sin(node), math.cos(I), math.sin(I)
    return ((cw * cO - sw * sO * ci) * xp + (-sw * cO - cw * sO * ci) * yp,
            (cw * sO + sw * cO * ci) * xp + (-sw * sO + cw * cO * ci) * yp,
            (sw * si) * xp + (cw * si) * yp)


def geocentric_radec(name, jd_tdb):
    p, earth = heliocentric(name, jd_tdb), heliocentric("EM Bary", jd_tdb)
    x, y, z = (pi - ei for pi, ei in zip(p, earth))
    ye, ze = y * math.cos(OBLIQUITY) - z * math.sin(OBLIQUITY), y * math.sin(OBLIQUITY) + z * math.cos(OBLIQUITY)
    dist = math.sqrt(x * x + y * y + z * z)  # geometric distance (no light-time correction)
    return math.degrees(math.atan2(ye, x)) % 360, math.degrees(math.asin(ze / dist)), dist


def period_years(a_au):
    return a_au ** 1.5  # Kepler's third law in years and au (Sun-dominated orbit)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--jd", type=float, default=2461342.5, help="Julian Date (TDB); default 2026-10-29 0h")
    jd = p.parse_args().jd
    print(f"JD(TDB) {jd} | Kepler: M=1.0 rad, e=0.5 -> E = {solve_kepler(1.0, 0.5):.12f} rad")
    for name in ELEMENTS:
        x, y, z = heliocentric(name, jd)
        print(f"{name:<8} helio x={x:+.5f} y={y:+.5f} z={z:+.5f} au  r={math.sqrt(x*x+y*y+z*z):.5f} au  "
              f"period {period_years(ELEMENTS[name][0][0]):.4f} yr")
    for name in ("Mars", "Jupiter"):
        ra, dec, d = geocentric_radec(name, jd)
        print(f"{name:<8} geocentric RA {ra:8.4f} deg ({ra / 15:.4f} h)  Dec {dec:+8.4f} deg  distance {d:.4f} au")


if __name__ == "__main__":
    main()
