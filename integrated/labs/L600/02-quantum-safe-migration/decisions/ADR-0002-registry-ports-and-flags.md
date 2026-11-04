# ADR-0002: Services resolve algorithms through a registry behind ports; rollout is driven by owned, expiring flags

## Status
Accepted (2026-10-30)

## Context
The inventory found algorithms named directly in six services and three config files. Every future change (hybrid
now, ML-KEM-only later, a broken parameter set) would again mean editing every service. During the rollout some
servers stay on v1 (X25519 only) for weeks, so the client behaviour has to change in steps without redeploying.

## Decision
- Services ask by purpose (key exchange, signature, AEAD for "messaging"); crypto_registry.py maps purpose -> adapter
  using a policy table and two flags: pq_hybrid_kex.messaging (offer the hybrid first) and pq_required.messaging
  (refuse classical-only). adapters.py is the only module that names primitives.
- Every resolution is recorded (AUDIT) so a runtime check can match what went on the wire to what the registry chose.
- Flags live in flags.json with owner and expiry (application-architecture L400 #20); pq_required may only be turned
  on when every server is v2 (seams.can_require_pq), and v2 servers also refuse classical groups when it is on.

## Consequences
- Moving to ML-KEM-only later is a policy change, not a code change in services.
- A static lint (cryptography L400 #17) keeps algorithm names out of services, but cannot see code that loads modules
  by name - hence the runtime wire contract (ADR-0004).
- Flags add states to test: the seam tests run every rollout phase (all-v1, mixed, all-v2, rollback-v1).
