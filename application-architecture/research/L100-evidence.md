# L100 research evidence – Application Architecture

Method (per SPEC): 2–3 implementation questions per lesson → web_search/web_fetch of official
docs/specs/OSS repos → screen out marketing, stale or unclear-licence items → score kept sources
0–2 on implementable (I), current (C), authoritative (A), open (O), transferable (T), right depth (D)
→ keep ≥ 8/12 → cross-check each claim against ≥ 2 sources (≥ 1 official) or a local run.
All fetches done 2026-10-28. Scores: I/C/A/O/T/D = total.

---

## Lesson 1 – Set up your environment
**Questions**
1. Which Python version is safe to target, and how is it supported?
2. How do I run all tests in a folder with the stdlib only?
3. What open-source tools render C4 diagrams from text today, and how are they installed?

**Candidates**
| Source | Decision | I/C/A/O/T/D | Reason |
|---|---|---|---|
| docs.python.org unittest | kept | 2/2/2/2/1/2 = 11 | Official; `python -m unittest` = `discover`; `-v`, `-s`, `-p test*.py` |
| devguide.python.org/versions | kept | 1/2/2/2/1/2 = 10 | Official support status |
| github.com/mermaid-js/mermaid-cli | kept | 2/2/2/2/1/2 = 11 | MIT; exact `mmdc` usage |
| npmjs.com @mermaid-js/mermaid-cli | kept (supporting) | 1/2/2/2/0/2 = 9 | Version pin 11.17.0 |
| docs.structurizr.com/local (+ quickstart) | kept | 2/2/2/1/1/2 = 10 | Replacement for Lite; docker command |
| docs.structurizr.com/lite | kept (supporting) | 1/2/2/1/1/2 = 9 | States Lite is end-of-life |
| docs.structurizr.com (home) | kept (supporting) | 1/2/2/1/1/1 = 8 | Current binaries version v2026.09.19; commands free except `server` |
| hub.docker.com structurizr tags | kept (supporting) | 1/2/1/1/1/2 = 8 | Confirms tag `2026.09.19` exists |
| Structurizr Lite as main tool | **dropped** | – | End-of-life |

**Key facts**
- `python -m unittest` is the same as `python -m unittest discover`. The default pattern is `test*.py`, and `-v` gives verbose output. Source: https://docs.python.org/3/library/unittest.html. Cross-check: ran in all six labs on Python 3.12.15.
- Python 3.12 is in the "security" phase, with end-of-life 2028-10. Source: https://devguide.python.org/versions/
- Install with `npm install -g @mermaid-js/mermaid-cli` and render with `mmdc -i input.mmd -o output.svg`. With npx, use `npx -p @mermaid-js/mermaid-cli mmdc`. Sources: https://github.com/mermaid-js/mermaid-cli and https://www.npmjs.com/package/@mermaid-js/mermaid-cli (latest 11.17.0).
- "Structurizr Lite has reached end of life … please migrate to local". The `local` command "is equivalent to the previous Structurizr Lite tooling". It runs as `docker run -it --rm -p 8080:8080 -v PATH:/usr/local/structurizr structurizr/structurizr local`. Sources: https://docs.structurizr.com/lite, https://docs.structurizr.com/local, https://docs.structurizr.com/local/quickstart

## Lesson 2 – Layered structure
**Questions**
1. Which way should dependencies between presentation, domain and data layers point?
2. How do I use sqlite3 safely (placeholders, commit, threads) from an HTTP server?
3. What is the minimal correct way to write a JSON response with `BaseHTTPRequestHandler`?

**Candidates**
| Source | Decision | I/C/A/O/T/D | Reason |
|---|---|---|---|
| martinfowler.com PresentationDomainDataLayering | kept | 1/1/2/1/2/2 = 9 | Canonical, language-neutral description |
| docs.python.org/3.12 sqlite3 | kept | 2/2/2/2/2/2 = 12 | Official API; tutorial transfers to any DB-API 2.0 (PEP 249) driver |
| docs.python.org/3.12 http.server | kept | 2/2/2/2/1/2 = 11 | Official API + production warning |
| w3schools SQL (linked from sqlite3 docs) | **dropped** | – | Not needed; not fetched |

