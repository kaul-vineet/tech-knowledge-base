"""Computes every worked-example value used in content/concepts/L400/*.md (run: python research/L400_concept_examples.py).

Uses the L400 lab code and fake_server_l400.py (fresh server per measurement, so prefix-cache state never leaks
between measurements). Only deterministic values are printed: counts, tokens, model-based cost/latency estimates.
"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
L400 = HERE.parent / "labs" / "L400"
sys.path[:0] = [str(L400), str(HERE.parent / "labs" / "L300" / "15-safe-tool-execution")] + [str(L400 / d) for d in (
    "17-multi-agent-patterns", "18-durable-workflows", "19-cost-latency-model-choice", "20-deterministic-core",
    "21-governance-evals")]
import fake_server_l400 as fake  # noqa: E402


def server(**kw):
    return fake.start_in_thread(**kw)


def stop(s):
    s.shutdown()
    s.server_close()


print("== 17 multi-agent patterns (context 1000) ==")
import patterns  # noqa: E402
sys.path.insert(0, str(L400 / "17-multi-agent-patterns" / "solution"))
import trim_results  # noqa: E402  (the solution's trim)
s, url = server(context_limit=1000)
for name in patterns.PATTERNS:
    print(json.dumps(patterns.summary(patterns.evaluate(name, url, "fake-model"))))
print("estimate t07 / t01:", patterns.estimate(patterns.ow.TASKS[6][1]), patterns.estimate(patterns.ow.TASKS[0][1]),
      "threshold", 0.9 * patterns.CONTEXT_LIMIT)
print("single+trim:", json.dumps(patterns.summary(patterns.evaluate(
    "single+trim", url, "fake-model", fn=lambda run, task: patterns.single(run, task, trim=trim_results.trim)))))
stop(s)

print("== 18 durable workflows (12 crash points) ==")
import harness  # noqa: E402
s, url = server()
for variant in ("naive", "checkpoint-no-key", "durable"):
    rows = harness.sweep(variant, url, server=s)
    print(variant, "duplicate-refund points", sum(r["refunds"] > 1 for r in rows), "re-asked model",
          sum((r["model_calls"] or 0) > 1 for r in rows), [r["crash_at"] for r in rows if r["refunds"] > 1])
stop(s)

print("== 19 cost, latency, model choice ==")
import cost_model as cm  # noqa: E402
import route_cost as rc  # noqa: E402
for name in rc.STRATEGIES:
    s, url = server()
    print(json.dumps(rc.summary(rc.run(name, base_url=url))))
    stop(s)
for label, prompt in (("instructions first", rc.PROMPT), ("ticket first", rc.TICKET_FIRST)):
    s, url = server()
    print(label, "cache ratio", rc.summary(rc.run("large-only", base_url=url, prompt=prompt))["cache_ratio"])
    stop(s)
for m in cm.MODELS:
    print(m, "KV kB/token", round(cm.kv_gb(m, 1) * 1e6, 1), "need GB @4k", round(cm.need_gb(m), 2),
          "decode tok/s est M6 16GB", round(cm.decode_tps(m, 153)), "M5 Pro", round(cm.decode_tps(m, 307)))
print("14b @32k x4 need GB", round(cm.need_gb("qwen2.5:14b", 32768, 4), 2))

print("== 20 deterministic core ==")
import edge  # noqa: E402
s, url = server()
for name in edge.OPTIONS:
    rows = edge.evaluate(name, url, "fake-model")
    print(name, "wrong", sum(not r["ok"] for r in rows), [(r["id"], r["action"], r["amount"]) for r in rows if not r["ok"]])
stop(s)

print("== 21 governance ==")
import governance as g  # noqa: E402
s, url = server()
tickets = [c["ticket"] for c in g.eval_gate.load_cases()]
lock = json.loads((L400 / "21-governance-evals" / "models.lock.json").read_text(encoding="utf-8"))
print("pin check:", g.pin_check(url, lock) or "OK")
report = g.evaluate_candidate(url, "fake-model", "fake-model:v2", tickets * 10)
print(json.dumps(report), g.decide_upgrade(report))
shipping = [c["ticket"] for c in g.eval_gate.load_cases() if c["expect"]["category"] == "shipping"]
print("category drift same / surge:", g.category_drift(url, "fake-model", tickets * 10, tickets * 5),
      g.category_drift(url, "fake-model", tickets * 10, tickets * 5 + shipping * 10))
s.retag("fake-model:latest", "fake-model:v2")
print("pin check after re-tag:", g.pin_check(url, lock))
stop(s)
with tempfile.TemporaryDirectory(dir=HERE) as d:
    log = g.AuditLog(Path(d) / "a.db")
    for day in range(4):
        log.append(day, "agent", "triage", f"text {day}")
    ok = log.verify()
    log.db.execute("UPDATE audit SET actor = 'bob' WHERE seq = 3")
    print("audit verify before/after edit:", ok, log.verify())
    log.db.close()
