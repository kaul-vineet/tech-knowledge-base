# L400 research evidence – Application Architecture (lessons 17–21 + capstone 22, "design it")

Method: unchanged from SPEC.md. Per lesson: 2–3 design questions → web_search / web_fetch of specs, official docs, primary
articles and maintained OSS → screen out vendor pages and unverifiable claims → score kept sources 0–2 on implementable (I),
current (C), authoritative (A), open (O), transferable (T), right depth (D) → keep ≥ 8/12 → cross-check each claim against
≥ 2 sources or a local run. All fetches on 2026-10-28. "search-only" = seen in a search result, not fetched; not used as a source.
Every number in the notes and ADRs comes from code that ran: `research/L400_concept_examples.py` →
`research/L400-concept-examples-output.txt`, and the lab READMEs.

## Lesson 17 – Strangler-fig decomposition
**Questions.** (1) What are the stages of an incremental extraction and which transitional code do they need? (2) How does a
parallel run compare results safely, and what must it never do? (3) What evidence justifies a cut-over?

| Source | Decision | Score | Reason |
|---|---|---|---|
| martinfowler.com/bliki/StranglerFigApplication.html (2024) | kept | 1/2/2/2/2/2 = 11 | Gradual replacement; transitional architecture is worth its cost; seams |
| martinfowler.com/bliki/BranchByAbstraction.html (2014) | kept | 2/1/2/2/2/2 = 11 | Abstraction layer, two implementations, flags to compare, delete the old |
| martinfowler.com/articles/patterns-legacy-displacement/transitional-architecture.html (2022) | kept | 1/2/2/2/2/2 = 11 | Transitional architecture must be removed; plan for its removal |
| github.com/github/scientist (README, MIT) | kept | 2/2/2/2/2/2 = 12 | use/try, always returns control, compare/clean/ignore, publish; "only safe for methods that aren't changing data" |
| import-linter.readthedocs.io/en/stable/contract_types/ | kept (equivalent + tool) | 2/2/2/2/1/2 = 11 | `forbidden` contract, `ignore_imports` |

**Key facts.** Scientist "will always return whatever the use block returns", randomizes order, compares, records exceptions in
the candidate and "is only safe for wrapping methods that aren't changing data" (github/scientist). Branch by abstraction lets
"multiple implementations co-exist" while the system "builds and runs correctly at all times" (Fowler). Transitional
architecture is software "we intend to remove when the displacement is complete" (Cartwright, Horn, Lewis).
Local run: 108 of 2,000 seeded requests differ (students at 1, 5, 9 … chargeable days); fixed service 0; HTTP shadow 3.0–26.6 s.

## Lesson 18 – Multi-tenancy
**Questions.** (1) Which isolation does each layout give and what does it cost to migrate? (2) How does SQLite behave for
"schema per tenant" (no CREATE SCHEMA) and for concurrent writers? (3) What database-side guard exists on server databases?

| Source | Decision | Score | Reason |
|---|---|---|---|
| postgresql.org/docs/current/ddl-rowsecurity.html (PostgreSQL 18) | kept | 2/2/2/2/2/2 = 12 | RLS default-deny, owner bypass, FORCE ROW LEVEL SECURITY |
| sqlite.org/limits.html (updated 2026-07-10) | kept | 2/2/2/2/1/2 = 11 | SQLITE_MAX_ATTACHED default 10, cannot exceed 125 |
| sre.google/sre-book/handling-overload/ | kept | 1/1/2/2/2/2 = 10 | Per-customer limits so only misbehaving customers get errors (noisy neighbour) |
| Vendor SaaS tenancy guides (AWS SaaS Lens, Azure tenancy models) | dropped (vendor) | – | Covered by primary sources and the lab's own measurements |

**Key facts.** "If no policy exists for the table, a default-deny policy is used"; table owners bypass RLS unless
`FORCE ROW LEVEL SECURITY` (PostgreSQL docs). "The number of simultaneously attached databases is limited to SQLITE_MAX_ATTACHED
which is set to 10 by default … cannot be increased above 125" (SQLite limits); reproduced locally: "too many attached databases - max 10".
Local run: shared schema leaked 686 of 700 rows with one missing filter; 20 of 20 neighbour writes blocked in one file, 0 with separate files.

## Lesson 19 – Policy as code
**Questions.** (1) What separates RBAC from ABAC, by the standards' definitions? (2) How are policies tested and covered? (3) What
belongs in a decision log and how is personal data kept out? (4) Which OPA version and licence are current?

| Source | Decision | Score | Reason |
|---|---|---|---|
| openpolicyagent.org/docs/policy-testing | kept | 2/2/2/2/2/2 = 12 | `test_` rules, `with input as`, `opa test -v`, coverage, `--fail-on-empty`, data-driven cases |
| openpolicyagent.org/docs/management-decision-logs | kept | 2/2/2/2/2/2 = 12 | Event fields (decision_id, path, input, result, bundles revision), `system.log.mask`, erased/masked |
| csrc.nist.gov/pubs/sp/800/162/upd2/final (SP 800-162) | kept | 1/1/2/2/2/2 = 10 | ABAC definition: attributes of subject, object, operation, environment |
| csrc.nist.gov/projects/role-based-access-control | kept | 1/1/2/2/2/1 = 9 | NIST RBAC model, INCITS 359-2012 (project archived; content stable) |
| github.com/open-policy-agent/opa + /releases | kept (version/licence) | 2/2/2/2/1/2 = 11 | Apache-2.0, CNCF graduated; v1.21.4 latest (≈2026-10-24) |
| formulae.brew.sh/formula/opa | kept (install) | 2/2/2/2/1/2 = 11 | `brew install opa`, stable 1.21.4, Apple-silicon bottles |
| winget-pkgs manifests for OPA | not fetched (page returned nothing) | – | Windows install documented as the release asset `opa_windows_amd64.exe` (seen on the releases page) |

