"""One tool, one round trip: model asks for get_time -> we run it locally -> model answers."""
import json
import os
from datetime import datetime, timezone

import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")

TOOLS = [{  # tool declaration: name + description + JSON-schema parameters
    "type": "function",
    "function": {
        "name": "get_time",
        "description": "Return the current UTC date and time in ISO 8601 format.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}]


def get_time():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


LOCAL_FUNCTIONS = {"get_time": get_time}  # allow-list: only these names can ever run


def chat(messages, base_url=BASE_URL, model=MODEL):
    resp = requests.post(f"{base_url}/chat/completions", timeout=120,
                         json={"model": model, "messages": messages, "tools": TOOLS, "temperature": 0})
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]


def run_tool(call):
    fn = LOCAL_FUNCTIONS.get(call["function"]["name"])
    if fn is None:
        return f"error: unknown tool {call['function']['name']!r}"
    raw = call["function"].get("arguments") or "{}"
    args = raw if isinstance(raw, dict) else json.loads(raw)  # /v1 sends a JSON string; some native APIs an object
    return str(fn(**args))


def ask(question, **kw):
    messages = [{"role": "user", "content": question}]
    reply = chat(messages, **kw)
    calls = reply.get("tool_calls") or []
    if not calls:                      # model answered directly
        return reply["content"]
    messages.append(reply)             # round trip: the assistant turn with tool_calls goes first
    for call in calls:
        print(f"model requested: {call['function']['name']}({call['function']['arguments']})")
        result = run_tool(call)
        print(f"tool result    : {result}")
        messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})  # id links result to call
    return chat(messages, **kw)["content"]  # second call: model sees the tool result


if __name__ == "__main__":
    print("final answer   :", ask("What time is it right now (UTC)?"))
