# Verified resources – Application Architecture L100 + L200

All URLs below were retrieved with web_fetch on 2026-10-28. Score = rubric 0–2 each on implementable, current,
authoritative, open, transferable, right depth (max 12; kept ≥ 8). "Primary" = listed in the lesson's
`sources` (max 4 per lesson); "supporting" = used to verify a version or a single fact.

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| unittest — Unit testing framework | https://docs.python.org/3/library/unittest.html | docs | PSF docs licence (not re-checked on page) | page rendered for 3.15.2; CLI/discover options used exist in 3.12 (`--durations` added 3.12) | 11 | 1 (primary), all labs |
| Status of Python versions | https://devguide.python.org/versions/ | docs | not checked | 3.12 = security phase, EOL 2028-10 | 10 | 1 (primary) |
| mermaid-js/mermaid-cli | https://github.com/mermaid-js/mermaid-cli | repo | MIT | README checked 2026-10-28 (`mmdc -i … -o …`, Docker, npx `-p`; Podman example; brew install unsupported) | 11 | 1 (primary), 6, CI (one row; duplicate merged 2026-10-28) |
| @mermaid-js/mermaid-cli (npm) | https://www.npmjs.com/package/@mermaid-js/mermaid-cli | repo (registry) | MIT | latest 11.17.0 | 9 | 1, 6, CI (supporting – version pin) |
| Structurizr – local command | https://docs.structurizr.com/local | docs | free & open source (per page) | 2026-10-28 | 10 | 1 (primary), 6 |
| Structurizr – local Quickstart | https://docs.structurizr.com/local/quickstart | docs | as above | `docker run … structurizr/structurizr local` | 10 | 1, 6 (supporting) |
| Structurizr Lite (EOL notice) | https://docs.structurizr.com/lite | docs | – | Lite end-of-life, migrate to `local` | 9 | 1 (supporting) |
| Structurizr docs home | https://docs.structurizr.com/ | docs | commands free except `server` binaries | binaries v2026.09.19 | 8 | 1, 6 (supporting) |
| Presentation Domain Data Layering (M. Fowler) | https://martinfowler.com/bliki/PresentationDomainDataLayering.html | article (bliki) – background | free to read (copyright author) | 2015-08-26; concept unchanged | 9 | 2 (primary) |
| sqlite3 — DB-API 2.0 interface (3.12) | https://docs.python.org/3.12/library/sqlite3.html | docs | PSF docs licence | Python 3.12.16 docs | 12 | 2, 8 (primary); 7, 9, 11 |
| http.server — HTTP servers (3.12) | https://docs.python.org/3.12/library/http.server.html | docs | PSF docs licence | Python 3.12.15 docs | 11 | 2, 4 (primary) |
| Import Linter documentation | https://import-linter.readthedocs.io/en/stable/ | docs | BSD-2-Clause (repo) | stable docs; contract types forbidden/protected/layers/independence/acyclic siblings | 11 | 3 (primary) |
| seddonym/import-linter | https://github.com/seddonym/import-linter | repo | BSD-2-Clause | v2.15 released "last month" | 10 | 3 (supporting – licence) |
| Spring Modulith – Fundamentals | https://docs.spring.io/spring-modulith/reference/fundamentals.html | docs | not shown on page | current reference (nested modules "as of 1.3") | 9 | 3 (supporting) |
| ArchUnit | https://www.archunit.org/ | docs | not shown on fetched page | v1.5.0 (2026-08-04) | 9 | 3 (primary) |
| sverweij/dependency-cruiser | https://github.com/sverweij/dependency-cruiser | repo | MIT | 18.7.0 | 10 | 3 (primary) |
| ast — Abstract syntax trees | https://docs.python.org/3/library/ast.html | docs | PSF docs licence | 3.15 page; `Import`/`ImportFrom(module, names, level)` unchanged since 3.12 | 11 | 3 (primary), 2 (used in test) |
| OpenAPI Specification v3.1.2 | https://spec.openapis.org/oas/v3.1.2.html | spec | Apache-2.0 | 3.1.2, 19 Sep 2025 | 12 | 4 (primary) |
| OpenAPI Specification – versions index | https://spec.openapis.org/oas/ | spec | Apache-2.0 | lists 3.2.1, 3.2.0, 3.1.2, 3.1.1, 3.1.0 … | 10 | 4 (primary) |
| schemathesis/schemathesis | https://github.com/schemathesis/schemathesis | repo | MIT | master 2026-10 | 10 | 4 (primary, equivalent) |
| Pact Docs – Introduction | https://docs.pact.io/ | docs | not shown | last updated 2026-08-25 (page carries a commercial banner – ignored) | 8 | 4 (supporting, equivalent) |
| The Twelve-Factor App – III. Config | https://12factor.net/config | article/methodology | not checked | page text unchanged core rule | 9 | 5 (primary) |
| os — os.environ / getenv (3.12) | https://docs.python.org/3.12/library/os.html | docs | PSF docs licence | Python 3.12.15 docs; the /3/ page adds: on Windows keys are upper-cased; UTF-8 mode default only from 3.15 | 11 | 5 (primary), platform fixes |
| OWASP Secrets Management Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html | docs (community standard) | not checked on page | current page 2026-10-28 | 10 | 5 (primary) |
| C4 model – Diagrams | https://c4model.com/diagrams | docs | not checked | context + container "sufficient for most teams" | 10 | 6 (primary) |
| C4 model – Container | https://c4model.com/abstractions/container | docs | not checked | "Not Docker!" definition | 10 | 6 (supporting) |
| Mermaid – C4 Diagrams | https://mermaid.js.org/syntax/c4.html | docs | Mermaid is MIT (repo; not re-checked) | experimental; wrapping default since v11.17.1 | 9 | 6 (primary) |
| Mermaid – Diagram Syntax (reference) | https://mermaid.js.org/intro/syntax-reference.html | docs | Mermaid is MIT (repo; not re-checked) | re-fetched 2026-10-28 on mermaid.js.org (line comments after `%% `) | 9 | 6 (comments in `c4-container.mmd`) |
| plantuml-stdlib/C4-PlantUML | https://github.com/plantuml-stdlib/C4-PlantUML | repo | MIT | v2.15.0 beta in progress | 10 | 6 (supporting – macro cross-check) |
| Structurizr DSL – Language reference | https://docs.structurizr.com/dsl/language | docs | free & open source tooling | 2026-10-28 | 11 | 6 (primary) |
| Structurizr – validate command | https://docs.structurizr.com/validate | docs | as above | `validate -workspace <file>` | 9 | 6, CI (supporting) |
| Documenting Architecture Decisions (M. Nygard) | https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions | blog post (template origin) – background | CC0-style waiver stated on page | 2011-11-15 (original) | 10 | 6 (primary) |
| Architectural Decision Records (adr.github.io) | https://adr.github.io/ | docs/community | "some rights reserved" | 2026 page | 9 | 6 (supporting) |
| Monolith First (M. Fowler) | https://martinfowler.com/bliki/MonolithFirst.html | article (bliki) – background | free to read (copyright author) | 2015-06-03; argument unchanged | 9 | concepts: primer, note 3 |
| Bounded Context (M. Fowler) | https://martinfowler.com/bliki/BoundedContext.html | article (bliki) – background | free to read (copyright author) | 2014-01-15 | 8 | concepts: primer concept map (L200 topic) |
| RFC 9110 – HTTP Semantics | https://www.rfc-editor.org/rfc/rfc9110.html | spec | IETF Trust (Revised BSD for code) | Internet Standard, June 2022 | 10 | concepts: note 4 |
| Building Evolutionary Architectures (Ford, Parsons, Kua) – fitness functions | https://evolutionaryarchitecture.com/ | book site (authors) – background | © 2017 authors | retrieved via web search 2026-10-28; defines fitness functions as automated checks of what "fit" means | 8 | concepts: primer; lesson 3 sources (replaces the Thoughtworks Radar blip, F15) |
| The Twelve-Factor App (index) | https://12factor.net/ | methodology | © Salesforce (footer) | "Last updated 2017"; list of 12 factors | 9 | concepts: note 5 |

