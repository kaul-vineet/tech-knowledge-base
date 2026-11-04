"""tryIt experiments for lesson 3 (run: python try_it.py)."""
from datetime import datetime, timezone

import timescales as ts

# 1. One second either side of the 2016-12-31 leap second. Predict: how much does TAI-UTC change?
for s in ("2016-12-31T23:59:59", "2017-01-01T00:00:01"):
    print(s, "TAI-UTC =", ts.scales(datetime.fromisoformat(s).replace(tzinfo=timezone.utc))["TAI-UTC s"], "s")

# 2. Move the observer 15 degrees east. Predict: how much does local sidereal time change?
g = ts.gmst_hours(ts.jd_utc(datetime(2026, 10, 29, 15, 30, tzinfo=timezone.utc)))
for lon in (77.03, 92.03):
    print(f"lon {lon:.2f}: LST {ts.hms((g + lon / 15) % 24)}")
