"""failureLab: the same 10 questions against a seeded flaky server (30% 503, 20% +2.0 s), naive vs hardened.

Run: python compare.py   (starts its own fake servers on 127.0.0.1; writes reliability.jsonl)
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
from fake_server_l300 import start_in_thread  # noqa: E402
from naive_agent import naive_answer  # noqa: E402
from resilient_agent import CANNED, Budget, Client, answer  # noqa: E402

FAULTS = {"fail_rate": 0.3, "slow_rate": 0.2, "slow_s": 2.0, "seed": 7}
QUESTIONS = ["What is 12*7?", "What is 9+10?", "What is 81/9?", "What is 12*7?", "What is 6*6?",
             "Add up 1+1, 2+2, 3+3, 4+4, 5+5, 6+6, 7+7 and 8+8.", "What is 100-58?", "What is 7*8?",
             "What is 2+40?", "What is 3*14?"]  # q4 repeats q1 (cache); q6 needs 9 model calls (budget)


def run(mode, retries=2, fallback=True):
    flaky, flaky_url = start_in_thread(**FAULTS)
    healthy, healthy_url = start_in_thread()  # the fallback: a smaller model on another endpoint
    rows, counter, events = [], {"tokens": 0}, []
    endpoints = [(flaky_url, "fake-model")] + ([(healthy_url, "fake-small")] if fallback else [])
    client = Client(endpoints, retries=retries, events=events)
    try:
        for q in QUESTIONS:
            start, before = time.perf_counter(), dict(counter)
            if mode == "naive":
                a = naive_answer(q, flaky_url, "fake-model", counter)
            else:
                budget = Budget()
                a = answer(q, client, budget=budget)
                counter["tokens"] += budget.tokens
            rows.append({"q": q[:22], "s": round(time.perf_counter() - start, 2), "tokens": counter["tokens"] - before["tokens"],
                         "canned": a == CANNED})
    finally:
        for s in (flaky, healthy):
            s.shutdown()
            s.server_close()
    calls = flaky.stats["requests"] + healthy.stats["requests"]
    return {"mode": mode, "wall_s": round(sum(r["s"] for r in rows), 1), "max_s": max(r["s"] for r in rows),
            "http_calls": calls, "tokens": counter["tokens"], "canned": sum(r["canned"] for r in rows),
            "faults": dict(flaky.stats), "rows": rows, "events": events}


if __name__ == "__main__":
    for mode in ("naive", "hardened"):
        res = run(mode)
        print(f"{mode:<9} wall {res['wall_s']:>4} s | slowest question {res['max_s']} s | HTTP calls {res['http_calls']} | "
              f"tokens {res['tokens']} | canned {res['canned']} | flaky server saw {res['faults']}")
        if mode == "hardened":
            Path("reliability.jsonl").write_text("".join(json.dumps(e) + "\n" for e in res["events"]), encoding="utf-8")
            kinds = {}
            for e in res["events"]:
                kinds[e["event"]] = kinds.get(e["event"], 0) + 1
            print("hardened events:", kinds)
