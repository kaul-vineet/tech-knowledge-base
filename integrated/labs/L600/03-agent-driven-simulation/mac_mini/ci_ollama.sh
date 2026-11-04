#!/usr/bin/env bash
# Project 03 experiments that need Ollama on this Mac (opt-in in CI: repository variable MAC_MINI_OLLAMA=true).
set -eu
cd "$(dirname "$0")"
export LOCAL_MODEL_URL="${LOCAL_MODEL_URL:-http://127.0.0.1:11434/v1}"
python3 compare_models.py --auto --out "${KB_RUNS_DIR:-$HOME/kb-runs}"
python3 export_rejections.py --runs "${KB_RUNS_DIR:-$HOME/kb-runs}"
