# 2. Re-plan the rest of the day when the demand twin's CUSUM alarms, not on a fixed timetable

## Status
Accepted (2026-10-28)

## Context
Today's demand runs 30% above forecast from 13:00. The feed is `data/today.jsonl`, one count per 15 minutes. Options:
- Static plan: the worst service level from 15:00 is 0.719.
- Re-plan every hour: needs a staffing run every hour even when nothing changed, and it chases Poisson noise.
- Event-driven: a scalar Kalman filter on the demand multiplier m plus the lesson 17 tabular CUSUM (k 0.5, h 8, inherited from `twin.Twin.drift_check`). Measured: no alarm before 13:00, alarm at 14:15 (75 min), m̂ 1.201. Re-planning from 15:00 adds 14 agent-hours and the worst service level becomes 0.896.

## Decision
Use the event-driven re-plan. When an alarm fires, scale the remaining hours by m̂ at alarm time and re-run the staffing optimiser from the next full hour.

## Consequences
- Hours 13:00-15:00 stay understaffed (detection delay plus the hour boundary). A lower h detects sooner but raises more false alarms (see lesson 17 tryIt 1).
- The re-planned rates (up to 6.16 calls/min) are outside the validated envelope (5.6), so the decision is published with a REVIEW flag (ADR 0003).
- Fitness function: `test_fitness.py::test_twin_alarm_timing` (no alarm before the surge, alarm within 90 min).
