# ADR 0020: A calibrated twin with a CUSUM drift check, not a per-window threshold

## Status
Accepted (2026-10-28), on stub-network telemetry (validated-stub).

## Context
The gateway sees, per board, when each reading was taken and stored and what it said. A twin of the
network predicts two things per 30-reading window: the share of readings that needed a radio
retransmission (Monte Carlo of lab 17's ARQ on a link with loss l) and the temperature (a first-order
room model plus a per-board offset). Both are calibrated on the first 6 windows (3 minutes). The twin
must notice slow drift (a link getting worse, a sensor reading high) within 5 minutes, and an alarm
must be rare enough that a teacher still reads it. The lab measured on 20 minutes of telemetry from
lab 17's network (`drift_eval.py`; n5's link loss ramps 0.15 -> 0.45 and n3's sensor +1.5 C from
minute 10) and on 1,000 nominal windows drawn from the model itself:

* |z| > 2 per window (`twin.py`): both drifts after 7 windows; 13 false alarms on the run, 80 per 1,000.
* |z| > 3 per window: drifts after 9 and 10 windows; 3 false alarms, 12 per 1,000.
* CUSUM, K = 0.75, H = 5 (`solution.py`): drifts after 8 (temperature) and 9 (link) windows; 2 alarms on
  nominal streams of the run, 0 per 1,000. K = 0.5 (the textbook value) gave up to 7 per 1,000 at 4 %
  loss because the retry share is a skewed binomial there.

## Decision
We will run a CUSUM per board and signal on the twin's z-scores (K = 0.75, H = 5, alarm latched until
re-calibration) and compare a retry SHARE, not a mean latency, because one 2-second outlier moves a
window mean by 5 or more model standard deviations. `test_fitness.py` keeps it true: <= 5 alarms per
1,000 nominal windows at 4 % and 10 % loss (3 seeds each) and both drifts found within 10 windows.

## Consequences
* The twin needs re-calibration after a real change (moving a board); a latched alarm says "re-check".
* The model treats links as independent. On the run, n1's retry share rose while n5 was failing (n5's
  retries load the shared relay); the CUSUM flagged it at 1,050 s. The other alarm on a
  nominal stream (n2, 450 s) followed two windows with 5 of 30 readings retried each, a real burst. That is a model gap, not a sensor
  fault: the twin's alarms are hypotheses for a person or for lab 21's explanation, never actions.
* Whole-degree readings put a floor of 1/sqrt(12) C on the temperature residual's spread; smaller sensor
  drifts are invisible at 30-reading windows.
