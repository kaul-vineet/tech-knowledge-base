"""L400 digital twin: a zone-temperature twin kept in step with a live feed (JSON lines replay).

Model: T[k+1] = T[k] + a(T_out - T[k]) + b*heater + g[k]; the Kalman filter estimates state x = [T, g]
(g = heat gain the model does not explain). A two-sided CUSUM on standardised innovations detects drift;
an alarm triggers recalibration of (a, b) by least squares on the last WINDOW accepted readings.
python twin.py            (replays sensor_feed.jsonl; writes twin_log.jsonl)
"""
import json
from pathlib import Path

import numpy as np

import make_feed  # the "real building": also gives the true temperature, so forecasts are scored honestly

HERE = Path(__file__).resolve().parent
LOG = HERE / "twin_log.jsonl"
A0, B0 = 0.020, 0.30  # design-time calibration (commissioning data)
R_MEAS, Q = 0.15 ** 2, np.diag([0.03 ** 2, 0.002 ** 2])  # sensor noise; process noise for T and for g
CUSUM_K, CUSUM_H = 0.5, 8.0  # k = half the shift to detect (in sigmas), h = alarm threshold (NIST 6.3.2.3)
WINDOW, HORIZON = 48, 12  # recalibrate on 4 h of data; forecast 1 h ahead


def read_feed(path=HERE / "sensor_feed.jsonl"):
    """Replay a JSON-lines feed in arrival order; drop duplicates and late messages, count null readings."""
    msgs, skipped = [], {"late_or_duplicate": 0, "null_reading": 0}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            msg = json.loads(line)
            if msgs and msg["t_min"] <= msgs[-1]["t_min"]:  # a twin must never move backwards in time
                skipped["late_or_duplicate"] += 1
                continue
            skipped["null_reading"] += msg["zone_C"] is None  # kept: the twin predicts through the gap
            msgs.append(msg)
    return msgs, skipped


class Twin:
    def __init__(self, a=A0, b=B0, recalibrate=True):
        self.a, self.b, self.recalibrate = a, b, recalibrate
        self.x, self.P = np.array([20.0, 0.0]), np.diag([1.0, 0.01])
        self.s_hi = self.s_lo = 0.0
        self.refit_pending = False  # set by a drift alarm; the refit waits for WINDOW post-alarm readings
        self.history, self.events = [], []  # accepted (T_prev, outdoor, heater, T_meas) rows; JSON-lines events

    def step_matrices(self, outdoor, heater):
        A = np.array([[1 - self.a, 1.0], [0.0, 1.0]])
        u = np.array([self.a * outdoor + self.b * heater, 0.0])  # known inputs enter like B*u
        return A, u

    def predict(self, outdoor, heater):
        A, u = self.step_matrices(outdoor, heater)
        self.x, self.P = A @ self.x + u, A @ self.P @ A.T + Q  # x- = Ax + Bu ; P- = A P A' + Q

    def innovation(self, z):
        S = self.P[0, 0] + R_MEAS  # H = [1, 0]: we measure temperature only
        return z - self.x[0], S

    def update(self, t, z, prev_meas, outdoor, heater):
        nu, S = self.innovation(z)
        zscore = nu / np.sqrt(S)
        K = self.P[:, 0] / S  # K = P- H' (H P- H' + R)^-1
        self.x = self.x + K * nu
        self.P = self.P - np.outer(K, self.P[0, :])  # P = (I - K H) P-
        if prev_meas is not None:
            self.history = (self.history + [(prev_meas, outdoor, heater, z)])[-WINDOW:]
        self.drift_check(t, zscore)
        if self.refit_pending and len(self.history) == WINDOW:
            self.refit(t)

    def drift_check(self, t, zscore):
        self.s_hi = max(0.0, self.s_hi + zscore - CUSUM_K)  # tabular CUSUM on standardised innovations
        self.s_lo = max(0.0, self.s_lo - zscore - CUSUM_K)
        if max(self.s_hi, self.s_lo) > CUSUM_H and not self.refit_pending:
            self.events.append({"t_min": t, "event": "drift_alarm", "s_hi": round(self.s_hi, 2),
                                "s_lo": round(self.s_lo, 2)})
            self.s_hi = self.s_lo = 0.0
            if self.recalibrate:  # recalibration trigger: refit on data from AFTER the change only
                self.refit_pending, self.history = True, []

    def refit(self, t):
        """Recalibration trigger fired: least squares on dT = a(T_out - T) + b*heater over the window."""
        h = np.array(self.history)
        X = np.column_stack([h[:, 1] - h[:, 0], h[:, 2]])
        (a, b), *_ = np.linalg.lstsq(X, h[:, 3] - h[:, 0], rcond=None)
        self.a, self.b = float(np.clip(a, 0.001, 0.2)), float(np.clip(b, 0.0, 1.0))
        self.x[1], self.P[1, 1] = 0.0, 0.01  # the refit model now explains the gain the filter was carrying
        self.refit_pending, self.s_hi, self.s_lo = False, 0.0, 0.0  # a fresh model starts a fresh CUSUM
        self.events.append({"t_min": t, "event": "recalibrated", "a": round(self.a, 4), "b": round(self.b, 3)})

    def forecast(self, inputs):
        """What-if / look-ahead: run the model forward from the current state without new measurements."""
        x = self.x.copy()
        for outdoor, heater in inputs:
            A, u = self.step_matrices(outdoor, heater)
            x = A @ x + u
        return float(x[0])


