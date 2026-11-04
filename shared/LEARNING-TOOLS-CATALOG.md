# Learning-tools catalogue (visual / GUI / low-code)

Checked **2026-10-28** against official sites, repos, release pages, PyPI/CRAN/Homebrew and vendor docs only (no blogs).
Target hardware: Apple-silicon Mac mini (macOS arm64) and a Windows 11 PC. Machine-readable copy: `learning-tools.json`.

**Roles:** SEE = visualise a concept · BUILD WITHOUT CODE = prototype visually · CHECK = compare your code's result · INSPECT = look inside traffic or data.
**Rules applied:** open-source (OSI) first; proprietary / fair-code tools are listed only in *Mentioned, not catalogued*; tools with no release/commit for >2–3 years or an unverifiable licence are under *Considered and dropped*.
"≈" = the source showed a relative date ("4 days ago") on 2026-10-28; "year inferred" = GitHub omitted the current year. Exercises are **suggestions** that fit our lesson titles; tool facts are verified.

## Corrections to the original list

- **RapidMiner — no open-source core today.** The AGPL-3.0 repos stop at RapidMiner 9.7 (`rapidminer-studio`, described as "Outdated version … 7.x – 9.7") and 9.10 (`rapidminer-studio-modular`), ≈5–6 years old. Altair completed the RapidMiner acquisition on 2022-09-16, and Siemens completed its acquisition of Altair on 2025-03-26. The current product (docs now say "Rapidminer AI Studio", versions up to 2026.0) requires a licence and EULA on first launch → **proprietary, not OSI**. Sources: github.com/rapidminer/rapidminer-studio, github.com/rapidminer/rapidminer-studio-modular, prnewswire.com (Altair completion release), press.siemens.com (Altair acquisition), docs.rapidminer.com/latest/studio/installation/.
- **KNIME** is GPL-3.0 **plus KNIME's additional permissions under GPLv3 §7** (Eclipse interop; third-party nodes may carry any licence). The desktop Analytics Platform is free; KNIME Pro, Team and Business Hub are paid. Local LLMs are verified via Ollama (OpenAI Authenticator → `http://localhost:11434/v1`) and the GPT4All connector node.
- **Rattle** is no longer "just the R package": the current Rattle is a **Flutter GUI (GPL-3.0, v6.5.x, github.com/gjwgit/rattle)** with an R back-end; CRAN `rattle` 5.6.2 (2026-02-08) now only supports that GUI (the old RGtk2 GUI needs rattle 5.5.1). rattle.togaware.com is the *older V5* site; the current page is togaware.com/projects/rattle.
- **WEKA**: GPL-3.0 (versions > 3.7.5); current stable 3.8.7 with arm64 macOS and Windows installers that bundle a JVM. The GitHub mirror `Waikato/weka-3.8` was archived in 2022 — the official repo is git.cms.waikato.ac.nz.
- **Orange**: GPL-3.0-or-later, latest 3.40.0 (2025-12-20). Add-ons exist as claimed (Text, Network, Timeseries, Explain), but **Timeseries' last release is 2024-03-15**, the **Text add-on's licence could not be confirmed** (possibly AGPL-3.0), and Orange has **no LLM widget** — Text's *Document Embedding* sends tokens to a biolab server (not local).
- **Apache Superset**: Apache-2.0 confirmed (6.1.0, 2026-05-13). Not container-only: `pip install apache_superset` is documented too. But **"Superset does not have official support for Windows"** — on the Windows PC use Docker Desktop (unofficial).
- **Grafana** is **AGPL-3.0** (since 2021), not Apache-2.0; pick the *Open Source* download, not the default *Enterprise* build.
- **n8n** is fair-code (Sustainable Use License) — not OSI. **Open WebUI** is no longer OSI-licensed (custom licence with a branding clause). **Flowise** reached end of life on 2026-08-31.
- **IBM Quantum Composer** is a proprietary IBM web service and supports **OpenQASM 2.0 only**. **Quirk** still works but has had no release since 2019.
- **Structurizr Lite is EOL** (archived 2026-02-04) → use `structurizr/structurizr local`. **draw.io Desktop moved from Apache-2.0 to GPL-3.0** in 31.5.2 (the jgraph/drawio core stays Apache-2.0).
- **Mu editor** was archived 2025-08-31. **Wokwi** does not support the micro:bit. **micro:bit CreateAI** needs a physical board.
- **XCA** lives at `chris2511/xca` (not hohnstaedt/xca). **mkcert** and **JCrypTool** are stale. The Microsoft `qsharp` package is archived → use `qdk`. **OpenModelica** has no native macOS build since 1.16 (Docker + XQuartz on the Mac).

## Quantum computing

| Tool | Role | Licence (OSI) | Latest | Mac / Win |
|---|---|---|---|---|
| Qiskit visualization (qiskit.visualization) | SEE | Apache-2.0 (yes) | qiskit 2.6.1 (2026-10-22) | yes / yes |
| Microsoft Quantum Development Kit (qdk + VS Code extension) | SEE / CHECK | MIT (yes) | qdk 1.33.1 (2026-10-08) | yes / yes |
| OpenQASM 3 spec + openqasm3 reference parser | CHECK | Apache-2.0 (yes) | spec 3.1; openqasm3 1.0.1 (parser 2025-02-19) | yes / yes |
| qiskit-qasm3-import | CHECK | Apache-2.0 (yes) | 0.6.0 (2025-06-10) | yes / yes |

#### Qiskit visualization (qiskit.visualization)
- **Role:** SEE — draw circuits, Bloch spheres, histograms and device coupling maps from your own circuits.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** qiskit 2.6.1 (2026-10-22) · maintained: yes
- **macOS arm64:** yes — pip install 'qiskit[visualization]'
- **Windows 11:** yes — pip install "qiskit[visualization]"
- **Lessons (suggested exercises):**
  - L100 #2: Call plot_bloch_multivector after each gate (H, X, S) and predict the arrow before you look.
  - L100 #3: plot_histogram of counts for 100 vs 10 000 shots; see the sampling noise shrink.
  - L100 #4: plot_state_city on the Bell state: only |00> and |11> amplitudes are non-zero.
  - L200 #11: plot_circuit_layout / plot_coupling_map before and after transpile(optimization_level=3) on a line coupling map.
- **Notes:** Docs warn the visualisers may call system programs on input — use on trusted circuits only.
- **Sources:** https://pypi.org/project/qiskit/ · https://quantum.cloud.ibm.com/docs/en/api/qiskit/visualization