| Homebrew formula python@3.12 | https://formulae.brew.sh/formula/python@3.12 | package index | Python-2.0 (formula) | 3.12.16, arm64 bottles | 9 | 1 (supporting) |
| Homebrew formula node@24 | https://formulae.brew.sh/formula/node@24 | package index | MIT | 24.22.1, keg-only, deprecation 2027-10-30 (checked 2026-10-28) | 8 | 1, 6, 9 (supporting) |
| Homebrew formula node@22 (superseded) | https://formulae.brew.sh/formula/node@22 | package index | MIT | 22.23.4, deprecation 2026-10-30 – reason for the move to Node 24 | 8 | 1, 6 (history) |
| Homebrew formula podman / cask podman-desktop | https://formulae.brew.sh/formula/podman | package index | Apache-2.0 AND GPL-3.0-or-later | podman 6.1.4; cask 1.30.5 (https://formulae.brew.sh/cask/podman-desktop) | 8 | 1 (supporting) |
| Homebrew formula ollama | https://formulae.brew.sh/formula/ollama | package index | MIT | 0.40.11; `brew services start ollama` | 8 | 1 (supporting) |
| winget-pkgs manifests (Python.Python.3.12, OpenJS.NodeJS.LTS, RedHat.Podman, RedHat.Podman-Desktop, Ollama.Ollama) | https://github.com/microsoft/winget-pkgs/tree/master/manifests/p/Python/Python/3/12 | package index (repo) | MIT (repo) | folders present 2026-10-28; also /o/OpenJS/NodeJS (LTS), /r/RedHat, /o/Ollama/Ollama | 9 | 1 (supporting) |
| venv – Creation of virtual environments (3.12) | https://docs.python.org/3.12/library/venv.html | docs | PSF | 3.12.16 docs: activation per shell, ExecutionPolicy note | 11 | 1 |
| Using Python on Windows (3.12) | https://docs.python.org/3.12/using/windows.html | docs | PSF | 3.12.16 docs: `py -3.12`, UTF-8 mode | 11 | 1 |
| about_Environment_Variables (PowerShell) | https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables | docs | MIT (docs repo) / CC-BY | updated 2025-10-01: `$Env:`, Remove-Item Env:, case note | 11 | 5 |
| about_Execution_Policies (PowerShell) | https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies | docs | as above | updated 2026-08-31 | 9 | 1 (supporting) |
| about_Automatic_Variables (PowerShell) | https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables | docs | as above | `$LASTEXITCODE`, `$PWD` | 9 | 3, 5 (supporting) |
| Podman installation | https://podman.io/docs/installation | docs | Apache-2.0 (project) | machine on macOS VM / Windows WSL 2; Homebrew "not recommended" | 10 | 1 |
| Podman for Windows | https://github.com/containers/podman/blob/main/docs/tutorials/podman-for-windows.md | docs (repo) | Apache-2.0 | Podman 6: WSL 2/Hyper-V, Windows 11, `wsl --install`, Windows-path volumes | 10 | 1, 6 |
| structurizr/structurizr tags | https://hub.docker.com/r/structurizr/structurizr/tags | registry | not shown | 2026.09.19: linux/amd64 + linux/arm64, 267.71 / 266.8 MB | 8 | 6, CI (image pin; duplicate merged) |
| GitHub-hosted runners reference | https://docs.github.com/en/actions/reference/runners/github-hosted-runners | docs | CC-BY-4.0 (docs) | macos-latest = arm64 M1; no nested virtualization | 10 | CI |
| GitHub Actions contexts / workflow syntax | https://docs.github.com/en/actions/reference/workflows-and-actions/contexts | docs | CC-BY-4.0 | env allowed in defaults.run; bash on Windows = Git for Windows (https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) | 10 | CI |
| Ollama OpenAI compatibility | https://docs.ollama.com/api/openai-compatibility | docs | MIT (project) | `/v1/chat/completions` (OpenAI-compatible API) | 10 | 6 |
| Ollama hardware support | https://docs.ollama.com/gpu | docs | MIT (project) | Metal; NVIDIA CC 5.0+, driver 550+; AMD ROCm v7 / Vulkan | 9 | HARDWARE |
| Ollama on Windows (docs source) | https://github.com/ollama/ollama/blob/main/docs/windows.mdx | docs (repo) | MIT | Windows 10 22H2+, ≥ 4 GB binaries, NVIDIA/AMD | 9 | HARDWARE |
| qwen2.5:1.5b model page | https://ollama.com/library/qwen2.5:1.5b | model card | Apache-2.0 (1.5B) | 986 MB, Q4_K_M | 8 | 1, 6 |

