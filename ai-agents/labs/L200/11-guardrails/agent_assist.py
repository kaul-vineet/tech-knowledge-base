"""Agent assist (lesson 11): the model PROPOSES a risk label per tool; the policy table in code decides."""
import json
import os

import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
TOOLS = {"search_docs": "Search the local notes.", "send_email": "Send an email to a recipient.",
         "archive_notes": "Move old notes to cold storage."}
POLICY = {"search_docs": "low", "send_email": "high", "archive_notes": "high"}  # authoritative, reviewed by humans


def propose_labels(base_url=BASE_URL, model=MODEL):
    listing = "\n".join(f"{n}: {d}" for n, d in TOOLS.items())
    prompt = f"Label each tool's risk as high or low. Reply with a JSON object only.\n<tool_list>\n{listing}\n</tool_list>"
    resp = requests.post(f"{base_url}/chat/completions", timeout=120, json={
        "model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0})
    return json.loads(resp.json()["choices"][0]["message"]["content"])


def review(proposed):
    """Code decides: the policy label always wins; disagreements go to a human reviewer as a list."""
    final = {name: POLICY.get(name, "high") for name in TOOLS}  # unknown tool -> high (fail safe)
    disagreements = [f"{n}: model said {proposed.get(n)!r}, policy says {final[n]!r}"
                     for n in TOOLS if proposed.get(n) != final[n]]
    return final, disagreements


if __name__ == "__main__":
    proposed = propose_labels()
    final, disagreements = review(proposed)
    print("proposed:", proposed)
    print("final   :", final)
    print("review  :", disagreements)
