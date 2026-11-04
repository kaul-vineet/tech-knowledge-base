"""L500 #23 Foundations I: numerical checks of Kepler's third law, vis-viva + escape velocity, the virial theorem
and the spherical-trigonometry altitude formula used in lesson 2 (labs/L100/02-coordinates/sky.py).

python mechanics.py            # runs every check, prints the evidence, exits 1 if any check fails
Units in the orbit checks: au, years, solar masses, so GM_sun = 4 pi^2 (as in lesson 11). Constants in SI come from
IAU 2015 Resolution B3 (nominal GM, radii) and IAU 2012 B2 (au).
"""
import math
import sys
from pathlib import Path

import numpy as np

GM_SUN = 1.3271244e20      # m^3 s^-2, IAU 2015 B3 nominal solar mass parameter
GM_EARTH = 3.986004e14     # m^3 s^-2, IAU 2015 B3 nominal terrestrial mass parameter
GM_JUP = 1.2668653e17      # m^3 s^-2, IAU 2015 B3 nominal jovian mass parameter
R_EARTH = 6.3781e6         # m, IAU 2015 B3 nominal equatorial Earth radius
AU = 149_597_870_700.0     # m, IAU 2012 B2 (exact)
DAY = 86_400.0
SIDEREAL_DAY = 86_400.0 * 24.0 / 24.065709824279  # s, from the USNO GMST rate used in lesson 2
GM4 = 4 * math.pi ** 2     # GM_sun in au^3 / yr^2


def kepler_period(a, gm):
    """Circular two-body orbit: T = 2 pi sqrt(a^3 / G(M + m)); pass gm = G(M + m)."""
    return 2 * math.pi * math.sqrt(a ** 3 / gm)


def vis_viva(r, a, gm):
    return gm * (2.0 / r - 1.0 / a)


def leapfrog(r0, v0, gm, dt, n):
    """Kick-drift-kick integration of the relative two-body orbit; returns positions and velocities, shape (n+1, 2)."""
    acc = lambda r: -gm * r / np.linalg.norm(r) ** 3
    r, v = np.array(r0, float), np.array(v0, float)
    rs, vs = np.empty((n + 1, 2)), np.empty((n + 1, 2))
    rs[0], vs[0] = r, v
    a = acc(r)
    for i in range(n):
        v = v + 0.5 * dt * a
        r = r + dt * v
        a = acc(r)
        v = v + 0.5 * dt * a
        rs[i + 1], vs[i + 1] = r, v
    return rs, vs


def measured_period(rs, dt):
    """Time between successive upward crossings of y = 0 (linear interpolation between steps)."""
    y = rs[:, 1]
    idx = np.where((y[:-1] < 0) & (y[1:] >= 0))[0]
    t = (idx + (-y[idx]) / (y[idx + 1] - y[idx])) * dt
    return float(np.mean(np.diff(t)))


def check_kepler3():
    lines = []
    t_earth = kepler_period(AU, GM_SUN) / DAY
    t_with_jup = kepler_period(5.2026 * AU, GM_SUN + GM_JUP) / kepler_period(5.2026 * AU, GM_SUN)
    lines.append(f"Earth (a = 1 au, GM_sun): T = {t_earth:.4f} d")
    lines.append(f"Jupiter's own mass shortens its period by a factor {t_with_jup:.6f} (= (1 + m/M)^-1/2)")
    mu = 9.546e-4  # Jupiter-like mass ratio, as in lesson 11
    gm = GM4 * (1 + mu)
    rs, _ = leapfrog([1.0, 0.0], [0.0, math.sqrt(gm)], gm, 1e-4, 50_000)
    t_num, t_formula = measured_period(rs, 1e-4), kepler_period(1.0, gm)
    rel = abs(t_num - t_formula) / t_formula
    lines.append(f"leapfrog circular orbit, m/M = {mu}: T = {t_num:.8f} yr vs formula {t_formula:.8f} yr (rel. diff {rel:.1e})")
    ok = abs(t_earth - 365.2569) < 0.01 and rel < 1e-6
    return lines, ok