**Key facts**
- "The dependencies generally run from top to bottom through the layer stack: presentation depends on the domain, which then depends on the data source." "These layers are logical layers not physical tiers." Source: Fowler. Cross-check: import-linter offers a "Layers" contract and ArchUnit checks "layers and slices", so tools enforce the same idea.
- "Always use placeholders instead of string formatting to bind Python values to SQL statements, to avoid SQL injection attacks." `check_same_thread` defaults to True. If False, "write operations may need to be serialized by the user". `":memory:"` creates an in-memory database. `lastrowid` holds the id of the last inserted row. Source: https://docs.python.org/3.12/library/sqlite3.html. Cross-check: lab 2 run, 12 tests OK.
- `send_response` adds the status line plus Server and Date headers. `send_header` must be followed by `end_headers()`. `log_message` "is typically overridden". "http.server is not recommended for production." Source: https://docs.python.org/3.12/library/http.server.html. Cross-check: labs 2 and 4 run.

## Lesson 3 – Modular monolith boundaries
**Questions**
1. How do mainstream tools express "module A must not use module B's internals"?
2. How can a stdlib-only script find every import, including relative ones?
3. Where should the check run (test vs. CI)?

**Candidates**
| Source | Decision | I/C/A/O/T/D | Reason |
|---|---|---|---|
| import-linter.readthedocs.io (stable) | kept | 2/2/2/2/1/2 = 11 | Python equivalent; contract types |
| github.com/seddonym/import-linter | kept (supporting) | 1/2/2/2/1/2 = 10 | Licence BSD-2-Clause, v2.15 |
| archunit.org | kept | 2/2/2/1/1/1 = 9 | Java equivalent; licence not on page |
| github.com/sverweij/dependency-cruiser | kept | 2/2/2/2/1/1 = 10 | JS/TS equivalent; MIT |
| docs.spring.io Spring Modulith fundamentals | kept (supporting) | 2/2/2/1/1/1 = 9 | Concrete "API package vs internal sub-package" model |
| docs.python.org ast | kept | 2/2/2/2/1/2 = 11 | `Import`, `ImportFrom(module, names, level)` |
| import-linter contract_types.html | **dropped** | – | Fetch returned no content |

**Key facts**
- Import Linter "allows you to impose constraints on the imports between your Python modules". Its contract types are Forbidden, Protected, Layers, Independence, Acyclic siblings and custom. It runs as `lint-imports` with a `.importlinter` config. Source: import-linter docs.
- ArchUnit "can check dependencies between packages and classes, layers and slices, check for cyclic dependencies" by analysing bytecode inside "any plain Java unit test framework". Source: https://www.archunit.org/
- In Spring Modulith, an application module's base package is the API package. "Sub-package … is considered an internal one. Code within those must not be referred to from other modules". `ApplicationModules.of(…).verify()` checks this. Source: Spring Modulith fundamentals. Cross-check: this matches the lab's `internal/` convention and the import-linter "forbidden" example.
- dependency-cruiser validates dependencies "against (your own) rules" through `forbidden` rules (MIT). Source: GitHub README.
- `ImportFrom.module` has no leading dots, and `level` is "the level of the relative import (0 means absolute import)". Source: ast docs. Cross-check: relative-import test in lab 3 passes.

## Lesson 4 – API-first with OpenAPI
**Questions**
1. What is the current OpenAPI 3.1.x version, and which fields are required?
2. How are path parameters templated and matched?
3. Which OSS tools test a provider against its OpenAPI document, and what does consumer-driven contract testing add?

