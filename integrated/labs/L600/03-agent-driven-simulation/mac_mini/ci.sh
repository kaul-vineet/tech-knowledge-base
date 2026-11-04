#!/usr/bin/env bash
# Mac experiments for project 03 that need no model server (run by .github/workflows/mac-mini.yml and by hand).
# Medium sizes (minutes on a Mac mini); the overnight sizes are in README.md.
set -eu
cd "$(dirname "$0")"
python3 overnight_sweep.py coverage --experiments 300 --reps 10 --out "${KB_RUNS_DIR:-$HOME/kb-runs}"
python3 overnight_sweep.py sobol --n 1024 --out "${KB_RUNS_DIR:-$HOME/kb-runs}/03-sobol"
