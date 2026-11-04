"""Model choice on the lesson-12 golden set: small vs large, a validated cascade, rules + cascade; prompt-cache
friendly ordering; batching. Cost and latency come from cost_model.py (named assumptions), tokens from the server."""
import json
import math
import os
import re
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
GOLDEN = HERE.parent.parent / "L300" / "12-eval-golden-set"
sys.path[:0] = [str(HERE), str(GOLDEN)]
import cost_model as cm  # noqa: E402
import eval_gate  # noqa: E402  (L300: golden set + checks)

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
SMALL = os.environ.get("SMALL_MODEL", "fake-small")
LARGE = os.environ.get("LARGE_MODEL", "fake-large")
PROMPT = (GOLDEN / "prompts" / "v1.txt").read_text(encoding="utf-8")  # stable instructions first, ticket last
TICKET_FIRST = "<ticket>{{ticket}}</ticket>\n" + PROMPT.replace("<ticket>{{ticket}}</ticket>", "").strip()
HARD = re.compile(r"\b(urgent|asap|immediately|down)\b", re.I)  # from the small model's eval failures, not a guess
STRATEGIES = {
    "large-only": lambda ticket: [LARGE],
    "small-only": lambda ticket: [SMALL],
    "cascade": lambda ticket: [SMALL, LARGE],  # escalate when code rejects the cheap answer
    "rules+cascade": lambda ticket: [LARGE] if HARD.search(ticket) else [SMALL, LARGE],
}


def call(model, prompt, ticket, base_url=BASE_URL):
    r = requests.post(f"{base_url}/chat/completions", timeout=60, json={
        "model": model, "messages": [{"role": "user", "content": prompt.replace("{{ticket}}", ticket)}], "temperature": 0})
    r.raise_for_status()
    body = r.json()
    return body["choices"][0]["message"]["content"], body["usage"]


def valid(output):
    """Structural validator: needs no labels, so it can run in production on every answer."""
    try:
        data = json.loads(output)
    except ValueError:
        return False
    return isinstance(data, dict) and all(data.get(k) in allowed for k, allowed in eval_gate.FIELDS.items())


def run(strategy, base_url=BASE_URL, prompt=PROMPT, cases=None):
    for model in dict.fromkeys(STRATEGIES[strategy]("") + STRATEGIES[strategy]("urgent")):
        call(model, prompt, "", base_url)  # warm-up (not counted): every run starts from the same cache state
    rows = []
    for case in cases or eval_gate.load_cases():
        cost, latency, used, prompt_tokens, cached = 0.0, 0.0, [], 0, 0
        for model in STRATEGIES[strategy](case["ticket"]):
            out, usage = call(model, prompt, case["ticket"], base_url)
            cost, latency = cost + cm.call_cost(model, usage), latency + cm.call_latency_ms(model, usage)
            prompt_tokens += usage["prompt_tokens"]
            cached += usage["prompt_tokens_details"]["cached_tokens"]
            used.append(model)
            if valid(out):
                break
        rows.append({"strategy": strategy, "id": case["id"], "pass": not eval_gate.check(case, out), "models": used,
                     "cost": round(cost, 1), "latency_ms": round(latency, 1), "prompt_tokens": prompt_tokens, "cached": cached})
    return rows


def summary(rows):
    lat = sorted(r["latency_ms"] for r in rows)
    return {"strategy": rows[0]["strategy"], "passed": sum(r["pass"] for r in rows), "cases": len(rows),
            "cost": round(sum(r["cost"] for r in rows), 1), "p50_ms": lat[len(lat) // 2],
            "p95_ms": lat[math.ceil(0.95 * len(lat)) - 1], "escalated": sum(len(r["models"]) > 1 for r in rows),
            "cache_ratio": round(sum(r["cached"] for r in rows) / sum(r["prompt_tokens"] for r in rows), 2)}


def batching(rows, model="qwen2.5:7b", parallel=(1, 4)):
    """Server-side batching estimate: memory-bound decode serves N slots per weight read (upper bound)."""
    per_request = sum(r["latency_ms"] for r in rows) / len(rows)
    return [{"parallel": p, "kv_gb": round(cm.kv_gb(model, 4096, p), 2), "need_gb": round(cm.need_gb(model, 4096, p), 2),
             "wall_s_for_batch": round(math.ceil(len(rows) / p) * per_request / 1000, 2)} for p in parallel]


if __name__ == "__main__":
    print("assumptions:", json.dumps(cm.ASSUMPTIONS))
    results = {name: run(name) for name in STRATEGIES}
    for name, rows in results.items():
        print(json.dumps(summary(rows)))
    for label, prompt in (("instructions first", PROMPT), ("ticket first", TICKET_FIRST)):
        s = summary(run("large-only", prompt=prompt))
        print(f"prompt order {label:<18}: cached {s['cache_ratio']:.0%} of prompt tokens, cost {s['cost']}, p50 {s['p50_ms']} ms")
    for b in batching(results["large-only"]):
        print("batching:", json.dumps(b))