**Candidates**
| Source | Decision | I/C/A/O/T/D | Reason |
|---|---|---|---|
| spec.openapis.org/oas/v3.1.2.html | kept | 2/2/2/2/2/2 = 12 | Normative text, Apache-2.0 |
| spec.openapis.org/oas/ | kept | 1/2/2/2/1/2 = 10 | Version list (3.2.1 … 3.1.2 …) |
| docs.python.org http.server | kept | (as lesson 2) | Implementation API |
| github.com/schemathesis/schemathesis | kept | 2/2/2/2/1/1 = 10 | MIT; OpenAPI-driven testing |
| docs.pact.io | kept (supporting) | 1/2/2/1/1/1 = 8 | Clear definitions; page also has a commercial sign-up banner, which was ignored |
| Commercial contract-testing SaaS pages | **dropped** | – | Marketing |

**Key facts**
- Published versions: v3.2.1, v3.2.0, v3.1.2, v3.1.1, v3.1.0, v3.0.x, v2.0. 3.1.2 is dated 19 Sep 2025. Sources: https://spec.openapis.org/oas/ and https://spec.openapis.org/oas/v3.1.2.html (two official pages agree).
- `openapi` is REQUIRED and "MUST be the version number of the OpenAPI Specification". `info` is REQUIRED, with `title` and `version` REQUIRED inside it. An OAD "MUST contain at least one paths field, components field, or webhooks field". Tooling "SHOULD NOT" consider the patch version. Source: OAS 3.1.2.
- Path templating: "Each template expression in the path MUST correspond to a path parameter". "Concrete (non-templated) paths would be matched before their templated counterparts". It is RECOMMENDED to name the entry document `openapi.json` or `openapi.yaml`. Source: OAS 3.1.2.
- Schemathesis "tests OpenAPI and GraphQL APIs by generating inputs from your schema". It sends real requests, so point it at dev/staging, not production. MIT. Source: GitHub README.
- In Pact, a contract is "enforced by executing a collection of test cases … 'contract by example'". Provider contract testing checks a provider against its OpenAPI document but "does not provide any test based assurance that the consumers are calling the provider in the correct manner". Source: docs.pact.io. Cross-check: matches the Schemathesis description of schema-driven testing.

## Lesson 5 – 12-factor configuration
**Questions**
1. What exactly counts as "config", and where should it live?
2. How do I read env vars with defaults in Python, and when are they captured?
3. Are environment variables a safe place for secrets?

**Candidates**
| Source | Decision | I/C/A/O/T/D | Reason |
|---|---|---|---|
| 12factor.net/config | kept | 1/1/2/1/2/2 = 9 | The methodology the user asked to verify against |
| docs.python.org/3.12 os | kept | 2/2/2/2/1/2 = 11 | `os.environ`, `os.getenv` semantics |
| OWASP Secrets Management Cheat Sheet | kept | 1/2/2/1/2/2 = 10 | Security nuance on env vars |
| Vendor secret-manager product pages | **dropped** | – | Marketing; not needed for L100 |

**Key facts**
- Config is "everything that is likely to vary between deploys". The methodology "requires strict separation of config from code" and "stores config in environment variables". Env vars "are never grouped together as 'environments'". The litmus test is whether the codebase "could be made open source at any moment, without compromising any credentials". Source: https://12factor.net/config
- `os.environ` "is captured the first time the os module is imported, typically during Python startup". `os.getenv(key, default=None)` returns the default if the variable is missing. Source: Python 3.12 os docs. Cross-check: lab 5 subprocess tests.
- OWASP: secrets "should never be hardcoded using docker ENV or docker ARG". "Environment variables are generally accessible to all processes and may be included in logs or system dumps … not recommended unless the other methods are not possible." Source: OWASP cheat sheet. **Cross-check note:** this qualifies 12-factor. The lesson keeps env vars for non-secret config and adds a caution for secrets.

## Lesson 6 – Documenting architecture
**Questions**
1. Which C4 diagrams should an L100 team draw, and what is a "container"?
2. What is the exact current syntax for Mermaid C4 and Structurizr DSL context/container views, and how is it validated?
3. What is the original Nygard ADR format and where should ADRs live?

