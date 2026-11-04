#!/usr/bin/env bash
# Nightly run of the eight L600 integrated projects on the Mac mini (launchd starts it; see ../README.md).
# For every project: the scorecard (must exit 0) and the seeded failure lab (must exit non-zero).
# Writes one JSON line per step to $KB_RUNS_DIR/YYYY-MM-DD.jsonl (default ~/kb-runs), full logs to
# $KB_RUNS_DIR/logs/YYYY-MM-DD/, and deletes run files older than $KB_KEEP_DAYS days (default 30).
#
#   nightly.sh                  run everything (the Mac)
#   nightly.sh --with-tests     also run each project's unit tests and checks_NN.py
#   nightly.sh --only "03 08"   run a subset (project numbers)
#   nightly.sh --here           dry run: print the planned commands, write "planned" records and apply retention
#                               (sandbox mode; default output folder ./kb-runs-here)
# Env overrides (tests use them): KB_ROOT, KB_RUNS_DIR, KB_KEEP_DAYS, PYTHON, KB_LABS ("dir:inject:nn ...").
# Exit status: 0 if every step behaved as expected, 1 otherwise.
set -u

HERE_MODE=0
WITH_TESTS=0
ONLY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --here) HERE_MODE=1 ;;
    --with-tests) WITH_TESTS=1 ;;
    --only) shift; ONLY="${1:-}" ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KB_ROOT="${KB_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"
if [ "$HERE_MODE" = 1 ]; then RUNS_DIR="${KB_RUNS_DIR:-$PWD/kb-runs-here}"; else RUNS_DIR="${KB_RUNS_DIR:-$HOME/kb-runs}"; fi
KEEP_DAYS="${KB_KEEP_DAYS:-30}"
PY="${PYTHON:-python3}"
LAB_ROOT="${KB_LAB_ROOT:-$KB_ROOT/integrated/labs/L600}"
LABS="${KB_LABS:-01-pq-replicated-messaging:leader-counter:01 02-quantum-safe-migration:bypass:02 \
03-agent-driven-simulation:few-reps:03 04-microbit-sensor-fleet:wallclock-lww:04 05-observatory-scheduler:local-as-utc:05 \
06-signed-science-data:float-format:06 07-quantum-job-service:lease-expiry:07 08-secure-agent-tools:naive-host:08}"

DAY="$(date -u +%Y-%m-%d)"
OUT="$RUNS_DIR/$DAY.jsonl"
LOGS="$RUNS_DIR/logs/$DAY"
mkdir -p "$LOGS"
export PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
STATUS=0

record() {  # record <lab> <step> <exit> <expect: zero|nonzero|planned> <seconds> <logfile>
  "$PY" - "$@" >> "$OUT" <<'PYEOF'
import json, sys, datetime, pathlib
lab, step, code, expect, secs, log = sys.argv[1:7]
last = None
p = pathlib.Path(log)
if p.is_file():
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines()[::-1]:
        line = line.strip()
        if line.startswith("{"):
            try:
                last = json.loads(line)
            except ValueError:
                last = line[:300]
            break
ok = None if expect == "planned" else ((int(code) == 0) == (expect == "zero"))
print(json.dumps({"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "lab": lab,
                  "step": step, "exit": None if expect == "planned" else int(code), "expect": expect, "ok": ok,
                  "seconds": float(secs), "last_json": last, "log": log}))
PYEOF
}

run_step() {  # run_step <lab> <step> <expect> <dir> <command...>
  local lab="$1" step="$2" expect="$3" dir="$4"; shift 4
  local log="$LOGS/$lab-$step.log"
  if [ "$HERE_MODE" = 1 ]; then
    echo "[plan] (cd $dir && $*)"
    record "$lab" "$step" 0 planned 0 "$log"
    return
  fi
  local t0 t1 code
  t0=$(date +%s)
  (cd "$dir" && "$@") > "$log" 2>&1
  code=$?
  t1=$(date +%s)
  record "$lab" "$step" "$code" "$expect" "$((t1 - t0))" "$log"
  if { [ "$expect" = zero ] && [ "$code" -ne 0 ]; } || { [ "$expect" = nonzero ] && [ "$code" -eq 0 ]; }; then
    echo "[FAIL] $lab $step (exit $code, expected $expect) - see $log"
    STATUS=1
  else
    echo "[ok]   $lab $step (exit $code)"
  fi
}

for entry in $LABS; do
  lab="${entry%%:*}"; rest="${entry#*:}"; inject="${rest%%:*}"; nn="${rest#*:}"
  if [ -n "$ONLY" ] && ! printf ' %s ' $ONLY | grep -q " $nn "; then continue; fi
  dir="$LAB_ROOT/$lab"
  run_step "$lab" scorecard zero "$dir" "$PY" run_project.py
  run_step "$lab" failure-lab nonzero "$dir" "$PY" run_project.py --inject "$inject"
  if [ "$WITH_TESTS" = 1 ]; then
    run_step "$lab" tests zero "$dir" "$PY" -m unittest discover -s tests
    run_step "$lab" checks zero "$dir" "$PY" "$KB_ROOT/integrated/research/checks_$nn.py"
    if [ -d "$dir/mac_mini/tests" ]; then
      run_step "$lab" mac-tests zero "$dir/mac_mini" "$PY" -m unittest discover -s tests
    fi
  fi
done

# Retention: keep $KEEP_DAYS days of JSONL files and log folders.
find "$RUNS_DIR" -maxdepth 1 -type f -name '*.jsonl' -mtime +"$KEEP_DAYS" -print -delete
find "$RUNS_DIR/logs" -mindepth 1 -maxdepth 1 -type d -mtime +"$KEEP_DAYS" -print -exec rm -rf {} +

echo "wrote $OUT (status $STATUS)"
exit "$STATUS"
