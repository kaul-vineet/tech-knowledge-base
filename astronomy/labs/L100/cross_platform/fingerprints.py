"""Results of every L100 lab, at the precision the lab READMEs print.

CI runs test_fingerprints.py on Linux, macOS (Apple silicon) and Windows: all three must reproduce golden.json.
python fingerprints.py           # print the fingerprints of this machine
python fingerprints.py --write   # overwrite golden.json (only after an intended change to a lab)
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLDEN = HERE / "golden.json"
for lab in ("01-setup-workbench", "02-coordinates", "03-time-systems", "04-units-magnitudes", "05-orbits-kepler",
            "06-light-spectra"):
    sys.path.insert(0, str(HERE.parent / lab))

import check_env  # noqa: E402
import kepler  # noqa: E402
import light  # noqa: E402
import sky  # noqa: E402
import timescales  # noqa: E402
import units  # noqa: E402


def compute():
    when = datetime(2026, 10, 29, 15, 30, tzinfo=timezone.utc)
    rows = sky.sky_table(*sky.GURGAON, when)
    s = timescales.scales(when)
    ra, dec, d = kepler.geocentric_radec("Mars", 2461342.5)
    return {
        "01 seed 42 stars": [list(x) for x in check_env.synthetic_stars(42)],
        "02 Gurgaon alt/az 21:00 IST": [[n, f"{a:.2f}", f"{z:.2f}"] for n, a, z, _ in rows],
        "03 JD(TT) / GMST / J2000 in UTC": [f"{s['JD(TT)']:.6f}", timescales.hms(timescales.gmst_hours(s["JD(UTC)"])),
                                            datetime.fromtimestamp(946728000 - 32 - 32.184, timezone.utc).isoformat(timespec="milliseconds")],
        "04 pc in m / Sun m": [f"{units.PC:.6e}", f"{4.83 + units.distance_modulus(units.AU / units.PC):.2f}"],
        "05 Mars RA / Dec / distance": [f"{ra:.4f}", f"{dec:+.4f}", f"{d:.4f}"],
        "06 Sun peak nm / H-alpha km/s": [f"{light.peak_wavelength(5772) * 1e9:.1f}",
                                          f"{light.doppler_velocity(656.50e-9, light.H_ALPHA) / 1000:+.1f}"],
    }


if __name__ == "__main__":
    result = compute()
    if "--write" in sys.argv:
        GOLDEN.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))
