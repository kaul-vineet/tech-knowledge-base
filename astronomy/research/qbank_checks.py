"""Recompute every calculation answer and execute every code-reading snippet in content/qbank/L100-L500.json
and in content/assessment/concept-inventory.json (L500 pre/post inventory).

python research/qbank_checks.py      (from the astronomy folder; prints OK and exits 0 when every answer matches)
Needs Python 3.12+ and numpy (the snippets use numpy, as the labs do).
"""
import contextlib
import io
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

QBANK = Path(__file__).resolve().parents[1] / "content" / "qbank"
C = 299_792_458.0
B_WIEN = 2.897771955e-3
R_SUN_KM, R_EARTH_KM = 695_700.0, 6_378.1  # IAU 2015 nominal solar radius, IAU nominal equatorial Earth radius


def jd_utc(dt):
    return 2440587.5 + dt.timestamp() / 86400.0


def gmst_hours(jd_ut):
    return (18.697375 + 24.065709824279 * (jd_ut - 2451545.0)) % 24.0


def vincenty_deg(ra1, dec1, ra2, dec2):
    r1, d1, r2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    dra = r2 - r1
    num = math.hypot(math.cos(d2) * math.sin(dra), math.cos(d1) * math.sin(d2) - math.sin(d1) * math.cos(d2) * math.cos(dra))
    return math.degrees(math.atan2(num, math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2) * math.cos(dra)))


def tan_ra(xi_deg, eta_deg, ra0, dec0):
    """Inverse gnomonic projection (Calabretta & Greisen 2002), RA only."""
    xi, eta, d0 = math.radians(xi_deg), math.radians(eta_deg), math.radians(dec0)
    return (ra0 + math.degrees(math.atan2(xi, math.cos(d0) - eta * math.sin(d0)))) % 360


def kasten_young(h_deg):
    if h_deg <= 0:
        return math.inf
    return max(1.0, 1.0 / (math.sin(math.radians(h_deg)) + 0.50572 * (h_deg + 6.07995) ** -1.6364))


