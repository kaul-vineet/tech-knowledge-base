"""Minimal chat client for any OpenAI-compatible local server (Ollama, llama.cpp server, vLLM).

Env vars:
  LOCAL_MODEL_URL  base URL, default http://localhost:11434/v1  (Ollama on the Mac mini or Windows PC)
  LOCAL_MODEL      model name, default "qwen2.5:1.5b"
Stdlib only, so it runs the same on macOS and Windows.
"""
import json
import os
import urllib.request

DEFAULT_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "qwen2.5:1.5b"


def chat(messages, base_url=None, model=None, temperature=0, timeout=60, **extra):
    """Send a chat-completions request and return the assistant's text."""
    url = (base_url or os.environ.get("LOCAL_MODEL_URL") or DEFAULT_URL).rstrip("/") + "/chat/completions"
    body = {"model": model or os.environ.get("LOCAL_MODEL") or DEFAULT_MODEL,
            "messages": messages, "temperature": temperature, **extra}
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # timeout: never hang on a slow model
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"].get("content") or ""
