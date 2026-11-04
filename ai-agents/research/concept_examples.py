"""Computes every worked-example value used in content/concepts/*.md (run: python research/concept_examples.py).

Uses the stdlib, requests, and the lab fake server so the numbers match what learners see in the labs.
"""
import json
import math
import os
import sys

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
LABS = os.path.join(HERE, "..", "labs", "L100")
sys.path.insert(0, os.path.join(LABS, "01-setup"))
sys.path.insert(0, os.path.join(LABS, "04-structured-output"))
sys.path.insert(0, os.path.join(LABS, "06-minimal-agent-loop"))
from fake_model_server import start_in_thread  # noqa: E402
from structured_output import validate  # noqa: E402
from agent_loop import REGISTRY  # noqa: E402

server, base = start_in_thread()


def post(payload):
    return requests.post(f"{base}/chat/completions", json=payload, timeout=10).json()


print("== 01 setup: one request on the wire ==")
req = {"model": "fake-model", "messages": [{"role": "user", "content": "Reply with the single word: ready"}]}
body = json.dumps(req)
print("request body bytes:", len(body.encode()))
resp = post(req)
print("finish_reason:", resp["choices"][0]["finish_reason"], "| usage:", resp["usage"])

print("\n== 02 temperature: softmax(logits / T) ==")
logits = [2.0, 1.0, 0.1]
for t in (1.0, 0.5, 0.2):
    exps = [math.exp(z / t) for z in logits]
    probs = [e / sum(exps) for e in exps]
    print(f"T={t}: " + ", ".join(f"{p:.3f}" for p in probs))
history = [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello!"},
           {"role": "user", "content": "What did I just say?"}]
print("2nd-turn request carries", len(history), "messages")

print("\n== 03 chat template (ChatML-style, illustrative) ==")
msgs = [{"role": "system", "content": "You are a sentiment classifier. Reply with one word: positive, negative or neutral."},
        {"role": "user", "content": "The battery died after two days."}]
rendered = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs) + "<|im_start|>assistant\n"
print(rendered)
print("rendered characters:", len(rendered), "| messages:", len(msgs))
print("fake reply:", post({"model": "fake-model", "messages": msgs})["choices"][0]["message"]["content"])
sys.path.insert(0, os.path.join(LABS, "03-prompt-structure"))
from prompt_structure import run_all  # noqa: E402
out = run_all(base, "fake-model")
print("lab 3 words per layout:", {k: len(v.split()) for k, v in out.items()})

print("\n== 04 parsing and validating ==")
fenced = 'Sure! Here is the JSON:\n```json\n{"name": "Maria", "age": 34, "city": "Lisbon"}\n```'
try:
    json.loads(fenced)
except json.JSONDecodeError as e:
    print("json.loads(fenced) ->", f"{e.msg}: line {e.lineno} column {e.colno} (char {e.pos})")
print("validate(age '34')  ->", validate({"name": "Maria", "age": "34", "city": "Lisbon"}))
print("validate(age 34.0)  ->", validate(json.loads('{"name": "Maria", "age": 34.0, "city": "Lisbon"}')))
print("isinstance(True, int) ->", isinstance(True, int))
print("validate(age True)  ->", validate({"name": "Maria", "age": True, "city": "Lisbon"}))
print("validate(ok)        ->", validate({"name": "Maria", "age": 34, "city": "Lisbon"}))

print("\n== 05 one tool round trip (fake server) ==")
tools = [{"type": "function", "function": {"name": "get_time", "parameters": {"type": "object", "properties": {}}}}]
m = [{"role": "user", "content": "What time is it?"}]
r1 = post({"model": "fake-model", "messages": m, "tools": tools})["choices"][0]
print("finish_reason:", r1["finish_reason"])
print("assistant message:", json.dumps(r1["message"]))
call = r1["message"]["tool_calls"][0]
print("type(arguments):", type(call["function"]["arguments"]).__name__, "->", json.loads(call["function"]["arguments"]))
m += [r1["message"], {"role": "tool", "tool_call_id": call["id"], "content": "2026-10-28T06:00:00+00:00"}]
r2 = post({"model": "fake-model", "messages": m, "tools": tools})["choices"][0]
print("messages sent on call 2:", len(m), "| final:", r2["message"]["content"])
bad = m[:-1] + [{"role": "tool", "tool_call_id": "call_999", "content": "x"}]
print("wrong tool_call_id -> HTTP", requests.post(f"{base}/chat/completions", timeout=10,
      json={"model": "fake-model", "messages": bad, "tools": tools}).status_code)

print("\n== 06 agent loop: message growth per step ==")
schemas = [s for _, _, s in REGISTRY.values()]
m = [{"role": "system", "content": "Use the calculator tool."},
     {"role": "user", "content": "Compute 17*23 and (120-20)/4."}]
print("before step 1:", len(m), "messages")
for step in range(1, 6):
    reply = post({"model": "fake-model", "messages": m, "tools": schemas})["choices"][0]["message"]
    m.append(reply)
    for c in reply.get("tool_calls") or []:
        fn = REGISTRY[c["function"]["name"]][0]
        m.append({"role": "tool", "tool_call_id": c["id"], "content": str(fn(**json.loads(c["function"]["arguments"])))})
    print(f"after step {step}: {len(m)} messages, tool_calls={len(reply.get('tool_calls') or [])}")
    if not reply.get("tool_calls"):
        print("final:", reply["content"])
        break
server.shutdown()