**Kept: 38 sources** (21 distinct primary sources across the six lessons, plus 12 supporting sources for version and fact checks; 5 more were added for the concepts layer on 2026-10-28). Dropped items are listed in `research/L100-evidence.md`. **Platform + agent pass (2026-10-28): +21 sources** (package indexes, OS shell docs, Podman, Ollama, GitHub runners), all fetched that day; 59 in total.

## L200 (lessons 7–11) and the Node 24 move – all fetched 2026-10-28
| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| A. Cockburn – Hexagonal (Ports & Adapters) Architecture, original 2005 article | https://alistair.cockburn.us/hexagonal-architecture | article (pattern origin) | © A. Cockburn | 2005-09-04 (HaT TR 2005.02); text retrieved via web search 2026-10-28 (direct fetch still filtered) | 10 | 7 (primary) |
| AWS Prescriptive Guidance – Hexagonal architecture pattern | https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/hexagonal-architecture.html | vendor docs – one `equivalents` line only | not checked | page current 2026-10-28 | 10 | 7 (equivalents line; removed from sources, F15) |
| Ports and Adapters Pattern (J. M. Garrido de Paz) | https://jmgarridopaz.github.io/content/hexagonalarchitecture.html | article | not checked | 2018-08-29; concept unchanged | 10 | 7 (primary) |
| typing — Support for type hints | https://docs.python.org/3/library/typing.html | docs | PSF docs licence | page rendered for 3.15.2; Protocol exists in 3.12 | 10 | 7 (primary) |
| Martin Fowler – DDD_Aggregate | https://martinfowler.com/bliki/DDD_Aggregate.html | article (bliki) – background | free to read | 2013-04-23; concept unchanged | 10 | 8 (primary) |
| Vaughn Vernon – Effective Aggregate Design (DDD Community) | https://www.dddcommunity.org/library/vernon_2011/ | article index | not checked | 2011 (summary page; PDFs not fetched) | 8 | 8 (primary) |
| SQLite – Partial Indexes | https://sqlite.org/partialindex.html | docs | public domain (SQLite) | updated 2022-04-18; since 3.8.0 | 11 | 8 (primary) |
| microservices.io – Transactional outbox | https://microservices.io/patterns/data/transactional-outbox.html | pattern | © C. Richardson (free to read) | 2026 page | 10 | 9 (primary) |
| microservices.io – Domain event | https://microservices.io/patterns/data/domain-event.html | pattern | as above | 2026 page | 8 | 9 (primary) |
| AsyncAPI Specification 3.1.0 | https://www.asyncapi.com/docs/reference/specification/v3.1.0 | spec | Apache-2.0 | 3.1.0 (latest) | 12 | 9 (primary) |
| AsyncAPI Spec 3.1.0 release notes | https://www.asyncapi.com/blog/release-notes-3.1.0 | release notes (blog) – background | not checked | 2026-01-31 | 10 | 9 (primary) |
| asyncapi/spec releases | https://github.com/asyncapi/spec/releases | repo | Apache-2.0 | v3.1.0 latest | 9 | 9 (supporting) |
| asyncapi/cli releases | https://github.com/asyncapi/cli/releases | repo | Apache-2.0 | v6.2.1 (pinned) | 9 | 9, CI (supporting) |
| OpenID Connect Core 1.0 (errata set 2) | https://openid.net/specs/openid-connect-core-1_0.html | spec | OpenID Foundation notice | 2023-12-15 | 12 | 10 (primary) |
| RFC 7636 – PKCE | https://www.rfc-editor.org/rfc/rfc7636 | spec | IETF Trust (BSD code) | 2015, Proposed Standard | 12 | 10 (primary) |
| RFC 9700 – OAuth 2.0 Security BCP | https://www.rfc-editor.org/rfc/rfc9700.html | spec | IETF Trust (BSD code) | January 2025, BCP 240 | 12 | 10 (primary) |
| Keycloak – Securing apps with OIDC | https://www.keycloak.org/securing-apps/oidc-layers | docs | Apache-2.0 (project) | current guide | 11 | 10 (primary) |
| Keycloak – Getting started (Docker) | https://www.keycloak.org/getting-started/getting-started-docker | docs | Apache-2.0 (project) | image 26.8.1 | 11 | 10, CI (supporting) |
| secrets — secure random numbers | https://docs.python.org/3/library/secrets.html | docs | PSF docs licence | page for 3.15.2; API in 3.12 | 11 | 10 (supporting) |
| The Practical Test Pyramid (H. Vocke) | https://martinfowler.com/articles/practical-test-pyramid.html | article | free to read | 2018-02-26; concept unchanged | 10 | 11 (primary) |
| Getting started with Testcontainers for Python | https://testcontainers.com/guides/getting-started-with-testcontainers-for-python/ | guide | not checked | postgres:16-alpine, psycopg 3 | 11 | 11 (primary) |
| testcontainers (PyPI) | https://pypi.org/project/testcontainers/ | package index | Apache-2.0 | 4.15.0 (2026-07-24) | 10 | 11 (primary), CI |
| testcontainers-python – PostgresContainer | https://testcontainers-python.readthedocs.io/en/latest/modules/postgres/README.html | docs | Apache-2.0 | `driver=None` | 10 | 11 (supporting) |
| psycopg (PyPI) | https://pypi.org/project/psycopg/ | package index | LGPL-3.0-only | 3.3.6 (2026-09-18) | 8 | 11, CI (supporting) |
| time — perf_counter (3.12) | https://docs.python.org/3.12/library/time.html | docs | PSF docs licence | 3.12.15 docs | 10 | 11 (primary) |
| Node.js Release WG – schedule | https://github.com/nodejs/Release | repo | MIT | 24.x LTS 2025-10-28, maintenance 2026-10-20, EOL 2028-04-30 | 11 | 1, 6, 9, CI (supporting) |
| Node.js schedule.json | https://raw.githubusercontent.com/nodejs/Release/main/schedule.json | data | MIT | as above | 11 | as above (supporting) |
| Node.js – Releases | https://nodejs.org/en/about/previous-releases | docs | not checked | v24 "LTS", last updated 2026-10-20 | 10 | as above (supporting) |
| winget-pkgs OpenJS.NodeJS / OpenJS.NodeJS.LTS | https://github.com/microsoft/winget-pkgs/tree/master/manifests/o/OpenJS/NodeJS/LTS | package index (repo) | MIT (repo) | LTS manifests up to 24.19.0; no `.24` id | 9 | 1, 9 (supporting) |

