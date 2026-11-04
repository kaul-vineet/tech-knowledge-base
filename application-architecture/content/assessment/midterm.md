# Midterm exam – Application Architecture (week 7)

**Covers:** L100 lessons 1–6, L200 lessons 7–11, L500 lesson 23. **Time:** 90 minutes. **Total:** 60 marks.
**Allowed:** one A4 sheet of your own notes; no devices. Show reasoning – a correct number without working earns half marks.
Numbers in model answers were computed by code (`research/l500_checks.py`, section "exam numbers").

---

### Q1 (derivation / proof, 10 marks)
(a) Define a strict layering of a dependency graph. (b) Prove that a graph with a strict layering has no cycle.
(c) The architecture guide of a team says "a module may depend on modules in its own layer or below". Give the smallest
counterexample showing this rule does not prevent cycles.

**Model answer.** (a) A function ℓ from modules to natural numbers with ℓ(u) > ℓ(v) for every dependency u → v (2).
(b) A cycle v₀ → v₁ → … → v_k = v₀ would give ℓ(v₀) > ℓ(v₁) > … > ℓ(v_k) = ℓ(v₀), i.e. ℓ(v₀) > ℓ(v₀) – impossible (5:
cycle set-up 1, strictness on every edge 2, contradiction 2). (c) Two modules a, b in the same layer with a → b and
b → a: both satisfy "same layer or below", and a → b → a is a cycle (3).

### Q2 (calculation, 10 marks)
A service has six modules and these import edges: web → svc, cli → svc, svc → port, sqlite → port, app → web, app → cli,
app → svc, app → sqlite. `port` contains 2 classes, both abstract Protocols; `svc` contains 3 concrete classes; every
other module has at most one concrete class. (a) Compute Ca, Ce, I, A and Dn = |A + I − 1| for `svc` and `port`.
(b) Give a strict layering. (c) Which module is furthest from the main sequence, and is that a problem?

**Model answer.** (a) svc: Ca = 3 (web, cli, app), Ce = 1 (port), I = 0.25, A = 0, Dn = 0.75. port: Ca = 2 (svc, sqlite),
Ce = 0, I = 0, A = 1, Dn = 0 (5). (b) Longest-path layering: port 0; svc 1, sqlite 1; web 2, cli 2; app 3 (2). (c) svc,
Dn = 0.75: stable (three dependents) and fully concrete – Martin's "zone of pain" side. It is expected for a domain service
that holds the rules; reduce the pain by keeping its interface small and stable, or by having adapters depend on an
abstract port rather than on svc's concrete classes (3).

### Q3 (short explanation, 8 marks)
Parnas (1972) compares two decompositions of a KWIC index. Explain the criterion behind the second decomposition and why
it makes a change to "how lines are stored in memory" cheaper. Name one cost Parnas himself acknowledges.

**Model answer.** Criterion: each module hides a design decision likely to change, behind an interface that does not
reveal it (3). In the conventional, processing-step decomposition the storage format is known by input, shift,
alphabetise and output, so all change; in the hiding decomposition only the line-storage module knows it (3). Cost: if
modules are implemented naively as subroutine calls, the hiding decomposition may be less efficient – he sketches another
way to implement it (2).

### Q4 (prediction, 8 marks)
In lesson 5 you start the service with `LOANS_PORT=abc` and `LOANS_LOG_LEVEL=LOUD`. Predict what happens, the exit code,
and why this behaviour is preferable to starting with defaults.

**Model answer.** The service refuses to start, prints one message listing both errors (`LOANS_PORT='abc' is not an
integer; LOANS_LOG_LEVEL='LOUD' must be one of [...]`) and exits with code 2 (4). Fail-fast configuration turns a silent
misconfiguration into an immediate, explicit failure at deploy time, before any request is served; reporting all errors at
once saves redeploy cycles (4).

### Q5 (prediction, 8 marks)
In lesson 9 the relay publishes the same `LoanCreated` event twice (the process crashed after publishing, before marking
the outbox row as sent). A naive consumer and an idempotent consumer both send a confirmation e-mail. Predict how many
e-mails each sends and explain the mechanism that makes the difference.

**Model answer.** Naive: 2 e-mails; idempotent: 1, the duplicate is ignored (the lab prints "naive consumer sent 2 mails,
idempotent consumer sent 1") (4). The idempotent consumer records the `eventId` of each handled event and skips any event
it has already processed; the outbox gives at-least-once delivery, so duplicates are expected and must be absorbed by the
consumer (4).

### Q6 (design critique, 10 marks)
A pull request enforces "at most 3 active loans per member" in the HTTP handler. The CLI adapter and the nightly import
job call the repository directly. Critique the design using lessons 7 and 8 and propose a fix with a test.

**Model answer.** The rule lives in one driving adapter, so other paths (CLI, import job) bypass it; the invariant is not a
property of the domain and can be violated (4). Fix: move the check into the aggregate root (`Member.borrow`) or the
domain service behind the driving port, make all adapters go through it, and expose loans read-only (3). Test: a
domain-level unit test that the fourth borrow raises `LoanLimitReached` without changing state, plus a boundary check that
adapters do not import the repository directly (3).

### Q7 (short explanation, 6 marks)
In lesson 10, what attack does PKCE (S256) prevent in the authorization-code flow, and what must the relying party still
check on the ID token?

**Model answer.** PKCE binds the code exchange to the client that started the flow: an attacker who intercepts the
authorization code cannot redeem it without the `code_verifier` whose SHA-256 hash was sent as `code_challenge` (3). The
relying party must still verify the token signature and the `iss`, `aud`, `exp`, `iat` and `nonce` claims, and check
`state` on the redirect (3).
