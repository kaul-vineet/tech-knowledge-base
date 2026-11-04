"""Agent assist (lab 08): a LOCAL model explains a logged CSV; code computes the stats.

Rule (same as lab 05 and the LPC1768 capstone): the LLM explains, it never decides.
  * stats() computes the real numbers: rows, duration, min/max/mean/first/last, trend.
  * The agent only gets the raw CSV and writes a short plain-language summary.
  * check_explanation() verifies the text: every number it quotes must match a value
    in the CSV or a computed stat (within 0.05, i.e. rounding to 1 decimal), and a
    "rose"/"fell" claim about a column must match the computed trend.
    A failed check means the explanation is NOT shown; the code summary is.

Run (PC, no board):
  python3 agent_assist.py --fake            # built-in fake model server (no download)
  python3 agent_assist.py                   # real local model, LOCAL_MODEL_URL (default Ollama :11434)
  python3 agent_assist.py --csv readings.csv  # a file written by export_csv.py
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
sys.path.insert(0, str(HERE))
from labtest import load_lab, serial  # noqa: E402
from local_agent.client import chat  # noqa: E402
import export_csv  # noqa: E402
import microbit  # noqa: E402

# Fixed demo scenario (temp C, light) run through the lab's own setup()/step() on the stub.
SCENARIO = [(21, 120), (21, 118), (22, 110), (23, 90), (24, 60), (24, 41)]
UP = re.compile(r"\b(rose|rising|increased|went up|climbed)\b")
DOWN = re.compile(r"\b(fell|falling|decreased|went down|dropped)\b")
SYSTEM = ("You summarise a CSV log from a BBC micro:bit for a beginner in 3-4 plain sentences. "
          "Quote only numbers that are in the CSV or that you computed exactly from it, "
          "rounded to 1 decimal. Do not give advice or commands.")


def scenario_csv():
    """Serial CSV lines printed by the real lab for SCENARIO (1 s apart on the stub clock)."""
    lab = load_lab(str(HERE))
    with serial() as out:
        lab.setup()
        state = lab.new_state()
        for temp_c, light in SCENARIO:
            microbit._inject_temperature(temp_c)
            microbit.display.inject_light_level(light)
            lab.step(state)
            microbit.sleep(lab.INTERVAL_MS)
    return out.getvalue().splitlines()


def stats(header, rows):
    """Deterministic facts. These are the numbers that count."""
    times = [int(r[0]) for r in rows]
    facts = {"n": len(rows), "duration_s": (times[-1] - times[0]) / 1000, "cols": {}}
    for i, name in enumerate(header[1:], 1):
        v = [float(r[i]) for r in rows]
        trend = "up" if v[-1] > v[0] else "down" if v[-1] < v[0] else "flat"
        facts["cols"][name] = {"min": min(v), "max": max(v), "mean": sum(v) / len(v),
                               "first": v[0], "last": v[-1], "trend": trend}
    allowed = {facts["n"], facts["duration_s"]} | {float(x) for r in rows for x in r}
    for c in facts["cols"].values():
        allowed |= {c["min"], c["max"], c["mean"], c["last"] - c["first"]}
    facts["allowed"] = allowed
    return facts


def build_messages(lines):
    user = ("[[MICROBIT-CSV]] Summarise this micro:bit log (temp in degrees C, light 0-255, "
            "time_ms = milliseconds since start):\n<csv>\n" + "\n".join(lines) + "\n</csv>")
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def check_explanation(text, facts, header):
    """Return a list of problems; empty list = explanation accepted."""
    problems = []
    nums = re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?", text)
    ok = {0.0, 255.0}       # the 0-255 light scale the prompt mentions
    bad = sorted({q for q in nums if float(q) not in ok
                  and not any(abs(float(q) - a) <= 0.05 for a in facts["allowed"])}, key=float)
    if bad:
        problems.append("numbers not in the CSV or its stats: %s" % bad)
    for sentence in re.split(r"(?<=[.;])\s+", text.lower()):
        for name, col in facts["cols"].items():
            if name not in sentence:
                continue
            if UP.search(sentence) and col["trend"] != "up":
                problems.append("says %s rose, but it went %s" % (name, col["trend"]))
            if DOWN.search(sentence) and col["trend"] != "down":
                problems.append("says %s fell, but it went %s" % (name, col["trend"]))
    return problems


def code_summary(facts):
    parts = ["%s %g..%g mean %.1f (%s)" % (k, c["min"], c["max"], c["mean"], c["trend"])
             for k, c in facts["cols"].items()]
    return "code stats (authoritative): %d rows over %g s; %s" % (
        facts["n"], facts["duration_s"], "; ".join(parts))


def run(lines, base_url=None, model=None):
    header, rows, _ = export_csv.extract(lines)
    facts = stats(header, rows)
    clean = [",".join(header)] + [",".join(r) for r in rows]
    out = [code_summary(facts)]
    try:
        text = chat(build_messages(clean), base_url=base_url, model=model, timeout=60)
    except OSError as exc:      # server not running / timeout: the code result still stands
        out.append("agent: unavailable (%s) -> code summary only" % exc.__class__.__name__)
        return out
    problems = check_explanation(text, facts, header)
    if problems:
        out.append("agent explanation REJECTED: " + "; ".join(problems))
    else:
        out.append("agent explanation (checked): " + text)
        out.append("check: PASS (every number matches the CSV or a computed stat; trends match)")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", type=Path, help="CSV file from export_csv.py (or a serial transcript)")
    ap.add_argument("--fake", action="store_true", help="use the built-in deterministic fake server")
    args = ap.parse_args(argv)
    lines = args.csv.read_text(encoding="utf-8").splitlines() if args.csv else scenario_csv()
    server, base_url = None, None
    if args.fake:
        from local_agent import fake_model_server
        server, base_url = fake_model_server.start_in_thread()
    try:
        print("csv:")
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
