# L600 Mac mini track — use the Mac mini for more than "run the lab"

The eight integrated projects (`../labs/L600/`) run anywhere in seconds with a fake model, small simulations and stubs.
That proves the seams, not the system. An Apple-silicon Mac mini that is always on can do five things the sandbox cannot:

| What | Why it matters | Where |
|---|---|---|
| Real local models (Ollama, Metal) | the fake model obeys rules; a real one makes the mistakes your gates exist for | 03, 05, 08 (+ model server for the Windows PC) |
| Bigger simulations, all cores | 100k Monte Carlo nights, large Sobol/replication runs: the numbers stop moving | 03, 05 (+ B's projects) |
| Real simulators | INDI telescope + CCD simulators execute the plan; Stellarium checks the sky | 05 |
| Real processes and network | replicas as separate processes on loopback/LAN instead of threads | see the other projects' `mac_mini/` |
| Always-on runs + macOS CI | nightly launchd job and a self-hosted GitHub Actions runner | `scripts/nightly.sh`, `RUNNER.md` |

Rules carried over from the projects: open source only; the agent proposes or explains, deterministic code decides;
every number that needs the Mac is **pendingMac** until you run it — the folders say what you should see and how to
read it, never what you "got".

## Order (one evening each, then leave it overnight)
1. **Profile the machine** — `python3 integrated/mac-mini/scripts/mac_profile.py` (below). Everything else sizes itself
   from it (`--json`).
2. **Model server** — install Ollama, pull the models the profile recommends: [MODEL-SERVER.md](MODEL-SERVER.md).
3. **Per project** — each `integrated/labs/L600/NN-*/mac_mini/README.md`: 2–3 experiments, each with zsh commands,
   what to record and which ADR/fitness threshold the result changes. Every script has `--here` (runs anywhere).
4. **Nightly** — install the launchd job (below): all 8 scorecards + failure labs every night, JSONL in `~/kb-runs/`.
5. **CI** — optional: register the Mac mini as a self-hosted runner: [RUNNER.md](RUNNER.md) and
   `.github/workflows/mac-mini.yml`.
6. Containers: 03 and 08 need none; 05's optional INDI-in-Debian route uses one; a project's `mac_mini/README.md` says
   when it needs one. Guide: [COLIMA.md](COLIMA.md).

## Which Mac mini? (RAM decides)
RAM is not known in advance, so nothing is hard-coded: `mac_profile.py` reads `hw.memsize` and the performance-core
count with `sysctl` and computes the rest. The table below is its output for the four sizes (`--table 16 24 32 64
--markdown`, ctx 4096, 1 parallel request):

| Mac mini RAM | budget GB | largest local model | spare GB | compare (03/05/08) | max qubits c128 | max qubits c64 |
|---|---|---|---|---|---|---|
| 16 GB | 10.06 | qwen2.5:14b | 0.26 | qwen2.5:3b, qwen2.5:7b, qwen2.5:14b | 28 | 29 |
| 24 GB | 17.79 | qwen2.5:14b | 7.98 | qwen2.5:3b, qwen2.5:7b, qwen2.5:14b | 29 | 30 |
| 32 GB | 25.52 | qwen2.5:32b | 4.45 | qwen2.5:7b, qwen2.5:14b, qwen2.5:32b | 29 | 30 |
| 64 GB | 56.45 | qwen2.5:32b | 35.38 | qwen2.5:7b, qwen2.5:14b, qwen2.5:32b | 30 | 31 |

How it is computed (printed by `mac_profile.py --ram 16`):
- RAM is sold in GiB: 16 GB = 17.18 GB decimal. **usable** = RAM − 6 GB for macOS and apps (assumption from ai-agents
  L400 #19); **budget** = usable × 0.9 so a simulation can run next to the model.
- **need(model)** = Q4_K_M download size (ollama.com) + f16 KV cache = 2 × layers × KV heads × head dim × 2 bytes ×
  context × parallel (Qwen2.5 `config.json`). qwen2.5:14b: 9.0 + 0.805 = 9.805 GB → it fits a 16 GB Mac mini with
  0.26 GB to spare: usable, but close the browser and check `ollama ps` (it must say `100% GPU`).
- **statevector**: 16 bytes per amplitude (complex128) × 2ⁿ × 2 copies ≤ budget → 28 qubits on 16 GB; each extra
  qubit doubles memory, so 64 GB buys only 2 more. complex64 halves the bytes: one more qubit, less precision.
- Change an assumption (`ASSUMPTIONS` in the script), and the table, the per-project model lists and the nightly sizes
  all follow. Measure the real footprint with `ollama ps` (SIZE column) and Activity Monitor → Memory.

## Nightly runs (launchd)
`scripts/nightly.sh` runs, for every project, the scorecard (must exit 0) and the failure lab (`--inject`, must exit
non-zero); with `--with-tests` also the unit tests, `checks_NN.py` and `mac_mini/tests`. One JSON line per step goes to
`~/kb-runs/YYYY-MM-DD.jsonl` (`lab, step, exit, expect, ok, seconds, last_json` = the final scorecard line), full logs to
`~/kb-runs/logs/DATE/`; files older than 30 days are deleted. Exit status 1 if anything behaved unexpectedly — including
a failure lab that *passes*, which means a seam test stopped biting.

```zsh
cd ~/kb                                                  # the repository root (kb/)
bash integrated/mac-mini/scripts/nightly.sh --here       # dry run: prints the 16 planned commands
bash integrated/mac-mini/scripts/nightly.sh --only "03 05 08"   # a real run of three projects, now
bash integrated/mac-mini/scripts/install_nightly.sh install     # LaunchAgent local.kb.nightly, 02:30 every night
bash integrated/mac-mini/scripts/install_nightly.sh run-now     # = launchctl kickstart -p gui/$(id -u)/local.kb.nightly
bash integrated/mac-mini/scripts/install_nightly.sh status      # = launchctl print gui/$(id -u)/local.kb.nightly
bash integrated/mac-mini/scripts/install_nightly.sh uninstall   # = launchctl bootout gui/$(id -u)/local.kb.nightly
jq -c 'select(.ok == false)' ~/kb-runs/$(date -u +%F).jsonl     # what broke last night (jq is optional; grep works)
```
`install` renders `launchd/local.kb.nightly.plist.template` into `~/Library/LaunchAgents/`, checks it with
`plutil -lint`, then `launchctl bootstrap gui/$(id -u) <plist>`. The job runs `caffeinate -i` around the script so the
Mac does not idle-sleep mid-run. Apple's launchd documentation: a `StartCalendarInterval` job missed while the Mac was
**asleep** runs at wake; one missed while it was **off** does not run until the next 02:30.
**What you should see:** 16 lines per night with `"ok": true` (32 with `--with-tests`, more where a project has
`mac_mini/tests`). Read `seconds` over a month: a project that gets slower every night is a regression worth an issue.

## Files
| File | What |
|---|---|
| `scripts/mac_profile.py` | detects arch/RAM/cores/macOS; model size class and statevector limit with the maths; `--ram N` simulates |
| `scripts/nightly.sh`, `scripts/install_nightly.sh`, `launchd/*.plist.template` | nightly run, install/uninstall |
| `MODEL-SERVER.md` | Ollama on the Mac mini serving the Windows PC over the LAN (and why only the LAN) |
| `RUNNER.md` | self-hosted GitHub Actions runner on the Mac mini; `../../.github/workflows/mac-mini.yml` |
| `COLIMA.md` | open-source container runtime, only if a project's `mac_mini/` needs containers |
| `tests/test_shared.py` | runs here: profile maths, nightly run against fake labs (incl. retention), plist rendering |

### Convention for every project's `mac_mini/` folder (so CI and the nightly job find it)
`README.md` (experiments) · scripts with `--here` · `tests/` (unittest, run here) · optional `ci.sh` (Mac experiments that
need nothing but numpy/cryptography; the workflow runs it) · optional `ci_ollama.sh` (needs the model server; runs only
when the repository variable `MAC_MINI_OLLAMA` is `true`) · `integrated/research/checks_NN_mac.py`. JSONL outputs go to
`$KB_RUNS_DIR` (default `~/kb-runs`).

Validation: `python -m unittest discover -s integrated/mac-mini/tests` ran here (Linux, Python 3.12); nothing in this
folder has run on macOS yet (pendingMac: `sysctl` detection, launchd install, the self-hosted runner).
Sources: `../research/mac-mini-evidence.md`.

## GPU memory cap: why the "largest model" column is an upper bound

macOS lets the GPU use only part of unified memory by default. Metal reports the cap as `recommendedMaxWorkingSetSize`; Apple doesn't
publish an exact fraction, but in practice it is about two-thirds of RAM up to 32 GB (≈10.7 GB on a 16 GB Mac) and about
three-quarters above that. Read the real figure on your Mac: `ollama serve` (or llama.cpp) logs it at startup.

- **16 GB Mac mini:** use the **7B** model day to day. The 14B model fits only with almost nothing to spare, and none of the
  simulations can run alongside it.
- **24–32 GB:** 14B is comfortable. 32B needs 32 GB or more, and is tight even then.
- Keep the context at 4,096 tokens (as these numbers assume), or set `OLLAMA_KV_CACHE_TYPE=q8_0`: the cache grows with context.
- `sudo sysctl iogpu.wired_limit_mb=…` raises the cap until the next restart. Apple doesn't support it, so don't use it
  for these labs: if it pushes macOS into swap, results get slower and noisier.
