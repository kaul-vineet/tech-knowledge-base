"""Check that a chat-completions server is up: list models, then send one chat request.

Real model : LOCAL_MODEL_URL=http://localhost:11434/v1 LOCAL_MODEL=qwen2.5:1.5b python check_endpoint.py
Fake model : LOCAL_MODEL_URL=http://127.0.0.1:8765/v1  LOCAL_MODEL=fake-model   python check_endpoint.py
The older names BASE_URL / MODEL still work as a fallback (LOCAL_MODEL_URL / LOCAL_MODEL win if both are set).
"""
import os
import sys

import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")  # one wire format, many servers: only the URL + model name change


def check(base_url=BASE_URL, model=MODEL):
    models = requests.get(f"{base_url}/models", timeout=10)  # health check: what can this server serve?
    models.raise_for_status()
    ids = [m["id"] for m in models.json()["data"]]
    print("models served:", ids)
    if model not in ids:
        print(f"WARNING: {model!r} not listed - pull it first (ollama pull {model})")
    resp = requests.post(f"{base_url}/chat/completions", timeout=120, json={
        "model": model,
        "messages": [{"role": "user", "content": "Reply with the single word: ready"}],
        "temperature": 0,
    })
    resp.raise_for_status()
    reply = resp.json()["choices"][0]["message"]["content"]
    print("chat reply:", reply)
    return ids, reply


if __name__ == "__main__":
    try:
        check()
    except requests.ConnectionError:
        sys.exit(f"Cannot reach {BASE_URL} - is the server running?")
