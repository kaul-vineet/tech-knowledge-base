# 1. Keep the zone twin in step with a Kalman filter, a CUSUM drift alarm and post-alarm recalibration

## Status
Accepted (2026-10-28)

## Context
The twin of one office zone must forecast the zone temperature 1 hour ahead from a JSON-lines sensor feed. The feed has duplicates, late messages, a missing reading and an 85.0 °C glitch. From t = 2500 min the plant changes: a window is left ajar, and a goes from 0.020 to 0.035. Constraints: no false drift alarm on a healthy plant, detection within 60 min, a 1-hour RMSE at most 0.15 °C after the change, and parameters that explain the change. Options were measured by `twin.py` (solution) against the plant's true temperature. 1-hour RMSE before the drift / on the last day:
- A, open-loop model: 0.167 / 6.316 °C.
- B, Kalman filter only (state [T, g]): 0.189 / 0.194 °C. a stays at 0.020.
- C, Kalman filter + CUSUM (k 0.5, h 8) + refit on 48 post-alarm readings + 5σ innovation gate: 0.189 / 0.127 °C. Alarm after 25 min, a refitted to 0.0331, 0 false alarms.

## Decision
Use option C. Gate innovations above 5 predicted sigmas. Start the refit window at the alarm, and reset the CUSUM after each refit.

## Consequences
- The twin reports a physical diagnosis (heat-loss coefficient up by about 65%), not just a better forecast.
- Two parameters (h, gate) need tuning. tryIt shows h = 4 causes 2 false alarms and gate 2.5σ causes lockout (366 rejected readings, no detection). Bursts of rejected readings must themselves be treated as a drift signal (follow-up).
- Recalibration waits 4 h (WINDOW = 48) after an alarm. Forecasts in that gap rely on the g state.
- Fitness function: `test_fitness.py` (no false alarm, delay ≤ 60 min, |a − 0.035|/0.035 < 15%, last-day RMSE ≤ 0.15 °C and below option B).
