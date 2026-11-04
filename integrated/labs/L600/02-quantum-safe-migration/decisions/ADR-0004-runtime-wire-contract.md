# ADR-0004: A runtime wire contract backs the static inventory and lint

## Status
Accepted (2026-10-30)

## Context
In the failure lab a "latency fast path" in messaging loads the X25519 module by name from a config string and skips
the registry. The AST inventory reports messaging as migrated, F1 passes and the agility lint finds nothing, yet all
messaging sessions are classical X25519 while the rollout flag still allows it. Static analysis cannot see a module
named in a runtime string.

## Decision
- Seam test S3 records every flight (wire.Tap) and checks that the groups offered equal registry.expected_offers()
  and that every share and signature has the size its adapter advertises (1216/1120 B hybrid, 3309 B ML-DSA-65).
- Fitness F3 also requires at least one client registry resolution per handshake (AUDIT), in every rollout phase.
- The build task extends the inventory to report importlib.import_module / __import__ of cryptography modules.

## Consequences
- The bypass fails S3 and F3 (run_project.py --inject bypass exits 1) months before pq_required would have broken it.
- The contract needs a traffic run per rollout phase in CI; in production the same check reads TLS telemetry
  (negotiated group per connection) - pending, not built here.