**L200: +29 sources kept** (19 primary in lesson `sources`, 10 supporting), plus the `node@24` row added to the L100 table above. Dropped: Cockburn's hexagonal page (filtered),
npm @asyncapi/cli page and the testcontainers-python GitHub source (empty fetches), one vendor blog (sales funnel). Total now 89.

## Update pass – learning tools + review fixes (UPDATE-TOOLS-REVIEW-SPEC.md, 2026-10-28)
Tool facts come from the KB catalogue (`../../shared/LEARNING-TOOLS-CATALOG.md`, checked 2026-10-28 against these URLs).
| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| structurizr/structurizr (local) | https://github.com/structurizr/structurizr | repo | Apache-2.0 (open-core) | v2026.10.26 (catalogue); Lite archived 2026-02-04 | 10 | 6 (learningTools) |
| Swagger Editor | https://github.com/swagger-api/swagger-editor | repo | Apache-2.0 | v5.10.0 (2026-10-21, "add support for AsyncAPI 3.1.0" on the releases page) | 10 | 4, 9 (learningTools) |
| AsyncAPI Studio | https://github.com/asyncapi/studio | repo | Apache-2.0 | @asyncapi/studio 1.4.2 (catalogue) | 9 | 9 (learningTools) |
| Bruno | https://github.com/usebruno/bruno | repo | MIT (open-core) | v4.3.0 (catalogue) | 9 | 4, 11 (learningTools) |
| Keycloak – Getting started (Docker) | https://www.keycloak.org/getting-started/getting-started-docker | docs | Apache-2.0 (project) | 26.8.1 (already listed above for lesson 10) | 11 | 10 (learningTools) |
| import-linter | https://github.com/seddonym/import-linter | repo | BSD-2-Clause | 2.15 (already listed above for lesson 3) | 10 | 3, 7 (learningTools) |
| OpenAPI Specification v3.2.0 | https://spec.openapis.org/oas/v3.2.0.html | spec | Apache-2.0 | 3.2.0, 19 Sep 2025 (3.2.1 also listed); §2.1: minor versions may carry incompatible changes; Path Item `query`, `additionalOperations` | 12 | 4 (F11 rationale) |

