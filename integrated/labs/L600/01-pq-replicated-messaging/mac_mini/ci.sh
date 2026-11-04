#!/usr/bin/env bash
# Mac experiments for project 01 that need no model server (run by .github/workflows/mac-mini.yml and by hand).
# Medium sizes (minutes on a Mac mini); the overnight size is in README.md.
set -eu
cd "$(dirname "$0")"
OUT="${KB_RUNS_DIR:-$HOME/kb-runs}"
mkdir -p "$OUT"
python3 bench_crypto.py --out "$OUT/01-bench.jsonl"
python3 multiproc.py --messages 2000 --kills 20 --out "$OUT/01-multiproc.jsonl"
python3 multiproc.py --messages 300 --kills 4 --nonce derived --no-fsync --out "$OUT/01-multiproc-derived.jsonl"
if python3 multiproc.py --messages 300 --kills 4 --nonce leader-counter --no-fsync --out "$OUT/01-multiproc-failure-lab.jsonl"; then
  echo "leader-counter did not reuse a nonce across real processes"; exit 1
fi