**Candidates**
| Source | Decision | I/C/A/O/T/D | Reason |
|---|---|---|---|
| c4model.com/diagrams | kept | 1/2/2/1/2/2 = 10 | Official C4 site |
| c4model.com/abstractions/container | kept (supporting) | 1/2/2/1/2/2 = 10 | Container definition |
| mermaid.js.org/syntax/c4.html (→ mermaid.ai/open-source/…) | kept | 2/2/2/1/1/1 = 9 | Official syntax; page includes a discount banner for a commercial editor, which was ignored |
| github.com/plantuml-stdlib/C4-PlantUML | kept (supporting) | 2/2/2/2/1/1 = 10 | Mermaid says its syntax is compatible; cross-checks macro signatures |
| docs.structurizr.com/dsl/language | kept | 2/2/2/1/2/2 = 11 | Normative DSL reference |
| docs.structurizr.com/validate | kept (supporting) | 2/2/2/1/1/1 = 9 | CI validation command |
| cognitect.com Nygard 2011 | kept | 2/1/2/2/2/1 = 10 | Template origin; copyright waived on page |
| adr.github.io | kept (supporting) | 1/2/2/1/2/1 = 9 | Credits Nygard's post for popularising ADRs; lists other templates |

**Key facts**
- "You don't need to use all 4 levels of diagram … the system context and container diagrams are sufficient for most software development teams." Source: https://c4model.com/diagrams
- "In the C4 model, a container represents an application or a data store … Not Docker!" Data storage you own (e.g. DB schemas) is treated as containers. Source: https://c4model.com/abstractions/container
- Mermaid C4 "is an experimental diagram for now. The syntax and properties can change". It is "compatible with plantUML". Supported elements include `Person`, `System`, `System_Ext`, `Container (alias, label, ?techn, ?descr …)`, `ContainerDb`, `Container_Boundary`, `Rel (from, to, label, ?techn …)`, and `UpdateLayoutConfig`. Layout follows statement order. Source: Mermaid C4 page. Cross-check: the C4-PlantUML README lists the same macro signatures.
- Structurizr DSL: `workspace [name] [description] { model { … } views { … } }`. Elements are declared as `person <name> [description]`, `softwareSystem <name> [description] [tags] { container <name> [description] [technology] [tags] }`. Relationships are written `<id> -> <id> [description] [technology]`. Views are `systemContext <system id> [key]` and `container <system id> [key]`, with `include *` and `autoLayout`, and styles use `element <tag> { shape Cylinder … }`. Source: https://docs.structurizr.com/dsl/language. Validate with `validate -workspace <file>` (https://docs.structurizr.com/validate).
- Nygard's ADR parts are Title ("short noun phrases", e.g. "ADR 9: LDAP for Multitenant Integration"), Context, Decision ("We will …"), Status ("proposed", "accepted", "deprecated" or "superseded"), and Consequences ("all consequences … not just the positive ones"). ADRs are "numbered sequentially and monotonically. Numbers will not be reused". Location: "doc/arch/adr-NNN.md". Source: the Nygard post. Cross-check: adr.github.io calls this the post "that popularized the concept" and defines an ADR as capturing "a single AD and its rationale".

---

## Concepts layer (CONCEPTS-SPEC.md) – added 2026-10-28
**Questions**
1. Which sources back the "why" behind each lesson: layering, monolith-first modularity, fitness functions, HTTP uniform interface, the 12 factors?
2. Which worked-example values can be computed from the lab code rather than worked out by hand?

