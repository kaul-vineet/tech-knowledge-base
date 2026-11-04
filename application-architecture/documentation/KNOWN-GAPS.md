# Known gaps – Application Architecture L100 + L200

## Not run locally (pending-ci)
| Item | Why | What covers it |
|---|---|---|
| Rendering `c4-context.mmd` / `c4-container.mmd` | No mermaid-cli locally; npm has no network access in the sandbox | CI job `diagrams` renders them with mermaid-cli 11.17.0 and uploads the SVGs. The local `check_docs.py` only checks structure (defined aliases, brackets). |
| Parsing `workspace.dsl` with the real Structurizr parser | No Docker/Java locally | CI runs `structurizr/structurizr:2026.09.19 validate -workspace …`. Syntax was hand-checked against the DSL language reference. |
| `.github/workflows/labs.yml` itself | GitHub Actions cannot run here | Only checked that the YAML parses (PyYAML) and lists jobs `python-labs` and `diagrams`. |

## Unverified or assumed
- **Structurizr `validate` via the Docker image.** The docs show `docker run … structurizr/structurizr local`. We assume `validate -workspace …` uses the same entrypoint the same way. Not executed.
- **Implied relationships in Structurizr.** The system context view relies on the DSL's default implied relationships (`member -> api` implies `member -> loans`). We did not fetch the exact default strategy page; CI rendering will show whether it holds.
- **Mermaid C4 is "experimental".** Its syntax "can change in future releases" (Mermaid docs). The diagrams use only the listed, supported macros: `Person`, `System`, `System_Ext`, `Container`, `ContainerDb`, `Container_Boundary`, `Rel`.
- **mermaid-cli version.** npm shows 11.17.0 as latest. The GitHub repo shows a "Bump version 12.0.0" commit that may be unreleased. We pin 11.17.0. CI now uses Node 24 (moved from 22 on 2026-10-28); a "Node ≥ 22.13.0" requirement mentioned in the repo is met by 24.x, but mermaid-cli 11.17.0 was not rendered on Node 24 here (CI only).
- **GitHub Actions versions** (`actions/checkout@v4`, `setup-python@v5`, `setup-node@v4`, `upload-artifact@v4`) were not re-verified against the actions' release pages in this session.
- **`openapi.json` was not checked with an OpenAPI validator** such as the official JSON Schema at spec.openapis.org: that needs a JSON Schema 2020-12 validator, which is not in the stdlib. The required fields (`openapi`, `info.title`, `info.version`, `paths`) are asserted by a test.
- **Licences were not shown on the fetched pages** for ArchUnit, Spring Modulith, Pact docs, 12factor.net, c4model.com and the OWASP cheat sheet. VERIFIED-RESOURCES records them as "not checked" rather than guessing.
- **unittest and ast docs** were fetched from the `/3/` (3.15) pages. The APIs used (`discover`, `-v`, `ast.Import`, `ast.ImportFrom.level`) were confirmed to work by running the labs on 3.12.15.

## Simplifications in the labs (on purpose, L100)
- `contract_check.py` is not a full JSON Schema validator. It checks declared path and status, required fields, primitive types and `enum`. Use Schemathesis or another OpenAPI validator for real projects.
- `check_boundaries.py` sees static `import` statements only. It misses `importlib` and string-based imports.
- `http.server` is used for teaching only. The Python docs say it is not recommended for production.
- Lab 5 passes the secret through an env var. OWASP recommends mounted files or a secrets manager in production.
- Labs 2–5 each keep their own small copy of the Library Loans code so that every lab runs on its own. They are not one shared package.

## Concepts layer gaps
- **The L200–L400 concept map in `CONCEPTS-PRIMER.md` is a proposal.** No agreed curriculum file was found in the KB, so it is marked "proposed" there.
- **Cockburn's hexagonal-architecture page could not be fetched** (the content filter withheld it). Hexagonal architecture is described only through Fowler's layering article, and is the L200 topic named in note 2.
- **RFC 9110 status-code definitions (409/422) were not retrieved.** The page text was cut off before section 15, so the notes don't quote definitions of HTTP status codes.
- **The "implied relationships" worked example in note 6 is computed by our own lifting script**, not by Structurizr. Whether Structurizr's default strategy gives the same 4 relationships is confirmed only when CI renders the diagrams.

