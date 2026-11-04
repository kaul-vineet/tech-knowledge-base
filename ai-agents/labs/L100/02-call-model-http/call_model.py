"""Call a chat model over plain HTTP (no SDK): POST /v1/chat/completions and read the reply."""
import json
import os

import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")  # Ollama default
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")


def chat(messages, base_url=BASE_URL, model=MODEL, temperature=0.0, max_tokens=200):
    payload = {
        "model": model,
        "messages": messages,          # stateless: the WHOLE {"role", "content"} history, every call
        "temperature": temperature,    # sampling: 0 = most repeatable; higher = more varied
        "max_tokens": max_tokens,      # hard cap on reply length
    }
    resp = requests.post(f"{base_url}/chat/completions", json=payload, timeout=120)
    resp.raise_for_status()            # turn 4xx/5xx into an exception
    return resp.json()


if __name__ == "__main__":
    data = chat([{"role": "user", "content": "Say hello in one short sentence."}])
    choice = data["choices"][0]
    print("reply        :", choice["message"]["content"])
    print("finish_reason:", choice["finish_reason"])  # "stop" = done, "length" = hit max_tokens
    print("usage        :", json.dumps(data.get("usage")))
    print("top-level keys:", sorted(data))
