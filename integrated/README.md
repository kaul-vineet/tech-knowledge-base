# Integrated Projects (L600 · Integrate it)

Eight projects that each combine two or three topics into one working system. Real systems fail where technologies meet,
so every project names its **seams** (the contract that crosses each boundary), guards each seam with a test, and ships a
**failure lab**: a seeded fault that only exists because the topics meet. You reproduce it, diagnose it and fix it.

Prerequisite: the L100–L400 lessons of the topics a project combines (each lesson's *Builds on* list links them).

| # | Project | Combines | Lab | Failure lab |
|---|---|---|---|---|
| 1 | Post-quantum secure messaging over a replicated log | Cryptography, Distributed Systems, App Architecture | `labs/L600/01-pq-replicated-messaging` | `--inject leader-counter` |
| 2 | Quantum-safe migration: from Shor in a simulator to a crypto inventory | Quantum, Cryptography, App Architecture | `labs/L600/02-quantum-safe-migration` | `--inject bypass` |
| 3 | An AI agent that runs simulation experiments — and can't fool you | AI Agents, Simulation, App Architecture | `labs/L600/03-agent-driven-simulation` | `--inject few-reps` |
| 4 | An offline-first micro:bit sensor fleet | micro:bit, Distributed Systems, App Architecture | `labs/L600/04-microbit-sensor-fleet` | `--inject wallclock-lww` |
| 5 | A robotic-observatory night scheduler | Astronomy, Simulation, AI Agents | `labs/L600/05-observatory-scheduler` | `--inject local-as-utc` |
| 6 | A verifiable, replicated science-data release pipeline | Astronomy, Cryptography, Distributed Systems | `labs/L600/06-signed-science-data` | `--inject float-format` |
| 7 | A reliable quantum-job service on unreliable backends | Quantum, Distributed Systems, App Architecture | `labs/L600/07-quantum-job-service` | `--inject lease-expiry` |
| 8 | A tool platform for AI agents with least privilege and an audit trail | AI Agents, Cryptography, App Architecture | `labs/L600/08-secure-agent-tools` | `--inject naive-host` |

## Run a project (Mac mini or Windows, from the repository root)
```
cd integrated/labs/L600/<project>
python run_project.py                       # scorecard: every milestone, seam and fitness function must PASS
python run_project.py --inject <fault>      # reproduce the failure lab: the scorecard must FAIL
python -m unittest discover -s tests -v     # unit, seam and failure-lab tests
python ../../../research/checks_NN.py       # recomputes every number in the lesson and its questions
```
Only `numpy` and `cryptography` are needed (versions in `shared/WORKSTATION-SETUP.md`). Projects 03, 05 and 08 use the
shared local-agent fake by default; set `LOCAL_MODEL_URL` / `LOCAL_MODEL` to use a real local model (Ollama or llama.cpp).
The model only proposes or explains; deterministic code always decides.

Each project folder has: `README.md` (real output), `architecture.mmd`, `decisions/` (ADRs), `tests/`, `try_it/`,
`solution/` (build task with the `BUILD_TARGET=mine` switch) and `_kb.py`, which imports the earlier labs in place instead
of copying them.

## Mac mini track
`mac-mini/README.md`: use the Apple-silicon Mac mini for real local models, bigger simulations, real simulators,
overnight runs and a self-hosted macOS runner. Each project's `labs/L600/<project>/mac_mini/` folder has 2-3 experiments
(every script also runs here with `--here`); results that need the Mac are marked pendingMac.

## Practice
`content/qbank/L600.json`: 261 multiple-choice questions (≥32 per project) on seams, calculations, diagnosing failures,
code reading and design trade-offs. On the website choose **Integrated Projects (L600) → Practice**.
