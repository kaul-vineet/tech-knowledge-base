"""BUILD TASK (shipped UNFIXED): parse the start time an agent wrote in its plan.

Agents write times many ways: '2026-11-19T13:20:00Z', '2026-11-19T18:50:00+05:30', '2026-11-19T18:50' (no zone).
This version reads every one of them as UTC: an explicit +05:30 is RELABELLED (replace, not convert) and a naive
local time is silently accepted - the same seam bug as the failure lab, now at the agent boundary.
Make parse_plan_time() convert zoned times to UTC and raise ValueError for anything without a zone.
Check: BUILD_TARGET=mine python -m unittest tests.test_obs_build_task -v
"""
from datetime import datetime, timezone

from timeutil import UtcInstant


def parse_plan_time(text):
    return UtcInstant(datetime.fromisoformat(text.strip().replace("Z", "+00:00")).replace(tzinfo=timezone.utc))
