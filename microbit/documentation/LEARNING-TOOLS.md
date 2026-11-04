# Learning tools — micro:bit (L100–L400)

Open-source tools that sit next to the labs. Facts come from `../../shared/LEARNING-TOOLS-CATALOG.md`
(checked 2026-10-28). Each lesson's exercise is in its `learningTools` field (`content/L100.json` … `L400.json`).

| Tool | Role | Licence (OSI) | Mac mini | Windows | Lessons |
|---|---|---|---|---|---|
| [micro:bit Python Editor v3](https://github.com/microbit-foundation/python-editor-v3) (V2 simulator) | CHECK / SEE | MIT (yes) | Browser: python.microbit.org; offline app | same | L100 #5, #6 · L200 #8 · L300 #13, #14 · L400 #18, #19 |
| [Microsoft MakeCode for micro:bit](https://github.com/microsoft/pxt-microbit) | BUILD WITHOUT CODE / SEE | MIT (yes) | Browser: makecode.microbit.org | Browser | L100 #6 · L200 #7, #11 · L300 #12, #13 |
| [micropython-microbit-v2-simulator](https://github.com/microbit-foundation/micropython-microbit-v2-simulator) (standalone) | CHECK | MIT (yes) | Build/serve `demo.html` locally | same | L200 #7 · L300 #12 · L400 #17, #18 |
| [Renode](https://github.com/renode/renode) 1.17.0 | CHECK / INSPECT | MIT (yes) | `renode-1.17.0.osx-arm64-portable.dmg` | `renode-1.17.0.setup.exe` | L300 #16 |
| [Orange Data Mining](https://orangedatamining.com/download/) 3.40.0 | BUILD WITHOUT CODE / SEE | GPL-3.0-or-later (yes) | `.dmg`, conda or `pip install PyQt6 PyQt6-WebEngine orange3` | `winget install --id UniversityofLjubljana.Orange` | L200 #8 · L300 #14, #15 |
| [Apache Superset](https://github.com/apache/superset/releases) 6.1.0 | SEE | Apache-2.0 (yes) | `docker compose -f docker-compose-image-tag.yml up` or `pip install apache_superset` | Partial: Docker Desktop (unofficial) | L200 #8 · L300 #15 · L400 #17 · Capstone |
| [Prometheus](https://github.com/prometheus/prometheus/releases) 3.15.1 (+ promtool) | CHECK | Apache-2.0 (yes) | `prometheus-3.15.1.darwin-arm64.tar.gz` | `prometheus-3.15.1.windows-amd64.zip` | Capstone (`out/metrics.txt`) |
| [Grafana OSS](https://github.com/grafana/grafana/releases) | SEE / INSPECT | AGPL-3.0-only (yes) | `brew install grafana && brew services start grafana` | Installer or zip (Open Source edition) | Capstone (via Prometheus) |
| [JupyterLab](https://pypi.org/project/jupyterlab/) (+ Desktop) | CHECK / SEE | BSD-3-Clause (yes) | `pip install jupyterlab` | same, or `winget install jupyterlab` | L400 #20 |
| [SimPy](https://pypi.org/project/simpy/) | CHECK | MIT (yes) | `pip install simpy` | same | L400 #20 |
| [Ollama](https://github.com/ollama/ollama/releases) (supporting runtime) | CHECK | MIT (yes) | `brew install ollama && brew services start ollama` | `irm https://ollama.com/install.ps1 \| iex` | L400 #21 (L100 #5, L200 #8, L300 #15 agent assists) |

## How to use these tools
They complement the labs: you still write the code and run the tests in `labs/`. Everything here ran only on the
CPython stub (`validated-stub`), so a Python Editor run is the first real MicroPython run. Use it to **check** what the
stub predicts, for example the SipHash reference value and its time per tag in L400 #19. Use MakeCode to **see** an idea in
blocks. Use Orange or Superset on the CSVs the labs write, and Prometheus + Grafana on the capstone's `metrics.txt`, and
compare the picture with what your code computed. JupyterLab and SimPy **re-check** the digital twin (L400 #20). Ollama
replaces the fake model server: the alarms must not change (L400 #21). Every exercise awaits a manual run; its `expected` says what it should match.

## Not recommended / changed
- **Wokwi**: the micro:bit is not on its supported-hardware list.
- **Mu editor**: the repository was archived on 2025-08-31.
- **Thonny (micro:bit back-end)** and **micro:bit CreateAI**: both need a physical board; this track is simulator-only.
- **Grafana with CSV**: core Grafana has no CSV data source; the capstone exports Prometheus text instead.
- **MakeCode datalogger blocks**: they need a V2 hardware flash; use the Python Editor.
- **MQTT Explorer**: CC BY-ND 4.0 is not a software licence, and the last stable release is from 2019. Use `mosquitto_sub`.
- **Eclipse Mosquitto** is the lab broker (CI), not a separate tool. **promptfoo** red-teaming is not used for L400 #21:
  by default it uses a hosted service (review R3-07). The lab's `fuzz.py` stays local.
