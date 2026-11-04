"""Agent assist (lab 15): a LOCAL model explains gateway telemetry anomalies; CODE decides alarms.

Rule (same as labs 05 and 08): the LLM explains, it never decides.
  * decide_alarms() is the only place alarms come from (fixed thresholds below).
  * The agent gets the metrics and the alarms the code raised and explains them.
  * check_explanation() verifies the text: every number must come from the metrics,
    the alarms or the damaged-frame percentage (1 decimal); every alarm name it uses
    must be one the code raised; and it must name every raised alarm.
    A failed check means the explanation is NOT shown; the code's alarms are.

Run (PC, no board):
  python3 agent_assist.py --fake     # built-in fake model server (no download)
  python3 agent_assist.py            # real local model, LOCAL_MODEL_URL (default Ollama :11434)
Windows: use `py` instead of `python3`.
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "_shared"))
sys.path.insert(0, str(HERE))
from local_agent.client import chat  # noqa: E402
import serial_link  # noqa: E402
import solution  # noqa: E402

LINK_NOISY_PCT = 2.0          # damaged frames above this share -> LINK_NOISY
TEMP_HIGH_C = 30              # any accepted reading at or above -> TEMP_HIGH
ALARM_NAMES = ("LINK_NOISY", "SEQ_GAP", "TEMP_HIGH")
SYSTEM = ("You explain telemetry from a micro:bit serial gateway to an engineer in 3-4 plain sentences. "
          "Quote only numbers given to you. Name only the alarms listed as raised. "
          "Do not invent causes you cannot see, and do not give commands.")


def gateway_run():
    """Run the hardened gateway on the seeded noisy demo link; return metrics + readings."""
    pub = solution.JsonLinesPublisher(io.StringIO())
    chunks, _ = serial_link.noisy(serial_link.device_bytes(), **serial_link.FAULTS)
    metrics = solution.run(chunks, pub)
    readings = [m["payload"] for m in pub.sent if m["topic"].endswith("/telemetry")]
    return metrics, readings


def decide_alarms(metrics, readings):
    """Deterministic alarm rules. These decide; the agent never does."""
    damaged = metrics["bad_crc"] + metrics["bad_len"]
    pct = round(100.0 * damaged / (metrics["frames_ok"] + damaged), 1)
    seqs = sorted(r["seq"] for r in readings)
    missing = (seqs[-1] - seqs[0] + 1 - len(seqs)) if seqs else 0
    alarms = []
    if pct > LINK_NOISY_PCT:
        alarms.append({"name": "LINK_NOISY", "value": pct, "limit": LINK_NOISY_PCT})
    if missing:
        alarms.append({"name": "SEQ_GAP", "value": missing})
    hot = max((r["temp"] for r in readings), default=None)
    if hot is not None and hot >= TEMP_HIGH_C:
        alarms.append({"name": "TEMP_HIGH", "value": hot, "limit": TEMP_HIGH_C})
    return alarms, pct, missing


def build_messages(metrics, alarms, missing):
    data = json.dumps({"metrics": metrics, "alarms": alarms, "missing": missing}, sort_keys=True)
    user = "[[MICROBIT-GATEWAY]] Explain these gateway counters and alarms:\n<gateway>" + data + "</gateway>"
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def check_explanation(text, metrics, alarms, pct, missing):
    problems = []
    allowed = set(float(v) for v in metrics.values()) | {pct, float(missing)}
    allowed |= set(float(a.get(k)) for a in alarms for k in ("value", "limit") if k in a)
    allowed.add(float(metrics["frames_ok"] + metrics["bad_crc"] + metrics["bad_len"]))
    nums = re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?", text)
    bad = sorted({n for n in nums if float(n) not in allowed}, key=float)
    if bad:
        problems.append("numbers not in the metrics: %s" % bad)
    raised = set(a["name"] for a in alarms)
    named = set(n for n in ALARM_NAMES if n in text)
    if named - raised:
        problems.append("names alarms the code did not raise: %s" % sorted(named - raised))
    if raised - named:
        problems.append("does not mention raised alarms: %s" % sorted(raised - named))
    return problems


def run(base_url=None, model=None):
    metrics, readings = gateway_run()
    alarms, pct, missing = decide_alarms(metrics, readings)
    out = ["metrics: " + json.dumps(metrics, sort_keys=True),
           "alarms (decided by code): " + (", ".join("%s=%s" % (a["name"], a["value"]) for a in alarms) or "none")]
    try:
        text = chat(build_messages(metrics, alarms, missing), base_url=base_url, model=model, timeout=60)
    except OSError as exc:
        out.append("agent: unavailable (%s) -> alarms above stand" % exc.__class__.__name__)
        return out
    problems = check_explanation(text, metrics, alarms, pct, missing)
    if problems:
        out.append("agent explanation REJECTED: " + "; ".join(problems))
    else:
        out.append("agent explanation (checked): " + text)
        out.append("check: PASS (numbers from the metrics; alarm names match the code's alarms)")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fake", action="store_true", help="use the built-in deterministic fake server")
    args = ap.parse_args(argv)
    server, base_url = None, None
    if args.fake:
        from local_agent import fake_model_server
        server, base_url = fake_model_server.start_in_thread()
    try:
        for line in run(base_url=base_url, model="fake-model" if args.fake else None):
            print(line)
    finally:
        if server:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
