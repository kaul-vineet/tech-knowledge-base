# ADR 0022: Build the capstone firmware from the labs' files, not from a copy

## Status
Accepted (2026-10-28).

## Context
The capstone board must combine lab 17's radio node (ARQ, jitter, relay) with lab 19's SipHash tags.
Copying both into one new file would fork them: a fix in lab 17 would silently not reach the capstone.
A micro:bit can hold several .py files (flat file system), but in the CPython stub one module object
would then be shared by all seven simulated boards and bind to the first board's radio. The capstone
also needs four small changes: a 96-byte radio length (a 64-bit tag in hex), sealing the payload,
relay dedupe on (seq, payload) and the sealing function itself.

## Decision
We will generate `build/classroom_node.py` with `build_firmware.py` from `frame_auth.py` (lab 19) and
lab 17's `solution.py`, applying the patches listed in `firmware_patches.json`; every patch must
match exactly once or the build fails. Tests check that the generated file parses and contains both
parts.

## Consequences
A change in lab 17 or 19 reaches the capstone on the next build, or breaks the build loudly when a
patch no longer matches. The generated file is the one to flash; learners must edit the labs, not the
build output. Patching by text is fragile against reformatting - the "exactly once" rule is the guard.
