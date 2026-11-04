# ADR-001: Session capability tokens are macaroon-style chained-HMAC tokens with first-party caveats

## Status
Accepted (2026-10-30). Fitness: `tests/test_m2_capabilities.py`, `tests/test_fitness.py` (F3), seam `tests/test_seam_scope_args.py`.

## Context
Every agent session must be limited to the tools - and argument shapes - its task needs, for a short time, and a
sub-agent should be able to receive a NARROWER token without calling back to the issuer. Only one service verifies
tokens: this host. Options measured in the lab: (1) a server-side session table (no offline narrowing, every
check is a lookup); (2) a signed JWT-style token (cryptography L200 #11) with a `scope` claim - narrowing needs the
issuer to sign a new token; (3) a macaroon (Birgisson et al., NDSS 2014): sig_i = HMAC(sig_{i-1}, caveat_i), so any
holder can append a caveat but nobody can remove one. Token size here: 4 caveats -> 5 HMAC-SHA256 computations,
a 32-byte tag, a 252-character base64url token for the corpus session.

## Decision
We will mint one macaroon per session with caveats `session = <id>`, `expires < <now+ttl>` (ttl <= 300 s),
`tool in <list>` and optional `arg <tool>.<field> prefix|endswith|in <value>`. The host verifies the chain with its
root key and then requires EVERY caveat to hold for the parsed, schema-valid arguments; unknown caveats fail
(deny by default). Path arguments are normalised and email arguments must be a single address before matching.

## Consequences
- Narrowing for sub-agents is offline and safe: try_it_2 shows attenuation can never widen.
- A symmetric root key means only the host can verify; a second verifier would need the key or a switch to
  public-key tokens (option 2) - revisit if tools move to separate services.
- Caveat checks are only as good as the argument they see: the scope<->argument seam is tested with traversal,
  recipient lists and type confusion. Revocation before expiry needs a deny-list (not built: short TTL instead).
