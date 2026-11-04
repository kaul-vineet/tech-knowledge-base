# ADR 0018: Two-phase configuration updates with probation, rollback and a canary rollout

## Status
Accepted (2026-10-28). Measured on the CPython stub (validated-stub); a board/simulator run is pending.

## Context
The classroom fleet (six boards) needs configuration changes over the radio: sampling interval,
temperature alarm threshold, radio group. Constraints: no device may run a configuration version the
gateway has not acknowledged (otherwise the dashboard and the alarms describe a fleet that does not
exist); a bad configuration must not need a physical re-flash; at most one device may be exposed to a
bad version; links lose 10-30 % of frames. The lab measured (`fleet_sim.py`, seed 18, 10 % loss,
v2 good then v3 with a wrong radio group):

* One-phase push to all (`config_agent.py`): 12,086 device-ticks on unacknowledged versions; five
  devices end on v3 in group 99 and stay deaf (120,800 device-ms and counting).
* Two-phase with probation, push to all (`solution.py`): 0 unacknowledged ticks; 4 devices ran v3 at
  the same time, 12,000 device-ms deaf, then all rolled back; v2 complete at 1,210 ms; 99 gateway frames.
* Two-phase with probation, staged (canary 1 -> 2 -> 3): 0 unacknowledged ticks; 1 device ran v3,
  3,000 device-ms deaf, rollout halted after the canary; v2 complete at 1,850 ms; 34 gateway frames.

## Decision
We will use two-phase updates (prepare -> K, commit -> A), a 3 s probation in which the device repeats
A every 500 ms and rolls back to its last-good configuration if no OK arrives, and staged rollouts
(one canary, then two, then the rest) that halt on any R, N or wave timeout. The gateway's registry of
acknowledged versions is the source of truth. `test_fitness.py` keeps it true: 5 seeds x 10/30 % loss
x both strategies, unacked_ticks == 0, staged blast radius <= 1.

## Consequences
* Rollouts are slower (1.85 s vs 1.21 s for six boards here) and need more state on the device.
* A probation that is too short or a single report turns packet loss into false rollbacks (tryIt).
* Configuration lives in RAM in this lab; on a board, persist last-good to flash (open()/write, ~30 kB
  file system) or a reset reverts to the factory config. Configuration frames are not authenticated
  yet: ADR 0019 adds a MAC, otherwise anyone in radio range can push a "valid" config.
