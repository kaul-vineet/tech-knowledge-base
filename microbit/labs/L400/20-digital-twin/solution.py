"""Lab 20 - digital twin drift check (AFTER = build task solution): CUSUM on the twin's z-scores.

Same model and z-scores as twin.py. Instead of judging one window, keep two cumulative sums per
device and signal (tabular CUSUM, NIST/SEMATECH e-Handbook 6.3.2.3, in sigma units):
  S_hi = max(0, S_hi + z - K)     S_lo = max(0, S_lo - z - K)
and alarm when either exceeds H = 5. The textbook slack is K = 0.5 (half a 1-sigma shift); here
K = 0.75, because the retry share of 30 readings on a 4 % link is a skewed binomial: K = 0.5 gave
up to 7 false alarms per 1,000 nominal windows, K = 0.75 at most 2 (drift_eval.py, 6 runs).
Noise makes S wander and fall back to 0; a persistent shift, even a small one, keeps adding to it.
An alarm latches: it is raised once per device and signal, then the twin needs re-calibration.
"""
import json

import twin_model

K, H = 0.75, 5.0


class Twin:
    def __init__(self, params):
        self.params = params
        self.alarms, self.log = [], []
        self.s = {}                           # (dev, signal) -> [S_hi, S_lo]
        self.latched = set()

    def update(self, dev, obs):
        z = twin_model.z_scores(self.params, dev, obs)
        raised = []
        for signal in ("lat", "temp"):
            s = self.s.setdefault((dev, signal), [0.0, 0.0])
            s[0] = max(0.0, s[0] + z[signal] - K)     # evidence for "higher than the model"
            s[1] = max(0.0, s[1] - z[signal] - K)     # evidence for "lower than the model"
            if max(s) > H and (dev, signal) not in self.latched:
                self.latched.add((dev, signal))
                raised.append({"t": obs["t"], "dev": dev, "alarm": "DRIFT_" + signal.upper(),
                               "z": round(z[signal], 1), "cusum": round(max(s), 1)})
        self.log.append(json.dumps({"t": obs["t"], "dev": dev, "z_lat": round(z["lat"], 2),
                                    "z_temp": round(z["temp"], 2),
                                    "s_lat": round(max(self.s[(dev, "lat")]), 2),
                                    "s_temp": round(max(self.s[(dev, "temp")]), 2)}))
        self.alarms += raised
        return raised
