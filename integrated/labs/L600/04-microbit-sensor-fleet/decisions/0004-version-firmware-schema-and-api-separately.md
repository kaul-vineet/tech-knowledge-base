# ADR 0004: Version the firmware record schema and the HTTP API separately; contracts pin the seam

## Status
Accepted (L600 #04). Guarded by `tests/test_seams.py` S4 and `tests/test_milestones.py` M4.

## Context
Firmware rolls out slowly: d17-d20 still run schema 1 (8-byte records, no light) next to schema 2 (9 bytes).
Dashboards upgrade on their own schedule: one still reads /v1. A gateway that assumes the newest layout misreads
or rejects old frames (`--inject schema-drift`: 2,880 readings never acked, 1,280 dropped from full flash logs).

## Decision
- The first byte of every frame is the schema; the gateway selects the record layout by it and rejects frames
  that are not a whole number of records. Firmware and gateway layout tables are compared by a test.
- The API is versioned in the path. /v2 exposes `schema` and returns `"light": null` for schema-1 devices.
  /v1 stays, with `Deprecation` (RFC 9745) and `Sunset` (RFC 8594) headers and a successor link.
- Each dashboard publishes a consumer contract (application-architecture L300 #14 ContractBuilder); the provider
  verifies both against the live API, bodies included.

## Consequences
+ Mixed fleets work; the v2 contract fails if a schema-1 device suddenly reports light 0 or loses `schema`.
- Contracts check shape, not completeness: with `--inject wallclock-lww` both contracts pass while 1,421 readings
  are gone. Completeness is a fitness function (F1), not a contract.
- Two API versions to run until the Sunset date.
