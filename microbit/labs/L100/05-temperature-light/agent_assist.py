"""Agent assist (lab 05): a LOCAL model explains serial telemetry; code decides.

Rule (same as the LPC1768 capstone): the LLM explains, it never decides.
  * classify() from main.py decides every state (ok / hot / dark) -> the alarm list.
  * The agent only writes a plain-language explanation of the telemetry.
  * check_explanation() verifies the text: every number must come from the
    telemetry or the thresholds, and every alarm state code found must be named.
    A failed check means the explanation is NOT shown; the code summary is.

Run (PC, no board):
  python3 agent_assist.py --fake           # built-in fake model server (no download)
  python3 agent_assist.py                  # real local model, LOCAL_MODEL_URL (default Ollama :11434)
  python3 agent_assist.py --log serial.txt # lines copied from the simulator's serial panel
Windows: use `py` instead of `python3`.
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABS = HERE.parent.parent
sys.path.insert(0, str(LABS / "sim_stub"))
sys.path.insert(0, str(LABS / "_shared"))
from labtest import load_lab, serial  # noqa: E402
from local_agent.client import chat  # noqa: E402
import microbit  # noqa: E402

LAB = load_lab(str(HERE))
LINE = re.compile(r"temp=(-?\d+),light=(\d+),state=(\w+)")
SCALE = {0, 255}  # light-level range the prompt mentions
# Fixed demo scenario (temp C, light) run through the lab's own step() on the stub.
SCENARIO = [(21, 128), (24, 120), (27, 110), (30, 35), (22, 200)]

SYSTEM = ("You explain BBC micro:bit sensor telemetry to a beginner in plain language, in 3-4 sentences. "
          "Only use numbers that appear in the telemetry. Do not give commands, do not change thresholds "
          "and do not decide alarms: the program already decided each state.")


def scenario_telemetry():
    """Serial lines produced by the real lab step() for SCENARIO (stub sensors)."""
    lines = []
    for temp_c, light in SCENARIO:
        microbit._inject_temperature(temp_c)
        microbit.display.inject_light_level(light)
        with serial() as out:
            LAB.step()
        lines.append(out.getvalue().strip())
    return lines


def parse(lines):
    """Keep only telemetry lines (the serial panel may also show other text)."""
    return [(int(t), int(l), s) for t, l, s in (LINE.search(x).groups() for x in lines if LINE.search(x))]


def decide(rows):
    """Deterministic facts and alarms. classify() is the only judge of state."""
    states = [LAB.classify(t, l) for t, l, _ in rows]
    mismatches = [i + 1 for i, (row, s) in enumerate(zip(rows, states)) if row[2] != s]
    alarms = [(i + 1, s, t, l) for i, ((t, l, _), s) in enumerate(zip(rows, states)) if s != "ok"]
    counts = {s: states.count(s) for s in ("ok", "hot", "dark")}
    allowed = ({t for t, _, _ in rows} | {l for _, l, _ in rows} | set(counts.values())
               | {len(rows), LAB.HOT_C, LAB.DARK_LEVEL} | SCALE)
    return {"n": len(rows), "counts": counts, "alarms": alarms, "mismatches": mismatches, "allowed": allowed}


def build_messages(lines):
    user = ("[[MICROBIT-TELEMETRY]] Explain these serial lines from a micro:bit "
            "(temp in degrees C, light 0-255):\n<telemetry>\n" + "\n".join(lines) + "\n</telemetry>")
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def check_explanation(text, facts):
    """Return a list of problems; empty list = explanation accepted."""
    problems = []
    # a minus sign counts only at the start of a number ("0-255" is a range, not -255)
    tokens = re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?", text)
    unknown = sorted({t for t in tokens if float(t) not in facts["allowed"]}, key=float)
    if unknown:
        problems.append(f"numbers not in telemetry: {unknown}")
    for state in ("hot", "dark"):
        if facts["counts"][state] and state not in text.lower():
            problems.append(f"does not mention '{state}' ({facts['counts'][state]} reading(s))")
    return problems


def code_summary(facts):
    alarms = ", ".join(f"#{i} {s} (temp={t}, light={l})" for i, s, t, l in facts["alarms"]) or "none"
    return f"code decision (authoritative): {facts['n']} readings, alarms: {alarms}"


def run(lines, base_url=None, model=None):
    rows = parse(lines)
    facts = decide(rows)
    out = [code_summary(facts)]
    if facts["mismatches"]:
        out.append(f"warning: logged state differs from classify() at reading(s) {facts['mismatches']}")
    try:
        text = chat(build_messages(lines), base_url=base_url, model=model, timeout=60)
    except OSError as exc:  # server not running / timeout: the code result still stands
        out.append(f"agent: unavailable ({exc.__class__.__name__}) -> code summary only")
        return out
    problems = check_explanation(text, facts)
    if problems:
        out.append("agent explanation REJECTED: " + "; ".join(problems))
    else:
        out.append("agent explanation (checked): " + text)
        out.append("check: PASS (numbers all from telemetry; alarm states named)")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--log", type=Path, help="text file with serial lines copied from the simulator")
    ap.add_argument("--fake", action="store_true", help="use the built-in deterministic fake server")
    args = ap.parse_args(argv)
    lines = (args.log.read_text(encoding="utf-8").splitlines() if args.log else scenario_telemetry())
    server, base_url = None, None
    if args.fake:
        from local_agent import fake_model_server
        server, base_url = fake_model_server.start_in_thread()
    try:
        print("telemetry:")
        for line in lines:
            print("  " + line)
        for line in run(lines, base_url=base_url, model="fake-model" if args.fake else None):
            print(line)
    finally:
        if server:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
