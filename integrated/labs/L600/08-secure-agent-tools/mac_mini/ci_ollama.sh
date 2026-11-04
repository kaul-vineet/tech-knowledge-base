#!/usr/bin/env bash
# Project 08 experiments that need Ollama on this Mac (opt-in in CI: repository variable MAC_MINI_OLLAMA=true).
set -eu
cd "$(dirname "$0")"
export LOCAL_MODEL_URL="${LOCAL_MODEL_URL:-http://127.0.0.1:11434/v1}"
python3 injection_eval.py --auto --naive --out "${KB_RUNS_DIR:-$HOME/kb-runs}"
