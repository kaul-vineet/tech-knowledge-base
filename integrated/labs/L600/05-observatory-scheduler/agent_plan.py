"""Agent at the edge: a local model PROPOSES a plan and EXPLAINS trade-offs; validator.py and this file DECIDE.

Fake-model rules (registered at runtime in kb/shared/local_agent/fake_model_server.EXTRA_RULES; the shared file is
not edited): '[[OBS-PLAN]]' -> a naive plan (priority order, back to back from dusk, windows ignored, last time
written as local wall clock without a zone); '[[OBS-EXPLAIN]]' -> 3 sentences built only from the <facts> numbers.
Prompts avoid the word 'j-s-o-n' (the fake's rule 6 would answer with a person record instead).
"""
import importlib.util
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import _kb
import sky
import validator
import weather

HERE = Path(__file__).resolve().parent
_pt = HERE / ("plan_times.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/plan_times.py")
_spec = importlib.util.spec_from_file_location("obs_plan_times", _pt)
plan_times = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(plan_times)
NUM = re.compile(r"-?\d+(?:\.\d+)?")


def _facts(text):
    m = re.search(r"<facts>(.*?)</facts>", text, re.S)
    return dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1) if m else "", re.M))


def _fake_plan(text):
    f = _facts(text)
    reqs = sorted((ln.split() for ln in f["requests"].split(";")), key=lambda r: (-int(r[1]), r[0]))
    t, lines = datetime.fromisoformat(f["dusk_utc"].replace("Z", "+00:00")), []
    for k, (name, _, exp_min) in enumerate(reqs[:5]):
        stamp = t.strftime("%Y-%m-%dT%H:%M:%SZ") if k < 4 else (t + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%dT%H:%M")
        lines.append(f"PLAN {name} {stamp}")
        t += timedelta(minutes=int(exp_min))
    return "\n".join(lines + ["WHY Highest priorities first, back to back from dusk, so nothing important waits."])


def _fake_explain(text):
    f = _facts(text)
    return (f"The optimised plan promises an expected value of {f['local_value']} against {f['greedy_value']} for "
            f"greedy, {f['margin_pct']} percent more. It starts with {f['first_target']} because it sets early. "
            f"{f['long_target']} is the riskiest promise: its block completes with probability {f['long_p']}.")


for marker, fn in (("[[OBS-PLAN]]", _fake_plan), ("[[OBS-EXPLAIN]]", _fake_explain)):
    if marker not in [m for m, _ in _kb.fake_model_server.EXTRA_RULES]:
        _kb.fake_model_server.EXTRA_RULES.append((marker, fn))


def plan_prompt(reqs, slots):
    reqs_txt = "; ".join(f"{r.name} {r.priority} {r.exp_min}" for r in reqs)
    return (f"[[OBS-PLAN]] Propose tonight's observing plan, one line per block: PLAN <target> <start, ISO 8601 UTC>.\n"
            f"<facts>\nsite: {sky.SITE['name']}\ndusk_utc: {slots[0].utc.iso()}\ndawn_utc: {slots[-1].utc.iso()}\n"
            f"requests: {reqs_txt}\nrules: airmass <= {sky.MAX_AIRMASS}; Moon >= {sky.MIN_MOON_SEP_DEG} deg\n</facts>")


def parse_plan(text):
    """Model text -> (rows, problems). Unparseable lines are problems, not guesses."""
    rows, problems = [], []
    for name, stamp in re.findall(r"^PLAN\s+(\S+)\s+(\S+)\s*$", text, re.M):
        try:
            rows.append({"target": name, "start": plan_times.parse_plan_time(stamp)})
        except ValueError as e:
            problems.append(f"{name}: {e}")
    return rows, problems


def decide(text, best_blocks, reqs, slots):
    """Code decides: adopt the agent plan only if it parses, validates and promises at least the optimiser's value."""
    rows, problems = parse_plan(text)
    problems += validator.validate(rows, reqs, slots) if rows else ["no PLAN lines"]
    if problems:
        return {"adopted": "optimiser", "agent_ok": False, "reasons": problems}
    idx = {r.name: i for i, r in enumerate(reqs)}
    first = slots[0].utc.dt
    blocks = [(int((r["start"].dt - first).total_seconds() // 600), reqs[idx[r["target"]]].exp_min // sky.STEP_MIN,
               reqs[idx[r["target"]]].priority) for r in rows]
    best = weather.expected([(s, n, reqs[i].priority) for s, n, i in best_blocks])
    agent_value = weather.expected(blocks)
    adopted = "agent" if agent_value >= best - 1e-12 else "optimiser"
    return {"adopted": adopted, "agent_ok": True, "agent_value": round(agent_value, 3), "reasons": []}


def explain_facts(r):
    long_i = max(r["local"], key=lambda b: b[1])
    return {"local_value": f"{r['local_value']:.3f}", "greedy_value": f"{r['greedy_value']:.3f}",
            "margin_pct": f"{100 * (r['local_value'] / r['greedy_value'] - 1):.1f}",
            "first_target": r["reqs"][r["local"][0][2]].name, "long_target": r["reqs"][long_i[2]].name,
            "long_p": f"{weather.p_complete(long_i[1]):.3f}"}


def explain_prompt(facts):
    body = "\n".join(f"{k}: {v}" for k, v in facts.items())
    return f"[[OBS-EXPLAIN]] Explain the trade-offs of tonight's plan in 3 plain sentences.\n<facts>\n{body}\n</facts>"


def checked_explanation(text, facts, reqs):
    """Publish only if every number is a fact and every capitalised target-like word is a requested target."""
    allowed = {float(n) for v in facts.values() for n in NUM.findall(v)}
    numbers = {float(n) for n in NUM.findall(text)}
    names = {r.name for r in reqs}
    stars = set(re.findall(r"\b(Vega|Altair|Deneb|Fomalhaut|Capella|Aldebaran|Betelgeuse|Sirius|Polaris|Canopus|"
                           r"Arcturus|Rigel|Procyon|Antares|Spica)\b", text))
    if not text or len(text) > 600 or not numbers <= allowed or not stars <= names:
        return False, (f"Optimised plan: expected value {facts['local_value']} vs greedy {facts['greedy_value']}; "
                       f"riskiest block {facts['long_target']} p={facts['long_p']}.")
    return True, text


def ask(prompt, base_url):
    return _kb.agent_client.chat([{"role": "user", "content": prompt}], base_url=base_url, timeout=60)
