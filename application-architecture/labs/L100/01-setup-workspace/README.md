# Lab 01 – Set up your workspace

Check that your machine can run every L100 lab: Python 3.12+ and the standard library only.
Diagram tools are optional and only matter for lesson 6.

## Files
| File | Purpose |
|---|---|
| `check_env.py` | Prints platform, Python/stdlib/SQLite status and which optional tools (node, npx, podman, docker, ollama) are found |
| `test_check_env.py` | unittest suite for the checker |
| `run_all_labs.py` | Runs `python -m unittest discover` in every `labs/L100/NN-*` folder |
| `try_it.py` | Runs the lesson's two tryIt experiments and prints what happened (never edits the lab files) |

## Run
Python 3.12+ in a virtual environment; after activation `python` is the same command on both machines.
Full workstation setup (canonical commands for every topic): [`../../../../shared/WORKSTATION-SETUP.md`](../../../../shared/WORKSTATION-SETUP.md).

**Mac mini (zsh)**
```bash
brew install python@3.12
python3.12 -m venv .venv && source .venv/bin/activate
cd labs/L100/01-setup-workspace
python check_env.py
python -m unittest -v
python run_all_labs.py
```
**Windows PC (PowerShell)**
```powershell
winget install -e --id Python.Python.3.12
py -3.12 -m venv .venv; .venv\Scripts\Activate.ps1   # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
$env:PYTHONUTF8 = "1"
cd labs\L100\01-setup-workspace
python check_env.py
python -m unittest -v
python run_all_labs.py
```

## Expected output (observed 2026-10-28, Python 3.12.15, Linux sandbox)
```
platform Linux x86_64
python   3.12.15    OK
stdlib   7 modules  OK
sqlite   3.44.0     OK
optional node       found - Node.js (for mermaid-cli)
optional npx        not found (ok) - runs mermaid-cli without a global install
optional podman     not found (ok) - Podman (for Structurizr; open source)
optional docker     not found (ok) - Docker (same role as podman)
optional ollama     not found (ok) - local model server (lesson 6 agent assist; optional)
```
On the Mac mini the first line reads `platform Darwin arm64`, on the Windows PC `platform Windows AMD64`
(not run here: macOS/Windows are covered by the CI matrix). Versions and optional-tool lines may differ.
```
test_all_required_stdlib_modules_import (test_check_env.CheckEnvTest.test_all_required_stdlib_modules_import) ... ok
test_current_python_is_supported (test_check_env.CheckEnvTest.test_current_python_is_supported) ... ok
test_main_returns_zero (test_check_env.CheckEnvTest.test_main_returns_zero) ... ok
test_old_python_is_rejected (test_check_env.CheckEnvTest.test_old_python_is_rejected) ... ok
test_optional_tools_cover_both_container_engines (test_check_env.CheckEnvTest.test_optional_tools_cover_both_container_engines) ... ok
test_unknown_module_is_reported (test_check_env.CheckEnvTest.test_unknown_module_is_reported) ... ok

----------------------------------------------------------------------
Ran 6 tests in 1.127s

OK
```
```
01-setup-workspace             OK
02-layered-structure           OK
03-modular-monolith            OK
04-api-first-openapi           OK
05-config-12factor             OK
06-documenting-architecture    OK
ALL LABS PASSED
```

## Optional tools (lesson 6 only)
| Need | Mac mini (zsh) | Windows PC (PowerShell) |
|---|---|---|
| Node.js 24 LTS for `npx` mermaid-cli 11.17.0 (MIT) | `brew install node@24` (keg-only: add `$(brew --prefix node@24)/bin` to PATH) | `winget install -e --id OpenJS.NodeJS.LTS --version 24.19.0` |
| Container engine for Structurizr (`structurizr/structurizr:2026.09.19`, amd64 + arm64 image) | `brew install podman` or the Podman pkg installer; `podman machine init && podman machine start` | install WSL 2 first (`wsl --install`, admin), then `winget install -e --id RedHat.Podman`; `podman machine init; podman machine start` |
| Local model for the agent assist | `brew install ollama && brew services start ollama && ollama pull qwen2.5:1.5b`, then `export LOCAL_MODEL_URL=http://localhost:11434/v1` and `export LOCAL_MODEL=qwen2.5:1.5b` | install `OllamaSetup.exe` from ollama.com/download (winget `Ollama.Ollama` lags behind), `ollama pull qwen2.5:1.5b`, then `$env:LOCAL_MODEL_URL="http://localhost:11434/v1"; $env:LOCAL_MODEL="qwen2.5:1.5b"` |

Podman Desktop (`brew install --cask podman-desktop`, `winget install -e --id RedHat.Podman-Desktop`) adds a GUI.
Docker Desktop, Colima (macOS) or Rancher Desktop work too: replace `podman` with `docker`.
Structurizr **Lite** has reached end of life; its replacement is the `local` command. See `documentation/HARDWARE.md`.

## Try it (observed 2026-10-28, Python 3.12.15)
Predict first, then run. `try_it.py` never edits the lab files (code changes go to a temporary `.tryit-work/` copy that is deleted afterwards); the tasks and predictions are in the lesson's `tryIt` field.
```bash
python try_it.py
```
```
[1] test file renamed to checks_env_test.py -> exit 5: NO TESTS RAN
[2] MIN_PYTHON=(3, 99) -> main() returns 1; python line: python   3.12.15    TOO OLD (need 3.12+)
```

## Troubleshooting
| Symptom | Action |
|---|---|
| `TOO OLD (need 3.12+)` | Install Python 3.12 (python.org or your OS package manager) and re-run with that interpreter. |
| `ModuleNotFoundError: check_env` when running tests | Run `python -m unittest` from inside this folder (discovery imports from the current directory). |
| Windows: `Activate.ps1 cannot be loaded because running scripts is disabled` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or call `.venv\Scripts\python.exe` directly. |
| macOS: `python` is missing or older than 3.12 outside the venv | Homebrew installs `python3.12`; create the venv with it, then use `python` inside the venv. |
