#!/usr/bin/env bash
# Project 08 Mac checks that need no model server: the loopback guard and the fake-model corpus (run by mac-mini.yml).
set -eu
cd "$(dirname "$0")"
python3 injection_eval.py --here --naive --out "${KB_RUNS_DIR:-$HOME/kb-runs}"
