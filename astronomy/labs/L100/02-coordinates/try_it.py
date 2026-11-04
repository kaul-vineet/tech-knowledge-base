"""tryIt experiments for lesson 2 (run: python try_it.py)."""
from datetime import datetime, timedelta, timezone

import sky

when = datetime(2026, 10, 29, 15, 30, tzinfo=timezone.utc)

# 1. Wait 3 hours (00:00 IST). Predict: which stars set, which rise?
for dt in (when, when + timedelta(hours=3)):
    up = [n for n, alt, _, is_up in sky.sky_table(*sky.GURGAON, dt) if is_up]
    print(f"{dt:%H:%M} UTC up: {', '.join(up)}")

# 2. Same clock time, observer moves from Gurgaon (28.46 N) to Sydney (33.87 S, 151.21 E). Predict: Canopus?
for name, (lat, lon) in (("Gurgaon", sky.GURGAON), ("Sydney", (-33.87, 151.21))):
    alt, az = sky.altaz(*sky.STARS["Canopus"], lat, lon, when)
    print(f"Canopus from {name}: alt {alt:6.2f} deg az {az:6.2f} deg")
