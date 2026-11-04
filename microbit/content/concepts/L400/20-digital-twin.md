# Concept: a digital twin that notices drift without crying wolf

## Why it matters
Classroom networks rarely break; they decay. A board slides behind a metal cupboard. A battery sags.
Afternoon sun reaches one sensor. Every reading still arrives, so "is it up?" monitoring stays green
while the data slowly stops meaning what it says. A digital twin is a model of the network that
predicts what the gateway should see. Comparing prediction with observation exposes the decay. Most
twins fail at the next step: they either alarm on noise or miss slow drift.

## Mental model
**A flight plan and a navigator.** The plan (the model) says where the aircraft should be; the
navigator compares it with the position reports (telemetry). One report off course is a gust. A small
error that keeps the same sign, report after report, is a heading problem. The navigator adds those
errors up (CUSUM) instead of judging each report alone.

```
gateway rows ─► window of 30 readings per board ─► observe: retry share, temp residual
twin model (Monte Carlo ARQ + room model, calibrated on windows 1-6) ─► predict mean + sd
z = (observed - predicted) / sd ─► S_hi = max(0, S_hi + z - K) ─► S_hi > H ? DRIFT alarm (latched)
```

## Design space
- **What the twin models.** Link: a Monte Carlo of lab 17's stop-and-wait ARQ with the same timer
  constants gives, for a loss l, the share of readings that needed a retransmission, and their p95
  latency. Room: a first-order thermal model plus a calibrated offset per board, reported in whole
  degrees. This reuses simulation ideas: Monte Carlo, time-stepped models, and calibration on early
  data checked on later data.
- **What it compares.** A mean latency per window is fragile, because one 2-second outlier moves it
  by 5 or more model standard deviations. The **share** of retried readings is a binomial count and
  robust to that. Whole-degree readings leave a rounding error of standard deviation 1/√12 ≈ 0.29 °C
  that does not average out within 30 readings. The temperature model must include it.
- **How it judges.** One window against a threshold (Shewhart style, no memory), or a cumulative sum
  (CUSUM, with slack K and limit H) that remembers small persistent shifts. A wider threshold trades
  false alarms for delay; CUSUM changes the trade-off itself.

## How to decide
The constraints are to find a slow drift within 10 windows (5 minutes) and keep alarms rare enough to
be read. The lab fed 20 minutes of gateway telemetry from lab 17's network into each detector. From
minute 10, n5's link loss ramps from 0.15 to 0.45 and n3 reads up to 1.5 °C high. It also drew 1,000
nominal windows from the twin's own model (`drift_eval.py`):

| Detector | Windows to find n3 / n5 drift | False alarms on the run | Per 1,000 nominal |
|---|---|---|---|
| \|z\| > 2 per window | 7 / 7 | 13 | 80 |
| \|z\| > 3 per window | 10 / 9 | 3 | 12 |
| CUSUM K = 0.75, H = 5 | 8 / 9 | 2 | 0 |

CUSUM keeps detection close to the tight threshold with almost no noise. The textbook slack K = 0.5
gave up to 7 false alarms per 1,000 windows on a 4 % link. That share is a skewed binomial, so
K = 0.75 was chosen on evidence, not by habit. Without slack (K = 0, tryIt) n5's sum crossed H before
the drift began, latched, and 74 false alarms per 1,000 followed.

## Failure modes at scale
- **Coupled devices.** The model treats links as independent, but n1's retry share rose while n5 was
  failing, because n5's retries load the shared relay. Watch for alarms on several boards at the same
  time.
- **Stale calibration.** After moving a board, everything the twin knew about it is wrong. A latched
  alarm should mean "re-calibrate or investigate", not "repair".
- **Twin trust.** The twin is a model. Its alarms are hypotheses for a person or for lab 21's
  explanation, never automatic actions.

## Common mistakes
- Comparing means of heavy-tailed quantities and then tuning thresholds against outliers.
- Calibrating on the same windows you test on.
- Copying K and H from a handbook without measuring the false-alarm rate on your own signal.
