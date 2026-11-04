# Concept: changing a fleet's configuration without losing track of it

## Why it matters
Once six boards are deployed, you will want to change them: sample faster, raise the alarm threshold,
move to another radio group. Re-flashing every board by hand does not scale, so configuration travels
over the radio. Then two new questions appear. Which configuration is each board actually running?
What happens when a change is wrong? A board that runs a version the gateway never acknowledged makes
the dashboard describe a fleet that does not exist. A bad radio group can make a board deaf to every
later fix.

## Mental model
**A ward round with sign-off.** The doctor (gateway) writes a new prescription (config v2). The nurse
(device) checks it can be given, puts it in the tray, and signs that it is ready (K). Only after the
doctor sees the signature does the doctor say "give it" (G). The nurse gives it, and keeps confirming
(A) until the doctor acknowledges (OK). If no acknowledgement comes within the agreed time, the nurse
goes back to the previous prescription and reports why (R). A new prescription is tried on one patient
(the canary) before the whole ward.

```
gateway: C(v2,cfg) ──► device: validate, stage ──► K(v2)
gateway: records K ──► G(v2) ──► device: keep last-good, apply, A(v2) every 500 ms
gateway: hears A ──► OK(v2) ──► device: probation over        no OK in 3 s ──► roll back, R(v2)
rollout: canary [n1] ─► [n2,n3] ─► [n4,n5,n6]     any R / N / timeout ─► HALT
```

## Design space
- **Device identity** must come from the device: `machine.unique_id()` on the board, never a typed-in
  name. **Versions** are integers that only increase. The gateway's registry of acknowledged versions
  per device is the source of truth.
- **One-phase push.** Apply on receipt, then ack. Simple, but the ack can be lost, and a change that
  cuts the board off has no way back.
- **Two-phase with probation.** Stage, ack, commit, confirm, with automatic rollback. A board never
  runs a version the gateway did not acknowledge, and a deaf board heals itself. The costs are more
  messages, more state on the device and a slower rollout.
- **Push-all versus staged.** Speed against blast radius. The canary waves trade time for exposure.

## How to decide
The constraints are a measurable invariant and a limit. Invariant: in every tick, every device runs a
version in the gateway's acknowledged set. Limit: at most one device ever runs a bad version. Run the
same seeded scenario (`fleet_sim.py`, 10 % loss; v2 good at t = 0, v3 with radio group 99 at 15 s) for
each option:

| Option | Unacked device-ticks | Devices on bad v3 | Deaf device-ms | v2 done | Gateway frames |
|---|---|---|---|---|---|
| One-phase, push-all | 12,086 | 5 (stuck) | 120,800 | 310 ms | 177 |
| Two-phase, push-all | 0 | 4 | 12,000 | 1,210 ms | 99 |
| Two-phase, staged | 0 | 1 | 3,000 | 1,850 ms | 34 |

Only the staged two-phase design meets both constraints. Its price, 640 ms more for six boards, is
cheap. The fitness test repeats the invariant over 5 seeds × 10 %/30 % loss × both strategies. The
probation parameters matter too. Report `A` once instead of every 500 ms, and a single lost frame
rolls back the GOOD v2 (final versions 111111). A 300 ms probation on a 30 % loss link does the same.
A safety net that is too tight produces false rollbacks.

## Failure modes at scale
- **Partial rollouts.** A halted rollout leaves mixed versions. The registry must show them, and the
  dashboard must group data by config version.
- **Persistence.** The lab keeps configuration in RAM. After a reset the board returns to factory
  settings unless last-good is written to flash. Watch for `reported` versions dropping to 1.
- **Long probations.** These multiply outage time for boards that really are broken. Watch the
  deaf device-ms.
- **Unauthenticated configuration.** A valid-looking C/G frame from anyone in range is accepted. Lab 19
  adds a MAC.

## Common mistakes
- Treating "sent" as "running": the registry must record acknowledgements, not intentions.
- A rollback that waits for the gateway: the device must decide alone, because it may be deaf.
- Rolling out to everyone because "the config is tiny"; size and risk are unrelated.