**Dropped in this pass:** Thoughtworks Radar blip (vendor-adjacent, F15), AWS page as a source (kept as one `equivalents` line),
`mermaid.ai` URLs (replaced by mermaid.js.org), three duplicate rows (mermaid-cli, structurizr tags, sqlite3 3.12) and the
duplicate `os` page (merged into the 3.12 row). Blog posts are marked "background".

## L300 (lessons 12–16, 2026-10-28)
Details, questions and dropped candidates: `research/L300-evidence.md`. "primary" = in the lesson's `sources`.
| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| Martin Fowler – CQRS | https://martinfowler.com/bliki/CQRS.html | article | free to read | 2011-07-14; caution still current | 10 | 12 (primary) |
| Azure Architecture Center – CQRS pattern | https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs | docs (vendor) – background | not checked | updated 2025-02-21 | 11 | none since the L300 update pass (R3-13: replaced by Fowler / Young) |
| Kurrent – Python client catch-up subscriptions (checkpoints) | https://docs.kurrent.io/clients/python/v1.0/subscriptions | docs (vendor) | not checked | client docs v1.0 | 10 | 12 (one `equivalents` line only; source replaced by Fowler – Event Sourcing, R3-13) |
| Marten – Rebuilding projections | https://martendb.io/events/projections/rebuilding.html | docs | MIT (project) | features tagged 7.28–9.13 | 11 | 12 (primary) |
| Martin Fowler – CircuitBreaker | https://martinfowler.com/bliki/CircuitBreaker.html | article | free to read | 2014-03-06 | 11 | 13 (primary) |
| resilience4j – CircuitBreaker | https://resilience4j.readme.io/docs/circuitbreaker | docs | not checked | page "updated almost 2 years ago"; defaults listed | 10 | 13 (primary) |
| resilience4j – Bulkhead | https://resilience4j.readme.io/docs/bulkhead | docs | not checked | maxConcurrentCalls 25 | 10 | 13 (primary) |
| resilience4j releases | https://github.com/resilience4j/resilience4j/releases | repo | not checked | v2.4.0 latest (year inferred) | 8 | 13 (supporting) |
| Polly – circuit breaker strategy (repo docs) | https://github.com/App-vNext/Polly/blob/main/docs/strategies/circuit-breaker.md | docs | not checked | Polly 8.8.0 latest (year inferred) | 11 | 13 (primary) |
| Polly – strategies; rate limiter | https://www.pollydocs.org/strategies/index.html | docs | not checked | v8; AddConcurrencyLimiter (Polly.RateLimiting) | 10 | 13 (supporting) |
| Azure Architecture Center – Bulkhead / Circuit Breaker patterns | https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead | docs (vendor) – background | not checked | updated 2026-03-19 (circuit-breaker page 2025-03-21) | 10 | 13 (one `equivalents` line only, R3-13; source: Google SRE Book ch. 22) |
| Python – concurrent.futures | https://docs.python.org/3/library/concurrent.futures.html | docs | PSF docs licence | page for 3.15.2; API in 3.12 | 11 | 13 (primary) |
| Pact docs – Introduction | https://docs.pact.io/ | docs | not checked (Pact Foundation; commercial banner ignored) | updated 2026-08-25 | 12 | 14 (primary) |
| Pact docs – How Pact works | https://docs.pact.io/getting_started/how_pact_works | docs | as above | updated 2024-12-23 | 11 | 14 (supporting) |
| Pact docs – Python consumer / provider | https://docs.pact.io/implementation_guides/python/docs/consumer | docs | as above | consumer page 2025-10-31; provider page `/docs/provider` | 11 | 14 (primary) |
| pact-python (PyPI) | https://pypi.org/project/pact-python/ | package index | MIT | 4.2.0 (2026-10-22), Python ≥ 3.11 | 11 | 14 (primary), CI |
| pact-python releases | https://github.com/pact-foundation/pact-python/releases | repo | MIT | 4.0.0 removed pact.v2 | 8 | 14 (supporting) |
| Pact Broker – can-i-deploy | https://docs.pact.io/pact_broker/can_i_deploy | docs | MIT (broker) | updated 2022-10-05 | 10 | 14 (supporting) |
| Pact Specification | https://github.com/pact-foundation/pact-specification | spec (repo) | MIT | V4 current | 9 | 14 (supporting) |
| Ian Robinson – Consumer-Driven Contracts | https://martinfowler.com/articles/consumerDrivenContracts.html | article | free to read | 2006-06-12; concept unchanged | 10 | 14 (primary) |
| Google SRE Workbook – Alerting on SLOs | https://sre.google/workbook/alerting-on-slos/ | book chapter | free to read | table 5-8 | 12 | 15 (primary) |
| Google SRE Book – Service Level Objectives | https://sre.google/sre-book/service-level-objectives/ | book chapter | free to read | ch. 4 | 11 | 15 (primary) |
| Google SRE Workbook – Implementing SLOs | https://sre.google/workbook/implementing-slos/ | book chapter | free to read | 4-week window example | 12 | 15 (primary) |
| Prometheus – Histograms and summaries | https://prometheus.io/docs/practices/histograms/ | docs | Apache-2.0 (project) | native histograms preferred | 11 | 15 (primary) |
| Prometheus releases | https://github.com/prometheus/prometheus/releases | repo | Apache-2.0 | 3.15.1 (2026-10-21) | 8 | 15 (equivalents) |
| Grafana licensing | https://grafana.com/licensing/ | docs (vendor) | AGPL-3.0 (Grafana, Loki, Tempo) | change announced 2021-04-20 | 8 | none (Grafana OSS left lesson 15's learningTools in the L300 update pass) |
| Python – timeit (3.12) | https://docs.python.org/3.12/library/timeit.html | docs | PSF docs licence | served as /3/ (3.15.2); API same in 3.12 | 11 | 16 (primary) |
| Python – sqlite3 (set_trace_callback) | https://docs.python.org/3/library/sqlite3.html | docs | PSF docs licence | callback since 3.3 | 11 | 16 (primary) |
| Grafana k6 – Thresholds | https://grafana.com/docs/k6/latest/using-k6/thresholds/ | docs | AGPL-3.0 (k6) | latest docs | 11 | 16 (primary) |
| Grafana k6 – Install | https://grafana.com/docs/k6/latest/set-up/install-k6/ | docs | AGPL-3.0 (k6) | brew / winget / docker | 9 | 16 (supporting) |
| grafana/k6 releases | https://github.com/grafana/k6/releases | repo | AGPL-3.0 | v2.3.0 (2026-09-21) | 8 | 16 (supporting), CI |
| Django – Database access optimization | https://docs.djangoproject.com/en/6.1/topics/db/optimization/ | docs | BSD-3-Clause (project) | Django 6.1 | 12 | 16 (primary) |
| import-linter (PyPI) | https://pypi.org/project/import-linter/ | package index | BSD-2-Clause | 2.15 (2026-09-04) | 11 | 16 (primary, learningTools) |
| pytest-benchmark (PyPI) | https://pypi.org/project/pytest-benchmark/ | package index | BSD-2-Clause | 5.3.0 (2026-08-23) | 10 | 16 (equivalents) |
| pyperf (PyPI) | https://pypi.org/project/pyperf/ | package index | MIT | 2.10.0 (2026-02-07) | 10 | 16 (equivalents) |

