"""Minimal agent loop without a framework: model -> tool calls -> results -> model, until done or out of budget."""
import ast
import json
import operator
import os

import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def calculator(expression):
    """Deterministic arithmetic in code (no eval): + - * / and parentheses only."""
    def ev(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -ev(node.operand)
        raise ValueError("unsupported expression")
    return ev(ast.parse(expression, mode="eval").body)


# tool registry = allow-list: name -> (function, needs human approval?, tool schema)
REGISTRY = {"calculator": (calculator, False, {"type": "function", "function": {
    "name": "calculator", "description": "Evaluate one arithmetic expression, e.g. '17*23'.",
    "parameters": {"type": "object", "properties": {"expression": {"type": "string"}},
                   "required": ["expression"]}}})}


def execute(name, args, approve=lambda name, args: False):
    if name not in REGISTRY:
        return f"error: unknown tool {name!r}"
    fn, needs_approval, _ = REGISTRY[name]
    if needs_approval and not approve(name, args):  # approval gate: default deny anything risky
        return "error: action denied by human reviewer"
    try:
        return str(fn(**args))
    except Exception as exc:  # errors are data: report them to the model instead of crashing
        return f"error: {exc}"


def run_agent(task, max_steps=5, base_url=BASE_URL, model=MODEL, approve=lambda n, a: False):
    messages = [{"role": "system", "content": "Use the calculator tool for every arithmetic step. "
                                              "You may call tools several times before answering."},
                {"role": "user", "content": task}]
    tools = [schema for _, _, schema in REGISTRY.values()]
    for step in range(1, max_steps + 1):  # step budget: at most max_steps model calls
        resp = requests.post(f"{base_url}/chat/completions", timeout=120, json={
            "model": model, "messages": messages, "tools": tools, "temperature": 0})
        resp.raise_for_status()
        reply = resp.json()["choices"][0]["message"]
        messages.append(reply)  # state = the message list, nothing else
        calls = reply.get("tool_calls") or []
        if not calls:  # stop condition: model gave a final answer
            print(f"step {step}: final -> {reply['content']}")
            return {"answer": reply["content"], "steps": step, "stopped": "final_answer"}
        for call in calls:
            raw = call["function"].get("arguments") or "{}"
            args = raw if isinstance(raw, dict) else json.loads(raw)
            result = execute(call["function"]["name"], args, approve)
            print(f"step {step}: tool  -> {call['function']['name']}({args}) = {result}")
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    print(f"stopped: max_steps={max_steps} reached without a final answer")
    return {"answer": None, "steps": max_steps, "stopped": "max_steps"}


if __name__ == "__main__":
    task = "Use the calculator to compute 17*23 and (120-20)/4, then report both results."
    print("== budget 5 ==")
    print(run_agent(task, max_steps=5))
    print("== budget 1 ==")
    print(run_agent(task, max_steps=1))
