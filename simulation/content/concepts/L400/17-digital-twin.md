**Concept: a digital twin kept honest by live data (state estimation, drift detection, recalibration)**

## Why it matters
A simulation model answers "what if?" once. A digital twin has to keep answering while the real system changes. NIST IR 8356 (2025) quotes a working description: a virtual representation of real-world entities and processes, "synchronized at a specified frequency and fidelity". Synchronised is the hard part. Sensors glitch, messages arrive twice or late, and the building itself changes: a window is left ajar, so the zone loses heat faster. Some twins just replay the model. Others trust every reading. Both drift quietly away from reality, and every forecast built on them is wrong without anyone noticing.

## Mental model
Three loops at three speeds: **assimilate** every reading, **watch** the surprises, **recalibrate** rarely.

```
feed (JSON lines) --> replay: drop late/duplicate --> predict x- = A x + B u
                                                         |
       reading z --> innovation nu = z - H x-  --gate--> update x = x- + K nu
                                     |
                          CUSUM on nu / sqrt(S) --alarm--> collect WINDOW new rows --> refit (a, b)
```
The innovation (Welch & Bishop call it the residual) is the twin's own measure of surprise. When the twin is right, standardised innovations look like noise with mean 0 and variance 1. A persistent bias means the physics has changed.

## Design space
- **A. Open-loop model.** Run the commissioned model on the measured inputs (outdoor temperature, heater state) and ignore the zone sensor. It is cheap and immune to sensor faults. It is also blind to any change in the plant.
- **B. Kalman filter only.** The state is [T, g], where g is unexplained heat gain modelled as a random walk. Every reading pulls the state towards reality, and g soaks up the model error. The forecasts stay reasonable, but the parameters (a, b) stay wrong, so the twin cannot tell you *what* changed.
- **C. Kalman filter + CUSUM + recalibration.** Add a tabular CUSUM on the standardised innovations (NIST e-Handbook 6.3.2.3, k = 0.5). When it alarms, start a fresh window of readings and refit a and b by least squares once WINDOW post-alarm rows exist.

The forces pull against each other: responsiveness against false alarms (the threshold h), robustness against sensor faults (the innovation gate), and identifiability against delay (the refit window).

## How to decide
Criteria: no false alarm on a healthy plant, detection within an hour, a 1-hour forecast good enough to pre-heat, and parameters that explain the change. The lab scores all three options against the plant's **true** temperature. That is possible only because the "real building" is itself a seeded simulation.

**Worked example (lab run, solution file):** before the drift the 1-hour RMSE is A 0.167, B 0.189 and C 0.189 °C. On the last day it is A 6.316, B 0.194 and C 0.127 °C. C raised its alarm 25 minutes after the window opened, recalibrated at t = 2765 min to a = 0.0331 (true 0.035), and raised 0 false alarms. Option A wins only while nothing changes. B forecasts acceptably but reports a heat gain it cannot explain. C is the decision (ADR 0001), and `test_fitness.py` keeps it true: no false alarm, delay ≤ 60 min, a within 15%, RMSE ≤ 0.15 °C and lower than B's.

## Failure modes at scale
- **No gate:** one 85.0 °C glitch gave the shipped twin 5 false alarms before the drift, a refit to a = 0.2 (the clip limit), and a 1.789 °C RMSE.
- **Gate lockout:** a gate that is too tight (2.5σ) rejected 366 real readings after the drift. The CUSUM never saw them, and the last-day RMSE reached 6.051 °C. Count rejections and alarm on bursts of them.
- **Threshold too low:** h = 4 gave 2 false alarms and a bad refit that locked the gate (490 rejections).
- **Many zones:** coupled zones need a multi-state filter. A linear filter on a nonlinear plant (variable-speed fans, humidity) needs an EKF or UKF. Watch for innovations that are not white.

## Common mistakes
- Refitting on a window that straddles the change. The first refit then mixes the old and new physics. Collect post-alarm data first.
- Letting the gate and the drift detector share a blind spot. A rejected reading is also evidence.
- Scoring the twin against the noisy sensor (or a glitch) instead of a trusted reference.