def fits_bytes(n):
    return -(-n // 2880) * 2880


def utc_at_tt_noon_2000():
    t = datetime(2000, 1, 1, 12, 0) - timedelta(seconds=32 + 32.184)
    return t.strftime("%H:%M:%S.%f")[:12]


MPC_KM = 149_597_870_700.0 * 648_000 / math.pi * 1e3  # 1 Mpc in km (IAU 2012 B2 au, IAU 2015 B2 parsec)
GYR_S = 365.25 * 86_400 * 1e9


def hubble_time_gyr(h0):
    return MPC_KM / h0 / GYR_S


CALC = {
    # L100
    "as-L100-009": lambda: f"{90 - 51.4778 + -52.6957:.1f} deg, so it never rises",
    "as-L100-016": lambda: f"{jd_utc(datetime(2026, 10, 29, 15, 30, tzinfo=timezone.utc)):.5f}",
    "as-L100-017": lambda: f"{37 + 32.184:.3f} s",
    "as-L100-020": lambda: f"{(gmst_hours(2461343.145833) + 77.03 / 15) % 24:.4f} h",
    "as-L100-025": lambda: f"{10 ** (-0.4 * (2.0 - 4.5)):.1f} times",
    "as-L100-026": lambda: f"{-2.5 * math.log10(3 * 10 ** (-0.4 * 7.0)):.2f}",
    "as-L100-027": lambda: f"{10 ** (7.5 / 5 + 1):.1f} pc",
    "as-L100-033": lambda: f"{math.sqrt(9.537 ** 3):.1f} yr",
    "as-L100-041": lambda: f"{B_WIEN / 9940 * 1e9:.1f} nm",
    "as-L100-043": lambda: f"{C * (656.05 - 656.28) / 656.28 / 1000:+.1f} km/s (approaching)",
    # L200
    "as-L200-002": lambda: f"{2 * math.sin(math.radians(60) / 2):.4f}",
    "as-L200-003": lambda: f"{vincenty_deg(10.0, 60.0, 10.5, 60.2) * 60:.2f} arcmin",
    "as-L200-011": lambda: f"{2880 + fits_bytes(101 * 101 * 4)}",
    "as-L200-018": lambda: f"{tan_ra(-10 / 3600, 0.0, 150.0, 60.0):.5f} deg",
    "as-L200-020": lambda: f"{2.5 / math.log(10) / 50:.4f} mag",
    "as-L200-021": lambda: f"{3000 / math.sqrt(3000 + math.pi * 6 ** 2 * (100 + 5 ** 2)):.1f}",
    "as-L200-022": lambda: f"{1 - math.exp(-3 ** 2 / (2 * 1.5 ** 2)):.4f}",
    "as-L200-030": lambda: f"{1 / (1 / 0.5671 - 1):.4f} d",
    "as-L200-039": lambda: f"{4e-10 * (0.001 / 0.002) ** 2:.0e}",
    # L300
    "as-L300-001": lambda: f"{kasten_young(30):.3f}",
    "as-L300-002": lambda: f"{kasten_young(5):.2f} vs {1 / math.sin(math.radians(5)):.2f}",
    "as-L300-013": lambda: f"{(1000 + 0.8 * 10000) / (1000 + 10000):.3f}",
    "as-L300-014": lambda: f"{100 / math.sqrt(200_000):.3f} %",
    "as-L300-022": lambda: f"{1 / math.cos(math.radians(62.1)):.2f}x",
    "as-L300-023": lambda: f"{math.sqrt(abs(-0.000481 * 0.000481 - 0.000278 * 0.000278)) * 3600:.2f} arcsec/px",
    "as-L300-031": lambda: f"{math.sqrt(0.0060 ** 2 * 4.13):.4f} h",
    "as-L300-032": lambda: f"{math.erf(0.5 / math.sqrt(2)):.3f}",
    "as-L300-033": lambda: f"{math.sqrt(0.010) * 0.8 * R_SUN_KM / R_EARTH_KM:.2f} Earth radii",
    "as-L300-044": lambda: f"{(2460500.25 - 2460000) - (2460500.25 - 2400000.5 - 60000):.1f} d",
    # L400
    "as-L400-003": lambda: f"{4096 * 4096 * 16 * 8 / 1e9:.2f} GB",
    "as-L400-004": lambda: f"{(512 * 2 ** 20) // (4096 * 4096 * 8)}",
    "as-L400-014": lambda: f"{58.2 * 0.045:.1f} vs {3.5 * 0.857:.1f}",
    "as-L400-020": lambda: f"{math.degrees(math.atan(math.sin(math.radians(5)) / math.sqrt(abs(math.cos(math.radians(75)) * math.cos(math.radians(85)))))):.2f} deg",
    "as-L400-027": lambda: f"{43.24 + 3 * math.log(40):.2f} vs {40.63 + 6 * math.log(40):.2f}",
    "as-L400-043": lambda: f"{math.sqrt(8169e-6) * R_SUN_KM / R_EARTH_KM:.2f} Earth radii",
    "as-L400-044": lambda: f"{1.5 * 13.0 * (12.35 / 365.25) ** (1 / 3):.2f} h",
    "as-L400-045": lambda: f"{(2.0 * R_EARTH_KM / R_SUN_KM) ** 2 * 1e6:.0f} ppm",
    # L500 (theory lessons 23-27)
    "as-L500-002": lambda: f"{(3.986004e14 * (86164.0905 / (2 * math.pi)) ** 2) ** (1 / 3) / 1000:.1f} km",
    "as-L500-010": lambda: f"{2 ** 2 * 2 ** 4} times",
    "as-L500-012": lambda: f"{10 * 2 ** (1 - 3.5):.2f} Gyr",
    "as-L500-019": lambda: f"{hubble_time_gyr(70):.2f} Gyr",
    "as-L500-021": lambda: f"{3 * (70e3 / (MPC_KM * 1e3)) ** 2 / (8 * math.pi * 6.67408e-11):.2e} kg/m^3",
    "as-L500-025": lambda: f"{0.95 * 0.02 / (0.95 * 0.02 + 0.02 * 0.98):.4f}",
    "as-L500-028": lambda: f"{10 ** 0.4:.2f} times",
    "as-L500-031": lambda: f"{math.degrees(math.acos(6378.1 / (6378.1 + 1200))):.1f} deg",
    "as-L500-037": lambda: f"{hubble_time_gyr(500):.2f} Gyr",
    # L500 concept inventory (content/assessment/concept-inventory.json)
    "as-L500-CI-008": lambda: f"{10 ** (0.4 * 5):.0f}",
    "as-L500-CI-011": lambda: f"{hubble_time_gyr(500):.2f} Gyr",
}

# Cross-checks of facts quoted in questions/explanations against the lab outputs they cite.
FACTS = [
    ("J2000.0 in UTC is 11:58:55.816", utc_at_tt_noon_2000() == "11:58:55.816"),
    ("lab LST at Gurgaon 15:30 UTC is 23.1671 h",
     f"{(gmst_hours(jd_utc(datetime(2026, 10, 29, 15, 30, tzinfo=timezone.utc))) + 77.03 / 15) % 24:.4f}" == "23.1671"),
    ("two m = 6 stars combine to 5.25", f"{6 - 2.5 * math.log10(2):.2f}" == "5.25"),
    ("1 pc = 3.2616 ly", f"{149_597_870_700.0 * 648_000 / math.pi / (C * 365.25 * 86400):.4f}" == "3.2616"),
    ("Sun peaks at 502.0 nm", f"{B_WIEN / 5772 * 1e9:.1f}" == "502.0"),
    ("H-alpha at 656.50 nm is +100.5 km/s", f"{C * (656.50 - 656.28) / 656.28 / 1000:.1f}" == "100.5"),
    ("Mars period 1.881 yr from a = 1.524 au", f"{1.524 ** 1.5:.3f}" == "1.881"),
    ("shipped airmass at -34.6 deg is -1.76", f"{1 / math.sin(math.radians(-34.6)):.2f}" == "-1.76"),
    ("BIC wiggles 62.76 with n = 40", f"{40.63 + 6 * math.log(40):.2f}" == "62.76"),
    ("Orion cos(-5.4) = 0.996, Cassiopeia cos(62) = 0.47",
     f"{math.cos(math.radians(-5.4)):.3f}" == "0.996" and f"{math.cos(math.radians(62)):.2f}" == "0.47"),
    ("capstone example: P = 6.27 d -> limit 5.03 h", f"{1.5 * 13.0 * (6.27 / 365.25) ** (1 / 3):.2f}" == "5.03"),
    # L500 debugging questions quote what the buggy snippet prints
    ("as-L500-008 buggy atan azimuth prints 45.0", f"{math.degrees(math.atan(-1.0 / -1.0)) % 360}" == "45.0"),
    ("as-L500-008 atan2 gives 225", f"{math.degrees(math.atan2(-1.0, -1.0)) % 360:.0f}" == "225"),
    ("as-L500-018 kpc bug prints -6.52, pc gives 8.48",
     f"{5 * math.log10(1 / 2.01) - 5:.2f}" == "-6.52" and f"{5 * math.log10(1000 / 2.01) - 5:.2f}" == "8.48"),
    ("as-L500-045 Mpc bug prints 12.33; pc gives -17.67",
     f"{11.8 - (5 * math.log10(3910 / 500) - 5):.2f}" == "12.33" and f"{11.8 - (5 * math.log10(3910 / 500 * 1e6) - 5):.2f}" == "-17.67"),
    ("as-L500-026 flat-prior estimate 70.95 and sd 6.55", f"{(7000 + 30000 + 112000) / 2100:.2f}" == "70.95" and f"{300 / math.sqrt(2100):.2f}" == "6.55"),
    ("as-L500-027 data-only posterior 71.7 +/- 6.5 (problem 25.8)", f"{150500 / 2100:.1f}" == "71.7" and f"{300 / math.sqrt(2100):.1f}" == "6.5"),
    ("as-L500-030 shadow limits 18.6 / 23.0 deg",
     f"{math.degrees(math.acos(6378.1 / 6728.1)):.1f}" == "18.6" and f"{math.degrees(math.acos(6378.1 / 6928.1)):.1f}" == "23.0"),
]


def run_snippet(code):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<snippet>", "exec"), {"__name__": "__snippet__"})
    return buf.getvalue().strip().replace("\n", " | ")


def main():
    errors, n_calc, n_code = [], 0, 0
    seen_calc = set()
    banks = [QBANK / f"{lv}.json" for lv in ("L100", "L200", "L300", "L400", "L500")]
    banks.append(QBANK.parent / "assessment" / "concept-inventory.json")
    for bank in banks:
        for q in json.loads(bank.read_text(encoding="utf-8")):
            correct = q["options"][q["answer"]]
            if q["type"] == "calculation":
                n_calc += 1
                seen_calc.add(q["id"])
                if q["id"] not in CALC:
                    errors.append(f"{q['id']}: calculation without a recomputation in CALC")
                    continue
                expected = CALC[q["id"]]()
                if expected != correct:
                    errors.append(f"{q['id']}: recomputed {expected!r} but the marked answer is {correct!r}")
                if sum(o == expected for o in q["options"]) != 1:
                    errors.append(f"{q['id']}: recomputed answer appears {sum(o == expected for o in q['options'])} times")
            elif q["type"] == "code-reading":
                n_code += 1
                out = run_snippet(q["code"])
                if out != correct:
                    errors.append(f"{q['id']}: snippet printed {out!r} but the marked answer is {correct!r}")
                if any(o == out for i, o in enumerate(q["options"]) if i != q["answer"]):
                    errors.append(f"{q['id']}: a distractor equals the real output")
    for qid in sorted(set(CALC) - seen_calc):
        errors.append(f"{qid}: in CALC but not a calculation question in the bank")
    for name, ok in FACTS:
        if not ok:
            errors.append(f"fact check failed: {name}")
    print(f"calculations recomputed: {n_calc} | code-reading snippets executed: {n_code} | facts checked: {len(FACTS)}")
    for e in errors:
        print("ERROR", e)
    if errors:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