def run(twin=None, path=HERE / "sensor_feed.jsonl", log_path=None, assimilate=True):
    """Replay the feed through the twin; score 1-hour-ahead forecasts against the plant's TRUE temperature.
    assimilate=False is the open-loop option: the model runs on the inputs and never sees a measurement."""
    twin = twin or Twin()
    msgs, twin.skipped = read_feed(path)
    forecasts = {}  # target t_min -> temperature forecast made HORIZON steps earlier
    for i, m in enumerate(msgs[1:], start=1):
        last = msgs[i - 1]
        twin.predict(last["outdoor_C"], last["heater_on"])
        if assimilate and m["zone_C"] is not None:
            twin.update(m["t_min"], m["zone_C"], last["zone_C"], last["outdoor_C"], last["heater_on"])
        if i + HORIZON < len(msgs):
            forecasts[msgs[i + HORIZON]["t_min"]] = twin.forecast(
                [(f["outdoor_C"], f["heater_on"]) for f in msgs[i:i + HORIZON]])
    actual = {row[0]: row[3] for row in make_feed.plant()}
    errors = [(t, forecasts[t] - actual[t]) for t in sorted(k for k in forecasts if k in actual)]
    if log_path:
        Path(log_path).write_text("".join(json.dumps(e) + "\n" for e in twin.events), encoding="utf-8")
    return twin, errors


def rmse(errors, t_from=0, t_to=10 ** 9):
    e = np.array([err for t, err in errors if t_from <= t < t_to])
    return float(np.sqrt(np.mean(e ** 2)))


def main():
    print("OPTIONS (1-h forecast RMSE vs true zone temperature, C): before drift | last day")
    for name, kw in (("A open-loop model", {"twin": Twin(recalibrate=False), "assimilate": False}),
                     ("B Kalman filter only", {"twin": Twin(recalibrate=False)})):
        _, err = run(**kw)
        print(f"  {name:22s} {rmse(err, 0, 2500):6.3f} | {rmse(err, 2880):6.3f}")
    twin, errors = run(log_path=LOG)
    print(f"  {'C KF + CUSUM + refit':22s} {rmse(errors, 0, 2500):6.3f} | {rmse(errors, 2880):6.3f}")
    print(f"feed: {len(errors)} scored forecasts; skipped {twin.skipped}")
    print(f"events: {len(twin.events)} (twin_log.jsonl); first 3:")
    for e in twin.events[:3]:
        print("  ", json.dumps(e))
    alarms = [e["t_min"] for e in twin.events if e["event"] == "drift_alarm"]
    print(f"alarms before the drift (t < 2500 min): {sum(t < 2500 for t in alarms)}; first alarm after it: "
          f"{next((t for t in alarms if t >= 2500), None)} min")
    print(f"final model: a={twin.a:.4f} b={twin.b:.3f} (plant after drift: a=0.035 b=0.30)")


if __name__ == "__main__":
    main()