#### Microsoft Quantum Development Kit (qdk + VS Code extension)
- **Role:** SEE / CHECK — circuit diagrams and breakpoint debugging for OpenQASM (and Q#) in VS Code; a second simulator to cross-check results.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** qdk 1.33.1 (2026-10-08) · maintained: yes (commit 4 days before check)
- **macOS arm64:** yes — pip install qdk ; VS Code extension 'Microsoft Quantum Development Kit (QDK)' (or vscode.dev/quantum/playground)
- **Windows 11:** yes — pip install qdk ; same VS Code extension
- **Lessons (suggested exercises):**
  - L100 #5: Open your exported .qasm file in VS Code with the QDK extension, view the circuit diagram, set a breakpoint and step.
  - L200 #8: Step through the Grover iteration in the debugger and watch the marked state's amplitude grow.
  - L100 #6: Use qdk[qiskit] interop to run the same circuit and compare counts with Qiskit/Cirq (a third framework).
- **Notes:** The older 'qsharp' PyPI package was archived 2026-08-24 — use 'qdk'. Python telemetry on by default (QDK_PYTHON_TELEMETRY=none). Extension version/licence text not shown on Marketplace page (repo is MIT).
- **Sources:** https://pypi.org/project/qdk/ · https://github.com/microsoft/qdk · https://marketplace.visualstudio.com/items?itemName=quantum.qsharp-lang-vscode · https://pypi.org/project/qsharp/

#### OpenQASM 3 spec + openqasm3 reference parser
- **Role:** CHECK — parse your exported OpenQASM 3 and walk the AST; read the live spec for the standard gate set.
- **Licence:** Apache-2.0 (spec repo and parser) · OSI-approved: **yes**
- **Latest:** spec 3.1; openqasm3 1.0.1 (parser 2025-02-19) · maintained: spec: yes (commit ≈3 months before check); parser: last release ≈20 months ago
- **macOS arm64:** yes — pip install "openqasm3[parser]"
- **Windows 11:** yes — pip install "openqasm3[parser]"
- **Lessons (suggested exercises):**
  - L100 #5: Parse the Bell-pair QASM 3 you exported from Qiskit and count gate calls in the AST; hand-write the same circuit from the spec's stdgates.inc.
- **Notes:** Parser API is declared not yet stable.
- **Sources:** https://github.com/openqasm/openqasm · https://pypi.org/project/openqasm3/

#### qiskit-qasm3-import
- **Role:** CHECK — enables qiskit.qasm3.load/loads so a QASM 3 file round-trips back into Qiskit.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** 0.6.0 (2025-06-10) · maintained: yes (described by maintainers as a stop-gap)
- **macOS arm64:** yes — pip install qiskit-qasm3-import (or qiskit extra qasm3-import)
- **Windows 11:** yes — same
- **Lessons (suggested exercises):**
  - L100 #5: qasm3.dumps → qasm3.loads round-trip; assert both circuits give the same counts.
  - L100 #6: Export from Cirq with circuit.to_qasm(version='3.0'), load into Qiskit, compare counts.
- **Notes:** Cirq QASM import is 'experimental' and covers a limited subset.
- **Sources:** https://pypi.org/project/qiskit-qasm3-import/ · https://pypi.org/project/qiskit/ · https://quantumai.google/cirq/build/interop

## Cryptography

| Tool | Role | Licence (OSI) | Latest | Mac / Win |
|---|---|---|---|---|
| CyberChef | CHECK / SEE | Apache-2.0 (yes) | v11.5.0 (≈2026-09-18 (year inferred)) | yes / yes |
| Wireshark | INSPECT | GPL-2.0 (yes) | 4.6.9 (stable) (not shown on fetched page (2026)) | yes / yes |
| XCA (X Certificate and Key management) | BUILD WITHOUT CODE / INSPECT | BSD-3-Clause (yes) | 2.9.0 (2025-03-28) | yes / yes |
| KeyStore Explorer | INSPECT | GPL-3.0 (yes) | 5.7.0 (≈2026-08-23 (year inferred)) | yes / yes |
| step CLI (smallstep) | CHECK | Apache-2.0 (yes) | v0.31.0 (2026-09-25) | yes / yes |
| CrypTool 2 | SEE | Apache-2.0 (yes) | 2.1 stable build 9778.2 (nightly 9843.1) (stable 2024-01-31; nightly 2025-12-19) | no / yes |

#### CyberChef
- **Role:** CHECK / SEE — browser 'recipe' workbench: re-compute your Python outputs (SHA-256, HMAC, AES-GCM, Argon2, JWT, X.509) without code.
- **Licence:** Apache-2.0 (Crown Copyright) · OSI-approved: **yes**
- **Latest:** v11.5.0 (≈2026-09-18 (year inferred)) · maintained: yes (commit 4 days before check)
- **macOS arm64:** yes — Browser, or download the offline copy (link top-left / release zip); Docker ghcr.io/gchq/cyberchef
- **Windows 11:** yes — Browser or offline zip (runs fully client-side)
- **Lessons (suggested exercises):**
  - L100 #2: Compare Python SHA-256 and HMAC-SHA256 hex with the SHA2 and HMAC operations.
  - L100 #4: Decrypt your Python AES-256-GCM output with AES Decrypt (GCM, tag + AAD); flip one byte and watch it fail.
  - L100 #5: Generate an Argon2id encoded hash with the Argon2 op (type Argon2id) and verify it in Python.
  - L100 #6: Chain To Base64 → SHA2 → AES Encrypt: reversible encoding vs one-way hash vs keyed encryption.
  - L200 #9: Paste your CA and leaf PEM into Parse X.509 certificate; check BasicConstraints and SAN.
  - L200 #11: JWT Decode / JWT Verify (HS256) on a token minted in Python.
- **Notes:** No Ed25519, X25519 or ChaCha20-Poly1305 AEAD operation (has ChaCha stream cipher and Derive HKDF key).
- **Sources:** https://github.com/gchq/CyberChef · https://github.com/gchq/CyberChef/releases · https://github.com/gchq/CyberChef/blob/master/src/core/config/Categories.json · https://github.com/gchq/CyberChef/blob/master/src/core/operations/AESEncrypt.mjs · https://github.com/gchq/CyberChef/blob/master/src/core/operations/Argon2.mjs

#### Wireshark
- **Role:** INSPECT — look inside your localhost TLS handshake and decrypt it with a key-log file.
- **Licence:** GPL-2.0 · OSI-approved: **yes**
- **Latest:** 4.6.9 (stable) (not shown on fetched page (2026)) · maintained: yes (4.6.3→4.6.9 in 2026)
- **macOS arm64:** yes — Official universal .dmg; brew install --cask wireshark-app
- **Windows 11:** yes — Official x64/Arm64 installer (bundles Npcap)
- **Lessons (suggested exercises):**
  - L200 #10: Set SSLKEYLOGFILE (Python create_default_context honours it, 3.8+), capture loopback, load the key log in Preferences → Protocols → TLS, and read the decrypted HTTP plus the TLS 1.3 key share and cipher suite.
  - L200 #8: In the same capture, find the X25519 key_share — the real-world version of your X25519+HKDF+AEAD lab.
- **Notes:** CLI companions verified: openssl s_client (OpenSSL 4.1.0 / 3.5.9 LTS, Apache-2.0, brew openssl@3), testssl.sh 3.2.4 (GPL-2.0, brew testssl; Windows unverified), sslscan 2.2.3 (GPL-3.0+).
- **Sources:** https://www.wireshark.org/faq.html · https://www.wireshark.org/download.html · https://www.wireshark.org/docs/relnotes/wireshark-4.6.9.html · https://formulae.brew.sh/cask/wireshark-app · https://wiki.wireshark.org/TLS · https://docs.python.org/3/library/ssl.html

#### XCA (X Certificate and Key management)
- **Role:** BUILD WITHOUT CODE / INSPECT — build root → intermediate → leaf certificates in a GUI and compare with your Python CA.
- **Licence:** BSD-3-Clause · OSI-approved: **yes**
- **Latest:** 2.9.0 (2025-03-28) · maintained: borderline (last release 19 months ago, last commit 2025)
- **macOS arm64:** yes — brew install --cask xca (xca-2.9.0-Darwin.dmg)
- **Windows 11:** yes — xca-2.9.0-win64.msi, portable zip, or Microsoft Store 9N9K02V7XR1B
- **Lessons (suggested exercises):**
  - L200 #9: Recreate the lesson's root → intermediate → localhost leaf (SAN localhost,127.0.0.1); export PEM and diff extensions against the Python-made cert.
  - L200 #7: Generate an Ed25519 key (supported since XCA 2.4.0) and compare the PEM with cryptography's output.
- **Notes:** Repo is chris2511/xca. Native arm64 vs Intel dmg not confirmed.
- **Sources:** https://github.com/chris2511/xca/blob/main/COPYRIGHT · https://github.com/chris2511/xca/releases · https://hohnstaedt.de/xca/index.php/download · https://formulae.brew.sh/cask/xca · https://apps.microsoft.com/detail/9n9k02v7xr1b

#### KeyStore Explorer
- **Role:** INSPECT — open keystores, PKCS#12 and certificates; view X.509 v3 extensions; sign a CSR in a GUI.
- **Licence:** GPL-3.0 · OSI-approved: **yes**
- **Latest:** 5.7.0 (≈2026-08-23 (year inferred)) · maintained: yes (commit 2 days before check)
- **macOS arm64:** yes — kse-570-arm64.dmg; brew install --cask keystore-explorer
- **Windows 11:** yes — kse-570-setup.exe (bundled JRE); winget KaiKramer.KeyStoreExplorer
- **Lessons (suggested exercises):**
  - L200 #9: Open the PKCS#12 your Python CA lab exports; inspect BasicConstraints/KeyUsage/SAN; sign a CSR in the GUI and compare.
- **Notes:** Ed25519 generation not confirmed (README says 'ECC').
- **Sources:** https://github.com/kaikramer/keystore-explorer · https://github.com/kaikramer/keystore-explorer/releases · https://formulae.brew.sh/cask/keystore-explorer

#### step CLI (smallstep)
- **Role:** CHECK — independent CLI for certificates and JWTs to cross-check your Python output.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** v0.31.0 (2026-09-25) · maintained: yes
- **macOS arm64:** yes — brew install step
- **Windows 11:** yes — step_windows_0.31.0_amd64.zip; winget Smallstep.step (manifest at 0.30.6)
- **Lessons (suggested exercises):**
  - L200 #9: Create root/intermediate/leaf with step certificate create and inspect with step certificate inspect; compare with your Python CA.
  - L200 #11: Verify a token minted in Python with step crypto jwt verify.
- **Notes:** Exact subcommand flags not checked against docs.
- **Sources:** https://formulae.brew.sh/formula/step · https://github.com/smallstep/cli/releases · https://github.com/microsoft/winget-pkgs/tree/master/manifests/s/Smallstep/step

#### CrypTool 2
- **Role:** SEE — visual programming with 200+ templates (e.g. AES ECB vs CBC, Diffie-Hellman). Windows only.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** 2.1 stable build 9778.2 (nightly 9843.1) (stable 2024-01-31; nightly 2025-12-19) · maintained: yes (repo commits ≈3 weeks before check)
- **macOS arm64:** no — not available (Windows/.NET WPF only)
- **Windows 11:** yes — EXE installer or ZIP from cryptool.org (no admin)
- **Lessons (suggested exercises):**
  - L100 #4: Open the AES ECB-vs-CBC template to see why the mode matters, before the GCM lab.
  - L200 #8: Step through the Diffie-Hellman template before writing the X25519 code.
- **Notes:** Windows PC only. AES-GCM/Argon2/Ed25519 components not checked.
- **Sources:** https://www.cryptool.org/en/ct2/downloads/ · https://github.com/CrypToolProject/CrypTool-2 · https://www.cryptool.org/cryptool2/

_CLI companions verified: OpenSSL 4.1.0 / 3.5.9 LTS (Apache-2.0), testssl.sh 3.2.4 (GPL-2.0), sslscan 2.2.3 (GPL-3.0+)._ Sources: https://openssl-library.org/source/ · https://formulae.brew.sh/formula/testssl · https://github.com/rbsec/sslscan/releases

## AI agents

| Tool | Role | Licence (OSI) | Latest | Mac / Win |
|---|---|---|---|---|
| MCP Inspector | INSPECT | MIT + Apache-2.0 (yes) | 2.12.0 (≈2026-10-21 (security release)) | yes / yes |
| promptfoo | CHECK | MIT (yes) | 0.125.1 (2026-10-25) | yes / yes |
| Langflow | BUILD WITHOUT CODE | MIT (yes) | 1.13.0 (≈2026-10-24) | yes / yes |
| AnythingLLM | SEE | MIT (yes) | v1.19.0 (≈2026-10-27) | yes / yes |
| Open WebUI | SEE | Open WebUI License (no) | v0.12.4 (≈2026-10-26) | yes / yes |
| Ollama (supporting runtime) | CHECK | MIT (yes) | v0.40.12 (≈2026-10-27) | yes / yes |

#### MCP Inspector
- **Role:** INSPECT — connect to your MCP server and call its tools/resources/prompts by hand before writing a client.
- **Licence:** MIT + Apache-2.0 (relicensing in progress; docs CC-BY-4.0) · OSI-approved: **yes**
- **Latest:** 2.12.0 (≈2026-10-21 (security release)) · maintained: yes (≈weekly)
- **macOS arm64:** yes — npx @modelcontextprotocol/inspector (Node.js)
- **Windows 11:** yes — same
- **Lessons (suggested exercises):**
  - L200 #10: Point the Inspector at your MCP server, list tools, call one with valid and invalid args; then script the same with --cli as a smoke test.
- **Notes:** 2.12.0 fixes 3 advisories affecting 2.0.0–2.11.0 — use ≥2.12.0.
- **Sources:** https://github.com/modelcontextprotocol/inspector · https://github.com/modelcontextprotocol/inspector/releases

#### promptfoo
- **Role:** CHECK — declarative evals: assert JSON validity, tool-call shape and rubric scores against a local model.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** 0.125.1 (2026-10-25) · maintained: yes
- **macOS arm64:** yes — npx promptfoo@latest or brew install promptfoo (Node ≥22.22)
- **Windows 11:** yes — npx promptfoo@latest / npm i -g promptfoo
- **Lessons (suggested exercises):**
  - L100 #4: Assert is-json (and a JSON schema) on your structured-output prompt across 10 inputs.
  - L100 #5: Use is-valid-openai-tools-call to check the model's tool call.
  - L200 #11: Write guardrail test cases (prompt injection, off-topic) and run them against the local agent with an ollama: provider.
- **Notes:** OpenAI announced acquisition 2026-03-09; project states it remains open source. Closing not verified.
- **Sources:** https://github.com/promptfoo/promptfoo/blob/main/LICENSE · https://github.com/promptfoo/promptfoo/releases · https://www.promptfoo.dev/docs/installation/ · https://www.promptfoo.dev/docs/providers/ollama/ · https://openai.com/index/openai-to-acquire-promptfoo/ · https://www.promptfoo.dev/blog/promptfoo-joining-openai/

#### Langflow
- **Role:** BUILD WITHOUT CODE — wire model, prompt, tools and vector store as a flow; compare with your hand-written loop.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** 1.13.0 (≈2026-10-24) · maintained: yes (≈weekly)
- **macOS arm64:** yes — uv pip install langflow && uv run langflow run (Python 3.10–3.14), or Langflow Desktop (macOS 13+)
- **Windows 11:** yes — same pip/uv route, Docker, or Desktop .msi (may need MS C++ Build Tools)
- **Lessons (suggested exercises):**
  - L100 #6: Rebuild the minimal agent loop as Agent + Ollama component; compare its tool-call trace with your code.
  - L200 #7: Ollama Embeddings → vector store → prompt RAG flow; compare answers with your lesson-7 pipeline.
  - L200 #10: Expose a flow as an MCP tool (/api/v1/mcp/project/<id>/streamable) and call it from your own MCP client.
- **Notes:** Since 1.13 auto-login is off: set LANGFLOW_SUPERUSER_PASSWORD. Desktop download asks for contact info — prefer pip/uv.
- **Sources:** https://github.com/langflow-ai/langflow/blob/main/LICENSE · https://github.com/langflow-ai/langflow/releases · https://docs.langflow.org/get-started-installation · https://docs.langflow.org/bundles-ollama · https://docs.langflow.org/mcp-server

#### AnythingLLM
- **Role:** SEE — desktop RAG workspaces + agents with MCP tools on a local model; a baseline to compare your RAG and MCP code with.
- **Licence:** MIT (repo); optional paid 'Pro' tier in the Desktop app since v1.15.0 · OSI-approved: **yes**
- **Latest:** v1.19.0 (≈2026-10-27) · maintained: yes
- **macOS arm64:** yes — Desktop app (native Apple Silicon build)
- **Windows 11:** yes — Desktop installer (x64 and ARM)
- **Lessons (suggested exercises):**
  - L200 #7: Create a workspace with Ollama embeddings over the lesson's documents; compare its retrieved chunks with yours.
  - L200 #10: Register your MCP server in AnythingLLM agents and watch the tool-approval prompt.
- **Notes:** Open-core-ish: Pro tier pricing/limits not verified.
- **Sources:** https://github.com/Mintplex-Labs/anything-llm/blob/master/LICENSE · https://github.com/Mintplex-Labs/anything-llm/releases · https://anythingllm.com/download

#### Open WebUI
- **Role:** SEE — chat UI over Ollama/OpenAI-compatible APIs with knowledge bases, function calling and tool approval.
- **Licence:** Open WebUI License (BSD-3-style + branding clause) — source-available, NOT OSI-approved · OSI-approved: **no**
- **Latest:** v0.12.4 (≈2026-10-26) · maintained: yes
- **macOS arm64:** yes — pip install open-webui && open-webui serve (Python 3.11/3.12), or uvx / Docker
- **Windows 11:** yes — same (PowerShell) or Docker Desktop + WSL 2
- **Lessons (suggested exercises):**
  - L200 #7: Upload the lesson's documents to a Knowledge base and compare answers with your embeddings pipeline.
  - L200 #11: Turn on tool approval ('ask first') to see a human-in-the-loop guardrail.
- **Notes:** Licence restricts removing branding above 50 users — fine for personal learning, but not OSI open source.
- **Sources:** https://github.com/open-webui/open-webui/blob/main/LICENSE · https://github.com/open-webui/open-webui/releases · https://docs.openwebui.com/getting-started/quick-start/

#### Ollama (supporting runtime)
- **Role:** CHECK — local model server so the GUI tools above and your own code hit the same OpenAI-compatible endpoint.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** v0.40.12 (≈2026-10-27) · maintained: yes
- **macOS arm64:** yes — Ollama-darwin.zip / ollama.com/download
- **Windows 11:** yes — irm https://ollama.com/install.ps1 | iex
- **Lessons (suggested exercises):**
  - L100 #2: Point the lesson's requests code at http://localhost:11434/v1 instead of the fake server; compare response shapes.
- **Sources:** https://github.com/ollama/ollama/blob/main/LICENSE · https://github.com/ollama/ollama/releases · https://ollama.com/download

## Distributed systems

| Tool | Role | Licence (OSI) | Latest | Mac / Win |
|---|---|---|---|---|
| Toxiproxy | BUILD WITHOUT CODE / INSPECT | MIT (yes) | v2.13.0 (≈2026-10-14) | yes / yes |
| Jaeger | SEE | Apache-2.0 (yes) | v2.22.0 (≈2026-10-08) | yes / yes |
| Maelstrom (Jepsen) | CHECK / SEE | EPL-1.0 (yes) | 0.2.4 (2024-12-04) | yes / partial |
| RabbitMQ + management UI | INSPECT | MPL-2.0 (yes) | 4.4.0 (≈2026-10-21) | yes / yes |
| NATS server + NATS CLI | INSPECT | Apache-2.0 (yes) | server v2.15.1 (brew 2.15.2); CLI 0.5.0 (server ≈2026-10-14; CLI 2026-09-17) | yes / partial |
| Grafana k6 | CHECK | AGPL-3.0 (yes) | v2.3.0 (2026-09-21) | yes / yes |

#### Toxiproxy
- **Role:** BUILD WITHOUT CODE / INSPECT — inject latency, timeouts, resets and bandwidth limits between your two services.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** v2.13.0 (≈2026-10-14) · maintained: yes
- **macOS arm64:** yes — brew tap shopify/shopify && brew install toxiproxy (or ghcr.io/shopify/toxiproxy)
- **Windows 11:** yes — toxiproxy-server/cli-windows-amd64.exe from releases
- **Lessons (suggested exercises):**
  - L100 #3: Add a 'timeout' toxic and prove your client timeout fires before the server answers.
  - L100 #4: Add 'reset_peer' with toxicity 0.3; count retries and check the retry budget caps them.
  - L200 #8: Add 'latency' larger than the visibility timeout and watch redelivery happen.
- **Notes:** HTTP API on :8474 is unauthenticated by default (TOXIPROXY_AUTH_TOKEN since 2.13.0) — bind to localhost.
- **Sources:** https://github.com/Shopify/toxiproxy · https://github.com/Shopify/toxiproxy/releases

#### Jaeger
- **Role:** SEE — trace timeline UI: see each retry, timeout and backoff gap as spans.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** v2.22.0 (≈2026-10-08) · maintained: yes (v1 EOL 2025-12-31)
- **macOS arm64:** yes — jaeger-2.22.0-darwin-arm64.tar.gz or container cr.jaegertracing.io/jaegertracing/jaeger:2.22.0
- **Windows 11:** yes — Windows binary or container
- **Lessons (suggested exercises):**
  - L100 #2: Instrument both services with OpenTelemetry (OTLP → :4318) and open http://localhost:16686.
  - L100 #4: Find the gaps between retry spans and check they match your backoff + jitter schedule.
  - L100 #5: Tag spans with the idempotency key and confirm a retried request produced one effect.
- **Sources:** https://github.com/jaegertracing/jaeger · https://github.com/jaegertracing/jaeger/releases · https://www.jaegertracing.io/docs/latest/getting-started/ · https://www.jaegertracing.io/download/ · https://opentelemetry.io/docs/languages/python/exporters/

#### Maelstrom (Jepsen)
- **Role:** CHECK / SEE — run your Python node against a checker; get Lamport-style message diagrams and latency plots.
- **Licence:** EPL-1.0 (or later) · OSI-approved: **yes**
- **Latest:** 0.2.4 (2024-12-04) · maintained: yes (commit ≈3 months before check)
- **macOS arm64:** yes — JDK 11+, Graphviz, Gnuplot; untar release and run ./maelstrom
- **Windows 11:** partial — No official statement; WSL2 likely (unverified)
- **Lessons (suggested exercises):**
  - L100 #6: Run the broadcast workload with a Python node; label events in messages.svg with your Lamport timestamps.
  - L100 #4: Add --nemesis partition and compare latency-raw.png with and without retries.
- **Notes:** Includes a Raft chapter and lin-kv workload — a stretch exercise after lesson 7.
- **Sources:** https://github.com/jepsen-io/maelstrom · https://github.com/jepsen-io/maelstrom/releases · https://github.com/jepsen-io/maelstrom/blob/main/doc/workloads.md · https://github.com/jepsen-io/maelstrom/blob/main/doc/results.md · https://github.com/jepsen-io/maelstrom/blob/main/doc/01-getting-ready/index.md

#### RabbitMQ + management UI
- **Role:** INSPECT — watch Ready/Unacked counts, redelivery and dead-lettering in a web UI.
- **Licence:** MPL-2.0 · OSI-approved: **yes**
- **Latest:** 4.4.0 (≈2026-10-21) · maintained: yes
- **macOS arm64:** yes — brew install rabbitmq; rabbitmq-plugins enable rabbitmq_management; http://localhost:15672
- **Windows 11:** yes — rabbitmq-server-4.4.0.exe (Erlang requirement not checked)
- **Lessons (suggested exercises):**
  - L200 #8: Consumer nacks a poison message; watch Ready/Unacked, set delivery-limit 3 by policy and find it in the DLX queue with x-death reason.
- **Sources:** https://github.com/rabbitmq/rabbitmq-server · https://github.com/rabbitmq/rabbitmq-server/releases · https://www.rabbitmq.com/docs/install-homebrew · https://www.rabbitmq.com/docs/management · https://www.rabbitmq.com/docs/dlx

#### NATS server + NATS CLI
- **Role:** INSPECT — JetStream consumers with ack wait / max deliver; live graphs with nats consumer graph and nats top.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** server v2.15.1 (brew 2.15.2); CLI 0.5.0 (server ≈2026-10-14; CLI 2026-09-17) · maintained: yes
- **macOS arm64:** yes — brew install nats-server nats
- **Windows 11:** partial — CLI: scoop install extras/natscli; server: Windows asset not confirmed (Docker fallback)
- **Lessons (suggested exercises):**
  - L200 #8: Alternative to RabbitMQ: a work-queue consumer that never acks; watch redeliveries in nats consumer info / graph.
- **Sources:** https://github.com/nats-io/nats-server/releases · https://formulae.brew.sh/formula/nats-server · https://github.com/nats-io/natscli · https://github.com/nats-io/natscli/releases

#### Grafana k6
- **Role:** CHECK — scripted load at a fixed arrival rate to measure your rate limiter's 200 vs 429 split.
- **Licence:** AGPL-3.0 · OSI-approved: **yes**
- **Latest:** v2.3.0 (2026-09-21) · maintained: yes
- **macOS arm64:** yes — brew install k6
- **Windows 11:** yes — winget install k6 --source winget, or official MSI
- **Lessons (suggested exercises):**
  - L200 #11: constant-arrival-rate above the token-bucket refill; check the 429 share and that Retry-After is present.
- **Notes:** Non-visual helpers also verified: etcd v3.7.3 (Apache-2.0, brew etcd) for lesson 7 leases; Valkey 9.1.3 (BSD-3, brew valkey; no native Windows → Docker) for lesson 10.
- **Sources:** https://github.com/grafana/k6 · https://github.com/grafana/k6/releases · https://grafana.com/docs/k6/latest/set-up/install-k6/

_Non-visual helpers verified: etcd v3.7.3 (Apache-2.0) for lesson 7; Valkey 9.1.3 (BSD-3) for lesson 10._ Sources: https://github.com/etcd-io/etcd/releases · https://github.com/valkey-io/valkey/releases

## Application architecture

| Tool | Role | Licence (OSI) | Latest | Mac / Win |
|---|---|---|---|---|
| Structurizr (local) | SEE | Apache-2.0 (yes) | v2026.10.26 (2026-10-26) | yes / yes |
| Swagger Editor v5 / Swagger UI | CHECK / SEE | Apache-2.0 (yes) | Editor v5.10.0; UI v5.34.0 (Editor 2026-10-21; UI 2026-10-19) | yes / yes |
| AsyncAPI Studio | SEE / CHECK | Apache-2.0 (yes) | @asyncapi/studio 1.4.2 (≈2026-08-24 (year inferred)) | yes / yes |
| Bruno | CHECK | MIT (yes) | v4.3.0 (≈2026-10-21) | yes / yes |
| Keycloak | SEE / BUILD WITHOUT CODE | Apache-2.0 (yes) | 26.8.1 (≈2026-10-14) | yes / yes |
| import-linter | CHECK / SEE | BSD-2-Clause (yes) | 2.15 (2026-09-04) | yes / yes |

#### Structurizr (local)
- **Role:** SEE — render C4 views and ADRs from a workspace.dsl model (successor to Structurizr Lite).
- **Licence:** Apache-2.0 (open-core: prebuilt 'server' needs a paid licence; 'local' is free) · OSI-approved: **yes**
- **Latest:** v2026.10.26 (2026-10-26) · maintained: yes
- **macOS arm64:** yes — docker run -it --rm -p 8080:8080 -v PATH:/usr/local/structurizr structurizr/structurizr local (Docker or Java 21+)
- **Windows 11:** yes — same
- **Lessons (suggested exercises):**
  - L100 #6: Write workspace.dsl with System Context + Container views, add one ADR, and browse both (Decision explorer) at localhost:8080.
- **Notes:** Structurizr Lite repo archived 2026-02-04 (EOL).
- **Sources:** https://github.com/structurizr/structurizr · https://github.com/structurizr/structurizr/releases · https://docs.structurizr.com/local · https://docs.structurizr.com/local/quickstart · https://github.com/structurizr/lite

#### Swagger Editor v5 / Swagger UI
- **Role:** CHECK / SEE — validate your OpenAPI 3.1 spec live and try endpoints with 'Try it out'.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** Editor v5.10.0; UI v5.34.0 (Editor 2026-10-21; UI 2026-10-19) · maintained: yes
- **macOS arm64:** yes — Browser or docker run -p 8080:80 docker.swagger.io/swaggerapi/swagger-editor:latest
- **Windows 11:** yes — same
- **Lessons (suggested exercises):**
  - L100 #4: Paste the lesson's openapi: 3.1.0 file into Editor v5, fix validation errors, then serve Swagger UI against the stdlib API.
- **Notes:** Editor v5 also validates AsyncAPI 2.x/3.x.
- **Sources:** https://github.com/swagger-api/swagger-editor · https://github.com/swagger-api/swagger-editor/releases · https://github.com/swagger-api/swagger-ui · https://github.com/swagger-api/swagger-ui/releases

#### AsyncAPI Studio
- **Role:** SEE / CHECK — edit and preview AsyncAPI 3.x documents for your event channels.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** @asyncapi/studio 1.4.2 (≈2026-08-24 (year inferred)) · maintained: yes
- **macOS arm64:** yes — Browser (local-folder editing needs Chromium); self-built Docker image
- **Windows 11:** yes — same
- **Lessons (suggested exercises):**
  - L200 #9: Describe the outbox → bus channel and OrderPlaced message in AsyncAPI 3.x and check the rendered docs.
- **Sources:** https://github.com/asyncapi/studio · https://github.com/asyncapi/studio/releases

#### Bruno
- **Role:** CHECK — API client whose collections are plain files in Git; run them as API tests with the CLI.
- **Licence:** MIT (open-core: Pro/Ultimate paid tiers) · OSI-approved: **yes**
- **Latest:** v4.3.0 (≈2026-10-21) · maintained: yes
- **macOS arm64:** yes — brew install --cask bruno
- **Windows 11:** yes — winget install Bruno.Bruno
- **Lessons (suggested exercises):**
  - L100 #4: Import the OpenAPI 3.1 spec into a collection, add assertions, run with bru run.
  - L200 #11: Use the same collection as the end-to-end layer of the testing pyramid and time it vs unit tests.
- **Notes:** OAuth2/PKCE in the free tier not confirmed — use Hoppscotch (MIT, has OAuth 2.0 PKCE) for lesson 10 if needed.
- **Sources:** https://github.com/usebruno/bruno · https://github.com/usebruno/bruno/releases · https://formulae.brew.sh/cask/bruno · https://www.usebruno.com/pricing

#### Keycloak
- **Role:** SEE / BUILD WITHOUT CODE — local OpenID Provider; create a realm and public client in the admin console, then run code flow + PKCE against it.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** 26.8.1 (≈2026-10-14) · maintained: yes
- **macOS arm64:** yes — docker run -p 127.0.0.1:8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:26.8.1 start-dev (or zip + OpenJDK 25)
- **Windows 11:** yes — same container, or zip: bin\kc.bat start-dev
- **Lessons (suggested exercises):**
  - L200 #10: Create realm 'learn' + a public client (Standard flow); have the stdlib app do code flow + PKCE S256 and inspect the ID token claims.
- **Notes:** start-dev is for local learning only.
- **Sources:** https://github.com/keycloak/keycloak · https://github.com/keycloak/keycloak/releases · https://www.keycloak.org/getting-started/getting-started-docker · https://www.keycloak.org/getting-started/getting-started-zip · https://www.keycloak.org/securing-apps/specifications

#### import-linter
- **Role:** CHECK / SEE — architecture contracts as a fitness function, with a browser UI to explore the import graph.
- **Licence:** BSD-2-Clause · OSI-approved: **yes**
- **Latest:** 2.15 (2026-09-04) · maintained: yes
- **macOS arm64:** yes — pip install import-linter (ui extra exists)
- **Windows 11:** yes — same
- **Lessons (suggested exercises):**
  - L100 #3: Write a contract forbidding one module from importing another's internals; run lint-imports, then import-linter explore to see violations.
  - L200 #7: Add a contract that the domain package never imports adapters (ports-and-adapters rule).
- **Notes:** Contract types not re-read from docs in this pass.
- **Sources:** https://github.com/seddonym/import-linter · https://pypi.org/project/import-linter/ · https://import-linter.readthedocs.io/en/stable/ui/

_Also verified, optional: draw.io Desktop 32.6.1 (GPL-3.0 since 31.5.2; C4 shape library; brew --cask drawio, winget JGraph.Draw), Mermaid Live Editor (MIT; C4 diagrams *experimental*), Hoppscotch 2026.9.0 (MIT, open-core; OAuth 2.0 PKCE), LikeC4 v1.60.0 (MIT), Archi 5.10.0 (MIT; ArchiMate, not C4 — low fit)._ Sources: https://github.com/jgraph/drawio-desktop/releases · https://www.drawio.com/docs/diagram-types/c4-modelling/ · https://mermaid.js.org/syntax/c4.html · https://github.com/hoppscotch/hoppscotch · https://github.com/likec4/likec4/releases · https://www.archimatetool.com/download/

## micro:bit (simulator-only)

| Tool | Role | Licence (OSI) | Latest | Mac / Win |
|---|---|---|---|---|
| Microsoft MakeCode for micro:bit | BUILD WITHOUT CODE / SEE | MIT (yes) | v9.0.12 (tag) (2026-08-21) | yes / yes |
| micro:bit Python Editor v3 (with V2 simulator) | SEE / CHECK | MIT (yes) | v3.1.14 (≈2026-10 (release page: 'last week')) | yes / yes |
| micropython-microbit-v2-simulator (standalone) | CHECK | MIT (yes) | no releases (commit-based) (last commit ≈2026-10-26) | yes / yes |

#### Microsoft MakeCode for micro:bit
- **Role:** BUILD WITHOUT CODE / SEE — blocks ↔ Python/JS editor with a browser simulator; radio code shows two simulated boards.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** v9.0.12 (tag) (2026-08-21) · maintained: yes (commit 5 days before check)
- **macOS arm64:** yes — Browser (makecode.microbit.org); works offline once cached
- **Windows 11:** yes — Browser; offline app availability unclear
- **Lessons (suggested exercises):**
  - L200 #7: Build Marco/Polo in blocks: with radio blocks the simulator shows two micro:bits running the same code — then compare with your Python radio lab.
  - L200 #11: Build the game's state machine in Blocks, switch to the Python view and compare with your version.
  - L100 #6: Use the simulator's sensor/gesture controls to trigger 'on shake' handlers.
- **Notes:** Datalogger blocks need V2 hardware flash; simulator support for them not confirmed.
- **Sources:** https://github.com/microsoft/pxt-microbit · https://github.com/microsoft/pxt-microbit/tags · https://makecode.microbit.org/device/simulator · https://makecode.microbit.org/v9/courses/csintro/radio/project · https://makecode.microbit.org/v1/courses/csintro/radio/activity · https://makecode.microbit.org/offline-app

#### micro:bit Python Editor v3 (with V2 simulator)
- **Role:** SEE / CHECK — the lessons' own editor: simulated accelerometer, temperature, light, serial console; data-logging API reference.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** v3.1.14 (≈2026-10 (release page: 'last week')) · maintained: yes
- **macOS arm64:** yes — Browser (python.microbit.org); installable as an offline app
- **Windows 11:** yes — same
- **Lessons (suggested exercises):**
  - L100 #5: Move the temperature and light sliders and confirm your thresholds trigger.
  - L100 #6: Trigger was_gesture('shake') from the simulator's gesture control.
  - L200 #8: Log temperature and light with log.add, vary sliders, compare rows with your local stub's output.
- **Notes:** Whether the simulator shows the data-log table is not documented.
- **Sources:** https://github.com/microbit-foundation/python-editor-v3 · https://github.com/microbit-foundation/python-editor-v3/releases · https://support.microbit.org/support/solutions/articles/19000135210-python-editor-guide · https://python.microbit.org/v/3/reference/data-logging · https://python.microbit.org/v/3/reference/accelerometer

#### micropython-microbit-v2-simulator (standalone)
- **Role:** CHECK — run the official simulator locally and inject radio packets as a 'second board'.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** no releases (commit-based) (last commit ≈2026-10-26) · maintained: yes (src/ last changed ≈2 years ago)
- **macOS arm64:** yes — Build/serve demo.html locally in a browser
- **Windows 11:** yes — same
- **Lessons (suggested exercises):**
  - L200 #7: Inject radio_input bytes via the embedder message API to act as board 2 for your receiver code.
- **Notes:** Embedding API declared not yet stable.
- **Sources:** https://github.com/microbit-foundation/micropython-microbit-v2-simulator

## Simulation (civilian)

| Tool | Role | Licence (OSI) | Latest | Mac / Win |
|---|---|---|---|---|
| NetLogo | SEE | GPL-2.0-or-later (yes) | 7.0.4 (2026-05-01) | yes / yes |
| JaamSim | BUILD WITHOUT CODE | Apache-2.0 (yes) | 2026-07 (≈2026-10-23) | partial / yes |
| Mesa (SolaraViz) | SEE / CHECK | Apache-2.0 (yes) | 3.5.1 (2026-03-15) | yes / yes |
| SimPy | CHECK | MIT (yes) | 4.1.2 (2026-05-23) | yes / yes |
| Scilab + Xcos | BUILD WITHOUT CODE | GPL-2.0 (yes) | 2027.0.0 (2026-10-15) | yes / yes |
| OpenModelica (OMEdit) | BUILD WITHOUT CODE / CHECK | OSMC-PL 1.8 (yes) | 1.27.1 (2026-09-08) | partial / yes |

#### NetLogo
- **Role:** SEE — run the built-in Segregation (Schelling) model and sweep parameters with BehaviorSpace.
- **Licence:** GPL-2.0-or-later (models have own licences, e.g. Segregation CC BY-NC-SA 3.0) · OSI-approved: **yes**
- **Latest:** 7.0.4 (2026-05-01) · maintained: yes
- **macOS arm64:** yes — brew install --cask netlogo (Apple-silicon build; bundles Java 17)
- **Windows 11:** yes — Installer (bundles Java 17)
- **Lessons (suggested exercises):**
  - L100 #5: Open Sample Models › Social Science › Segregation; sweep %-SIMILAR-WANTED 30→80 and compare final % similar with your numpy version.
  - L200 #10: BehaviorSpace with 10 repetitions and random-seed (474 + behaviorspace-run-number); export table CSV and compute 95% CIs in Python.
- **Sources:** https://github.com/NetLogo/NetLogo/releases · https://docs.netlogo.org/7.0.4/copyright · https://docs.netlogo.org/7.0.4/requirements · https://formulae.brew.sh/cask/netlogo · https://ccl.northwestern.edu/netlogo/models/Segregation · https://docs.netlogo.org/7.0.4/behaviorspace

#### JaamSim
- **Role:** BUILD WITHOUT CODE — drag-and-drop discrete-event models (generator → queue → server → sink) with distributions and examples.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** 2026-07 (≈2026-10-23) · maintained: yes (≈monthly releases)
- **macOS arm64:** partial — Universal JAR: java -jar JaamSim2026-07.jar (Java 17+, OpenGL 2.1+); no native Mac build
- **Windows 11:** yes — Self-contained JaamSim2026-07.exe
- **Lessons (suggested exercises):**
  - L100 #3: Build Generator → Queue → Server → Sink with exponential times; compare mean wait with your Python DES.
  - L200 #8: Open the 'Shared vs Unshared Queue' example and compare waits with your Erlang C result.
- **Notes:** 3D view on Apple-silicon JDK not confirmed.
- **Sources:** https://github.com/jaamsim/jaamsim · https://github.com/jaamsim/jaamsim/releases · https://jaamsim.com/downloads.html

#### Mesa (SolaraViz)
- **Role:** SEE / CHECK — Python agent-based models with a browser visualisation (sliders, step/play) and a Schelling example.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** 3.5.1 (2026-03-15) · maintained: yes
- **macOS arm64:** yes — pip install mesa (Python ≥3.12; pin mesa>=3.5,<4)
- **Windows 11:** yes — same
- **Lessons (suggested exercises):**
  - L100 #5: Run Mesa's Schelling example in SolaraViz; compare % similar at convergence with your numpy model at the same threshold.
- **Notes:** 4.0 (alpha) removes batch_run, mesa.space and the seed keyword.
- **Sources:** https://pypi.org/project/Mesa/ · https://github.com/projectmesa/mesa/releases · https://mesa.readthedocs.io/stable/apis/visualization.html · https://mesa.readthedocs.io/latest/examples.html

#### SimPy
- **Role:** CHECK — reference DES library to re-implement the queue and inventory labs and compare numbers.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** 4.1.2 (2026-05-23) · maintained: yes (after a 2.5-year gap)
- **macOS arm64:** yes — pip install simpy
- **Windows 11:** yes — same
- **Lessons (suggested exercises):**
  - L100 #3: Rebuild the single-server queue with simpy.Resource(capacity=1); compare mean wait for the same seed.
  - L200 #8: simpy.Resource(capacity=c) for c desks vs your Erlang C formula.
  - L200 #11: Model (s, S) inventory as processes; compare cost with common random numbers.
- **Notes:** Alternative: Ciw 3.2.7 (MIT, 2025-12-05) for M/M/c queueing networks — https://pypi.org/project/Ciw/
- **Sources:** https://pypi.org/project/simpy/

#### Scilab + Xcos
- **Role:** BUILD WITHOUT CODE — block-diagram ODE models (integrators, gains) with native Apple-silicon build.
- **Licence:** GPL-2.0 · OSI-approved: **yes**
- **Latest:** 2027.0.0 (2026-10-15) · maintained: yes
- **macOS arm64:** yes — Native macOS ARM64 .dmg
- **Windows 11:** yes — 64-bit Windows .exe
- **Lessons (suggested exercises):**
  - L100 #4: Build the parcel drop as integrator blocks in Xcos; compare the trajectory with your time-stepped Python.
  - L200 #9: Compare Xcos's result with scipy.integrate.solve_ivp at two tolerances.
- **Notes:** Xcos solver list/tolerance settings not checked.
- **Sources:** https://www.scilab.org/download · https://www.scilab.org/software/xcos

#### OpenModelica (OMEdit)
- **Role:** BUILD WITHOUT CODE / CHECK — equation-based models; switch solvers (DASSL vs GBODE) and tolerances.
- **Licence:** OSMC-PL 1.8 (public use under AGPL-3.0) · OSI-approved: **yes**
- **Latest:** 1.27.1 (2026-09-08) · maintained: yes
- **macOS arm64:** partial — No native Mac build since 1.16 — official Linux Docker image + XQuartz
- **Windows 11:** yes — Official installer
- **Lessons (suggested exercises):**
  - L200 #9: Model the drag-affected drop in OMEdit; compare DASSL vs GBODE and vary tolerance; compare with solve_ivp (best on the Windows PC).
- **Sources:** https://github.com/OpenModelica/OpenModelica/blob/master/OSMC-License.txt · https://github.com/OpenModelica/OpenModelica/releases · https://openmodelica.org/download/download-mac/ · https://openmodelica.org/download/download-windows/

_Also verified, optional: Ciw 3.2.7 (MIT; M/M/c), GAMA 2025.06.4 (GPL-3.0; agent-based GUI, Apple-silicon dmg)._ Sources: https://pypi.org/project/Ciw/ · https://github.com/gama-platform/gama/releases

## Cross-cutting: data & analytics tools

Where these fit: Orange/KNIME/Superset turn the CSVs our labs already write (simulation outputs, micro:bit logs, latency/429 counts, RAG embeddings) into charts without code; Grafana reads Jaeger traces; Jupyter/marimo are the code-first CHECK path. WEKA and Rattle are verified but have little or no fit in our lessons.

| Tool | Role | Licence (OSI) | Latest | Mac / Win |
|---|---|---|---|---|
| Orange Data Mining | BUILD WITHOUT CODE / SEE | GPL-3.0-or-later (yes) | 3.40.0 (2025-12-20) | yes / yes |
| KNIME Analytics Platform | BUILD WITHOUT CODE | GPL-3.0 + KNIME additional permissions (yes) | 5.12 (LTS 5.8.4) (5.12: 2026-07-06; 5.8.4: 2026-08-11) | yes / yes |
| Apache Superset | SEE | Apache-2.0 (yes) | 6.1.0 (7.0.0rc2 in vote) (2026-05-13) | yes / partial |
| Grafana OSS | SEE / INSPECT | AGPL-3.0-only (yes) | 13.3.0 (brew 13.2.4) (2026-10-28) | yes / yes |
| JupyterLab (+ JupyterLab Desktop) | CHECK / SEE | BSD-3-Clause (yes) | JupyterLab 4.6.4; Desktop v4.6.3-1 (4.6.4: 2026-09-21; Desktop: 2026-08-26) | yes / yes |
| marimo | CHECK / SEE | Apache-2.0 (yes) | 0.25.2 (2026-10-19) | yes / yes |
| Rattle (new Flutter GUI + R package) | SEE | GPL-3.0 (yes) | GUI 6.5.67; CRAN rattle 5.6.2 (GUI ≈2026-08 (no GitHub releases); CRAN 2026-02-08) | partial / yes |
| WEKA | SEE | GPL-3.0 (yes) | 3.8.7 (dev 3.9.7) (files dated 2026-03-27) | yes / yes |

#### Orange Data Mining
- **Role:** BUILD WITHOUT CODE / SEE — widget workflows to explore CSV outputs (distributions, box plots, t-SNE, clustering).
- **Licence:** GPL-3.0-or-later · OSI-approved: **yes**
- **Latest:** 3.40.0 (2025-12-20) · maintained: yes (commits 4 days before check; 3.41.0-dev)
- **macOS arm64:** yes — Orange3-3.40.0-Python3.12.10-arm64.dmg, conda, or pip install PyQt6 PyQt6-WebEngine orange3
- **Windows 11:** yes — Orange3-3.40.0-x86_64.exe; winget install --id UniversityofLjubljana.Orange
- **Lessons (suggested exercises):**
  - simulation L200 #7: load the service-time CSV into Distributions to eyeball the fit before the SciPy goodness-of-fit test.
  - simulation L200 #10: Box Plot of per-replication means for two scenarios.
  - microbit L200 #8: save the logged rows as CSV (from the stub/simulator), load them and plot temperature vs light.
  - ai-agents L200 #7: write the RAG lab's chunk embeddings to a CSV (one row per chunk), load it, t-SNE / Hierarchical Clustering to see which chunks sit together.
- **Notes:** Add-ons: Text 1.16.3 (2025-05-05, licence unverified — may be AGPL-3.0), Network 1.10.2 (2026-01-06, GPLv3+), Timeseries 0.6.3 (2024-03-15, GPLv3+, slow), Explain 0.6.11 (2026-02-23, GPL3+). No LLM widget; Text's Document Embedding sends tokens to a biolab server (not local).
- **Sources:** https://github.com/biolab/orange3 · https://github.com/biolab/orange3/releases · https://pypi.org/project/Orange3/ · https://orangedatamining.com/download/ · https://orangedatamining.com/widget-catalog/

#### KNIME Analytics Platform
- **Role:** BUILD WITHOUT CODE — node workflows incl. AI Extension (LLM Prompter, Text Embedder) that can target local Ollama/GPT4All.
- **Licence:** GPL-3.0 + KNIME additional permissions (Section 7); Pro/Team/Business Hub are commercial · OSI-approved: **yes**
- **Latest:** 5.12 (LTS 5.8.4) (5.12: 2026-07-06; 5.8.4: 2026-08-11) · maintained: yes
- **macOS arm64:** yes — brew install --cask knime (Apple Silicon) or .dmg
- **Windows 11:** yes — Installer / self-extracting archive / zip
- **Lessons (suggested exercises):**
  - ai-agents L100 #2: OpenAI Authenticator (base URL http://localhost:11434/v1) → LLM Selector → LLM Prompter; compare with your requests call.
  - ai-agents L200 #7: Text Embedder over the lesson documents; compare nearest neighbours with your numpy cosine search.
  - simulation L100 #2: read Monte Carlo CSV, compute percentiles with Statistics nodes, compare with your P50/P90.
- **Notes:** 'Some extensions may have limited support on Apple Silicon.' K-AI assistant quota without Pro not verified. Statistics-node exercise is a suggestion (node names not re-verified).
- **Sources:** https://www.knime.com/downloads/full-license · https://www.knime.com/downloads · https://www.knime.com/release-notes · https://formulae.brew.sh/cask/knime · https://docs.knime.com/ap/latest/analytics_platform_installation_guide/index.html · https://docs.knime.com/ap/latest/ai/overview/ · https://docs.knime.com/ap/latest/ai/local-model-ollama · https://docs.knime.com/ap/latest/ai/local-model-gpt4all

#### Apache Superset
- **Role:** SEE — upload a CSV and build dashboards (line charts, rolling mean, pivot) without code.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** 6.1.0 (7.0.0rc2 in vote) (2026-05-13) · maintained: yes
- **macOS arm64:** yes — docker compose -f docker-compose-image-tag.yml up (http://localhost:8088) or pip install apache_superset
- **Windows 11:** partial — No official Windows support — Docker Desktop (unofficial)
- **Lessons (suggested exercises):**
  - microbit L200 #8: upload the logged rows saved as CSV (Settings › Data › Upload CSV) and chart temperature over time with a 7-point rolling mean.
  - distributed-systems L200 #11: save per-second 200/429 counts from your load run as CSV, upload and chart them.
  - simulation L200 #10: chart running mean per replication to spot the warm-up period.
- **Notes:** Heavy for a learner (container stack); CSV upload must be enabled per database ('Allow file uploads to database').
- **Sources:** https://pypi.org/project/apache-superset/ · https://github.com/apache/superset/releases · https://superset.apache.org/admin-docs/installation/docker-compose/ · https://superset.apache.org/admin-docs/installation/pypi/ · https://superset.apache.org/user-docs/using-superset/exploring-data/

#### Grafana OSS
- **Role:** SEE / INSPECT — dashboards over Jaeger traces and Prometheus/PostgreSQL; TestData source for practice.
- **Licence:** AGPL-3.0-only (since 2021; previously Apache-2.0) · OSI-approved: **yes**
- **Latest:** 13.3.0 (brew 13.2.4) (2026-10-28) · maintained: yes
- **macOS arm64:** yes — brew install grafana && brew services start grafana
- **Windows 11:** yes — Windows installer or zip (choose the Open Source edition, not Enterprise)
- **Lessons (suggested exercises):**
  - distributed-systems L100 #4: add Jaeger as a data source (core) and explore retry traces next to your service logs.
  - distributed-systems L200 #11: TestData/Random walk panel first, then plot your rate-limiter metrics once exported to Prometheus or PostgreSQL.
- **Notes:** No CSV data source in core — micro:bit CSVs need a plugin or a database; use Superset/Orange for those.
- **Sources:** https://grafana.com/licensing/ · https://github.com/grafana/grafana/releases · https://formulae.brew.sh/formula/grafana · https://grafana.com/docs/grafana/latest/setup-grafana/installation/windows/ · https://grafana.com/docs/grafana/latest/datasources/

#### JupyterLab (+ JupyterLab Desktop)
- **Role:** CHECK / SEE — notebooks to re-run lab code step by step and plot results.
- **Licence:** BSD-3-Clause · OSI-approved: **yes**
- **Latest:** JupyterLab 4.6.4; Desktop v4.6.3-1 (4.6.4: 2026-09-21; Desktop: 2026-08-26) · maintained: yes (Desktop revived 2026)
- **macOS arm64:** yes — pip install jupyterlab, or Desktop arm64 installer
- **Windows 11:** yes — pip install jupyterlab, or Desktop x64 installer / winget install jupyterlab
- **Lessons (suggested exercises):**
  - quantum-computing L100 #3: plot counts vs shots and overlay the exact probabilities.
  - simulation L200 #10: plot the running mean per replication and mark the warm-up cut-off.
- **Sources:** https://pypi.org/project/jupyterlab/ · https://github.com/jupyterlab/jupyterlab-desktop · https://github.com/jupyterlab/jupyterlab-desktop/releases

#### marimo
- **Role:** CHECK / SEE — reactive Python notebooks stored as .py; change a parameter and dependent cells re-run.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** 0.25.2 (2026-10-19) · maintained: yes
- **macOS arm64:** yes — pip install marimo (marimo tutorial intro)
- **Windows 11:** yes — same
- **Lessons (suggested exercises):**
  - simulation L100 #2: make the Monte Carlo task-duration parameters a cell and watch P50/P90 update reactively.
  - simulation L200 #9: change solve_ivp rtol in one cell and see step count and error update.
- **Notes:** AI assistant is optional (bring your own key or local model).
- **Sources:** https://pypi.org/project/marimo/

#### Rattle (new Flutter GUI + R package)
- **Role:** SEE — point-and-click data exploration and modelling over R; the Script tab shows the generated R code.
- **Licence:** GPL-3.0 (GUI); R package GPL-2 | GPL-3 · OSI-approved: **yes**
- **Latest:** GUI 6.5.67; CRAN rattle 5.6.2 (GUI ≈2026-08 (no GitHub releases); CRAN 2026-02-08) · maintained: yes
- **macOS arm64:** partial — macOS zip from repo installers (arm64 not confirmed) + install R separately
- **Windows 11:** yes — Inno Setup installer + R
- **Lessons (suggested exercises):**
  - simulation L200 #7: (optional) load the service-time CSV in Explore and read the summary/distribution; copy the R code from the Script tab.
- **Notes:** Weak fit: no lesson teaches ML. Note (second check): CRAN points to rattle.togaware.com for installing the modern Rattle GUI, so it is not just the old V5 site; the CRAN R package is GPL-2 | GPL-3.
- **Sources:** https://github.com/gjwgit/rattle · https://cran.r-project.org/package=rattle · https://togaware.com/projects/rattle/index.html

#### WEKA
- **Role:** SEE — classic ML workbench (Explorer, package manager). Verified, but no direct lesson fit in our seven topics.
- **Licence:** GPL-3.0 (for >3.7.5) · OSI-approved: **yes**
- **Latest:** 3.8.7 (dev 3.9.7) (files dated 2026-03-27) · maintained: yes
- **macOS arm64:** yes — weka-3-8-7-bellsoft-arm-osx.dmg (bundled JVM)
- **Windows 11:** yes — weka-3-8-7-bellsoft-x64-windows.exe
- **Lessons:** none — no direct fit in our seven topics.
- **Notes:** GitHub mirror Waikato/weka-3.8 archived 2022-08-10; official repo is git.cms.waikato.ac.nz. Kept for completeness; prefer Orange for our lessons.
- **Sources:** https://waikato.github.io/weka-wiki/faqs/commercial_applications/ · https://ml.cms.waikato.ac.nz/weka/index.html · https://waikato.github.io/weka-wiki/downloading_weka/ · https://sourceforge.net/projects/weka/files/weka-3-8/3.8.7/

## Mentioned, not catalogued (proprietary / fair-code / source-available)

Per SPEC, these may appear at most as one line in a lesson's `equivalents`.

- **IBM Quantum Composer** (quantum-computing) — proprietary IBM web service. Drag-and-drop circuits, q-sphere/statevector views, step-through 'Inspect'; OpenQASM 2.0 only; ≤4 qubits simulated without sign-in. https://quantum.cloud.ibm.com/docs/en/guides/composer
- **n8n** (ai-agents) — Sustainable Use License (fair-code, NOT OSI); .ee files under Enterprise License. n8n@2.45.5 stable (2026-10-28); npm installs deprecated from 3.0 (Docker route). https://github.com/n8n-io/n8n/blob/master/LICENSE.md · https://github.com/n8n-io/n8n/releases · https://docs.n8n.io/hosting/installation/npm/
- **Dify** (ai-agents) — modified Apache-2.0 with multi-tenant and logo conditions (NOT OSI). Excluded from the catalogue. https://github.com/langgenius/dify/blob/main/LICENSE
- **Arize Phoenix** (ai-agents) — Elastic License 2.0 (source-available, NOT OSI). Only the licence was checked. https://github.com/Arize-ai/phoenix/blob/main/LICENSE
- **Rapidminer AI Studio (ex RapidMiner Studio / Altair AI Studio)** (cross-cutting) — proprietary (licence + EULA on first launch). See Corrections. Free non-commercial licence mentioned on an Altair campaign page only. https://docs.rapidminer.com/latest/studio/installation/ · https://web.altair.com/desafio-machine-learning-baja-rm
- **AnyLogic PLE** (simulation) — proprietary (free for evaluation/personal learning). 8.9.10 (2026-09-24); PLE caps: 10 agent types, 200 blocks/agent, 50 000 dynamic agents, animated runs ≤5 model-hours. https://www.anylogic.com/downloads/
- **jwt.io debugger** (cryptography) — proprietary (Okta/Auth0, all rights reserved). Use CyberChef JWT Decode/Verify instead (client-side). https://www.jwt.io/
- **Redis Insight** (distributed-systems) — SSPL (NOT OSI). Use valkey-cli instead. https://github.com/redis/RedisInsight

## Considered and dropped

- **Quirk (quantum)** — Apache-2.0 but last release v2.3 on 2019-09-11, last code commit ≈5 years ago → unmaintained. The page still works and Cirq can import Quirk URLs (cirq.quirk_url_to_circuit) if a learner already uses it. https://github.com/Strilanc/Quirk/releases · https://quantumai.google/reference/python/cirq/quirk_url_to_circuit
- **qsharp PyPI package** — Archived 2026-08-24 as a compatibility shim → replaced by qdk (kept). https://pypi.org/project/qsharp/
- **JCrypTool** — EPL-1.0; last release 1.0.9 and last commit Sep 2023 → unmaintained; unsigned macOS builds. https://github.com/jcryptool/core/releases
- **mkcert** — BSD-3; last release v1.4.4 (2022-04-26), code untouched ≈4 years → stale; also hides the CA-building that lesson 9 teaches. https://github.com/FiloSottile/mkcert/releases
- **CrypTool-Online** — Live site, but licence of the hosted site and of openssl-webterm could not be verified (only the cto plugin repo is Apache-2.0). https://www.cryptool.org/en/cto/ · https://github.com/orgs/cryptool-org/repositories
- **Flowise** — Apache-2.0 + commercial enterprise folder; repo archived 2026-08-13, end of life 2026-08-31 (after Workday acquisition 2025-08-14). https://github.com/FlowiseAI/Flowise/discussions/6727 · https://flowiseai.com/sunset
- **Langfuse** — MIT core + ee/ (open-core); release/version not verified in this pass. https://github.com/langfuse/langfuse/blob/main/LICENSE
- **RaftScope (raft.github.io) / The Secret Lives of Data** — ISC / MIT, still load as static pages, but repos untouched ≈11 and ≈5 years → fail the maintenance rule. Fine as a 5-minute watch-only link before distributed-systems lesson 7; not catalogued. https://github.com/ongardie/raftscope · https://raft.github.io/ · https://github.com/benbjohnson/thesecretlivesofdata
- **ShiViz (vector-clock log visualiser)** — Last commit ≈5 years ago; licence shown only as 'Other'; live app did not load. Maelstrom messages.svg covers lesson 6. https://github.com/DistributedClocks/shiviz
- **etcdkeeper** — Last commit ≈2 years ago, single maintainer; etcdctl covers lesson 7. https://github.com/evildecay/etcdkeeper
- **Structurizr Lite** — Archived 2026-02-04 (EOL) → replaced by structurizr/structurizr 'local' (kept). https://github.com/structurizr/lite · https://docs.structurizr.com/lite/usage
- **Mu editor** — Repo archived 2025-08-31; project no longer maintained. https://github.com/mu-editor/mu
- **Wokwi** — No micro:bit in the official supported-hardware list; wokwi-elements (MIT) is presentation only; service licence not verified. https://docs.wokwi.com/getting-started/supported-hardware · https://github.com/wokwi/wokwi-elements
- **micro:bit CreateAI** — Code MIT and active, but needs one or two physical micro:bits — our track is simulator-only. https://microbit.org/get-started/user-guide/microbit-createai/ · https://github.com/microbit-foundation/ml-trainer
- **Thonny (for micro:bit)** — MIT, 5.0.0 (2026-04-23), maintained — but its micro:bit back-end needs a board on USB. Usable only as a general Python debugger. https://pypi.org/project/thonny/ · https://github.com/thonny/thonny/wiki/MicroPython
- **Insight Maker** — No official repo/licence found; system dynamics is not in our lessons.
- **RapidMiner open-source core (AGPL)** — Frozen at 9.7 / 9.10 (≈5–6 years old); current product is proprietary — see Corrections. https://github.com/rapidminer/rapidminer-studio · https://github.com/rapidminer/rapidminer-studio-modular
- **Metabase** — AGPL OSS edition + commercial editions in one repo; version/install not verified in this pass. https://github.com/metabase/metabase

## Gaps (not verified — do not state as fact)

- Orange3-Text licence (LICENSE file would not load; commit message mentions AGPLv3).
- winget IDs for KNIME, Wireshark, XCA, Grafana (only third-party indexes or none); Wireshark 4.6.9 release date.
- Native arm64 vs Intel for: XCA dmg, Rattle macOS zip, Rapidminer AI Studio, Keycloak/Structurizr/Mermaid container images, JaamSim 3D view on an arm64 JDK.
- MakeCode: simulator support for datalogger blocks; offline desktop app status (page says none, yet lists builds).
- micro:bit Python Editor: whether the simulator shows the data-log table.
- Maelstrom on Windows (WSL2 assumed); NATS server native Windows asset; RabbitMQ Windows Erlang prerequisite; testssl.sh on Windows.
- CyberChef: whether `ChaCha` matches RFC 8439 and whether JWT ops support EdDSA; KeyStore Explorer Ed25519 support.
- Bruno free-tier OAuth2/PKCE; Keycloak admin-console field for enforcing PKCE; import-linter contract types; KNIME K-AI quota without Pro; whether the OpenAI–promptfoo deal has closed.
- Langfuse/Metabase versions; LM Studio and Jan not checked.
- No maintained, verifiable visual tool found for consistent hashing (distributed-systems lesson 9) or secure randomness (cryptography lesson 3) — these lessons keep their own code as the visual.

## Second check (2026-10-28, independent re-verification of 8 claims)

| # | Claim | Result | Evidence |
|---|---|---|---|
| 1 | RapidMiner has no open-source core today | **Confirmed** (core repo part). `rapidminer-studio` is labelled "Outdated version of RapidMiner Studio 7.x - 9.7", AGPL-3.0, last release 9.7.0 ≈6 years ago. Current "Rapidminer AI Studio" install asks you to configure a Units or Rapidminer licence and accept a EULA on first launch. The Altair/Siemens acquisition dates were not re-checked. | https://github.com/rapidminer/rapidminer-studio · https://docs.rapidminer.com/latest/studio/installation/ |
| 2 | KNIME = GPL-3.0 + additional permissions under GPLv3 §7 | **Confirmed.** The §7 text covers Eclipse interop, and says Nodes are separate works whose owners may choose any licence. | https://www.knime.com/downloads/full-license |
| 3 | Grafana is AGPL-3.0 since 2021 | **Confirmed.** Announced 2021-04-20: core projects moved from Apache-2.0 to AGPLv3. | https://grafana.com/licensing/ |
| 4 | Flowise EOL 2026-08-31; repo archived 2026-08-13 | **Confirmed.** The sunset page gives EOL 2026-08-31 (code freeze 2026-07-29; archival planned for 2026-08-10). GitHub shows the repo archived on Aug 13, 2026. The code stays Apache-2.0. The Workday acquisition was not re-checked. | https://flowiseai.com/sunset · https://github.com/FlowiseAI/Flowise |
| 5 | Structurizr Lite archived 2026-02-04 (EOL) | **Confirmed.** The repo was archived on Feb 4, 2026, and its README says "will not receive any further updates". Lite itself was MIT. | https://github.com/structurizr/lite |
| 6 | draw.io Desktop GPL-3.0 since 31.5.2; core stays Apache-2.0; latest 32.6.1 | **Confirmed, with one qualification.** The 31.5.3 notes cite "the licence change in 31.5.2", and 32.6.1 is the latest release (≈2026-10-24). The `jgraph/drawio` source is Apache-2.0, **but its icon sets and stencil libraries carry an extra restriction**: they may not be used in Atlassian products or the Atlassian marketplace. Exported diagrams are unaffected. | https://github.com/jgraph/drawio-desktop/releases · https://github.com/jgraph/drawio |
| 7 | Orange GPL-3.0-or-later, latest 3.40.0 (2025-12-20) | **Confirmed.** PyPI lists "GPLv3+" and a release on Dec 20, 2025, with macOS arm64 and Windows wheels. The winget id `UniversityofLjubljana.Orange` appears in the official README. | https://pypi.org/project/Orange3/ · https://github.com/biolab/orange3 |
| 8 | Rattle: Flutter GUI GPL-3.0 v6.5.x; CRAN 5.6.2 (2026-02-08); rattle.togaware.com is the *older V5* site | **Partly changed.** Confirmed: the GUI repo is GPL-3.0 (`rattle --version` → 6.5.67), and CRAN 5.6.2 was published 2026-02-08 (RGtk2 GUI needs 5.5.1). **Changed (1):** the CRAN R package is **GPL (≥ 2)** ("GPL-2 \| GPL-3"), not GPL-3.0 only. **Changed (2):** CRAN and the GUI README both point to **rattle.togaware.com for the modern GUI**, so calling it "the older V5 site" is not supported. CRAN's URL field is togaware.com/projects/rattle/. | https://github.com/gjwgit/rattle · https://cran.r-project.org/package=rattle |

Net result: 6 confirmed, 1 confirmed with a qualification (draw.io stencil restriction), 1 partly changed (Rattle). The entries above the "Second check" section were left as written; read them together with this table.

## L300 additions (2026-10-28)

Scope: L300 lessons 12-16 ("Harden it": failure modes, testing, observability) in all seven topics. Same rules as above: official repos, release pages, PyPI and vendor docs only; every fact below was read on 2026-10-28; "≈" = relative date on the page. Lesson numbers refer to `content/L300.json`. Exercises are suggestions; the per-lesson choice (max 2 tools) is in `L300-TOOLS-PROPOSAL.md`.

### New tools

| Tool | Topic | Role | Licence (OSI) | Latest | Mac / Win | L300 lesson |
|---|---|---|---|---|---|---|
| Mitiq | Quantum computing | CHECK | GPL-3.0 (yes) | 1.1.0 | yes / yes | #13 |
| OpenBao (transit engine + web UI) | Cryptography | SEE / CHECK | MPL-2.0 (yes) | v2.7.2 | yes / partial | #12 |
| minisign | Cryptography | CHECK | ISC (yes) | 0.12 | yes / yes | #14 |
| Gitleaks | Cryptography | CHECK | MIT (yes) | v8.30.1 | yes / yes | #16 |
| garak (NVIDIA) | AI agents | CHECK | Apache-2.0 (yes) | v0.17.1 | yes / yes | #16 |
| Temporal CLI dev server + Web UI | Distributed systems | SEE | MIT (yes) | CLI v1.9.1 | yes / yes | #14 |
| Pact Broker (OSS) | Application architecture | SEE / CHECK | MIT (yes) | v2.122.0 (Docker image pactfoundation/pact-broker) | yes / partial | #14 |
| Renode | micro:bit (simulator-only) | CHECK / INSPECT | MIT (yes) | 1.17.0 | yes / yes | #16 |
| SALib | Simulation (civilian) | CHECK / SEE | MIT (yes) | 1.6.0 | yes / yes | #14 |
| FMPy (GUI + CLI) | Simulation (civilian) | INSPECT / CHECK | BSD-2 variant (**no**) | 0.3.32 | yes / yes | #15 |
| Prometheus (+ expression browser, promtool) | Cross-cutting (Application architecture) | CHECK / SEE | Apache-2.0 (yes) | 3.15.1 (LTS 3.13.5) | yes / yes | #15 |

### Quantum computing — L300

#### Mitiq
- **Role:** CHECK — reference implementations of readout-error mitigation and zero-noise extrapolation (Linear/Richardson factories) to compare with your own code.
- **Licence:** GPL-3.0 · OSI-approved: **yes**
- **Latest:** 1.1.0 (2026-09-03) · maintained: yes (1.0.0 2026-03-25, 1.1.0 2026-09-03)
- **macOS arm64:** yes — pip install mitiq (Python >=3.11,<3.13; Cirq is a core dependency; add mitiq[qiskit] for Qiskit circuits)
- **Windows 11:** yes — pip install mitiq (same Python range; PyPI classifiers list macOS and Windows)
- **Lessons (suggested exercises):**
  - L300 #13: Run the lab's mitiq_zne.py, then swap the factory for zne.inference.LinearFactory and RichardsonFactory with scale_factors [1, 3, 5] and compare the zero-noise values with your own extrapolation.
- **Notes:** Library, not a GUI. Requires Python <3.13 (PyPI metadata). Whether a factory plotting helper exists was not checked — plot the scale/value pairs in JupyterLab.
- **Sources:** https://pypi.org/project/mitiq/ · https://mitiq.readthedocs.io/en/stable/guide/zne-1-intro.html · https://mitiq.readthedocs.io/en/stable/guide/zne-4-low-level.html

### Cryptography — L300

#### OpenBao (transit engine + web UI)
- **Role:** SEE / CHECK — key versions, rotate, rewrap and min_decryption_version for envelope encryption, as a running service with a browser UI.
- **Licence:** MPL-2.0 · OSI-approved: **yes**
- **Latest:** v2.7.2 (2026-10-27 (≈, 'yesterday' on the release page)) · maintained: yes (security releases 2.7.2 / 2.6.5 on the same day)
- **macOS arm64:** yes — brew install openbao (official install page), or the lab's container: podman/docker run docker.io/openbao/openbao:2.7.2 server -dev
- **Windows 11:** partial — Container (Docker Desktop / Podman) as in the lab README; a native Windows binary was not checked
- **Lessons (suggested exercises):**
  - L300 #12: Start the dev server from the lab README, run openbao_transit.py, then open the web UI and look at key orders-kl12: key versions after rotate, min decryption version, and a rewrap of a vault:v1 ciphertext.
- **Notes:** Dev mode is in-memory, unsealed, TLS off — learning only; bind to 127.0.0.1. Release notes list UI changes (e.g. PKI UI for external keys in 2.7.2); the UI URL path on the listener was not checked in the official docs. 2.7.2 fixes a transit key-backup path-traversal (GHSA-5pmx-2p74-x478).
- **Sources:** https://github.com/openbao/openbao/releases · https://github.com/openbao/openbao/blob/main/LICENSE · https://openbao.org/docs/install/

#### minisign
- **Role:** CHECK — sign and verify a release manifest with Ed25519 from the command line; no keyring, no network.
- **Licence:** ISC · OSI-approved: **yes**
- **Latest:** 0.12 (2025-01-15) · maintained: yes (last release 2025-01-15; repository commits within the last months)
- **macOS arm64:** yes — brew install minisign
- **Windows 11:** yes — Win64 zip from the GitHub releases (precompiled Win64 binaries since 0.10)
- **Lessons (suggested exercises):**
  - L300 #14: Generate a key pair, sign the lab's MANIFEST.json (-S -s key -m file), verify (-V -p pub -m file), then change one hex digit of a digest in MANIFEST.json and verify again.
- **Notes:** Signatures are compatible with OpenBSD signify. The lab's test_cli_equivalents.py already uses it when installed.
- **Sources:** https://github.com/jedisct1/minisign/releases · https://github.com/jedisct1/minisign/blob/master/LICENSE

#### Gitleaks
- **Role:** CHECK — pattern/entropy secret scanner for files, git history and stdin, with base64/hex/percent decoding.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** v8.30.1 (2026-03-20 (year inferred)) · maintained: yes (commits ≈2 months before check; release cadence slowed in 2026)
- **macOS arm64:** yes — brew install gitleaks (or gitleaks_8.30.1_darwin_arm64.tar.gz)
- **Windows 11:** yes — gitleaks_8.30.1_windows_x64.zip / windows_arm64.zip from the GitHub releases
- **Lessons (suggested exercises):**
  - L300 #16: Run gitleaks dir review_me.log -v, then pipe try_it's base64-encoded demo key through gitleaks stdin --max-decode-depth=2 and compare both results with the lab's scan_log.
- **Notes:** Decoding (hex, percent, base64) arrived in 8.26.0; archive scanning (--max-archive-depth) in 8.27.0. Demo values only — never scan a real secret store into a shared report.
- **Sources:** https://github.com/gitleaks/gitleaks/releases · https://github.com/gitleaks/gitleaks/blob/master/LICENSE

### AI agents — L300

#### garak (NVIDIA)
- **Role:** CHECK — LLM vulnerability scanner: probes (promptinject, encoding, DAN …) plus detectors, with a JSONL/HTML report of hit rates.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** v0.17.1 (≈2026-10-21 ('last week' on the release page)) · maintained: yes (monthly releases)
- **macOS arm64:** yes — python -m pip install -U garak (Python 3.11–3.14)
- **Windows 11:** yes — python -m pip install -U garak (project CI runs Windows tests)
- **Lessons (suggested exercises):**
  - L300 #16: Point garak at the local Ollama model (--target_type ollama --target_name qwen2.5:1.5b --spec probes.promptinject) and read the hit rate per probe; then explain why the lab's protected suite still passes.
- **Notes:** 0.16.0 introduced the unified --spec syntax (old --probes still accepted, deprecated). garak tests the model, not your tool-policy code. Ollama generator options appear in the 0.17.0 notes; the exact generator name was taken from those notes, not re-run.
- **Sources:** https://github.com/NVIDIA/garak/releases · https://github.com/NVIDIA/garak/blob/main/README.md

### Distributed systems — L300

#### Temporal CLI dev server + Web UI
- **Role:** SEE — a durable-workflow engine whose Web UI shows each workflow's event history: activities, failures, retries and compensations.
- **Licence:** MIT (CLI repository) · OSI-approved: **yes**
- **Latest:** CLI v1.9.1 (≈Oct 2026 (server release notes bump the default CLI to 1.9.1 two weeks before check; exact date not captured)) · maintained: yes
- **macOS arm64:** yes — brew install temporal; temporal server start-dev (UI http://localhost:8233)
- **Windows 11:** yes — Windows amd64 archive from the CLI README; temporal.exe server start-dev
- **Lessons (suggested exercises):**
  - L300 #14: Port the orchestrator to a Temporal workflow (activities create/charge/ship, compensations refund then cancel on failure), run the seed-14 fault and open o1's event history in the Web UI.
- **Notes:** The exercise needs the temporalio Python SDK — its version and licence were not checked in this pass. Dev server is in-memory by default.
- **Sources:** https://github.com/temporalio/cli · https://github.com/temporalio/cli/releases · https://github.com/temporalio/temporal/releases

### Application architecture — L300

#### Pact Broker (OSS)
- **Role:** SEE / CHECK — stores consumer contracts and provider verification results; browse pacts and the can-i-deploy matrix in a web UI.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** v2.122.0 (Docker image pactfoundation/pact-broker) (≈Sep–Oct 2026 ('last month' on the release page)) · maintained: yes
- **macOS arm64:** yes — docker run -p 9292:9292 with PACT_BROKER_DATABASE_ADAPTER=sqlite (multi-platform image: linux/amd64 + linux/arm64)
- **Windows 11:** partial — Same container via Docker Desktop (unofficial on Windows; the image is Linux-only)
- **Lessons (suggested exercises):**
  - L300 #14: Start a local broker with SQLite, publish the Pact V4 file written by pact/test_pact_contract.py (HTTP PUT or the broker client), and read the interactions and the matrix in the UI.
- **Notes:** SQLite is for spikes only (no concurrent requests; data lost when the container stops). PactFlow is the commercial fork — not used here. The lab's own lesson-format contract is not a Pact file; use the CI-only pact/ flow.
- **Sources:** https://github.com/pact-foundation/pact_broker/releases · https://github.com/pact-foundation/pact_broker · https://github.com/pact-foundation/pact-broker-docker

### micro:bit (simulator-only) — L300

#### Renode
- **Role:** CHECK / INSPECT — run the real firmware ELF on an emulated nRF52840 (close sibling of the micro:bit V2's nRF52833); Monitor, UART analyzer, Robot Framework tests, new web UI.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** 1.17.0 (2026-09-07 (year inferred)) · maintained: yes (commits days before check)
- **macOS arm64:** yes — renode-1.17.0.osx-arm64-portable.dmg (or the Antmicro Homebrew tap)
- **Windows 11:** yes — renode-1.17.0.setup.exe or windows-portable.zip
- **Lessons (suggested exercises):**
  - L300 #16: Run renode renode/microbit-v2-sibling.resc for the fixed build, then load the racy build with -e and compare the lost counters in the uart0 analyzer; try renode --ui for the web interface.
- **Notes:** No nRF52833 platform in Renode (lab README) — the 840 model is a sibling; no LED matrix/buttons. 1.17.0 added the web UI (renode --ui).
- **Sources:** https://github.com/renode/renode/releases · https://github.com/renode/renode/blob/master/LICENSE · https://github.com/renode/renode

### Simulation (civilian) — L300

#### SALib
- **Role:** CHECK / SEE — Sobol', Morris and other global-sensitivity methods; ProblemSpec.plot() draws S1/ST bars.
- **Licence:** MIT · OSI-approved: **yes**
- **Latest:** 1.6.0 (2026-09-19) · maintained: yes
- **macOS arm64:** yes — pip install SALib (Python >=3.10)
- **Windows 11:** yes — pip install SALib
- **Lessons (suggested exercises):**
  - L300 #14: Run the lab's sensitivity_salib.py, then rebuild it with the ProblemSpec chain (sample → evaluate → analyze_sobol) and call sp.plot() to see window_open's small S1 next to its larger ST.
- **Notes:** Library with basic plotting, not a GUI.
- **Sources:** https://pypi.org/project/SALib/

#### FMPy (GUI + CLI)
- **Role:** INSPECT / CHECK — open an FMU, read its variables and default experiment, simulate and plot; can create a Jupyter notebook for the FMU.
- **Licence:** BSD-2-Clause text plus an added clause (modifications may only be distributed under the same licence); bundled CVODE under its own BSD licence · OSI-approved: **NO** (not OSI-approved — see notes)
- **Latest:** 0.3.32 (2026-09-09) · maintained: yes (single maintainer)
- **macOS arm64:** yes — pip install "fmpy[complete]"; python -m fmpy.gui
- **Windows 11:** yes — pip install "fmpy[complete]"; python -m fmpy.gui
- **Lessons (suggested exercises):**
  - L300 #15: Open the RoomThermal.fmu exported by OpenModelica in the FMPy GUI, check its inputs/outputs and default experiment, then run the lab's fmpy_cosim.py with h = 60 s and 900 s.
- **Notes:** NOT plain OSI BSD-2: the extra 'modifications only under this licence' clause makes it a variant that is not on the OSI list — fine for personal learning. An FMU exported on the Windows PC carries win64 binaries only; on the Mac you need a source FMU or a Mac export.
- **Sources:** https://pypi.org/project/FMPy/ · https://github.com/CATIA-Systems/FMPy/blob/main/LICENSE.txt · https://github.com/CATIA-Systems/FMPy/releases

### Cross-cutting — L300

#### Prometheus (+ expression browser, promtool)
- **Role:** CHECK / SEE — PromQL for SLIs and burn rates; promtool test rules unit-tests alerting rules against synthetic series; the built-in UI graphs expressions.
- **Licence:** Apache-2.0 · OSI-approved: **yes**
- **Latest:** 3.15.1 (LTS 3.13.5) (2026-10-21) · maintained: yes
- **macOS arm64:** yes — prometheus-3.15.1.darwin-arm64.tar.gz (contains prometheus and promtool)
- **Windows 11:** yes — prometheus-3.15.1.windows-amd64.zip
- **Lessons (suggested exercises):**
  - Application architecture L300 #15: Write the 1h/5m latency burn-rate page rule (threshold 14.4) and a promtool test whose input_series encode the incident hour (360 requests, 71 slower than 300 ms; 10 of the last 30), then run promtool test rules.
- **Notes:** promtool tests need no running server. To graph the lab's own log in the expression browser you would have to export it as metrics first (not done in the lab).
- **Sources:** https://github.com/prometheus/prometheus/releases · https://prometheus.io/download/ · https://github.com/prometheus/prometheus/blob/main/LICENSE · https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/

### L300 mappings added to existing tools

Every tool already named in a lesson's `learningTools` (content/L300.json) now carries the matching L300 mapping in `learning-tools.json`; three new suggestions were added on top (marked *new*).

| Tool | L300 mappings |
|---|---|

### Considered for L300 and dropped

- **Zipkin** — Maintained (3.6.1, Apr 2026; Java/Docker), but duplicates Jaeger for distributed-systems #15 and ai-agents #13; licence not re-checked in this pass. https://github.com/openzipkin/zipkin/releases
- **Grafana Tempo** — AGPL-3.0-only (Apache-2.0 exceptions in LICENSING.md), actively developed — but a storage backend with no own UI (needs Grafana); Jaeger already gives a single-binary trace UI. https://github.com/grafana/tempo
- **Perses** — CNCF sandbox dashboards, 0.55.0 (2026-10-21), pre-1.0. 0.55.0 fixed many critical issues exploitable without authentication in the default configuration (JWT forgery, SSRF, path traversal). Duplicates Grafana; licence not re-checked. https://github.com/perses/perses/releases
- **TruffleHog** — AGPL-3.0 (OSI) and active, but overlaps Gitleaks for cryptography #16, and its verification step logs in to third-party services with the secrets it finds — not wanted for a learning lab. https://github.com/trufflesecurity/trufflehog/blob/main/LICENSE
- **Sigstore cosign** — v3.1.4 (≈Oct 2026), active; overlaps minisign for cryptography #14 and by default records signatures in the public Rekor log (lab README). Already documented as an equivalent in the lab; licence not re-verified here. https://github.com/sigstore/cosign/releases
- **Rekor Search UI (search.sigstore.dev)** — Apache-2.0, but last code change ≈10 months before check and it searches the public transparency log; the lab is offline and never uploads. https://github.com/sigstore/rekor-search-ui
- **MQTT Explorer** — Licence is CC BY-ND 4.0 (not a software licence, not OSI); last stable release 0.3.5 on 2019-07-17, latest pre-release 0.4.0-beta.6 on 2024-05-14. https://github.com/thomasnordquist/MQTT-Explorer/releases · https://github.com/thomasnordquist/MQTT-Explorer/blob/master/LICENSE.md
- **Eclipse Mosquitto as a separate learning tool** — Already the lab's broker (microbit #15 step 6, CI job gateway-mqtt) with mosquitto_sub as the viewer; not catalogued separately and version not re-checked.
- **Langfuse** — Licence re-checked: MIT for everything outside ee/, web/src/ee/, worker/src/ee/ and packages/shared/src/server/ee/ (enterprise licence); copyright line now 'ClickHouse, Inc.'. Open-core; version and self-host requirements not checked. Jaeger covers ai-agents #13 through the lab's OpenTelemetry path. https://github.com/langfuse/langfuse/blob/main/LICENSE
- **Qiskit noise visualisation** — not a new tool: `plot_histogram` / `plot_state_city` are part of the catalogued *Qiskit visualization* entry; quantum #12 and #14 mappings added.
- **OpenModelica OMEdit FMU export** — already catalogued (*OpenModelica (OMEdit)*); simulation #15 mapping added.
- **k6 web dashboard** — built into k6 (no extension); folded into the *Grafana k6* entry (see corrections).
- **Arize Phoenix** — re-checked: still Elastic License 2.0 → stays in *Mentioned, not catalogued*.

### L300 gaps (not verified — do not state as fact)

- OpenBao: web UI URL path and whether the Homebrew build ships the UI; native Windows binary.
- Temporal: temporalio Python SDK version/licence; exact CLI 1.9.1 release date.
- garak: exact Ollama generator invocation (taken from release notes, not run); Windows run not tried.
- Gitleaks: whether default rules flag the lab's low-entropy demo values.
- Pact Broker: native Windows (image is Linux-only); whether the lab's pact-python 4.2.0 V4 file renders fully in the OSS UI.
- Mitiq: a built-in plotting helper for factories; FMPy GUI with an FMU exported on the Mac (OpenModelica has no native Mac build).
- Existing entries' versions were not re-checked in this pass except where listed under *L300 corrections*.

## L300 corrections

Changes to existing entries found while checking L300 (2026-10-28). Entries above are left as written; read them with this list.

| Entry | Change | Evidence |
|---|---|---|
| Grafana k6 | **Addition:** k6 has a built-in web dashboard (not an extension): `K6_WEB_DASHBOARD=true` serves it on 127.0.0.1:5665; `K6_WEB_DASHBOARD_EXPORT=<file>.html` writes a self-contained HTML report (graphs only if the run is longer than 3 × `K6_WEB_DASHBOARD_PERIOD`, default 10s). This covers the visual part of distributed-systems #16 without exporting to Prometheus. JSON `notes` updated. | https://grafana.com/docs/k6/latest/results-output/web-dashboard/ |
| Langfuse (dropped) | **Licence detail updated:** MIT outside `ee/`, `web/src/ee/`, `worker/src/ee/` and (new) `packages/shared/src/server/ee/`; copyright line now "ClickHouse, Inc.". Still open-core; version not verified; still not catalogued. | https://github.com/langfuse/langfuse/blob/main/LICENSE |
| Arize Phoenix (mentioned) | **Re-confirmed** Elastic License 2.0 (not OSI); no change. | https://github.com/Arize-ai/phoenix/blob/main/LICENSE |
| learning-tools.json `_meta.lessons` | Now also defines L300 = lessons 12-16. | — |
| ai-agents lab 16 README | Says garak is "not in the learning-tools catalog" — it now is (garak 0.17.1, Apache-2.0). Lab text not changed in this pass. | https://github.com/NVIDIA/garak/releases |
| Licences / versions of other existing entries | Not re-read in this pass (only Phoenix and Langfuse were); no licence change was found, but none was looked for beyond those two. | — |


## Corrections after the L300 update pass (2026-10-28)
- Prometheus/promtool exercise (application-architecture #15): the lab's 12:00 window has 71 POST /loans requests in the last hour with 14 slow (burn 19.7) and 3 in the last 5 minutes with 1 slow (burn 33.3); the earlier "360 requests, 71 slow" figure was wrong.
- Pact Broker exercise (application-architecture #14): the lab's Pact test writes one interaction ('book b1 exists'); the 404 case exists only in the lesson's own contract file.
- Maelstrom on Windows: the project states no native Windows support; use WSL 2 (unverified) or the Mac mini.