## Items dropped
- **Structurizr Lite** as the main tool: it is end-of-life, replaced by Structurizr `local`.
- Promotional content on the Mermaid C4 page (an editor discount banner) and on docs.pact.io (a commercial sign-up banner). We used only the technical text from those pages.
- The w3schools SQL tutorial linked from the sqlite3 docs: not needed and not fetched.
- The import-linter `contract_types.html` page: the fetch returned no content, so the docs index page was used instead.

## Pages that could not be fetched
- https://import-linter.readthedocs.io/en/stable/contract_types.html returned an empty document; the tool reported that re-fetching returns the same result.

## Rebalance (REBALANCE-SPEC.md, 2026-10-28)
- **Concept share is 21% (concept 1530 / hands-on 5855 words, spec script)**, near the lower edge of the 20–25% L100 target. Adding much more hands-on text without lengthening the notes (max 250 words) would drop it below 20%.
- **`%%` comments added to `c4-container.mmd` are not parsed locally.** Mermaid's syntax reference says line comments start with `%%`; the local lint passes, but the official parse/render is confirmed only by the CI `diagrams` job (pending-ci, like the rest of the rendering).
- **tryIt 2 in lesson 1 prints the local Python version** (`3.12.15` here); your patch version may differ.
- **tryIt 2 in lesson 3 shows a known limit of the checker on purpose:** an `importlib.import_module("…internal…")` string is not caught.
- **The storage mount used for this build sometimes fails renames and in-place rewrites** (`sed -i` broke one diagram file, which was restored byte-for-byte from its printed content and re-checked). `try_it.py` deletes its `.tryit-work/` copy with retries for the same reason.
- Dropped from the notes and condensed into one-line lesson fields: the "In real systems" and "Use it when / avoid when" sections; "Check yourself" was cut to 2 questions per lesson to keep the share in range.

## Platform + local-agent pass (PLATFORM-AGENT-SPEC.md, 2026-10-28)
- **macOS and Windows were not run here** (Linux sandbox). Every lesson has `platforms: {mac: expected, windows: expected}`
  until the CI matrix (`ubuntu-latest`, `macos-latest` arm64, `windows-latest`) runs. Not run either: the zsh and
  PowerShell command lines in lessons 1, 3, 5 and 6 (the bash equivalents of the zsh lines were run). CI runs lesson 5's
  zsh and PowerShell sequences. The custom shell `zsh {0}` and the `cmd /c exit 0` reset in the PowerShell step were
  written from the workflow-syntax reference but were not executed.
- **Install commands are checked against package indexes, not run:** brew `python@3.12` (3.12.16), `node@24` (24.22.1, keg-only;
  deprecation 2027-10-30; replaced `node@22`, which Homebrew deprecates on 2026-10-30), `podman` (6.1.4), cask `podman-desktop`, `ollama`; winget
  `Python.Python.3.12`, `OpenJS.NodeJS.LTS`, `RedHat.Podman` (5.8.3 listed two months ago), `RedHat.Podman-Desktop`,
  `Ollama.Ollama`. Podman's own docs recommend its pkg installer over Homebrew on macOS. The Podman-for-Windows guide
  describes Podman 6 features, and winget may still deliver 5.x.
- **Podman + Structurizr and npx + mermaid-cli were not run on either OS.** The image tag lists linux/arm64, so no emulation is
  expected on the Mac mini. The Windows volume form `"${PWD}\doc\arch:/usr/local/structurizr"` follows the Podman-for-Windows
  guide (Windows-style paths are supported). mermaid-cli 11.17.0's minimum Node version was not checked: the repo's
  "Node ≥ 22.13" change is on the 12.0.0 line; CI's `node-version: "24"` satisfies it either way.
- **Structurizr is validated on Linux CI only:** GitHub's arm64 macOS runners do not support nested virtualization.
  We did not test whether Windows runners can run Linux containers, so that path is not used.
