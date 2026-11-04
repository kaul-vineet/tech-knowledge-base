"""Recompute every number quoted in the L100 concept notes and the primer (run: python concept_examples_L100.py)."""
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

LABS = Path(__file__).resolve().parents[1] / "labs" / "L100"
for d in ("01-setup-workbench", "02-coordinates", "03-time-systems", "04-units-magnitudes", "05-orbits-kepler", "06-light-spectra"):
    sys.path.insert(0, str(LABS / d))
import check_env, kepler, light, sky, timescales as ts, units  # noqa: E401,E402

when = datetime(2026, 10, 29, 15, 30, tzinfo=timezone.utc)
print("01 first seeded star:", check_env.synthetic_stars(42)[0])
rows = {r[0]: r for r in sky.sky_table(*sky.GURGAON, when)}
print(f"02 LST {(sky.gmst_hours(sky.julian_date(when)) + 77.03 / 15) % 24:.4f} h; Deneb {rows['Deneb'][1]:.2f}; Sirius {rows['Sirius'][1]:.2f};"
      f" Betelgeuse from Greenwich 21:00 {sky.altaz(*sky.STARS['Betelgeuse'], 51.4778, -0.0015, when.replace(hour=21, minute=0))[0]:.2f}")
print(f"02 precession J2000->2026 ~ 50.3 arcsec/yr x 26.8 yr = {50.3 * 26.8 / 3600:.2f} deg; Canopus max alt from London {-52.6957 + 90 - 51.4778:.1f}")
s = ts.scales(when)
print(f"03 JD {s['JD(UTC)']:.6f} TT-UTC {s['TT-UTC s']:.3f}; GMST {ts.hms(ts.gmst_hours(s['JD(UTC)']))} vs USNO full "
      f"{(ts.gmst_hours(s['JD(UTC)']) - ts.gmst_usno_full_hours(when)) * 3600:+.3f} s; J2000 GMST {ts.hms(ts.gmst_hours(2451545.0))} "
      f"IERS ERA {ts.hms(ts.era_hours(2451545.0))}; 2006 worked example GAST diff "
      f"{(ts.gast_hours(ts.WC06_JD_UT1, ts.WC06_JD_TT) - ts.WC06_GST_H) * 3600:+.3f} s")
print(f"04 pc = {units.PC:.4e} m = {units.PC / units.AU:.3f} AU = {units.PC / units.LY:.4f} ly; 1 mag x{units.flux_ratio(0, 1):.4f}; "
      f"x2 -> {units.mag_difference(2, 1):+.4f}; M4.83 at 100 pc {4.83 + units.distance_modulus(100):.2f}; Sun {4.83 + units.distance_modulus(units.AU / units.PC):.2f}; "
      f"two m6 {6 + units.mag_difference(2, 1):.2f}; 0.9/1.1 mas {1 / 0.0009:.0f}/{1 / 0.0011:.0f} pc")
ra, dec, d = kepler.geocentric_radec("Mars", 2461342.5)
print(f"05 E {kepler.solve_kepler(1.0, 0.5):.12f}; Earth r {math.dist((0, 0, 0), kepler.heliocentric('EM Bary', 2461342.5)):.5f}; "
      f"Mars r {math.dist((0, 0, 0), kepler.heliocentric('Mars', 2461342.5)):.5f}; RA {ra:.4f} Dec {dec:+.4f} d {d:.4f}; P {kepler.period_years(1.52371034):.4f}")
print(f"06 peaks {light.peak_wavelength(5772) * 1e9:.1f} / {light.peak_wavelength(3600) * 1e9:.1f} nm; flux {light.total_flux(5772):.4e}; "
      f"Halpha {light.doppler_velocity(656.50e-9, light.H_ALPHA) / 1000:+.1f}; z0.1 {light.C * 0.1 / 1000:.0f} vs {light.relativistic_velocity(0.1) / 1000:.0f}")
