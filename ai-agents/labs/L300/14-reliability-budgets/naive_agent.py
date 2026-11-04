"""The 'before' loop: no timeout, retry on ANY error immediately, no budgets, no cache (works on the happy path)."""
import json

import requests

from resilient_agent import TOOLS


def naive_answer(question, base_url, model, counter):
    messages = [{"role": "user", "content": question}]
    while True:  # no step budget
        try:
            body = requests.post(f"{base_url}/chat/completions",  # no timeout: waits as long as the server does
                                 json={"model": model, "messages": messages, "tools": TOOLS, "temperature": 0}).json()
            reply = body["choices"][0]["message"]
        except (requests.RequestException, KeyError, ValueError):
            continue  # 503 body has no "choices": retry at once, forever
        counter["tokens"] += body["usage"]["total_tokens"]
        messages.append(reply)
        if not reply.get("tool_calls"):
            return reply["content"]
        for call in reply["tool_calls"]:
            expr = json.loads(call["function"]["arguments"])["expression"]
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": str(eval(expr, {"__builtins__": {}}))})
