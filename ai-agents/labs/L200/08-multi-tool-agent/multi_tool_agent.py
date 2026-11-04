"""Agent with several tools: the model picks one, code validates its JSON arguments, errors go back to the model."""
import json
import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "L100" / "06-minimal-agent-loop"))
from agent_loop import calculator  # noqa: E402  (safe AST calculator from lesson 6)
from schema_check import validate  # noqa: E402

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
WEATHER_C = {"Paris": 18, "Oslo": 4, "Lima": 21}  # local stand-in data: no network calls
NOTES = ["The context window limits how many tokens one request can hold.",
         "Embeddings turn text into vectors for similarity search.",
         "Tool arguments must be validated in code before anything runs."]


def get_weather(city, unit="celsius"):
    c = WEATHER_C.get(city)
    if c is None:
        raise ValueError(f"no data for {city}")  # business error -> returned to the model as text
    return f"{c} C" if unit == "celsius" else f"{c * 9 / 5 + 32:.0f} F"


def search_docs(query, top_k=2):
    words = set(query.lower().split())
    ranked = sorted(NOTES, key=lambda n: -len(words & set(n.lower().rstrip(".").split())))
    return " | ".join(ranked[:top_k])


def tool(fn, description, properties, required=()):
    # JSON Schema for the arguments; additionalProperties: false rejects invented fields
    schema = {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False}
    return {"fn": fn, "schema": schema, "spec": {"type": "function", "function": {
        "name": fn.__name__, "description": description, "parameters": schema}}}


REGISTRY = {t["spec"]["function"]["name"]: t for t in [  # allow-list: these names, nothing else
    tool(calculator, "Evaluate one arithmetic expression, e.g. '17*23'.",
         {"expression": {"type": "string", "maxLength": 100}}, ["expression"]),
    tool(get_weather, "Current temperature for a city.",
         {"city": {"type": "string", "maxLength": 40}, "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}},
         ["city"]),
    tool(search_docs, "Search the local notes; returns the best matching lines.",
         {"query": {"type": "string", "minLength": 2, "maxLength": 200},
          "top_k": {"type": "integer", "minimum": 1, "maximum": 5}}, ["query"]),
]}


def execute(name, raw_args):
    if name not in REGISTRY:
        return f"error: unknown tool {name!r}; available: {sorted(REGISTRY)}"
    try:
        args = raw_args if isinstance(raw_args, dict) else json.loads(raw_args or "{}")
    except json.JSONDecodeError as exc:
        return f"error: arguments are not valid JSON ({exc.msg})"
    problems = validate(args, REGISTRY[name]["schema"])  # validate BEFORE running anything
    if problems:
        return "error: invalid arguments: " + "; ".join(problems)
    try:
        return str(REGISTRY[name]["fn"](**args))
    except Exception as exc:  # tool errors are data for the model, not crashes
        return f"error: {exc}"


def run_agent(task, max_steps=8, base_url=BASE_URL, model=MODEL):
    messages = [{"role": "system", "content": "Use the tools. Fix your arguments if a tool reports an error."},
                {"role": "user", "content": task}]
    tools = [t["spec"] for t in REGISTRY.values()]
    for step in range(1, max_steps + 1):
        reply = requests.post(f"{base_url}/chat/completions", timeout=120, json={
            "model": model, "messages": messages, "tools": tools, "temperature": 0}).json()["choices"][0]["message"]
        messages.append(reply)
        if not reply.get("tool_calls"):
            print(f"step {step}: final -> {reply['content']}")
            return {"answer": reply["content"], "steps": step, "stopped": "final_answer"}
        for call in reply["tool_calls"]:
            fn = call["function"]
            result = execute(fn["name"], fn.get("arguments"))
            print(f"step {step}: {fn['name']}({fn.get('arguments')}) -> {result}")
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    return {"answer": None, "steps": max_steps, "stopped": "max_steps"}


if __name__ == "__main__":
    print(run_agent('Compute 12*7, tell me the weather in Paris in kelvin, and search docs for "context window" top 50.'))
