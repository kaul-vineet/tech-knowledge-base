"""Computes every worked-example value used in content/concepts/L300/*.md (run: python research/L300_concept_examples.py).

Uses the L300 lab code and the L300 fake server, so the numbers match what learners see. Only deterministic values
are printed (counts, tokens, seeded delays); wall-clock timings vary by machine and are left out.
"""
import hashlib
import json
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
L300 = HERE.parent / "labs" / "L300"
sys.path[:0] = [str(L300)] + [str(L300 / d) for d in ("12-eval-golden-set", "13-tracing-observability",
                                                     "14-reliability-budgets", "15-safe-tool-execution", "16-red-team-injection")]
from fake_server_l300 import start_in_thread  # noqa: E402
import eval_gate  # noqa: E402
import traced_agent  # noqa: E402
import compare  # noqa: E402
import payments_service  # noqa: E402
import safe_tools  # noqa: E402
from naive_refund import send_refund_naive  # noqa: E402
import run_suite  # noqa: E402
import agent_assist  # noqa: E402

server, base = start_in_thread()
kw = {"base_url": base, "model": "fake-model"}

print("== 12 golden set ==")
baseline = json.loads((L300 / "12-eval-golden-set" / "baseline.json").read_text(encoding="utf-8"))
for v in ("v1", "v2"):
    rep = eval_gate.evaluate(L300 / "12-eval-golden-set" / "prompts" / f"{v}.txt", **kw)
    print(v, f"{rep['passed']}/{rep['total']}", rep["pass_rate"], eval_gate.gate(rep, baseline))
spot = eval_gate.evaluate(L300 / "12-eval-golden-set" / "prompts" / "v2.txt", eval_gate.load_cases()[:3], **kw)
print("v2 spot check of 3 cases:", f"{spot['passed']}/3")

print("== 13 tracing ==")
traced_agent._INDEX.clear()
with tempfile.TemporaryDirectory() as d:
    path = Path(d) / "t.jsonl"
    traced_agent.run('What is the weather in Paris? Also search docs for "rate limits" and compute 17*23.',
                     traced_agent.Tracer(path), **kw)
    rows = traced_agent.summarize(path)
    print("spans:", sum(r["count"] for r in rows), "| chat calls:", next(r["count"] for r in rows if r["name"].startswith("chat")),
          "| tokens:", sum(r["tokens"] for r in rows), "| slowest:", traced_agent.diagnose(path),
          "| search_docs ms (rounded to 100):", round(next(r["ms"] for r in rows if r["name"] == "execute_tool search_docs"), -2))

print("== 14 reliability ==")
rng = random.Random(7)
print("backoff schedule (seed 7, base 0.05, cap 0.4):",
      [round(min(0.4, 0.05 * 2 ** a) * rng.uniform(0.5, 1.0), 3) for a in range(4)])
for mode in ("naive", "hardened"):
    res = compare.run(mode)
    kinds = {}
    for e in res["events"]:
        kinds[e["event"]] = kinds.get(e["event"], 0) + 1
    print(mode, "| tokens", res["tokens"], "| canned", res["canned"], "| faults seen", res["faults"], "| events", kinds)

print("== 15 safe tools ==")
pay, url = payments_service.start_in_thread(slow_first=True)
send_refund_naive(url, "A-1001", 25.0)
print("naive refunds:", len(safe_tools.requests.get(f"{url}/refunds", timeout=5).json()))
pay.shutdown()
pay, url = payments_service.start_in_thread(slow_first=True)
with tempfile.TemporaryDirectory() as d:
    gate = safe_tools.ToolGate(Path(d) / "a.db", url)
    safe_tools.run_agent("Refund order A-1001 for 25.00, it arrived broken.", gate, "run-1", **kw)
    gate.decide(1, "alice", True)
    res = gate.execute_approved()
    print("keyed refunds:", len(safe_tools.requests.get(f"{url}/refunds", timeout=5).json()), "| replayed:", res[0]["replayed"],
          "| key:", hashlib.sha256(b"run-1:call_1:send_refund").hexdigest()[:32])
    print("audit:", [e for (e,) in gate.db.execute("SELECT event FROM audit ORDER BY id")])
    gate.db.close()
pay.shutdown()

print("== 16 red team ==")
results = run_suite.run_all(**kw)
for mode in ("unprotected", "protected"):
    rs = [r for r in results if r["mode"] == mode]
    print(mode, f"{sum(r['safe'] for r in rs)}/{len(rs)} safe")
rows = agent_assist.assess(agent_assist.validate(agent_assist.propose(**kw)), **kw)
print("variants: regex caught", sum(r["regex_screen_caught"] for r in rows), "of", len(rows),
      "| policy blocked", sum(r["protected_safe"] for r in rows), "of", len(rows))
server.shutdown()
