"""Deterministic core, LLM at the edge: three ways to let a model near a refund decision, measured on 12 cases.

  llm_decides    - the model reads the policy and decides; code executes what it says
  llm_validated  - the model decides; code checks schema, allow-list and amount, refuses (escalates) if invalid
  code_decides   - policy.decide() decides from system-of-record facts; the model only PROPOSES claims (which can
                   only escalate) and EXPLAINS (the explanation is checked against the decision)
"""
import json
import os
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent.parent / "L200" / "08-multi-tool-agent")]
import explain_check  # noqa: E402  (build task: shipped unfixed)
import policy  # noqa: E402
from schema_check import validate  # noqa: E402  (lesson 8 JSON Schema subset)

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
POLICY_TEXT = "Refund policy: deny if outside 30 days or more than paid; escalate 3+ refunds or over 50.00; else approve_auto."
DECISION_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["action", "amount"], "properties": {
    "action": {"type": "string", "enum": list(policy.ALLOWED_ACTIONS)}, "amount": {"type": "number", "minimum": 0},
    "rule": {"type": "string", "maxLength": 200}}}
PROPOSAL_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["claims", "summary"], "properties": {
    "claims": {"type": "object", "additionalProperties": False, "required": ["damaged", "threat"],
               "properties": {"damaged": {"type": "boolean"}, "threat": {"type": "boolean"}}},
    "summary": {"type": "string", "maxLength": 200},
    "suggested_action": {"type": "string", "enum": list(policy.ALLOWED_ACTIONS)}}}


def ask(prompt, base_url=BASE_URL, model=MODEL):
    """One model call. Any failure returns None: every caller has a refusal path for 'no usable answer'."""
    try:
        r = requests.post(f"{base_url}/chat/completions", timeout=30, json={
            "model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except (requests.RequestException, KeyError, ValueError):
        return None


def parse(text, schema):
    """(object, problems): untrusted text -> JSON -> schema (types, enums, lengths, no extra keys)."""
    try:
        obj = json.loads(text or "")
    except ValueError:
        return None, ["not JSON"]
    problems = validate(obj, schema)
    return (None, problems) if problems else (obj, [])


def facts_block(case):
    lines = "\n".join(f"{k}: {v}" for k, v in case["facts"].items())
    return f"{lines}\n<customer>{case['message']}</customer>"  # customer text is data, delimited


def llm_decides(case, ask=ask):
    out = json.loads(ask(f"{POLICY_TEXT}\nDecide as JSON.\n<decide>{facts_block(case)}</decide>"))
    return {"action": out["action"], "amount": out["amount"], "rule": "model"}


def llm_validated(case, ask=ask):
    out, problems = parse(ask(f"{POLICY_TEXT}\nDecide as JSON.\n<decide>{facts_block(case)}</decide>"), DECISION_SCHEMA)
    if problems or out["amount"] > case["facts"]["paid"]:  # refusal path: an invalid answer goes to a person
        return {"action": "escalate", "amount": 0.0, "rule": f"refused model output: {problems or 'amount over paid'}"}
    return {"action": out["action"], "amount": out["amount"], "rule": "model (validated)"}


def code_decides(case, ask=ask):
    decision = policy.decide(case["facts"])  # THE decision: code + facts; nothing the model says is an input
    proposal, problems = parse(ask(f"Extract claims as JSON.\n<propose>{facts_block(case)}</propose>"), PROPOSAL_SCHEMA)
    final = policy.combine(decision, proposal["claims"] if proposal else None)  # claims can only escalate
    text = ask(f"Explain this decision to the customer.\n<explain>{json.dumps(final)}\n{facts_block(case)}</explain>")
    return {**final, "proposal_problems": problems, "explanation": explain_check.checked(text, final)}


OPTIONS = {"llm_decides": llm_decides, "llm_validated": llm_validated, "code_decides": code_decides}


def evaluate(option, base_url=BASE_URL, model=MODEL, cases=CASES):
    call = lambda prompt: ask(prompt, base_url, model)
    rows = []
    for case in cases:
        out = OPTIONS[option](case, ask=call)
        rows.append({"option": option, "id": case["id"], "action": out["action"], "amount": out["amount"],
                     "expect": case["expect"], "ok": out["action"] == case["expect"], "explanation": out.get("explanation")})
    return rows


if __name__ == "__main__":
    for name in OPTIONS:
        rows = evaluate(name)
        print(f"{name:<14} wrong {sum(not r['ok'] for r in rows)}/12: {[(r['id'], r['action']) for r in rows if not r['ok']]}")
    for r in evaluate("code_decides"):
        print(json.dumps({k: r[k] for k in ("id", "action", "amount", "explanation")}))