def check_vis_viva():
    lines = []
    e, a = 0.6, 1.0
    rp = a * (1 - e)
    rs, vs = leapfrog([rp, 0.0], [0.0, math.sqrt(GM4 * (1 + e) / rp)], GM4, 2e-5, 100_000)
    r = np.linalg.norm(rs, axis=1)
    a_measured = 0.5 * (r.min() + r.max())  # semi-major axis read off the integrated orbit, not assumed
    v2 = np.sum(vs ** 2, axis=1)
    err = float(np.max(np.abs(v2 - vis_viva(r, a_measured, GM4)) / v2))
    lines.append(f"e = 0.6 orbit, {len(r)} samples: a measured = {a_measured:.6f} au, max |v^2 - GM(2/r - 1/a)| / v^2 = {err:.1e}")
    v_esc_earth = math.sqrt(2 * GM_EARTH / R_EARTH) / 1000
    v_esc_1au = math.sqrt(2 * GM_SUN / AU) / 1000
    lines.append(f"escape speed: Earth surface {v_esc_earth:.2f} km/s; from the Sun at 1 au {v_esc_1au:.1f} km/s")
    fates = []
    for f in (0.99, 1.01):
        rs2, vs2 = leapfrog([1.0, 0.0], [0.0, f * math.sqrt(2 * GM4)], GM4, 2e-3, 50_000)
        energy = 0.5 * np.sum(vs2[-1] ** 2) - GM4 / np.linalg.norm(rs2[-1])
        fates.append((f, float(np.linalg.norm(rs2[-1])), energy))
        lines.append(f"launch at {f:.2f} v_esc from 1 au: after 100 yr r = {fates[-1][1]:.1f} au, specific energy {energy:+.3f}")
    ok = err < 1e-6 and abs(v_esc_earth - 11.18) < 0.01 and fates[0][2] < 0 < fates[1][2] and fates[0][1] < fates[1][1]
    return lines, ok


def check_virial():
    lines = []
    e, a = 0.6, 1.0
    rp, dt = a * (1 - e), 2e-5
    steps_per_orbit = round(1.0 / dt)  # T = 1 yr for a = 1 au
    rs, vs = leapfrog([rp, 0.0], [0.0, math.sqrt(GM4 * (1 + e) / rp)], GM4, dt, 3 * steps_per_orbit)
    kin = 0.5 * np.sum(vs ** 2, axis=1)
    pot = -GM4 / np.linalg.norm(rs, axis=1)
    inst = 2 * kin / -pot
    lines.append(f"instantaneous 2K/|U| over an e = 0.6 orbit ranges {inst.min():.3f} .. {inst.max():.3f}")
    full = 2 * kin[:-1].mean() / -pot[:-1].mean()
    quarter = slice(0, steps_per_orbit // 4)
    part = 2 * kin[quarter].mean() / -pot[quarter].mean()
    lines.append(f"time-averaged 2<K>/|<U>| over 3 whole orbits = {full:.6f}; over the first quarter orbit = {part:.3f}")
    ok = abs(full - 1) < 1e-4 and abs(part - 1) > 0.1
    return lines, ok


def _sky_module():
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "L100" / "02-coordinates"))
    import sky  # the lesson-2 implementation being verified
    return sky


def altaz_rotation(ha_deg, dec_deg, lat_deg):
    """Independent route: rotate the unit vector from the (meridian-equator, east, pole) frame to (north, east, zenith)."""
    h, d, f = np.radians(ha_deg), np.radians(dec_deg), np.radians(lat_deg)
    s = np.array([np.cos(d) * np.cos(h), -np.cos(d) * np.sin(h), np.sin(d)])  # hour angle grows westward
    rot = np.array([[-np.sin(f), np.zeros_like(f), np.cos(f)],
                    [np.zeros_like(f), np.ones_like(f), np.zeros_like(f)],
                    [np.cos(f), np.zeros_like(f), np.sin(f)]])
    n, e, z = np.einsum("ij...,j...->i...", rot, s)
    return np.degrees(np.arcsin(z)), np.degrees(np.arctan2(e, n)) % 360.0


