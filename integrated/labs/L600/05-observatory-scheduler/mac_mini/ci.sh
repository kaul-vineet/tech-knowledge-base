#!/usr/bin/env bash
# Mac experiments for project 05 that need no model server (run by .github/workflows/mac-mini.yml and by hand).
# astropy_check skips cleanly without astropy; indi_export only writes the script (executing it needs indiserver).
set -eu
cd "$(dirname "$0")"
OUT="${KB_RUNS_DIR:-$HOME/kb-runs}"
python3 weather_overnight.py --nights 20000 --out "$OUT"
python3 astropy_check.py --out "$OUT"
python3 indi_export.py --out "$OUT/05-night-indi.sh"
python3 stellarium_export.py --out "$OUT/05-plan.ssc"
