#!/usr/bin/env bash
# Mac experiments for project 04 that need no model server (run by .github/workflows/mac-mini.yml and by hand).
# The simulator tests need Node 24 and internet; they are skipped (with a message) when npx is missing.
set -eu
cd "$(dirname "$0")"
OUT="${KB_RUNS_DIR:-$HOME/kb-runs}"
mkdir -p "$OUT"
python3 make_sim_programs.py --here --out "$OUT/04-sim-programs.jsonl"
if command -v npx >/dev/null 2>&1; then
  (cd sim && npm install --no-audit --no-fund && npx playwright install chromium && npx playwright test)
else
  echo "npx not found: MicroPython simulator tests skipped (install Node 24, see shared/WORKSTATION-SETUP.md)"
fi
python3 soak.py --boards 50 --days 1 --out "$OUT/04-soak-ci.jsonl"
