# 01 · Set up your simulation workbench

Check Python 3.12 + numpy, see the pinned SimPy/SciPy/Mesa versions CI installs, and prove a seed makes randomness repeatable.

Read the concept note first: `../../../content/concepts/01-setup-simulation-workbench.md`. Hardware notes: `../../../documentation/HARDWARE.md`.

## Install (Mac mini or Windows PC)
Full workstation setup (same commands for every topic): [`../../../../shared/WORKSTATION-SETUP.md`](../../../../shared/WORKSTATION-SETUP.md).

| Step | macOS (zsh) | Windows 11 (PowerShell) |
|---|---|---|
| Python 3.12 | `brew install python@3.12` | `winget install -e --id Python.Python.3.12` |
| venv (repo root) | `python3.12 -m venv .venv && source .venv/bin/activate` | `py -3.12 -m venv .venv; .venv\Scripts\Activate.ps1` |
| UTF-8 output | (default) | `$env:PYTHONUTF8 = "1"` |
| Pinned packages | `python -m pip install --only-binary=:all: -r labs/L100/01-setup-workbench/requirements.txt` | same command |
| Local model (optional, lessons 6-7) | `brew install ollama` → `brew services start ollama` → `ollama pull qwen2.5:1.5b` | Installer `OllamaSetup.exe` from ollama.com/download (winget `Ollama.Ollama` lags behind) → `ollama pull qwen2.5:1.5b` |
| Model endpoint | `export LOCAL_MODEL_URL=http://localhost:11434/v1` and `export LOCAL_MODEL=qwen2.5:1.5b` | `$env:LOCAL_MODEL_URL="http://localhost:11434/v1"` and `$env:LOCAL_MODEL="qwen2.5:1.5b"` |

If PowerShell says running scripts is disabled: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again. The Ollama server must be running before `ollama pull` (Mac alternative: `brew install --cask ollama-app`, then open Ollama.app once).
`--only-binary=:all:` makes pip fail fast instead of compiling numpy/SciPy from source when no wheel matches your machine.

## Run
```bash
python check_env.py
```

## Expected output (real run, Python 3.12.15, Linux x86_64, numpy 2.5.3; seeded, identical on every run)
```
Python 3.12.15 on Linux x86_64 | CPU cores: 1
  numpy  pin 2.5.3   installed 2.5.3
  simpy  pin 4.1.2   not installed -> runs in CI
  scipy  pin 1.18.1  not installed -> runs in CI
  mesa   pin 3.5.1   not installed -> runs in CI
seed 42 -> [0.773956, 0.438878, 0.858598]
seed 42 -> [0.773956, 0.438878, 0.858598] (identical = reproducible)
READY for local labs
```
On the Mac mini the first line reads `Darwin arm64`, on a Windows PC `Windows AMD64` (expected, not run here: CI covers both). The seed lines must be identical on every OS.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 5 tests ... OK` (includes a CRLF line-ending test for `requirements.txt`).

## Try it
```bash
python try_it.py
```
Observed:
```
unseeded equal? False
random.Random(42): 0.639427 | numpy default_rng(42): 0.773956
```

## Pinned toolchain
```
# Pinned versions checked on PyPI on 2026-10-28. numpy is used by local labs; the rest run in CI.
numpy==2.5.3
simpy==4.1.2
scipy==1.18.1
mesa==3.5.1
```

## Files
- `check_env.py` - main lab code
- `requirements.txt` - pins: numpy, simpy, scipy, mesa
- `test_setup.py` - version, numpy, pins (incl. CRLF), seeding
- `try_it.py` - tryIt script