**Key facts.** "Tests are expressed as standard Rego rules with a convention that the rule name is prefixed with test_"; `opa test`
reports PASS/FAIL/ERROR and coverage (OPA docs). Decision log events contain "the policy that was queried, the input to the query,
bundle metadata"; OPA "queries the data.system.log.mask path" and records `erased` pointers (OPA docs). ABAC evaluates "attributes
associated with the subject, object, requested operations, and … environment conditions against policy" (NIST SP 800-162).
v1.21.3 fixed a bundle signature side-step (GHSA-g2pf-6v5v-qcc8) – pin ≥ 1.21.3. Local run: RBAC 7/14, shipped policy 13/14, fixed 14/14.

## Lesson 20 – Evolutionary architecture and data migrations
**Questions.** (1) What are the phases of a backward-incompatible change done safely? (2) How do flags differ by category and how are
they retired? (3) How does an HTTP API announce deprecation and sunset? (4) What does SQLite support for column changes?

| Source | Decision | Score | Reason |
|---|---|---|---|
| martinfowler.com/bliki/ParallelChange.html (Sato, 2014) | kept | 2/1/2/2/2/2 = 11 | expand, migrate, contract; database refactoring; "discipline to finish" |
| martinfowler.com/articles/feature-toggles.html (Hodgson, 2017) | kept | 2/1/2/2/2/2 = 11 | Release toggles are transitional; expiry dates in toggle config; carrying cost |
| rfc-editor.org/rfc/rfc9745.html (March 2025, Standards Track) | kept | 2/2/2/2/2/2 = 12 | `Deprecation: @<epoch>`; Link rel="deprecation"; Sunset must not be earlier |
| rfc-editor.org/rfc/rfc8594.html (2019, Informational) | kept | 2/1/2/2/2/2 = 11 | `Sunset: <HTTP-date>`, a hint |
| sqlite.org/lang_altertable.html (updated 2026-10-05) | kept (supporting) | 2/2/2/2/1/2 = 11 | DROP COLUMN rewrites content; ALTER COLUMN … DROP NOT NULL since 3.53.0 |

**Key facts.** Parallel change "break[s] the change into three distinct phases: expand, migrate, and contract"; "if the contract phase
is not executed you might end up in a worse state" (Sato). Release toggles "should generally not stick around much longer than a week
or two"; teams add "an expiration date for toggles which are intended to be short lived" (Hodgson). RFC 9745: Deprecation is a
Structured-Field Date, e.g. `Deprecation: @1688169599`; the Sunset timestamp "MUST NOT be earlier". SQLite: DROP COLUMN "rewrites
its content"; `ALTER COLUMN … DROP NOT NULL` added in 3.53.0 (2026-04-09). The version that introduced DROP COLUMN is not stated on
the fetched page (see KNOWN-GAPS). Local run: big bang 36/100 failed; backfill-only guard 62/700; guarded 0/700; NOT NULL old column 38.

## Lesson 21 – Cost and capacity planning
**Questions.** (1) What does Little's law assume and what does it give? (2) How should capacity be modelled (QPS vs resources) and
what happens near saturation? (3) What headroom and spare policy keeps an SLO through failures and deploys?

| Source | Decision | Score | Reason |
|---|---|---|---|
| link.springer.com/content/pdf/10.1007/978-0-387-73699-0_5.pdf (Little & Graves) | kept | 1/1/2/1/2/2 = 9 | L = λW; requires stationarity, not distributions or server counts; back-of-envelope use |
| sre.google/sre-book/handling-overload/ | kept | 1/1/2/2/2/2 = 10 | "modeling capacity as queries per second … often makes for a poor metric"; per-customer limits |
| sre.google/workbook/alerting-on-slos/ | kept (from L300) | 2/1/2/2/2/2 = 11 | The SLO the plan must protect |
| MIT OCW 15.763J queuing formulas (Graves) | search-only | – | M/M/k formulas; not fetched, not used |

**Key facts.** Little's law L = λW "is remarkably simple and general … we require stationarity assumptions … [not] how many servers
there are … what the service time distributions are" (Little & Graves). Capacity should be measured "directly in available
resources"; QPS ratios change when software changes (SRE book). Local run: per-instance capacity 75 req/s at p99 ≤ 300 ms (80 req/s:
342.3 ms); sizing 6 / 3 / 3 instances; 2.08 USD per 1M requests at a stated hypothetical 0.10 USD per instance-hour.

## Capstone 22
**Questions.** (1) Which earlier decisions must hold together at release, and how is each measured? (2) How can an assistant help
without deciding? Sources: the lessons above, Patterns of Legacy Displacement (hub, fetched via search result text and the
Transitional Architecture page), OPA decision logs, Nygard's ADR post (already verified in L100). Local run: 19/19 GO; each of four
seeded faults NO-GO with the expected criteria.

## Learning tools (from the KB catalogue only)
import-linter, Structurizr (local), JupyterLab (+ JupyterLab Desktop), Keycloak, Swagger Editor v5 / Swagger UI, Grafana k6,
Bruno, Prometheus (+ expression browser, promtool). Install commands and licences copied from `shared/LEARNING-TOOLS-CATALOG.md`.
OPA is **not** in the catalogue: it appears only as an equivalent and as the CI engine for the same policy file.
