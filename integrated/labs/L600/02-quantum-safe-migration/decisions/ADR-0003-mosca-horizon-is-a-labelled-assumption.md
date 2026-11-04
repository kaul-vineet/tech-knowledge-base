# ADR-0003: The quantum horizon z is a labelled planning assumption, never derived from our simulator

## Status
Accepted (2026-10-30)

## Context
The lab factors 15 and 21 on a 12- and 15-qubit statevector with a compiled oracle. Published estimates for RSA-2048
are 20 million noisy qubits / 8 hours (Gidney & Ekera 2019/2021) and less than a million noisy qubits / less than a week
(Gidney 2025), both under stated hardware assumptions. None of these is a date. Mosca's inequality (x + y > z, as
stated in NIST IR 8547) needs z in years, and a too-large z silently empties the P1 list (z = 15 gives 0 P1 items).

## Decision
- migration_plan.Horizon carries z with a source that must be "planning-assumption" or a policy date; passing a
  simulator result raises TypeError. Today: z = 10, "team planning value for 2026, not a forecast".
- Statements about real key sizes may only quote CITED sources (estimates.check_claims); the simulator may only make
  claims about the N it ran.
- Mosca's inequality is strict: records (7 + 3 = 10, z = 10) is P2, not P1; the boundary is visible in the plan.

## Consequences
- Changing z is a reviewed one-line change with a reason; try_it shows z = 5 / 10 / 15 -> 5 / 3 / 0 P1 items.
- We cannot claim "safe until year N"; the plan is robust to z only within the range we test.
