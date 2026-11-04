"""Agent assist (lesson 8): the model DRAFTS a JSON Schema for a new tool; code checks and decides."""
import json
import os

import requests

from schema_check import validate

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
SPEC = """<tool_spec>
name: convert_temperature
- value (number, required)
- to (string, required, one of celsius|fahrenheit)
</tool_spec>"""
GOOD = [{"value": 21, "to": "fahrenheit"}]
BAD = [{"value": "21", "to": "fahrenheit"}, {"to": "celsius"}, {"value": 1, "to": "kelvin"}, {"value": 1, "to": "celsius", "x": 1}]


def draft_schema(base_url=BASE_URL, model=MODEL):
    prompt = "Write a JSON Schema (type object) for the arguments of this tool. Reply with the schema only.\n" + SPEC
    resp = requests.post(f"{base_url}/chat/completions", timeout=120, json={
        "model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0})
    return json.loads(resp.json()["choices"][0]["message"]["content"])  # not valid JSON -> raises: code rejects it


def check(schema):
    """Code is the judge: structure rules + example arguments that must pass / must fail."""
    notes = []
    if schema.get("type") != "object" or not isinstance(schema.get("properties"), dict):
        return False, ["schema must be an object with properties"]
    if schema.get("additionalProperties") is not False:
        schema["additionalProperties"] = False  # policy: never accept invented fields
        notes.append("added additionalProperties: false")
    wrong_accepts = [b for b in BAD if not validate(b, schema)]
    wrong_rejects = [g for g in GOOD if validate(g, schema)]
    notes += [f"accepted bad example {b}" for b in wrong_accepts] + [f"rejected good example {g}" for g in wrong_rejects]
    return not (wrong_accepts or wrong_rejects), notes


if __name__ == "__main__":
    draft = draft_schema()
    print("draft:", json.dumps(draft))
    ok, notes = check(draft)
    print("accepted" if ok else "rejected", notes)
