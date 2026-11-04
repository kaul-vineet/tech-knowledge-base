#!/usr/bin/env bash
# Mac experiments for project 07 that need no model server (run by .github/workflows/mac-mini.yml and by hand).
# Installs the pinned Qiskit wheels (wheels only); medium sizes, the overnight sizes are in README.md.
set -eu
cd "$(dirname "$0")"
OUT="${KB_RUNS_DIR:-$HOME/kb-runs}"
mkdir -p "$OUT"
python3 -m pip install --only-binary=:all: qiskit==2.6.1 qiskit-aer==0.18.2
python3 aer_backend.py --out "$OUT/07-aer.jsonl"
python3 qubit_sweep.py --aer --cap 120 --out "$OUT/07-sweep.jsonl"
python3 overnight_load.py --seeds 4 --jobs 1000 --copies 1 2 --out "$OUT/07-load-ci.jsonl"
