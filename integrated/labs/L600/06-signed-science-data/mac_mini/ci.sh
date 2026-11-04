#!/usr/bin/env bash
# Mac experiments for project 06 that need no model server (run by .github/workflows/mac-mini.yml and by hand).
# Medium sizes (minutes on a Mac mini); the overnight sizes are in README.md.
set -eu
cd "$(dirname "$0")"
OUT="${KB_RUNS_DIR:-$HOME/kb-runs}"
mkdir -p "$OUT"
python3 http_world.py --mirrors 8 --releases 10 --out "$OUT/06-http.jsonl"
if python3 http_world.py --here --inject float-format --out "$OUT/06-http-failure-lab.jsonl"; then
  echo "float-format did not break the HTTP mirrors"; exit 1
fi
python3 scale_bench.py --rows 1e5 --out "$OUT/06-scale.jsonl"
if command -v npm >/dev/null 2>&1; then
  (cd jcs_node && npm install --no-audit --no-fund)
  python3 jcs_crosscheck.py --out "$OUT/06-jcs.jsonl"
else
  python3 jcs_crosscheck.py --here --out "$OUT/06-jcs.jsonl"
fi