**L300 update pass (UPDATE-L300-SPEC.md, 2026-10-28)** – primary sources for R3-13 and the new learning tools (tool facts from the KB catalogue):
| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| Martin Fowler – Event Sourcing | https://martinfowler.com/eaaDev/EventSourcing.html | article (primary) | free to read | 2005-12-12 (draft, author says no updates); "Complete Rebuild … re-running the events"; "Should it crash it replays the events" | 10 | 12 (primary) |
| Greg Young – CQRS Documents | https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf | paper (primary) | free to read | 2010; PDF reachable, text not extracted by the fetch tool – background only | 9 | 12 (background) |
| Google SRE Book – Addressing Cascading Failures (ch. 22) | https://sre.google/sre-book/addressing-cascading-failures/ | book chapter (primary) | free to read | "return with an error early, rather than waiting the full deadline"; cap one client at 25% of threads; retry budgets | 12 | 13 (primary) |
| Prometheus – Unit testing for rules (promtool) | https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/ | docs | Apache-2.0 (project) | latest docs; Prometheus 3.15.1 (catalogue) | 11 | 15 (learningTools) |
| Prometheus – Download | https://prometheus.io/download/ | download page | Apache-2.0 | 3.15.1 (catalogue) | 9 | 15 (learningTools install) |
| pact-broker-docker | https://github.com/pact-foundation/pact-broker-docker | repo | MIT | image pactfoundation/pact-broker, broker v2.122.0 (catalogue) | 10 | 14 (learningTools) |

**L300: +35 sources kept** (21 primary in lesson `sources`, 14 supporting/equivalents/background). Learning tools added from the
KB catalogue (facts and URLs from `../../shared/LEARNING-TOOLS-CATALOG.md`): marimo, Toxiproxy, JupyterLab, Grafana OSS, Grafana k6.
Dropped: microservices.io CQRS page (bootcamp promotion), Axon and evolutionaryarchitecture.com (search-only), Rails N+1 section (cut off),
Spring Cloud Contract as a recommendation (archived 2026-07-07; kept as one equivalents line).

## L400 (lessons 17–22, 2026-10-28)
All retrieved with web_fetch on 2026-10-28 unless marked. Scores and decisions: `research/L400-evidence.md`.

| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| Strangler Fig (M. Fowler) | https://martinfowler.com/bliki/StranglerFigApplication.html | article (primary pattern text) | free to read (copyright author) | 2024-08-22 | 11 | 17 (primary) |
| Branch By Abstraction (M. Fowler) | https://martinfowler.com/bliki/BranchByAbstraction.html | article | free to read (copyright author) | 2014-01-07 | 11 | 17 (primary) |
| Transitional Architecture (Cartwright, Horn, Lewis) | https://martinfowler.com/articles/patterns-legacy-displacement/transitional-architecture.html | article | free to read (copyright author) | 2022-03-28 | 11 | 17 (primary) |
| Patterns of Legacy Displacement (hub) | https://martinfowler.com/articles/patterns-legacy-displacement/ | article | free to read (copyright author) | 2024-03-05 (search-result text) | 9 | 22 (primary) |
| github/scientist | https://github.com/github/scientist | repo | MIT | README, main (last commit ≈ Sep 2026) | 12 | 17 (primary) |
| import-linter – Contract types | https://import-linter.readthedocs.io/en/stable/contract_types/ | docs | BSD-2-Clause | stable docs (forbidden, ignore_imports) | 11 | 17 (equivalents, learningTools) |
| PostgreSQL 18 – Row Security Policies | https://www.postgresql.org/docs/current/ddl-rowsecurity.html | docs | PostgreSQL licence | PostgreSQL 18 | 12 | 18 (primary) |
| SQLite – Implementation Limits | https://www.sqlite.org/limits.html | docs | public domain | updated 2026-07-10 | 11 | 18 (primary) |
| SQLite – ALTER TABLE | https://www.sqlite.org/lang_altertable.html | docs | public domain | updated 2026-10-05 | 11 | 20 (supporting) |
| Google SRE Book – Handling Overload | https://sre.google/sre-book/handling-overload/ | book chapter | free to read | online edition | 10 | 18, 21 (primary) |
| OPA – Policy Testing | https://www.openpolicyagent.org/docs/policy-testing | docs | Apache-2.0 (project) | docs for v1.21.x | 12 | 19 (primary) |
| OPA – Decision Logs | https://www.openpolicyagent.org/docs/management-decision-logs | docs | Apache-2.0 (project) | docs for v1.21.x | 12 | 19, 22 (primary) |
| open-policy-agent/opa | https://github.com/open-policy-agent/opa | repo | Apache-2.0 | README; CNCF graduated | 11 | 19 (equivalents) |
| OPA releases | https://github.com/open-policy-agent/opa/releases | releases | Apache-2.0 | v1.21.4 latest (≈2026-10-24); v1.21.3 fixes GHSA-g2pf-6v5v-qcc8 | 11 | 19 (version pin, CI) |
| Homebrew formula opa | https://formulae.brew.sh/formula/opa | package index | Apache-2.0 | stable 1.21.4 | 11 | 19 (Mac install) |
| NIST SP 800-162 (ABAC) | https://csrc.nist.gov/pubs/sp/800/162/upd2/final | standard (guide) | public domain (US gov) | 2014, updates 2019-08-02 | 10 | 19 (primary) |
| NIST CSRC – Role Based Access Control | https://csrc.nist.gov/projects/role-based-access-control | project page (archived) | public domain (US gov) | updated 2026-03-04 | 9 | 19 (primary) |
| Parallel Change (D. Sato) | https://martinfowler.com/bliki/ParallelChange.html | article | free to read (copyright author) | 2014-05-13 | 11 | 20 (primary) |
| Feature Toggles (P. Hodgson) | https://martinfowler.com/articles/feature-toggles.html | article | free to read (copyright author) | 2017-10-09 | 11 | 20 (primary) |
| RFC 9745 – Deprecation HTTP header | https://www.rfc-editor.org/rfc/rfc9745.html | spec (Standards Track) | IETF Trust | March 2025 | 12 | 20 (primary) |
| RFC 8594 – Sunset HTTP header | https://www.rfc-editor.org/rfc/rfc8594.html | spec (Informational) | IETF Trust | May 2019 | 11 | 20 (primary) |
| Little & Graves – Little's Law (ch. 5) | https://link.springer.com/content/pdf/10.1007/978-0-387-73699-0_5.pdf | book chapter (primary) | © Springer (free chapter PDF) | 2008 | 9 | 21 (primary) |

**L400: +22 sources kept** (19 primary in lesson `sources`, 3 supporting). Dropped: vendor SaaS tenancy guides (AWS, Azure),
MIT OCW queuing slides (search-only), the winget-pkgs page for OPA (fetch returned nothing).

