"""pending-ci / manual: measure the numbers cost_model.py assumes, on YOUR Mac mini or Windows PC.

Uses Ollama's native /api/chat (timings in nanoseconds: prompt_eval_count, prompt_eval_cached_count,
prompt_eval_duration, eval_count, eval_duration). Same long prefix twice -> the second call reads it from the cache.
Run: python real_model_probe.py qwen2.5:1.5b qwen2.5:7b   (Ollama on http://localhost:11434)
"""
import json
import os
import sys

import requests

HOST = os.environ.get("OLLAMA_HOST_URL", "http://localhost:11434")
PREFIX = "You triage customer support tickets. " * 40


def probe(model):
    out = []
    for ticket in ("I was charged twice for my March invoice", "Mobile app crashes on start since the update"):
        r = requests.post(f"{HOST}/api/chat", timeout=600, json={
            "model": model, "stream": False, "options": {"temperature": 0, "num_predict": 64},
            "messages": [{"role": "user", "content": f"{PREFIX}\n<ticket>{ticket}</ticket>"}]}).json()
        out.append({"model": model, "prompt_tokens": r.get("prompt_eval_count"), "cached": r.get("prompt_eval_cached_count"),
                    "prefill_tok_s": round(r["prompt_eval_count"] / (r["prompt_eval_duration"] / 1e9), 1)
                    if r.get("prompt_eval_duration") else None,
                    "decode_tok_s": round(r["eval_count"] / (r["eval_duration"] / 1e9), 1), "load_ms": r["load_duration"] // 10**6})
    return out


if __name__ == "__main__":
    for m in sys.argv[1:] or ["qwen2.5:1.5b"]:
        for row in probe(m):
            print(json.dumps(row))
