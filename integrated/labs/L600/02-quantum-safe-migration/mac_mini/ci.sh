#!/usr/bin/env bash
# Mac experiments for project 02 that need no model server (run by .github/workflows/mac-mini.yml and by hand).
# Installs the pinned Qiskit wheels (wheels only: no compiling); medium sizes, the overnight size is in README.md.
set -eu
cd "$(dirname "$0")"
OUT="${KB_RUNS_DIR:-$HOME/kb-runs}"
mkdir -p "$OUT"
python3 -m pip install --only-binary=:all: qiskit==2.6.1 qiskit-aer==0.18.2
python3 qiskit_crosscheck.py --out "$OUT/02-qiskit.jsonl"
python3 pq_bench.py --out "$OUT/02-pq.jsonl"
python3 order_wall.py --max-n 143 --out "$OUT/02-wall.jsonl"
