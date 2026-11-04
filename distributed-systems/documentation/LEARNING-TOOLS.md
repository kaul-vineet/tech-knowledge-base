# Learning tools — distributed systems

Open-source tools to see, inspect or check what the labs do. Facts come from `../../shared/LEARNING-TOOLS-CATALOG.md` (checked 2026-10-28; URLs there). Exercises live in each lesson's `learningTools` field; none was run here (pending manual runs).

| Tool | Role | Licence (OSI) | 🍎 Mac mini | 🪟 Windows 11 | Lessons |
|---|---|---|---|---|---|
| Toxiproxy | BUILD WITHOUT CODE / INSPECT | MIT (yes) | `brew tap shopify/shopify && brew install toxiproxy` | `toxiproxy-server/cli-windows-amd64.exe` from releases | L100 #3, #4; L300 #13; L400 #19, #20 |
| Jaeger | SEE | Apache-2.0 (yes) | `jaeger-2.22.0-darwin-arm64.tar.gz` or container `cr.jaegertracing.io/jaegertracing/jaeger:2.22.0` | Windows binary or container | L100 #2, #4, #5; L300 #15; Capstone #22 |
| Maelstrom (Jepsen) | CHECK / SEE | EPL-1.0 (yes) | JDK 11+, Graphviz, Gnuplot; untar release, `./maelstrom` | no native support (project statement); WSL 2 (unverified) or the Mac mini | L100 #6; L300 #12, #13; L400 #17, #18, #21 |
| RabbitMQ + management UI | INSPECT | MPL-2.0 (yes) | `brew install rabbitmq; rabbitmq-plugins enable rabbitmq_management` → http://localhost:15672 | `rabbitmq-server-4.4.0.exe` (Erlang requirement not checked) | L200 #8 |
| NATS server + NATS CLI | INSPECT | Apache-2.0 (yes) | `brew install nats-server nats` | partial: CLI `scoop install extras/natscli`; server via container | L200 #8 |
| Grafana k6 (+ built-in web dashboard) | CHECK | AGPL-3.0 (yes) | `brew install k6` | `winget install k6 --source winget`, or MSI | L200 #11; L300 #16; L400 #19, #20 |
| Temporal CLI dev server + Web UI | SEE | MIT (yes) | `brew install temporal; temporal server start-dev` → http://localhost:8233 | Windows amd64 archive from the CLI README; `temporal.exe server start-dev` | L300 #14; Capstone #22 (+ `pip install temporalio==1.34.0`) |
| Grafana OSS (cross-cutting) | SEE / INSPECT | AGPL-3.0-only (yes) | `brew install grafana && brew services start grafana` | installer or zip — pick *Open Source* | L200 #11; L300 #15, #16 |
| Apache Superset (cross-cutting) | SEE | Apache-2.0 (yes) | `pip install apache_superset` or Docker Compose | partial: no official Windows support | L200 #11 (catalog only) |

Lessons 1, 7, 9 and 10 have no tool. In L400, Maelstrom checks the lab's verdicts (lin-kv, pn-counter), Toxiproxy turns the simulated region latencies and chaos faults into real socket faults, and k6 measures the steady state during them.

## How to use these tools
They complement the code labs: you still write and run the code; a tool lets you see the concept (Jaeger spans), build a failure without editing code (Toxiproxy), or check your result against an independent judge (Maelstrom's checker, k6's p99). Each exercise names the lab value it should match. Bind every tool to `127.0.0.1`: the Toxiproxy API on :8474 is unauthenticated by default.

L400 equivalents that are not learning tools: TLA+/TLC (lesson 21, run in CI) and Automerge (lesson 18, run in CI) are libraries/specification tools; Chaos Mesh (lesson 20) is named as a one-line Kubernetes equivalent only.

## Not recommended / changed
- **RaftScope / The Secret Lives of Data**: unmaintained. Fine as a 5-minute watch-only link before lesson 7.
- **ShiViz**: last commit ≈5 years ago, licence "Other". Use Maelstrom's `messages.svg`.
- **etcdkeeper**: ≈2 years without commits. Use `etcdctl`.
- **Redis Insight**: SSPL, not OSI-approved. Use `valkey-cli`.
- **Grafana**: AGPL-3.0 since 2021. Download the Open Source build.
- **Zipkin**, **Grafana Tempo**, **Perses**, **Langfuse** (L300 #15 candidates): duplicate Jaeger/Grafana, need Grafana, pre-1.0 with fixed critical issues, or open-core.
- **Maelstrom on Windows**: no native support; WSL 2 is unverified (KNOWN-GAPS R3-20).