## L500 (lessons 23–27, theory & rigour) – retrieved 2026-10-30
| title | url | type | licence | version-or-date checked | score/12 | used in lesson(s) |
|---|---|---|---|---|---|---|
| Parnas – On the criteria to be used in decomposing systems into modules (CACM 15(12), doi 10.1145/361598.361623) | https://cacm.acm.org/research/on-the-criteria-to-be-used-in-decomposing-systems-into-modules/ | paper (primary) | © ACM; ACM DL open access since 2026-01-01 – summarise only | Dec 1972 | 11 | 23, 27 (primary) |
| Martin – OO Design Quality Metrics: An Analysis of Dependencies | https://condor.depaul.edu/dmumaugh/OOT/Design-Principles/oodmetrc.pdf | paper (author's article, university mirror) | © 1994 R. C. Martin | 28 Oct 1994 | 10 | 23 (primary) |
| Zimmermann & Nagappan – Predicting defects using network analysis on dependency graphs (ICSE 2008) | https://www.microsoft.com/en-us/research/publication/predicting-defects-using-network-analysis-on-dependency-graphs/ | paper (empirical) | © ACM | May 2008 | 10 | 23, 25 (primary) |
| El Emam, Benlarbi, Goel & Rai – The confounding effect of class size on the validity of OO metrics (IEEE TSE 27(7)) | https://www.computer.org/csdl/journal/ts/2001/07/e0630/13rRUIJuxro | paper (empirical; abstract only) | © IEEE | Jul 2001 | 9 | 23, 25 (primary) |
| MacCormack, Rusnak & Baldwin – Exploring the structure of complex software designs (HBS working paper; Management Science 52(7)) | https://www.hbs.edu/ris/Publication%20Files/05-016.pdf | paper (empirical) | © authors / INFORMS | 2006 | 10 | 25 (primary) |
| Liskov & Wing – A behavioral notion of subtyping (TOPLAS 16(6), doi 10.1145/197320.197383) | https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf | paper (primary) | © ACM | Nov 1994 | 10 | 25 (primary) |
| ISO/IEC 25010:2023 – Product quality model (abstract page) | https://www.iso.org/standard/78176.html | standard (paywalled) | © ISO/IEC | Edition 2, 2023-11 | 9 | 24 (primary) |
| ISO/IEC 25010:2023 – foreword on the Online Browsing Platform (changes from 2011) | https://www.iso.org/obp/ui | standard (public preview) | © ISO/IEC | 2023-11 | 10 | 24 (primary) |
| Kazman, Klein & Clements – ATAM: Method for Architecture Evaluation (CMU/SEI-2000-TR-004) | https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/ | technical report (primary) | © 2000 Carnegie Mellon University; "unlimited distribution subject to the copyright" | Aug 2000 | 11 | 24, 27 (primary) |
| Treynor, Dahlin, Rau & Beyer – The Calculus of Service Availability (CACM 60(9)) | https://cacm.acm.org/practice/the-calculus-of-service-availability/ | article | © ACM | Sep 2017 | 11 | 24 (primary) |
| Gallager – MIT 6.262 Discrete Stochastic Processes, ch. 4 Renewal Processes | https://ocw.mit.edu/courses/6-262-discrete-stochastic-processes-spring-2011/resources/mit6_262s11_chap04/ | course notes | MIT OCW (CC BY-NC-SA) | Spring 2011 | 10 | 24 (primary) |
| W3C – Web Content Accessibility Guidelines (WCAG) 2.2 | https://www.w3.org/TR/WCAG22/ | spec (W3C Recommendation) | W3C document licence | 12 Dec 2024 (first 5 Oct 2023) | 12 | 26 (primary) |
| W3C WAI – What's New in WCAG 2.2 | https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/ | docs | W3C | 2026-10-30 | 12 | 26 (primary) |
| W3C WAI – Understanding SC 2.5.8 Target Size (Minimum) | https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html | docs | W3C | 2026-10-30 | 11 | 26 (supporting) |
| W3C press release – WCAG 2.2 approved as ISO/IEC 40500:2025 | https://www.w3.org/press-releases/2025/wcag22-iso-pas/ | press release | W3C | 21 Oct 2025 | 10 | 26 (primary) |
| Regulation (EU) 2016/679 (GDPR), Art. 25 | https://eur-lex.europa.eu/eli/reg/2016/679/oj | statute | EU law (reuse permitted) | OJ L 119, 4.5.2016 | 12 | 26 (primary) |
| Irish DPC – Inquiry concerning Meta Dataset (decision 25 Nov 2022) | https://www.dataprotection.ie/en/dpc-guidance/decisions/inquiry-concerning-meta-dataset-november-2022 | regulator decision | public | 25 Nov 2022 | 11 | 26 (primary) |
| Robles v. Domino's Pizza, LLC, 9th Cir. No. 17-55504 | https://cdn.ca9.uscourts.gov/datastore/opinions/2019/01/15/17-55504.pdf | court opinion | public (US court) | 15 Jan 2019 | 9 | 26 (primary) |
| Directive (EU) 2019/882 – European Accessibility Act (EUR-Lex summary) | https://eur-lex.europa.eu/legal-content/ENG/LSU/?uri=CELEX:32019L0882 | statute summary | EU law | 2019 (applies from 28 Jun 2025) | 9 | 26 (supporting) |
| ACM Code of Ethics and Professional Conduct | https://www.acm.org/code-of-ethics | professional code | © 2018 ACM (may be published unchanged) | adopted 22 Jun 2018 | 12 | 26 (primary) |
| Software Engineering Code of Ethics and Professional Practice 5.2 | https://www.computer.org/education/code-of-ethics | professional code | © ACM/IEEE-CS | v5.2 | 9 | 26 (primary) |
| ALA – Privacy: An Interpretation of the Library Bill of Rights | https://www.ala.org/advocacy/intfreedom/librarybill/interpretations/privacy | professional policy | © ALA | 2026-10-30 | 10 | 26 (primary) |
| Cunningham – The WyCash Portfolio Management System (OOPSLA '92 experience report) | https://c2.com/doc/oopsla92.html | report | © W. Cunningham | 1992 | 10 | 26 (primary) |
| ACM – ACM is now fully open access (bulletin) | https://www.acm.org/articles/bulletins/2026/january/acm-open-access | announcement | ACM | 1 Jan 2026 | 9 | 27 (supporting) |
| ACM/IEEE-CS/AAAI – CS2023 knowledge areas | https://csed.acm.org/knowledge-areas/ | curriculum | ACM | CS2023 | 10 | assessment/syllabus.md |
| ABET – Criteria for Accrediting Computing Programs 2026–2027 | https://www.abet.org/wp-content/uploads/2025/12/2026-2027_CAC_Criteria.pdf | accreditation criteria | © ABET (no reproduction – paraphrased) | 2026–2027 cycle | 10 | assessment/syllabus.md |
| ABET – Criteria for Accrediting Engineering Programs 2026–2027 | https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2026-2027/ | accreditation criteria | © ABET (paraphrased) | 2026–2027 cycle | 10 | assessment/syllabus.md |

**L500: +27 sources kept** (23 cited in lesson `sources`, 4 used to verify a fact or for the syllabus). Dropped: secondary WCAG/GDPR summaries
(wcag22aa.org, equalweb.com, thedpo.eu) and vendor ISO 25010 explainers (used only to cross-check names already on ISO pages).
