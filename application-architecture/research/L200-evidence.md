# L200 research evidence – Application Architecture (lessons 7–11)

Method (SPEC.md, unchanged): 2–3 implementation questions per lesson → web_search / web_fetch of official
docs, specs and maintained OSS → screen out marketing, stale or unclear-licence items → score kept sources
0–2 on implementable (I), current (C), authoritative (A), open (O), transferable (T), right depth (D) →
keep ≥ 8/12 → cross-check each claim against ≥ 2 sources (≥ 1 official) or a local run.
All fetches were done on 2026-10-28. Scores are given as I/C/A/O/T/D = total.

---

## Node 24 move (all lessons that use Node: 1, 6, 9; CI)
**Questions.** (1) Is Node 24 an LTS line today, and until when? (2) What are the exact brew and winget ids for Node 24?

| Source | Decision | Score | Reason |
|---|---|---|---|
| github.com/nodejs/Release (README + schedule.json) | kept | 2/2/2/2/1/2 = 11 | Official schedule |
| nodejs.org/en/about/previous-releases | kept | 1/2/2/2/1/2 = 10 | Official status table |
| formulae.brew.sh node@24 / node@22 | kept | 2/2/2/2/0/2 = 10 | Formula versions and deprecation dates |
| github.com/microsoft/winget-pkgs OpenJS/NodeJS (/, /LTS, /22) | kept | 2/2/1/2/0/2 = 9 | Which package ids and versions exist |

**Key facts**
- Node 24 "Krypton" started 2025-05-06 and entered LTS on 2025-10-28. Maintenance started 2026-10-20, and end-of-life is 2028-04-30 (schedule.json). Node 26 is scheduled to enter LTS on 2026-10-28. Node 22 reaches end-of-life on 2027-04-30. Sources: https://raw.githubusercontent.com/nodejs/Release/main/schedule.json, https://github.com/nodejs/Release. The nodejs.org table lists v24 as "LTS" (last updated Oct 20, 2026): https://nodejs.org/en/about/previous-releases. **Conclusion:** Node 24 is a supported LTS line (Maintenance LTS from 2026-10-20).
- Homebrew `node@24` is at 24.22.1, keg-only, with deprecation 2027-10-30 and disable 2028-10-30. `node@22` is at 22.23.4, with deprecation **2026-10-30**. Sources: https://formulae.brew.sh/formula/node@24, https://formulae.brew.sh/formula/node@22
- winget has no `OpenJS.NodeJS.24` id; only a `22` sub-package exists. The latest `OpenJS.NodeJS.LTS` manifest is 24.19.0, but that id follows the newest LTS line (26 from 2026-10-28). The lessons therefore pin `--version 24.19.0`. Sources: https://github.com/microsoft/winget-pkgs/tree/master/manifests/o/OpenJS/NodeJS/LTS, https://github.com/microsoft/winget-pkgs/tree/master/manifests/o/OpenJS/NodeJS

## Lesson 7 – Hexagonal architecture
**Questions.** (1) Who owns ports, and which way do dependencies point? (2) How are driving and driven adapters wired? (3) How do you express a port in Python without a framework?