- **Agent assist uses the fake server only.** The real-model path (`--real`, Ollama + qwen2.5:1.5b) was not run. Its output
  quality is unknown; the deterministic checks are the safeguard. The fake server's first draft says `Accepted.` on purpose
  (scripted failure, documented in the vendored server's header).
- **Concept share fell to 17%** (concept 1530 / hands-on 7532 words), below the 20–25% L100 target. The extra words are the
  `mac`/`windows` commands, the two new setup steps and the agent assist. The notes are already 244–249 words
  (limit 250), so they were not padded.
- **Ollama hardware claims** (Metal; NVIDIA CC 5.0+ with driver 550+; AMD ROCm v7/Vulkan on Windows; ≥ 4 GB disk on Windows)
  come from Ollama's docs and were not tested on hardware. `docs.ollama.com/windows` returned no content; the same page was read on GitHub.
- **The error wording for a busy port on macOS (`[Errno 48]`) and Windows (`[WinError 10048]`)** comes from the
  platforms' errno conventions. It was not observed here.

## L200 build (lessons 7–11, 2026-10-28)

### Not run locally (pending-ci)
| Item | Why | What covers it |
|---|---|---|
| Official AsyncAPI validation (`npx @asyncapi/cli@6.2.1 validate asyncapi.json`) | No npm access in the sandbox | CI job `asyncapi` (Node 24). Locally: `asyncapi_check.py` (structure subset) + payload validation of every event |
| Keycloak 26.8.1 + `keycloak_check.py` | No container engine | CI job `keycloak` (docker, ubuntu-latest) |
| `test_integration_postgres.py` + `postgres_store.py` (Testcontainers, psycopg 3) | No pip, no container engine; the adapter has never been executed | CI job `testcontainers`; the same contract tests pass on SQLite |
| Agent assist with a real model (`--real`) | No model in the sandbox | Fake server only (scripted first failure, documented in the vendored server header) |
| macOS / Windows runs of lessons 7–11 and their zsh/PowerShell lines | Linux sandbox | CI matrix; `platforms` stay `expected` |

### Unverified or assumed
- **OIDC Core §3.1.3.7 (ID Token Validation) and §10.1 (MAC signing with client_secret) were not retrieved.** The page fetch stopped
  in §3.1.2. The claim checks rest on §2 claim definitions (retrieved), RFC 9700 and tests. The mock's HS256-with-client-secret
  choice exists only because the stdlib has no RSA signing; real providers such as Keycloak use RS256 and `jwks_uri`.
- **Cockburn's hexagonal-architecture page is still blocked** by the content filter. Lesson 7 relies on AWS Prescriptive Guidance and Garrido de Paz.
- **`typing.runtime_checkable`'s own section was not in the fetched text.** Its behaviour (method presence only) was observed in tryIt 2.
- **@asyncapi/cli version.** GitHub releases (fetched) show v6.2.1 as latest; a search snippet showed v6.2.2. We pin 6.2.1. Whether
  6.2.1 bundles a parser with AsyncAPI 3.1.0 support, and whether it asks an interactive question on first run in CI, was not checked.
  The 3.1.0 release notes say the JS parser supports 3.1.0 with @asyncapi/specs 6.11.1.
- **Keycloak issuer in `start-dev`.** `keycloak_check.py` expects `http://127.0.0.1:8080/realms/master` (the request host). Not verified.
- **Node 24 status.** Per schedule.json, Node 24 moved from Active to **Maintenance LTS on 2026-10-20** (the Release README table snapshot
  still said "Active LTS"), and Node 26 is scheduled to become LTS on 2026-10-28. `OpenJS.NodeJS.LTS` will then move to 26.x, so the
  lessons pin `--version 24.19.0`. That pin blocks automatic 24.x patch updates: check `winget show OpenJS.NodeJS.LTS --versions`.
  The brew and winget commands were checked against the package indexes, not run.
- **Postgres image** `postgres:16-alpine` (from the Testcontainers guide) is a moving tag, not a digest.
- **AsyncAPI version.** The user asked for 3.0. The verified current version is 3.1.0 (minor, compatible), and the document uses 3.1.0.

### Simplifications (on purpose, L200)
- `mock_idp.py` is **learning-only**: no login UI, no TLS, HS256, in-memory single-use codes, no consent, refresh tokens or key rotation.
- `asyncapi_check.py` validates a JSON Schema subset (type, required, properties, additionalProperties, const, uuid, date-time).
- The relay polls synchronously; consumers keep processed ids in memory (production: an inbox table); the bus is in-process.
- `SqliteMemberRepository.save` deletes and re-inserts the member's loans (fine for small aggregates).
- Lab timings (lesson 11) come from a shared host with a network-mounted disk. They varied per run (unit 0.03–3.8 ms, integration
  82–201 ms, e2e 0.6–4.9 s), so READMEs give ranges and the budgets are generous.
- The vendored fake model server gained a second documented rule, `[[EVENT-SCHEMA]]` (lesson 9). The L100 `[[ADR-DRAFT]]` rule is unchanged.

### Measured (spec scripts)
- **Concept share L200: 26% (concept 2052 / hands-on 5982 words, REBALANCE-SPEC script on content/L200.json), inside the 25–30% target.**
  Notes are 397–400 words (`wc -w`). Hands-on text was trimmed (README/try_it rows, shorter walkthroughs) instead of padding the notes.
- The `try_it.py` scratch folders sometimes survive a delete on this mount. Subprocesses now run with `PYTHONDONTWRITEBYTECODE=1`;
  one leftover empty `.tryit-work/` was removed by hand.

## Update pass – learning tools + review fixes (UPDATE-TOOLS-REVIEW-SPEC.md, 2026-10-28)

### Learning tools (documentation/LEARNING-TOOLS.md, lesson field `learningTools`)
- **No learning-tool exercise was run here** (no container engine, no pip, no browser). Every `expected` names the lab output
  it should match and says "pending a manual run". Tool facts and install commands are copied from the KB catalogue.
- **import-linter:** contract option names (`forbidden`, `allow_indirect_imports`) and the `explore` UI were not re-read in its docs
  (the catalogue also says contract types were not re-checked). Lesson 3 needs `allow_indirect_imports = True` because
  `library.catalog` imports its own internals. Whether single-file top-level modules (lesson 7) are accepted as root packages is unknown.
- **Swagger Editor "Try it out":** `server.py` sends no CORS headers, so browser calls are probably blocked (not tested).
- **AsyncAPI Studio 1.4.2 and AsyncAPI 3.1.0:** not checked; Swagger Editor 5.10.0's release notes add AsyncAPI 3.1.0 support.
- **Bruno:** the `bru` CLI install is not in the catalogue; free-tier OAuth2/PKCE is unconfirmed (Hoppscotch suggested for lesson 10).
- **Structurizr:** the lab pins image `2026.09.19`; the catalogue's latest is v2026.10.26 (not re-pinned, CI not re-run).
- **Concept share went down** with the new `learningTools` / `seeAlso` / `pendingCi` fields (measured below); notes were not padded.

### Review findings (REVIEW-L100-L200.md)
| ID | Status | What changed / why not |
|---|---|---|
| F01 | recorded | README now starts with "Status: not yet run on macOS or Windows; CI matrix pending." The root CI job is a separate task; `.github/` untouched. |
| F03 | checked | L100 `next` already named real L200 lessons; L200 `next` now reads "L300 (planned): …". |
| F04 | fixed (docs) | HARDWARE/README say "Node 24 (Maintenance LTS)"; the winget pin `--version 24.19.0` stays. |
| F05 | fixed | Lesson 1 steps use `shared/WORKSTATION-SETUP.md` commands (Ollama on Windows: `OllamaSetup.exe`, not winget; `brew services start ollama` before `pull`; `$env:PYTHONUTF8`; canonical ExecutionPolicy) and link to it. |
| F07 | fixed | `validation.pendingCi` on all 11 lessons. |
| F08 | fixed | `seeAlso`: lesson 4 ↔ ai-agents L200 #10; lesson 9 ↔ distributed-systems L100 #5 and L200 #8 ("idempotent consumer"); lesson 10 ↔ cryptography L200 #11. |
| F11 | fixed (kept 3.1) | Moving to 3.2.x is not "trivial and verified": no OpenAPI/JSON Schema validator runs here, OAS 3.2.0 §2.1 allows incompatible minor changes, the catalogued tools target 3.1, and Swagger's own 3.2.0 announcement (vendor blog, background: https://swagger.io/blog/swagger-launches-support-for-openapi-3-2-0/) says gaps remain. Lesson 4 overview, README and a 3.2 `equivalents` line now say so. |
| F14 | fixed | The localhost URL is gone from VERIFIED-RESOURCES. |
| F15 | fixed | Lesson 3: Thoughtworks Radar → evolutionaryarchitecture.com (Ford/Parsons/Kua, background); lesson 7: AWS → Cockburn's original article (text retrieved via web search; direct fetch still filtered), AWS kept as one `equivalents` line; `mermaid.ai` → mermaid.js.org. |
| F16 | fixed | Duplicate rows merged (mermaid-cli, structurizr tags, sqlite3 3.12, os docs). |
| F22 | fixed | L100 troubleshooting trimmed to 2 rows (lessons 1, 3, 5, 6); the extra rows live in the lab READMEs. Overviews stay at 2 sentences (within spec). |
| F23 | fixed | Lesson 10 checkpoint = "all tests pass"; the state/nonce/PKCE/aud question moved to `checkYourself`. |
| F27 | fixed | `__pycache__` folders removed; no stray logs in this topic. Tests recreate `__pycache__` unless `PYTHONDONTWRITEBYTECODE=1` is set. |
| F09 | recorded | Concept share below target (see the measurement below); the extra words are hands-on material. |

### Measured after this pass (REBALANCE-SPEC script)
- **L100: 16%** (concept 1530 / hands-on 8072; was 17%) · **L200: 24%** (concept 2052 / hands-on 6614; was 25%). Both below target;
  the new words are `learningTools`, `seeAlso` and `pendingCi`. Notes unchanged (L100 244–249, L200 397–400 words).
- **Tests:** all 12 test folders pass (147 tests, 3 skipped). One of five runs of `labs/L200/11-testing-pyramid` failed once on timing
  (shared network-mounted disk) and passed on four re-runs; no code was changed in this pass.

## L300 build (lessons 12–16, L300-SPEC.md, 2026-10-28)

### Not run locally (pending-ci)
| Item | Why | What covers it |
|---|---|---|
| `pact/test_pact_contract.py` with pact-python 4.2.0 (lesson 14) | No pip in the sandbox | CI job `pact`. Written from the 4.x docs; only checked here to skip cleanly (`OK (skipped=2)`) |
| `k6 run k6/overdue.js` (lesson 16) | k6 not installed, no container engine | CI job `k6` (`grafana/k6:2.3.0` image) |
| `agent_assist.py --real` (lesson 15) | No model in the sandbox | Fake server only; the scripted first failure is documented in the vendored server header |
| macOS / Windows runs of lessons 12–16 | Linux sandbox | CI matrix; `platforms` stay `expected` |
| All L300 learning-tool exercises (marimo, Toxiproxy, Bruno, JupyterLab, Grafana OSS, k6, import-linter) | No GUI, pip or container engine | Each `expected` names the lab value to match and says "pending a manual run" |

### Unverified or assumed
- **pact-python API details.** `match.like` is assumed to exist in `pact.match` (the docs page showed `from pact import Pact, match`
  but no `like` call). `state_handler(url, body=True)` posting `{"state": ...}` to our `/_contract/state` hook is assumed from the
  provider docs (since 4.x URLs must be plain `str`). Whether `pact.v3` still exists after 4.0 was not confirmed (not used).
- **`grafana/k6:2.3.0` image tag** is assumed to exist (the install page says `docker pull grafana/k6`; the tag itself was not checked).
  `docker run -i ... run - < script` (script on stdin) was not re-read in the docs.
- **resilience4j v2.4.0 and Polly 8.8.0 release years** are inferred (the release pages omit the year). Licences of resilience4j and Polly
  were not shown on the fetched pages. pollydocs.org's circuit-breaker page was blocked by the fetch filter; its GitHub copy was used.
- **"A timeout does not stop the running thread"** is not a sentence in the Python docs. It follows from `Future.cancel()` and
  `shutdown()` wording and is shown by `test_timeout_frees_the_caller_not_the_thread`.
- **SRE Workbook config.** The chapter's example config also has a 24h/2h ticket at burn rate 3, which table 5-8 does not list; the lab uses
  the table only. The workbook uses 30-day windows in the alerting chapter and 4 weeks in "Implementing SLOs"; the lab uses 30 days.
- **Grafana TestData exercise** (lesson 15): Grafana core has no CSV/JSON-lines data source (catalogue note); the panel steps were not tried.
- **import-linter with single-file top-level modules** (lesson 16 exercise) is unverified, as in L200 lesson 7.
- **Fitness-function definition** (Ford/Parsons/Kua) was seen only in a search snippet of evolutionaryarchitecture.com; the notes describe it
  in our own words and cite no page for it.

### Simplifications (on purpose, L300)
- Lesson 12: `LoanCommands` loads and appends without a version check (lesson 8's optimistic concurrency is left out), so two concurrent
  borrows by one member could both pass the rule; the demo issues commands from one thread. Read and write sides are two in-memory SQLite
  databases in one process; the "crash" is an exception and the "restart" a new object on the same read database.
- Lesson 13: dependencies are in-process functions with `sleep`/`Event.wait`, not network services; the breaker uses a 10-call window
  (resilience4j defaults to 100) so the demo opens quickly.
- Lesson 14: `contract.py` is a teaching subset of Pact (GET only, `like` type matcher only, no broker, no message pacts) with its own file format;
  the provider-state hook is test-only and enabled with `states=True`.
- Lesson 15: the log is synthetic (one request every 10 s for 3 days); burn rates are recomputed from raw lines instead of counters, and
  percentiles use nearest rank. The 5-minute window holds about 6 POST /loans requests, which is why the page fires later than the formula predicts.
- Lesson 16: the "network round trip" is a `time.sleep` in the SQLite trace callback (it overshoots: about 1 ms per call here; Windows timers are coarser).

### Measured (spec scripts)
- **Concept share L300: 22% (concept 2714 / hands-on 9829 words, REBALANCE-SPEC script on content/L300.json)**, below the 30–35% target.
  The notes are at full length (516–536 words with `wc -w`; 527–549 with a UTF-8 locale, where arrows and box characters count as words).
  The hands-on side is larger than at L200 because every lesson now carries a failureLab, tradeOffs, a 6–7 item walkthrough and code files of
  80–125 lines. Labs were not cut to reach the target.
- Timing-dependent outputs (lesson 12 lag, lesson 13 request `ms`, lesson 16 benchmarks and p95) were recorded as ranges over several runs
  on a shared host with a network-mounted disk; counts, drift lists, alerts and query counts are deterministic and repeat exactly.
- `resilience.py` is 123 lines and `projector.py` 102 (main-file guide: 60–120).
- The vendored fake model server gained a third documented rule, `[[INCIDENT-SUMMARY]]` (lesson 15); the `[[ADR-DRAFT]]` and
  `[[EVENT-SCHEMA]]` rules are unchanged.

## L300 update pass (UPDATE-L300-SPEC.md, REVIEW-L300.md, 2026-10-28)

### Review findings
| ID | Status | What changed |
|---|---|---|
| R3-04 | fixed | `seeAlso` added: #12 → distributed-systems L300 #14 (sagas); #13 → distributed-systems L300 #16 and ai-agents L300 #14 (same circuit breaker); #15 → distributed-systems L300 #16. Titles copied from those topics' `content/L300.json` and checked by script. The back-links live in the other topics (not edited here). |
| R3-05 | fixed | L200 #7 → L300 #14, #8 and #9 → L300 #12 (exact titles), #10 → "L400 (planned)". Unbuilt follow-ups moved to *L400 candidates* below. |
| R3-06 | already met | All five `test_build_task.py` have `CHECK_MINE=1`; re-run in this pass: each fails on the shipped (unfixed) lab file and passes on `solution/`. |
| R3-08 | fixed | #15 "JupyterLab" → "JupyterLab (+ JupyterLab Desktop)"; same class also fixed in L200 #10 ("Keycloak admin console" → "Keycloak"). Every `learningTools.name` in L100–L300 now matches `learning-tools.json` (script check). |
| R3-13 | fixed | #12: Kurrent docs replaced as a source by Fowler – Event Sourcing (Greg Young's CQRS Documents listed as background); Kurrent stays one `equivalents` line. #13: Google SRE Book ch. 22 added as primary; Azure stays one `equivalents` line. Azure CQRS is cross-check only. |
| R3-14 | fixed | Concept share for all levels in `documentation/README.md` (L100 15.9%, L200 23.6%, L300 21.1%; all below target, notes not padded). |
| R3-16 | fixed | `LEARNING-TOOLS.md` rewritten: 599 words (`wc -w`). That is within this pass's limit (≤ 650) but above the original 250–500 band. |
| R3-01 | open | No macOS/Windows run yet; `platforms` stay `expected`. |
| R3-20 | open (shared) | Toxiproxy Mac install keeps the catalogue's `brew tap shopify/shopify &&` (toxiproxy is in homebrew-core). This lesson changes when the catalogue does. |

### Learning tools (pending a manual run)
- **Pact Broker (OSS)** (#14) and **Prometheus (+ expression browser, promtool)** (#15, replaces Grafana OSS) did not run here (no container engine, no downloads).
  Unverified: whether the OSS broker UI renders pact-python 4.2.0's V4 file fully; native Windows (the image is Linux-only, so "partial").
  The exact publish command (HTTP PUT path or broker client) is not spelled out because it was not checked.
- **Proposal/catalogue values corrected in the lesson, not in `shared/` (read-only here):**
  - The promtool exercise says "360 requests, 71 slower than 300 ms; 10 of the last 30". Recomputed from `traffic.py` + `solution/slo.py` at 12:00 UTC:
    the last hour has 360 requests on all routes, of which **71 are POST /loans and 14 are slow** (14/71 = 19.7%). The last 5 min have 30 requests,
    of which **3 are POST /loans and 1 is slow** (1/3, burn 33.3). The lesson uses these counts.
  - The Pact Broker row expects two interactions. `pact/test_pact_contract.py` writes **one** ("book b1 exists" → 200). The 404 case exists only in the lesson-format contract.

### L400 candidates (from the old L200 `next` pointers)
- Peeling a module off into its own service behind the same port (L200 #7).
- Eventual consistency between aggregates with sagas (L200 #8). Sagas are covered in distributed-systems L300 #14.
- Sync vs async integration and sagas across services (L200 #9).
- Access tokens for APIs: scopes, audience and token exchange (L200 #10).

## L400 build (lessons 17–22, L400-SPEC.md, 2026-10-28)

### Not run locally (pending-ci or manual)
- macOS (arm64) and Windows 11 runs of every L400 lab and the capstone (`platforms: expected`), carried over from R3-01.
- OPA 1.21.4: `opa test policy/ -v` and `opa_parity.py` (lesson 19) – CI job `opa`. Whether `opa test policy/` loads
  `policy/cases.json` as `data.cases` (directory-relative data paths) is assumed from the OPA loading rules, not run.
- Agent assists with a real model: lesson 21 `agent_assist.py --real`, capstone `agent_assist.py --real`.
- Learning-tool exercises (import-linter, Structurizr, JupyterLab, Keycloak, Swagger Editor, k6, Bruno, promtool): manual.
- A real load test (k6) confirming lesson 21's simulated per-instance capacity.

### Unverified or assumed
- Lesson 21's per-instance capacity is a seeded queue simulation fed with lesson 15's logged service times, not a load test
  of a real server. Two boundary points are close to the SLO (sync option 299.9 ms at 35 req/s, async 245.2 ms at 75 req/s);
  identical results across platforms rely on CPython's deterministic `random.Random`.
- Lesson 21's peak factor (3x), worker count (4), email time (150 ms) and price (0.10 USD per instance-hour) are stated
  assumptions of the brief, not measurements or vendor prices.
- The SQLite release that introduced `ALTER TABLE … DROP COLUMN` is not stated on the fetched page; the lab only claims it works
  with SQLite 3.44.0 (bundled here).
- Keycloak mapping of a `tenant` user attribute into tokens (lesson 19 learning tool): mapper type not verified.
- import-linter with top-level single-file modules (lesson 17 learning tool): unverified, as in lesson 16.
- OPA on Windows: install via the release asset `opa_windows_amd64.exe`; no winget id verified.

### Simplifications (on purpose, L400)
- `rego_lite.py` reads a small Rego v1 subset (no comprehensions, functions, `some`, `every`, partial evaluation); it re-parses
  expressions per decision (290–1,145 µs here). OPA is the production engine for the same file.
- "Schema per tenant" is modelled as one table per tenant in one SQLite file (SQLite has no `CREATE SCHEMA`; `ATTACH` is shown in try-it 1).
- The tenant guard checks that the current tenant's quoted id appears in the expanded SQL; it would accept
  `tenant_id = 'lib00' OR 1=1`. Bound parameters plus the static gate cover that case in the labs.
- Rolling deploys, instance versions and the contract guard's fleet list are simulated in one process (lesson 20).
- The capstone uses one SQLite connection in memory, an in-process bus and `X-Subject` as a learning-only caller identity
  (the contract's provider state supplies it, because the lesson-14 contract format has no headers). Its contract
  type-matches `loans` as a list; items are not checked (no `eachLike` in that format).
- The capstone projection keys active loans by member id across libraries (lesson 9's consumer); the check compares sums per member id.

### Environment notes (this sandbox)
- The workspace is a network mount: wall times are dominated by I/O (capstone tests 32–170 s wall, ≈2 s CPU; per-file appends ≈ 7 ms).
  The capstone and lesson 19 write decision logs once per run, not once per decision, for that reason.
- Twice a module import failed transiently with `ModuleNotFoundError` on the mount; immediate reruns passed. Not reproducible locally.
- Full-topic run after the L400 build: every test file passed (L400 + capstone 3x, L300 #12/#13/#16 3x) except one run of
  L200 #11 `test_real_suite_meets_the_default_budget` (integration mean 3,159.8 ms > 1,000 ms budget on this mount); two reruns passed.
  A wall-clock budget, like R3-02; not changed in this pass.

### Measured (spec scripts)
- Concept notes L400: 737–748 words (17–21, `wc -w`; 746–750 with a UTF-8 locale, where arrows count as words), capstone note 513 (529).
- Concept share L400 (REBALANCE-SPEC script on content/L400.json): concept 4271 / hands-on 14996 = **22.2 %** (target 35–40 %).
  Notes are at full length; the hands-on side includes the main code files (314–735 words each) and the new design fields.

### L400 candidates (further study)
- Access tokens for APIs: scopes, audience and token exchange (from L200 #10).
- Sagas across extracted services when a loan spans fines and loans (distributed-systems L300 #14).
- Eventual consistency between aggregates; read models per tenant (L200 #8, L300 #12).
- Row-level security on PostgreSQL as a third tenant guard; per-tenant rate limits and quotas.
- Real load testing and autoscaling policies (k6 + Prometheus) to replace the simulated benchmark.
- OPA bundles with signatures (v1.21.3 fix) and partial evaluation for list filtering.

## L500 build (lessons 23–27, L500-SPEC.md, 2026-10-30)
| Item | Status / why | What covers it |
|---|---|---|
| macOS (arm64) and Windows runs of `labs/L500/*` | Sandbox is Linux; `platforms` stay "expected" | CI matrix step "L500 theory checks" runs `research/l500_checks.py`, both qbank checks and every L500 lab's unittest suite on all three OSes |
| ISO/IEC 25010:2023 full text | Paywalled; only the abstract page and the public foreword (list of changes) were read | Lesson 24 names the nine characteristics and the listed changes only; sub-characteristic definitions are not quoted. Six unchanged characteristic names were cross-checked on two secondary pages |
| ABET outcome wording | ABET criteria may not be reproduced | `syllabus.md` paraphrases and links the 2026–2027 CAC/EAC documents. Finding: the spec's "outcomes 1–7" is the EAC list; CAC has 1–5 (+6 for CS); both mapped |
| "14-week plan (from the review)" | No 14-week plan was found in REVIEW-L100-L200.md or REVIEW-L300.md | `syllabus.md` builds its own plan from the L100–L500 lesson order |
| Parnas KWIC "knows" sets | `modularity.KWIC_*` is our model of the paper's argument, not data from the paper | Labelled as a model in code, note, P23-5; lesson 27 asks students to check it against the paper |
| Martin's D formula | The 1994 paper prints the distance as (A+I−1)÷2 in absolute value but states the range [0, ~0.707] (i.e. ÷√2) | Lesson 23 uses Dn = abs(A+I−1) and proves the √2 form (T23.3); the discrepancy is stated |
| El Emam et al. (2001) | Paywalled; only the abstract was read | Lessons cite only what the abstract states |
| dl.acm.org DOI pages | web_fetch returned no text; ACM's open-access status verified from the acm.org bulletin | Readings link the CACM article page and give the DOI |
| Legal content in lesson 26 | Not legal advice; EAA scope for a public library service is left to counsel | Case study and note say so explicitly |
| Static `__main__` cycle in L200 #7 | Found by the L500 analysis: `driving_cli`'s `__main__` block imports `app`; not changed (other lessons are out of scope) | Problem P23-6 discusses it; a fix is proposed there |
| Concept-inventory learning gain | Instrument written; no cohort data | Syllabus: pre (week 1) / post (week 14), normalised gain |
| Full-topic test run (2026-10-30) | All 26 suites (L100–L500 + local_agent) passed except L300 #14, which intermittently hit `OSError: [Errno 5]` / `FileNotFoundError` when its test overwrites `contracts/loans-service--catalogue-service.json` on this sandbox mount; it passed on a re-run, the regenerated contract was byte-identical, and the file was restored | Mount limitation (in-place overwrite), not an L500 or lab defect; CI runs on normal file systems |
