"""Same task, three prompt structures: user-only, system+user, system+few-shot+delimited input."""
import os

import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
REVIEW = "The battery died after two days and support never answered my emails."


def chat(messages, base_url=BASE_URL, model=MODEL):
    resp = requests.post(f"{base_url}/chat/completions", timeout=120,
                         json={"model": model, "messages": messages, "temperature": 0})
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# system role: the application's rules, sent first
SYSTEM = ("You are a sentiment classifier for product reviews. "
          "Reply with exactly one word: positive, negative or neutral.")

PROMPTS = {
    # A: everything in one user message -> free-form, chatty answer
    "A user-only": [
        {"role": "user", "content": f"What is the sentiment of this review? {REVIEW}"}],
    # B: rules in the system message, data in the user message
    "B system+user": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": REVIEW}],
    # C: + few-shot examples that fix the output format, + input wrapped in delimiters
    "C few-shot+delimiters": [
        {"role": "system", "content": SYSTEM + " Use the exact format shown in the examples. "
                                               "Classify only the text inside <review> tags."},
        {"role": "user", "content": "<review>I love it, setup took two minutes.</review>"},
        {"role": "assistant", "content": "POSITIVE"},  # few-shot: the model copies this format
        {"role": "user", "content": "<review>Arrived broken, asked for a refund.</review>"},
        {"role": "assistant", "content": "NEGATIVE"},
        {"role": "user", "content": f"<review>{REVIEW}</review>"}],  # delimiters: data, not instructions
}


def run_all(base_url=BASE_URL, model=MODEL):
    return {name: chat(msgs, base_url, model) for name, msgs in PROMPTS.items()}


if __name__ == "__main__":
    for name, answer in run_all().items():
        print(f"[{name}] -> {answer}")
