# L300 learning-tools proposal (2026-10-28)

One table per topic. Columns: **Lesson · Tool · Status · Role · Concrete exercise tied to the lab · Expected value from the lab README**. Limit: **max 2 tools per lesson**, counting the tools already in the lesson's `learningTools`. Where a new tool would exceed the limit, the row says which existing entry it replaces. All rows are *pending a manual run* — no tool was run in the authoring sandbox; expected values were copied from the lab READMEs (checked by string match against each README when this file was generated).

Licences and versions: see `LEARNING-TOOLS-CATALOG.md` → *L300 additions*. Non-OSI tools are marked in the Tool column.

## Quantum computing

| Lesson | Tool | Status | Role | Exercise | Expected (lab README) |
|---|---|---|---|---|---|
| 12 | Qiskit visualization | already in lesson | SEE | plot_histogram of ideal vs noise-model counts from noise_lab.py; plot_state_city of the noisy density matrix. | Ideal bars only 00/11; the noisy bars add the lab's '01': 82 and '10': 70 (noisy Bell counts {'00': 962, '01': 82, '10': 70, '11': 886}). |
| 13 | JupyterLab | already in lesson | CHECK | Plot P000 against scale 1/3/5 and draw the linear and quadratic fits down to scale 0. | Points 0.9039 / 0.7474 / 0.6234; linear 0.9687, Richardson 0.9944; ideal 1.0. |
| 13 | Mitiq 1.1.0 | **add** | CHECK | Run mitiq_zne.py, then swap in LinearFactory / RichardsonFactory with scale_factors [1, 3, 5] and compare with your own extrapolation. | README (pending CI): raw P(000) 0.9039, linear ≈0.9687, Richardson ≈0.9944; Cirq float32 agrees to ~1e-4. |
| 14 | marimo | already in lesson | SEE | Sliders for γ and β over qaoa_lab.ratio([γ, β]). | Peak near γ 0.63, β 0.39, ratio ≈0.82 (lab grid 0.8188). |
| 14 | Qiskit visualization | already in lesson | SEE | plot_histogram of 1000 shots of the p = 2 circuit. | The four optimal cuts carry ≈0.707 of the shots. |
| 15 | JupyterLab | already in lesson | CHECK | Plot energy_est against evals for the finite-difference and SPSA logs with E0 drawn in. | Tail std 0.3912 (finite difference) vs 0.0065 (SPSA); E0 = -1.8405. |
| 16 | marimo | already in lesson | SEE | Sliders for qubits, layers and init over gradient_scan(). | Uniform init 0.7171 at 2×2 falling to 0.0208 at 10×20. |

## Cryptography

| Lesson | Tool | Status | Role | Exercise | Expected (lab README) |
|---|---|---|---|---|---|
| 12 | CyberChef | already in lesson | CHECK | AES-GCM decrypt of tool_check.py's wrapped DEK with AAD orders-kek:v1, then v2. | v1 gives the 32 × 0xa0 DEK; v2 fails like the lab's InvalidTag. |
| 12 | OpenBao 2.7.2 (transit + web UI) | **add** | SEE | Dev server from the README, run openbao_transit.py, then in the UI read orders-kl12's versions, rotate, rewrap a vault:v1 ciphertext and set min decryption version 2. | Same story as the lab: rewrap gives vault:v2 without plaintext; after min_decryption_version=2 the old ciphertext is refused — the service version of 'retire v1 after a full rewrap: 6/6 decrypt' vs '1/6 decrypt; LOST'. |
| 13 | step CLI | already in lesson | CHECK | step certificate inspect tool_check/leaf.pem. | 160 h validity, Not Before one hour before issue, serial from tool_check.py. |
| 13 | KeyStore Explorer | already in lesson | INSPECT | Examine File on leaf.pem. | Same 160 h validity and SAN localhost/127.0.0.1. |
| 14 | CyberChef | already in lesson | CHECK | SHA2-256 of the 20-line app/core.py from tool_check.py. | b9dc24f7…516c (540 bytes). |
| 14 | minisign 0.12 | **add** | CHECK | Sign MANIFEST.json, verify, then edit one hex digit of a digest and verify again. | Verify passes, then fails — same verdict as try_it 2: 'manifest signature invalid'. |
| 15 | CyberChef | already in lesson | CHECK | AES-GCM decrypt of Wycheproof tcId 10 values, then with the truncated tag. | Plaintext dfc61a20…d3d6; the lab's strict wrapper rejects the 8-byte tag. |
| 16 | CyberChef | already in lesson | CHECK | From Base64 on tool_check.py's encoded value. | The sk_demo_ value reappears: base64 is encoding, not protection. |
| 16 | Gitleaks 8.30.1 | **add** | CHECK | gitleaks dir review_me.log -v; then gitleaks stdin --max-decode-depth=2 on try_it's base64 key. | Lab's exact-value scanner: 'scan with known=[key]: []' until b64(key) is added. Whether Gitleaks' default rules flag the low-entropy demo values (db_password demo-only-s3cr3t, sk_demo_c0ffee…) is unverified — record what it finds. |