def check_altaz():
    lines = []
    rng = np.random.default_rng(23)
    a, b, c = (v / np.linalg.norm(v, axis=0) for v in rng.normal(size=(3, 3, 10_000)))
    side = lambda p, q: np.arccos(np.clip(np.sum(p * q, axis=0), -1, 1))
    ta = lambda p, q: q - np.sum(p * q, axis=0) * p  # tangent at p towards q
    tb, tc = ta(a, b), ta(a, c)
    ang_a = np.arccos(np.clip(np.sum(tb * tc, axis=0) / np.linalg.norm(tb, axis=0) / np.linalg.norm(tc, axis=0), -1, 1))
    sa, sb, sc = side(b, c), side(a, c), side(a, b)
    cos_err = float(np.max(np.abs(np.cos(sa) - (np.cos(sb) * np.cos(sc) + np.sin(sb) * np.sin(sc) * np.cos(ang_a)))))
    lines.append(f"spherical cosine rule on 10000 random triangles: max error {cos_err:.1e}")
    sky = _sky_module()
    ha, dec, lat = rng.uniform(0, 360, 20_000), rng.uniform(-89, 89, 20_000), rng.uniform(-89, 89, 20_000)
    alt_r, az_r = altaz_rotation(ha, dec, lat)
    alt_f = np.degrees(np.arcsin(np.sin(np.radians(dec)) * np.sin(np.radians(lat))
                                 + np.cos(np.radians(dec)) * np.cos(np.radians(lat)) * np.cos(np.radians(ha))))
    lines.append(f"sin h = sin d sin phi + cos d cos phi cos H vs rotation matrix, 20000 points: max |d alt| = {np.max(np.abs(alt_f - alt_r)):.1e} deg")
    from datetime import datetime, timezone
    when = datetime(2026, 10, 29, 15, 30, tzinfo=timezone.utc)
    lst = (sky.gmst_hours(sky.julian_date(when)) * 15 + sky.GURGAON[1]) % 360
    worst_alt = worst_az = 0.0
    for name, (ra, de) in sky.STARS.items():
        alt_l, az_l = sky.altaz(ra, de, *sky.GURGAON, when)
        alt_m, az_m = altaz_rotation((lst - ra) % 360, de, sky.GURGAON[0])
        worst_alt = max(worst_alt, abs(alt_l - float(alt_m)))
        if alt_l < 89.9:  # azimuth is undefined at the zenith
            worst_az = max(worst_az, abs((az_l - float(az_m) + 180) % 360 - 180))
    deneb = sky.altaz(*sky.STARS["Deneb"], *sky.GURGAON, when)[0]
    lines.append(f"lesson-2 sky.altaz vs rotation, {len(sky.STARS)} stars at Gurgaon 15:30 UTC: max |d alt| {worst_alt:.1e} deg, max |d az| {worst_az:.1e} deg; Deneb alt {deneb:.2f} deg")
    ok = cos_err < 1e-12 and np.max(np.abs(alt_f - alt_r)) < 1e-9 and worst_alt < 1e-9 and worst_az < 1e-9 and f"{deneb:.2f}" == "56.27"
    return lines, ok


CHECKS = {"kepler3": check_kepler3, "vis_viva": check_vis_viva, "virial": check_virial, "altaz": check_altaz}


def main():
    all_ok = True
    for name, fn in CHECKS.items():
        lines, ok = fn()
        all_ok &= ok
        print(f"[{name}] {'PASS' if ok else 'FAIL'}")
        for line in lines:
            print("  " + line)
    print("ALL CHECKS PASS" if all_ok else "SOME CHECKS FAILED")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