| Source | Decision | Score | Reason |
|---|---|---|---|
| AWS Prescriptive Guidance – Hexagonal architecture | kept | 2/2/1/1/2/2 = 10 | Python example; applicability + maintenance-overhead caveats. AWS-specific sections ignored |
| jmgarridopaz.github.io – Ports and Adapters Pattern | kept | 2/1/1/2/2/2 = 10 | Driver/driven ports, composition root, test adapters (author reviewed with Cockburn's terms) |
| docs.python.org typing (Protocol, structural subtyping) | kept (supporting) | 2/2/2/2/1/1 = 10 | `Protocol`; runtime does not enforce annotations |
| alistair.cockburn.us/hexagonal-architecture | **dropped** | – | Content filter withheld the page (again, as in L100) |

**Key facts**
- The pattern was proposed by Alistair Cockburn in 2005. Ports are technology-agnostic entry points, and adapters translate a technology to a port. Source: AWS page (above).
- "Ports belong to the application". Driven adapters implement a driven port, driver adapters use a driver port, and a composition root picks the adapters at startup. Source: https://jmgarridopaz.github.io/content/hexagonalarchitecture.html. Cross-checked by the AWS page ("exchange dependent components by changing the adapter") and by our own run (`domain.py` imports only `dataclasses` and `ports`).
- "The Python runtime does not enforce function and variable type annotations". Source: https://docs.python.org/3/library/typing.html. The lab's tryIt 2 shows the consequence: `isinstance` is False and the error only appears on the call.

## Lesson 8 – Aggregates and invariants
**Questions.** (1) What is the consistency boundary, and how is it persisted? (2) How do you stop concurrent lost updates without locks? (3) Where do rules that span aggregates go?

| Source | Decision | Score | Reason |
|---|---|---|---|
| Fowler – DDD_Aggregate | kept | 1/1/2/2/2/2 = 10 | Load/save whole aggregates; transactions do not cross boundaries |
| DDD Community – Vernon, Effective Aggregate Design | kept | 1/1/2/1/2/1 = 8 | Small aggregates, true invariants (summary page; PDFs not fetched) |
| SQLite – Partial Indexes | kept | 2/2/2/2/1/2 = 11 | Unique partial index example (one leader per team) |
| Python 3.12 sqlite3 docs | kept (supporting) | 2/2/2/2/1/2 = 11 | Transaction control, legacy mode default |

**Key facts**
- "Aggregates are the basic element of transfer of data storage - you request to load or save whole aggregates. Transactions should not cross aggregate boundaries." Source: https://martinfowler.com/bliki/DDD_Aggregate.html
- A `UNIQUE` partial index "provides a mechanism for enforcing uniqueness across some subset of the rows". Partial indexes are supported since SQLite 3.8.0. Source: https://sqlite.org/partialindex.html. Verified locally: the second active loan of b1 fails with "UNIQUE constraint failed: loans.book_id".
- `autocommit` defaults to `LEGACY_TRANSACTION_CONTROL` in 3.12. DML implicitly opens a transaction, and the connection context manager commits or rolls back. Source: https://docs.python.org/3.12/library/sqlite3.html. Cross-checked by tests: the rollback leaves version 0.

## Lesson 9 – Event-driven integration
**Questions.** (1) How do you update the database and publish an event atomically without 2PC? (2) What delivery guarantee results, and what must consumers do? (3) What is the current AsyncAPI version, and what does a v3 operation look like?

| Source | Decision | Score | Reason |
|---|---|---|---|
| microservices.io – Transactional outbox | kept | 2/2/1/1/2/2 = 10 | Problem, forces, relay, duplicates → idempotent consumers. Book/course promotion on the page ignored |
| microservices.io – Domain event | kept (supporting) | 1/2/1/1/2/1 = 8 | Aggregates emit domain events; outbox publishes them |
| AsyncAPI Specification 3.1.0 | kept | 2/2/2/2/2/2 = 12 | Required fields, channels, operations (`send`/`receive`), messages; Apache-2.0 |
| AsyncAPI 3.1.0 release notes | kept | 1/2/2/2/1/2 = 10 | 3.1.0 = minor, no breaking changes, switch by version string |
| github.com/asyncapi/spec releases | kept (supporting) | 1/2/2/2/0/2 = 9 | v3.1.0 latest (2026-01-31) |
| github.com/asyncapi/cli releases | kept (supporting) | 1/2/2/2/0/2 = 9 | CLI v6.2.1 (pin) |
| npmjs.com @asyncapi/cli | **dropped** | – | Fetch returned no document |

**Key facts**
- The outbox: "store the message in the database as part of the transaction that updates the business entities. A separate process then sends the messages". Messages are sent "if and only if the database transaction commits", in order. The relay "might publish a message more than once", so "a message consumer must be idempotent". Source: https://microservices.io/patterns/data/transactional-outbox.html. Cross-checked by tests (`test_failed_event_rolls_back_the_change`, `test_redelivery_is_ignored_by_idempotent_consumers`).
- AsyncAPI 3.1.0 is the latest version. It is "a minor release" that adds ROS 2 bindings; documents switch from `'3.0.0'` to `'3.1.0'` "without any issues". Sources: https://www.asyncapi.com/blog/release-notes-3.1.0, https://github.com/asyncapi/spec/releases. **Decision:** the lesson targets 3.1.0 (the user asked for 3.0; 3.1.0 is the verified current version, compatible).
- `asyncapi` and `info` (title, version) are REQUIRED. An operation's `action` is `"send" | "receive"`, and `channel` must be a `$ref` to a root channel. An operation's `messages` must be a subset of that channel's messages. "Every message sent to this channel MUST be valid against one, and only one, of the message objects". Source: https://www.asyncapi.com/docs/reference/specification/v3.1.0. These are implemented in `asyncapi_check.py`; the official CLI runs in CI.

## Lesson 10 – OpenID Connect
**Questions.** (1) Which parameters does the code flow need, and what does each prevent? (2) How is PKCE S256 computed and verified (test vector)? (3) Which ID token claims must the RP check?

| Source | Decision | Score | Reason |
|---|---|---|---|
| OpenID Connect Core 1.0 (errata set 2) | kept | 2/2/2/2/2/2 = 12 | §2 claims (iss, sub, aud, exp, iat, nonce, azp), §3.1.2.1 request params. §3.1.3.7 not retrieved (page truncated) |
| RFC 7636 (PKCE) | kept | 2/2/2/2/2/2 = 12 | Verifier 43–128 chars, S256, invalid_grant, Appendix B vector |
| RFC 9700 (OAuth 2.0 Security BCP) | kept | 2/2/2/2/2/2 = 12 | PKCE for public clients and RECOMMENDED for confidential; no implicit/ROPC; exact redirect match |
| Keycloak – Getting started (Docker) + Securing apps (OIDC endpoints) | kept | 2/2/2/2/1/2 = 11 | Image 26.8.1, `start-dev`, `/realms/{realm}/.well-known/openid-configuration` |
| Python secrets docs | kept (supporting) | 2/2/2/2/1/2 = 11 | `token_urlsafe`, 32 bytes guidance, `compare_digest` |
| safeguard.sh "OIDC ID token validation checklist" (search result) | **dropped** | – | Vendor blog with a sales funnel; not authoritative |

**Key facts**
- `aud` "MUST contain the OAuth 2.0 client_id of the Relying Party". After `exp` the token "MUST NOT be accepted", with "some small leeway, usually no more than a few minutes". If `nonce` is present, clients "MUST verify that the nonce Claim Value is equal to the value of the nonce parameter sent". ID tokens "MUST NOT use none as the alg value" unless registered for code flow. Source: https://openid.net/specs/openid-connect-core-1_0.html §2. Cross-checked by RFC 9700 and by tests.
- When max_age is used, "the ID Token returned MUST include an auth_time Claim Value". This is the build task. Source: same, §3.1.2.1.
- PKCE: `code_challenge = BASE64URL-ENCODE(SHA256(ASCII(code_verifier)))`, a verifier of 43–128 characters, S256 "Mandatory To Implement", and a mismatch → `invalid_grant`. Appendix B: `dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk` → `E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM`. Source: https://www.rfc-editor.org/rfc/rfc7636. Verified by `test_rfc7636_appendix_b_vector`.
- "Public clients MUST use PKCE"; for confidential clients PKCE "is RECOMMENDED". Authorization servers must use exact redirect URI matching, should publish `code_challenge_methods_supported`, and the implicit grant SHOULD NOT be used. Source: https://www.rfc-editor.org/rfc/rfc9700.html §2.1. Implemented in the mock IdP and `keycloak_check.py`.
- Keycloak runs with `docker run -p 127.0.0.1:8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:26.8.1 start-dev`. Its discovery endpoint is `/realms/{realm-name}/.well-known/openid-configuration`. Sources: https://www.keycloak.org/getting-started/getting-started-docker, https://www.keycloak.org/securing-apps/oidc-layers

## Lesson 11 – Testing pyramid
**Questions.** (1) What shape and layer names should a suite have? (2) How do you test a database adapter against a real database in Python? (3) How do you measure test duration precisely with the stdlib?

| Source | Decision | Score | Reason |
|---|---|---|---|
| martinfowler.com – The Practical Test Pyramid (Vocke) | kept | 2/1/2/1/2/2 = 10 | Layers, narrow integration tests, avoid an ice-cream cone |
| testcontainers.com – Getting started for Python | kept | 2/2/2/2/1/2 = 11 | `PostgresContainer("postgres:16-alpine")` + psycopg |
| PyPI testcontainers 4.15.0 / testcontainers-python Postgres docs | kept (supporting) | 2/2/2/2/0/2 = 10 | Version pin; `driver=None` → URL without driver |
| PyPI psycopg 3.3.6 | kept (supporting) | 1/2/2/1/0/2 = 8 | Version pin, `psycopg[binary]` (LGPL-3.0) |
| Python time.perf_counter (3.12) | kept (supporting) | 2/2/2/2/1/1 = 10 | "highest available resolution to measure a short duration" |
| testcontainers-python GitHub source (postgres module) | **dropped** | – | Fetch returned no document; readthedocs page used |

**Key facts**
- "Write lots of small and fast unit tests. Write some more coarse-grained tests and very few high-level tests". Narrow integration tests check "one integration point at a time". Source: https://martinfowler.com/articles/practical-test-pyramid.html. Measured locally with `pyramid.py`: unit 0.03–3.8 ms, integration 82–201 ms, e2e 0.6–4.9 s per test.
- The Testcontainers Python guide uses `PostgresContainer("postgres:16-alpine")` with psycopg 3. `PostgresContainer(..., driver=None)` gives a URL without a driver. Sources: https://testcontainers.com/guides/getting-started-with-testcontainers-for-python/, https://testcontainers-python.readthedocs.io/en/latest/modules/postgres/README.html. Not run locally (pending-ci).

## Concept notes
Worked-example numbers: `research/L200_concept_examples.py` → `research/L200-concept-examples-output.txt` (run 2026-10-28).
