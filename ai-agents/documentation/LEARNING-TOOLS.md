# Learning tools – AI agents

Open-source GUI and low-code tools for this topic. Facts come from `../../shared/LEARNING-TOOLS-CATALOG.md` (checked 2026-10-28); exercises are in each lesson's `learningTools`.
Roles: SEE · BUILD WITHOUT CODE · CHECK (compare with your result) · INSPECT (look inside traffic/data).

| Tool | Role | Licence (OSI) | Mac mini install | Windows install | Lessons |
|---|---|---|---|---|---|
| Ollama 0.40.12 (runtime) | CHECK | MIT (yes) | `brew install ollama` → `brew services start ollama` | `OllamaSetup.exe` from ollama.com/download | 1, 2, 19 (speed probe) |
| KNIME Analytics Platform 5.12 | BUILD WITHOUT CODE | GPL-3.0 + KNIME permissions (yes) | `brew install --cask knime` | Installer from knime.com/downloads | 2 |
| promptfoo 0.125.1 | CHECK | MIT (yes) | `npx promptfoo@latest` or `brew install promptfoo` | `npx promptfoo@latest` / `npm i -g promptfoo` | 4, 5, 11, 12, 16 (local-first), 20, 21 |
| Langflow 1.13.0 | BUILD WITHOUT CODE | MIT (yes) | `uv pip install langflow && uv run langflow run` | same | 6, 7, 17 |
| Orange 3.40.0 | SEE | GPL-3.0-or-later (yes) | arm64 .dmg from orangedatamining.com | `winget install --id UniversityofLjubljana.Orange` | 7, 13, 22 (span durations) |
| MCP Inspector 2.12.0 | INSPECT | MIT + Apache-2.0 (yes) | `npx @modelcontextprotocol/inspector` (Node 24) | same | 10, 22 |
| AnythingLLM v1.19.0 | SEE | MIT (yes) | Desktop app | Desktop installer | 10 |
| Open WebUI v0.12.4 | SEE | Open WebUI License (**no**) | `pip install open-webui && open-webui serve` | same | 11, 15 (tool approval) |
| Jaeger v2.22.0 | SEE | Apache-2.0 (yes) | `jaeger-2.22.0-darwin-arm64.tar.gz` or container | Windows binary or container | 13 (`otel_sdk_equivalent.py --otlp`) |
| Toxiproxy v2.13.0 | BUILD WITHOUT CODE | MIT (yes) | `brew tap shopify/shopify && brew install toxiproxy` | `toxiproxy-server/cli-windows-amd64.exe` from releases | 14, 18 (reset after a payment) |
| Temporal CLI 1.9.1 dev server + Web UI | SEE | MIT (yes) | `brew install temporal; temporal server start-dev` | Windows amd64 archive; `temporal.exe server start-dev` | 18 (event history) |
| garak (NVIDIA) v0.17.1 | CHECK | Apache-2.0 (yes) | `python -m pip install -U garak` (Python 3.11–3.14) | same | 16, 21 (candidate model) |

Node 24 / Python 3.12: `../../shared/WORKSTATION-SETUP.md`. Use MCP Inspector ≥ 2.12.0 (earlier 2.x: three advisories). Langflow ≥ 1.13 needs `LANGFLOW_SUPERUSER_PASSWORD`.

## How to use these tools
They complement the code labs: you still write the code. Use a tool to see a concept, prototype a flow, or check your result – each exercise names a value the lab printed (`get_time({})`, `391`, `isError: true`, a nearest-neighbour pair) to compare against. Point every tool at the same local endpoint (Ollama on `127.0.0.1:11434`); never paste secrets. Set `PROMPTFOO_DISABLE_TELEMETRY=1` before any promptfoo run. A GUI still needs the checks the labs teach: validation, citations, approval, budgets.

## Not recommended / changed
- **Flowise** – end of life 2026-08-31 (repo archived).
- **n8n** – fair-code (Sustainable Use License), not OSI.
- **Dify** – modified Apache-2.0 with extra conditions, not OSI.
- **Langfuse** – open-core (MIT outside `ee/`); not catalogued.
- **Arize Phoenix** – Elastic License 2.0, not OSI.
- **Open WebUI** – no longer OSI-licensed (branding clause); kept above only for its tool-approval UI.
- **promptfoo red team (changed)** – uses promptfoo's hosted inference by default (purpose, prompts, target responses, your email go to api.promptfoo.app). Lesson 16 runs it local-first: `PROMPTFOO_DISABLE_REMOTE_GENERATION=true`, `PROMPTFOO_DISABLE_TELEMETRY=1`, Ollama as attacker and grader, no remote-only plugins. The npm download and account/usage checks still go out; garak is the alternative that talks only to Ollama.
- **Zipkin / Tempo** – dropped: Zipkin duplicates Jaeger; Tempo has no own UI.
- **RapidMiner** – now proprietary; open core frozen at 9.7/9.10.
- **Orange Text add-on Document Embedding** – sends text to a remote server; use the lab's `export_embeddings.py` CSV.
