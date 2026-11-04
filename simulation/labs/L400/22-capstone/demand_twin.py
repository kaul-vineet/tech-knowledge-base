"""Capstone milestone 5b: a demand twin fed by today's live call counts (data/today.jsonl, 15-minute slots).

Reuses the L400 lesson 17 Twin's tabular CUSUM (drift_check) by subclassing it; the state here is ONE number,
the demand multiplier m (today's calls / planned calls), tracked by a scalar Kalman filter.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent / "17-digital-twin"))
import twin as lesson17  # noqa: E402

Q_M = 0.02 ** 2  # how fast true demand may drift per 15-minute slot (random walk on m)


class DemandTwin(lesson17.Twin):
    def __init__(self, planned_rates):
        self.planned, self.m, self.p = planned_rates, 1.0, 0.05 ** 2
        self.s_hi = self.s_lo = 0.0
        self.recalibrate, self.refit_pending, self.history, self.events = False, False, [], []

    def observe(self, slot, calls):
        """One 15-minute count: predict, update m, run the lesson 17 CUSUM on the standardised innovation."""
        expected = self.planned[slot // 4] * 15  # planned calls in this slot
        self.p += Q_M
        s = expected ** 2 * self.p + expected * self.m  # innovation variance: uncertainty in m + Poisson noise
        nu = calls - expected * self.m
        k = expected * self.p / s
        self.m, self.p = self.m + k * nu, (1 - k * expected) * self.p
        before = len(self.events)
        self.drift_check(15 * slot, nu / np.sqrt(s))  # inherited from lesson 17: tabular CUSUM, k = 0.5, h = 8
        return len(self.events) > before  # True = a drift alarm was raised in this slot


def replay(planned_rates, path=HERE / "data" / "today.jsonl"):
    tw, alarms = DemandTwin(planned_rates), []
    for line in path.read_text(encoding="utf-8").splitlines():
        msg = json.loads(line)
        if tw.observe(msg["slot"], msg["calls"]):
            alarms.append({"slot": msg["slot"], "t_min": msg["t_min"], "m": round(float(tw.m), 3)})
    return tw, alarms