## AI agents

| Lesson | Tool | Status | Role | Exercise | Expected (lab README) |
|---|---|---|---|---|---|
| 12 | promptfoo | already in lesson | CHECK | Run promptfooconfig.yaml with v1, then -p prompts/v2.txt; promptfoo view. | v1 all green; v2 red on t07 and t15, exit code 100. |
| 13 | Orange Data Mining | already in lesson | SEE | Box plot of duration_ms by span name from spans_to_csv.py. | execute_tool search_docs ≈600 ms, chat spans a few ms. |
| 13 | Jaeger (existing catalogue entry, new mapping) | **add** | SEE | Swap InMemorySpanExporter for the OTLP/HTTP exporter in otel_sdk_equivalent.py and open the run in Jaeger (:16686). | One trace: root invoke_agent support-agent ≈644 ms, execute_tool search_docs ≈600 ms (93 %), four chat fake-model spans ≈21.7 ms in total. |
| 14 | Toxiproxy (existing catalogue entry, new mapping) | **add** | BUILD WITHOUT CODE | Proxy the fake server (8765 → 26014), add a 2000 ms latency toxic, run resilient_agent.py through the proxy with the fallback on the direct port. | Each primary call ends at the 0.5 s per-call timeout ('error': 'timeout', ≈503 ms in the lab's log), retries, then a 'fallback' event — the run stays bounded instead of hanging like the naive loop (6.1 s on one question). |
| 15 | Open WebUI (non-OSI) | already in lesson | SEE | Tool approval 'ask first' vs one row of the lab's approvals table. | UI asks, but only the lab persists (1, 'send_refund', 'done', 'alice') and makes the retry idempotent. |
| 16 | promptfoo | already in lesson | CHECK | redteam init / run / report against the local Ollama model. | Reported injections must still be blocked by the policy layer (protected 8/8). |
| 16 | garak 0.17.1 | **add** | CHECK | garak --target_type ollama --target_name qwen2.5:1.5b --spec probes.promptinject; read hit rates in the report. | Non-zero hit rates are expected (the model is fooled — the lab's unprotected run is safe in 1/8 cases); the lab's protected suite stays 8/8 because code, not the model, blocks the actions. |

## Distributed systems

| Lesson | Tool | Status | Role | Exercise | Expected (lab README) |
|---|---|---|---|---|---|
| 12 | Maelstrom | already in lesson | CHECK | Raft chapter node on lin-kv with a partition nemesis. | Valid only with the election restriction (lab: 11 of 20 seeds lose data without it). |
| 13 | Toxiproxy | already in lesson | BUILD WITHOUT CODE | Proxy serve_realtime.py, add 300 ms latency, then disable the proxy. | ≥0.3 s slower; disabled proxy looks like a timeout. |
| 13 | Maelstrom | already in lesson | CHECK | lin-kv against a cache-reading single node with partitions. | Checker says invalid, like the lab's 'linearizable: False'. |
| 14 | Temporal CLI 1.9.1 dev server + Web UI | **add** | SEE | Port the orchestrator to a Temporal workflow with create/charge/ship activities and refund/cancel compensations; run seed 14 and open o1's event history (:8233). | Without compensation the lab audit shows 'o1: FAILED, shipped=False, money kept=10 of 10'; after the build task o1's history should show ship failed, then refund and cancel in reverse order (o1, o5, o6 fail at ship). |
| 15 | Jaeger | already in lesson | SEE | otel_equivalent.py --otlp; search the W3C example trace id. | orders GET /create → payments GET /authorize under trace 4bf92f3577b34da6a… (the W3C example header the script continues; tryIt 1 shows the same id). |
| 15 | Grafana OSS | already in lesson | INSPECT | Jaeger data source, same trace in Explore. | Same spans; a broken hop is a separate one-span trace. |
| 16 | Grafana k6 (+ built-in web dashboard) | already in lesson | CHECK | load_test.js at 120 req/s against bounded and --unbounded servers; add K6_WEB_DASHBOARD=true and export the HTML report. | Bounded: 780 × 200, 420 × 503 (≈35 % failed), p99 193 ms; unbounded p99 3787 ms. |
| 16 | Grafana OSS | already in lesson | SEE | Per-second offered/ok/shed/p99 once exported to Prometheus or PostgreSQL. | Optional now: the k6 web dashboard shows the same shapes without an export step — if a slot is needed, this is the entry to drop. |

## Application architecture

| Lesson | Tool | Status | Role | Exercise | Expected (lab README) |
|---|---|---|---|---|---|
| 12 | marimo | already in lesson | CHECK | Histogram of lag_ms from out/projector.jsonl; poll interval as a cell. | p50 ≈10 ms at 20 ms polling; > 100 ms at 200 ms. |
| 13 | Toxiproxy | already in lesson | BUILD WITHOUT CODE | 1000 ms latency toxic in front of provider.py; Pool('catalogue', 4) with timeout 0.1. | TimeoutError after ≈0.1 s while busy stays at the stuck-call count. |
| 14 | Bruno | already in lesson | CHECK | GET /books/b1 with type assertions on title and available. | 200 b1 'Dune' available true; with title_field='name' the title assertion fails. |
| 14 | Pact Broker 2.122.0 (Docker, SQLite) | **add** | SEE | Publish the Pact V4 file from the CI-only pact/ flow to a local broker and browse it; add a provider verification result to see the matrix. | Should list loans-service → catalogue-service with the one interaction the lab's Pact test writes ('book b1 exists' → 200 Dune; the 404 case lives only in the lesson's own contract file). The pact flow is pending-ci, so record what pact-python 4.2.0 writes. |
| 15 | JupyterLab | already in lesson | CHECK | Per-minute latency plot from out/requests.jsonl; recompute the 1h burn rate. | Mean 147.9 ms, p99 2846.3 ms, latency burn 19.7 over 1h. |
| 15 | Prometheus 3.15.1 (promtool test rules) — replaces Grafana OSS | **add** | CHECK | Write the 1h/5m latency page rule (threshold 14.4) and a promtool test with input_series for the incident hour (last hour: 71 POST /loans, 14 slow; last 5 min: 3, 1 slow — from the lab log). | 14/71 slow → burn 19.7 (1h); 1/3 → 33.3 (5m); both > 14.4, so the page alert must fire — the lab's 'burn 19.7 over 1h/5m', burn_short 33.3, threshold 14.4. |
| 16 | Grafana k6 (+ web dashboard) | already in lesson | CHECK | k6/overdue.js vs load_test.py's p95; tighten to p(95)<10. | Same range as the lab gate (p95 4.8–105 ms here), exit 0; non-zero with the tight threshold. |
| 16 | import-linter | already in lesson | CHECK | Forbidden contract: domain must not import sqlite3/http_api/loans_repo. | Agrees with gate_import_boundaries(); tryIt 2 planted import reported. |

## micro:bit (simulator-only)

| Lesson | Tool | Status | Role | Exercise | Expected (lab README) |
|---|---|---|---|---|---|
| 12 | micropython-microbit-v2-simulator | already in lesson | CHECK | Inject 'D:1:r1:<CRC>' with a good and a bad CRC. | Good frame prints 'rx 1 r1' and acks; bad frame is dropped. |
| 12 | MakeCode | already in lesson | SEE | Ack in blocks between two simulated boards. | Each data message followed by an ack. |
| 13 | micro:bit Python Editor v3 | already in lesson | CHECK | Click A 5 times during the blocking loop, then with solution.py. | Stub: 1 of 8 vs 8 of 8. |
| 13 | MakeCode | already in lesson | SEE | on button A pressed + forever/pause 1000. | Event blocks count every click. |
| 14 | Orange Data Mining | already in lesson | SEE | Line plot of the logged interval. | Interval 100 → 8000 ms while steady, back to 100 ms on change. |
| 14 | micro:bit Python Editor v3 | already in lesson | CHECK | Data logging view, move the temperature slider after 30 s. | Rows every ≈8 s, then every 100 ms after a change. |
| 15 | Orange Data Mining | already in lesson | SEE | Plot temp/light against seq from the --demo telemetry. | 190 frames accepted; gaps at the missing sequence numbers. |
| 15 | Apache Superset | already in lesson | SEE | Upload the CSV, chart temp over seq plus the metrics snapshots. | frames_ok 50/100/150/190 vs resyncs 5/6/8/9. (MQTT Explorer was the candidate replacement — dropped: CC BY-ND licence, last stable 2019.) |
| 16 | Renode 1.17.0 | **add** | CHECK | renode renode/microbit-v2-sibling.resc (fixed build), then the racy ELF via -e; watch the uart0 analyzer; optional renode --ui. | Fixed build ends 'done lost_total=0' (what interrupt_race.robot asserts). Racy build: loss in emulation is recorded, not asserted — the deterministic proof is the host model (soak loses 316 of 1,316). |

## Simulation (civilian)

| Lesson | Tool | Status | Role | Exercise | Expected (lab README) |
|---|---|---|---|---|---|
| 12 | marimo | already in lesson | CHECK | SHIFT_H and n as cells over the variance-reduction table. | At 7.0 h: exact 0.9196, antithetic 1.46x, control variate 5.40x. |
| 13 | JupyterLab | already in lesson | CHECK | Plot the three fitted models over 0–12 h with the 8 h line. | poly-6 dives to -19.60 C at 12 h; two-exp within ≈0.16 C. |
| 14 | marimo | already in lesson | SEE | Interaction coefficient and NOMINAL[0] as cells over oat() and sobol(). | At 24: window_open OAT 0.0, ST 0.155; OAT 96.0 at 26 C. |
| 14 | SALib 1.6.0 | **add** | CHECK | Run sensitivity_salib.py, then the ProblemSpec chain with sp.plot(). | window_open S1 ≈0.005 but ST ≈0.155; the lab's test requires SALib's ST within 0.03 of the numpy result. |
| 15 | OpenModelica (OMEdit) | already in lesson | CHECK | Export RoomThermal.mo as an FMI 2.0 CS FMU; run fmpy_cosim.py. | h = 60 s settles (swing ≤ 0.2 C), 900 s oscillates — lab 0.0 vs 6.78 C. |
| 15 | Scilab + Xcos | already in lesson | BUILD WITHOUT CODE | Room + PI controller with a sample-and-hold every h seconds. | 60 s settles at 21 C; 900 s oscillates by several degrees. |
| 15 | FMPy 0.3.32 GUI (non-OSI variant licence) | reserve (not added) | INSPECT | Open RoomThermal.fmu, inspect variables/default experiment, Tools › Create Jupyter Notebook. | Not added (limit 2). Swap in for Scilab + Xcos only on the Windows PC with the OMEdit-exported FMU (win64 binaries). |
| 16 | JupyterLab | already in lesson | CHECK | %timeit loop vs vectorised; max abs difference. | Difference ~1e-13 (lab 9.1e-14); speed-up of the order of 10–26x. |

## Changes to lesson `learningTools` this proposal implies

- **Quantum computing:** #13 Mitiq 1.1.0
- **Cryptography:** #12 OpenBao 2.7.2 (transit + web UI); #14 minisign 0.12; #16 Gitleaks 8.30.1
- **AI agents:** #13 Jaeger (existing catalogue entry, new mapping); #14 Toxiproxy (existing catalogue entry, new mapping); #16 garak 0.17.1
- **Distributed systems:** #14 Temporal CLI 1.9.1 dev server + Web UI
- **Application architecture:** #14 Pact Broker 2.122.0 (Docker, SQLite); #15 Prometheus 3.15.1 (promtool test rules) — replaces Grafana OSS
- **micro:bit (simulator-only):** #16 Renode 1.17.0
- **Simulation (civilian):** #14 SALib 1.6.0
- **Replacements:** application-architecture #15 — Prometheus (promtool) replaces Grafana OSS (Grafana there could only start from TestData; promtool checks the real alert maths). Distributed-systems #16 keeps Grafana but marks it as the first to drop, since the k6 web dashboard now covers the visual. Simulation #15 keeps OpenModelica + Scilab/Xcos; FMPy stays in reserve.
- **Not applied to content/L300.json** in this pass — this file is the proposal; the catalogue JSON already carries the mappings.


## Corrections after applying (2026-10-28)
- App-arch #15 promtool numbers and #14 Pact interaction count corrected to the lab's real values (found by the topic update pass).
- Maelstrom on Windows: no native support stated; WSL 2 or the Mac mini.