**Candidates**
| Source | Decision | I/C/A/O/T/D | Reason |
|---|---|---|---|
| martinfowler.com/bliki/MonolithFirst.html | kept | 1/1/2/1/2/2 = 9 | Modularity before microservices |
| martinfowler.com/bliki/BoundedContext.html | kept (supporting) | 1/1/2/1/2/1 = 8 | Names the L200 topic in the primer's concept map |
| rfc-editor.org RFC 9110 | kept | 1/2/2/1/2/2 = 10 | HTTP's uniform interface hides the implementation |
| thoughtworks.com Radar – architectural fitness function | kept | 1/1/2/1/2/1 = 8 | Short definition; the newsletter sign-up on the page was ignored; blip is from 2018 |
| 12factor.net (index) | kept | 1/1/2/1/2/2 = 9 | Config is factor III of twelve |
| alistair.cockburn.us/hexagonal-architecture/ | **dropped** | – | Fetch was withheld by the content filter; Hexagonal is mentioned only via Fowler's page |
| RFC 9110 sections 15.5.x (409/422 wording) | **not used** | – | The fetched text was cut off before section 15, so no status-code definitions are quoted |

**Key facts**
- "Almost all the successful microservice stories have started with a monolith that got too big and was broken up". A gradual route to microservices "required a relatively good modular design to start with". Source: https://martinfowler.com/bliki/MonolithFirst.html. Cross-check: Spring Modulith's module verification serves the same goal inside one deployable.
- An architectural fitness function "provides an objective integrity assessment of some architectural characteristics, which may encompass existing verification criteria, such as unit testing, metrics, monitors". Source: Thoughtworks Radar. Cross-check: the ArchUnit and import-linter pages describe architecture rules run as tests.
- "HTTP hides the details of how a service is implemented by presenting a uniform interface to clients". Source: RFC 9110 §1.1. Cross-check: OAS 3.1.2 says an OpenAPI description lets consumers use a service "without requiring access to source code".
- The twelve factors list "III. Config – Store config in the environment" among 12 factors (last updated 2017). Source: https://12factor.net/
- Bounded Context is "a central pattern in Domain-Driven Design". Source: Fowler BoundedContext. Used only as an L200 topic name.

**Worked examples.** Every number in `content/concepts/*.md` comes from `research/concept_examples.py`, which runs the lab code in a subprocess per lab. The verbatim output is in `research/concept-examples-output.txt`.

## Rebalance (REBALANCE-SPEC.md) – 2026-10-28
No new sources. Concept notes were cut to 200–250 words (`wc -w`: 244–249) and the removed parts moved into
lesson fields: `inRealSystems` and `useWhen` (one line each, condensed from the notes' existing, already
cross-checked bullets), `checkYourself` (2 items each), and `next`. "Go deeper" links were merged into each
lesson's `sources` (added: Spring Modulith and Thoughtworks Radar to lesson 3, Pact to lesson 4, C4 Container
to lesson 6 – all already in VERIFIED-RESOURCES). The worked-example numbers kept in the notes were re-checked:
`python research/concept_examples.py` output is identical to `research/concept-examples-output.txt`.
Each `tryIt` `expected` value is pasted from the real output of `python try_it.py` in that lab (Python 3.12.15).
The only new external fact used is from the Mermaid syntax reference (https://mermaid.ai/open-source/intro/syntax-reference.html,
retrieved via web search 2026-10-28): "Line comments can ignore anything on the line after '%% '." It justifies the
`%%` comments in `c4-container.mmd`; parser confirmation is pending CI.
Concept share measured with the spec script: before 45% (3840 / 4656), after 21% (1530 / 5855).

## Platform + local-agent pass (PLATFORM-AGENT-SPEC.md) – 2026-10-28
**Questions.** (1) Exact install ids for Python 3.12, Node 22 (moved to Node 24 on 2026-10-28, see research/L200-evidence.md), Podman and Ollama on macOS (brew) and Windows (winget)?
(2) How do zsh and PowerShell set, unset and case-match env vars, and how do they show an exit code? (3) Do the Podman
and Structurizr images run on Apple silicon and Windows, and how are Windows paths mounted? (4) Which CI runners can
run what? (5) Does Ollama expose the OpenAI-compatible endpoint the shared client uses, and on which GPUs?

