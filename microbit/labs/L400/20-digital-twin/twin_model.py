"""The digital twin's MODEL of the classroom network (CPython only).

Two sub-models, both simulation ideas from the simulation topic:
  latency  Monte Carlo of lab 17's protocol (stop-and-wait ARQ with the same timer constants) on a
           link with data/ack loss l: when does each reading reach the store? -> the share of
           readings that needed a retransmission, and the p95 latency, for any l.
  room     a time-stepped first-order thermal model of the room (heating towards 22 C with time
           constant TAU_S) plus a per-sensor offset; the board reports whole degrees.
calibrate() fits each device's loss l (grid search on latency) and offset (mean residual) on the
first CALIB_WINDOWS windows only - like calibrating on data, then checking it on later data.
"""
import math
import random
import statistics

# lab 17 solution.py constants (test_main checks they still match the file)
TIMEOUT_MS, MAX_TIMEOUT_MS, MAX_TRIES, SAMPLE_MS = 100, 800, 6, 1000
BASE_MS = 13                  # one tick to the relay + UART time, measured p50 in lab 17
WINDOW = 30                   # readings per window (30 s)
RETRY_MS = BASE_MS + 50       # a reading slower than this needed at least one retransmission
QUANT_SD = 1 / math.sqrt(12)  # whole-degree readings: rounding error sd, does not average out in 30 s
CALIB_WINDOWS = 6
T_START, T_END, TAU_S = 20.0, 22.0, 600.0


def room_temp(t_ms):
    return T_END + (T_START - T_END) * math.exp(-t_ms / 1000.0 / TAU_S)


def one_reading(l, rng):
    """(latency_ms, busy_ms) of one reading under stop-and-wait with loss l on data and on ack."""
    t, latency, timeout = 0, None, TIMEOUT_MS + rng.randint(0, TIMEOUT_MS // 10) * 10
    for _ in range(MAX_TRIES):
        data_ok = rng.random() >= l
        if data_ok and latency is None:
            latency = BASE_MS + t
        if data_ok and rng.random() >= l:
            return latency, t + BASE_MS
        t += timeout
        timeout = min(timeout * 2, MAX_TIMEOUT_MS) + rng.randint(0, 5) * 10
    return latency, t


def latency_stats(l, n=4000, seed=1):
    """Monte Carlo on a link with loss l: P(a reading needed a retransmission) and p95 latency.

    The retry share is the twin's link signal: one 2 s outlier moves a window MEAN by 5+ sd,
    but a share only by one reading in WINDOW (robust to the tail the model does not capture).
    """
    rng = random.Random(seed)
    lats = []
    while len(lats) < n:
        lat, _ = one_reading(l, rng)
        if lat is not None:
            lats.append(lat)
    lats.sort()
    return sum(x > RETRY_MS for x in lats) / len(lats), lats[int(0.95 * len(lats)) - 1]


GRID = [i / 100 for i in range(0, 51)]
_CACHE = {}


def stats_for(l):
    if l not in _CACHE:
        _CACHE[l] = latency_stats(l)
    return _CACHE[l]


def windows(rows):
    """Group one device's rows (sorted by seq) into consecutive WINDOW-sized windows."""
    return [rows[i:i + WINDOW] for i in range(0, len(rows) - WINDOW + 1, WINDOW)]


def observe(win):
    lat = sum(r["t_store"] - r["t_sensor"] > RETRY_MS for r in win) / len(win)
    resid = statistics.fmean(r["temp"] - room_temp(r["t_sensor"]) for r in win)
    return {"t": win[-1]["t_sensor"], "lat": lat, "resid": resid}


def calibrate(by_dev):
    """Per device: loss l, temperature offset and the sd of the window residual, from early windows."""
    params = {}
    for dev, rows in sorted(by_dev.items()):
        obs = [observe(w) for w in windows(rows)[:CALIB_WINDOWS]]
        share = statistics.fmean(o["lat"] for o in obs)
        l = min(GRID, key=lambda g: abs(stats_for(g)[0] - share))
        resid = [o["resid"] for o in obs]
        params[dev] = {"loss": l, "offset": statistics.fmean(resid),
                       "temp_sd": max(statistics.pstdev(resid), QUANT_SD)}
    return params


def z_scores(params, dev, o):
    """Predicted vs observed for one window, in standard deviations of the model."""
    share = max(stats_for(params[dev]["loss"])[0], 0.02)
    sd = math.sqrt(share * (1 - share) / WINDOW)                 # binomial share of WINDOW readings
    p = params[dev]
    return {"lat": (o["lat"] - share) / sd, "temp": (o["resid"] - p["offset"]) / p["temp_sd"]}
