"""Same call as call_model.py using only the standard library (urllib) - zero dependencies."""
import json
import os
import urllib.request

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")


def chat(messages, base_url=BASE_URL, model=MODEL, temperature=0.0):
    body = json.dumps({"model": model, "messages": messages, "temperature": temperature}).encode()
    req = urllib.request.Request(f"{base_url}/chat/completions", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:  # raises HTTPError on 4xx/5xx
        return json.load(resp)


if __name__ == "__main__":
    data = chat([{"role": "user", "content": "Say hello in one short sentence."}])
    print("reply:", data["choices"][0]["message"]["content"])