**Key facts (with source).**
- brew `python@3.12` 3.12.16 with arm64 bottles; Homebrew installs `python3.12` (https://formulae.brew.sh/formula/python@3.12).
  winget manifests exist for `Python.Python.3.12`, `OpenJS.NodeJS.LTS`, `RedHat.Podman`, `RedHat.Podman-Desktop`, `Ollama.Ollama`
  (https://github.com/microsoft/winget-pkgs). Cross-check: `py -3.12` and venv activation per shell from the Python 3.12 docs
  (https://docs.python.org/3.12/using/windows.html, https://docs.python.org/3.12/library/venv.html).
- "On Windows, the keys are converted to uppercase" (os.environ, https://docs.python.org/3/library/os.html). PowerShell:
  "Unlike Windows, environment variable names on macOS and Linux are case-sensitive"; `$Env:Foo = '...'`; `Remove-Item Env:\Foo*`;
  changes "affect only the current session" (about_Environment_Variables). `$LASTEXITCODE` holds the last native exit code
  (about_Automatic_Variables). Lesson 5 now has a test that asserts the case rule of the OS it runs on.
- Python 3.12 does not use UTF-8 mode by default (the default starts in 3.15, per the os docs), and Windows uses the ANSI code page
  for text files (Using Python on Windows §4.7). That is why every `read_text`/`write_text`/subprocess call in the labs now passes `encoding="utf-8"`.
- Podman on macOS runs a VM, and on Windows a WSL 2 (or Hyper-V) machine. WSL must be installed first (`wsl --install`, admin).
  Windows-style paths work in `-v` (https://podman.io/docs/installation, Podman-for-Windows guide). Podman's registries.conf comment
  recommends fully qualified image names, so the lessons use `docker.io/structurizr/structurizr:2026.09.19`.
- The structurizr 2026.09.19 tag is published for linux/amd64 and linux/arm64 (Docker Hub tags page).
- mermaid-cli: `npx -p @mermaid-js/mermaid-cli mmdc ...`; brew install "no longer supported" (README).
- GitHub runners: `macos-latest` is arm64 (M1), and "Nested-virtualization is not supported" there. `windows-latest` is x64
  (runners reference). `env` is allowed in `jobs.<id>.defaults.run` (contexts reference). `shell: bash` on Windows uses Git for Windows (workflow syntax).
- Ollama serves `/v1/chat/completions` at `http://localhost:11434/v1` (OpenAI compatibility docs). Metal on Apple; NVIDIA CC 5.0+
  (driver 550+); AMD via ROCm v7 or Vulkan; CPU otherwise (hardware docs). `qwen2.5:1.5b` = 986 MB (model page).

**Kept / dropped.** Kept 21 (scores 8–11, see VERIFIED-RESOURCES). Dropped: `docs.ollama.com/windows` (fetch returned no content; GitHub
copy used); the Docker Hub v2 tags API (empty fetch; tags page used); Colima / Rancher Desktop / Docker Desktop install pages (not fetched,
so they are named only in `equivalents`, with no commands or licence claims).

**Cross-platform fixes in lab code.** (1) `check_boundaries.py`: module names now come from `Path.parts` through `package_of()`, and
reports use `relative.as_posix()`, so output is identical on Windows. A new test feeds a `PureWindowsPath`. (2) Explicit
`encoding="utf-8"` in 19 `read_text`/`write_text`/subprocess calls across labs 1–6. (3) `check_env.py` prints the platform and looks for
`npx`, `podman` and `ollama` (`shutil.which` honours PATHEXT on Windows). (4) Lesson 5 gets a test for the env-name case rule. The grep for
`SIGALRM`, `fork`, `os.uname`, hard-coded `/tmp` and `0.0.0.0` found nothing. Servers already bound 127.0.0.1, and subprocesses already used `sys.executable`.

**Agent assist.** It is in lesson 6 only: an ADR is a document, and a deterministic checker can judge it fully. The vendored helper is unchanged
except for one `[[ADR-DRAFT]]` rule, which the header of the copy documents. Validation: 10 unit tests and `python agent_assist.py`, both against the fake server.
Concept share after: 17% (1530 / 7532). Before this pass: 21%.
