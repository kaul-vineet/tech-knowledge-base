"""Ask for JSON matching a schema, parse it, validate it with stdlib checks, retry if invalid."""
import json
import os

import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
SCHEMA = {
    "type": "object",
    "properties": {"name": {"type": "string"}, "age": {"type": "integer"}, "city": {"type": "string"}},
    "required": ["name", "age", "city"],
    "additionalProperties": False,
}


def chat(messages, response_format=None, base_url=BASE_URL, model=MODEL):
    payload = {"model": model, "messages": messages, "temperature": 0}
    if response_format:
        payload["response_format"] = response_format  # constrained decoding on the server, where supported
    resp = requests.post(f"{base_url}/chat/completions", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def validate(obj):
    """Return a list of problems (empty list = valid). Plain code, no model involved."""
    # trust boundary: model JSON is untrusted input until this returns []
    if not isinstance(obj, dict):
        return ["top level must be an object"]
    errors = [f"missing key {k!r}" for k in SCHEMA["required"] if k not in obj]
    errors += [f"unexpected key {k!r}" for k in obj if k not in SCHEMA["properties"]]
    if "name" in obj and not isinstance(obj["name"], str):
        errors.append("name must be a string")
    if "city" in obj and not isinstance(obj["city"], str):
        errors.append("city must be a string")
    if "age" in obj and (type(obj["age"]) is not int or not 0 <= obj["age"] <= 150):
        errors.append("age must be an integer 0-150")
    return errors


def extract_person(text, use_response_format=False, max_attempts=3, **kw):
    messages = [
        {"role": "system", "content": "Extract the person from the text inside <input> tags. Reply with "
                                      "ONLY a JSON object matching this JSON schema:\n" + json.dumps(SCHEMA)},
        {"role": "user", "content": f"<input>{text}</input>"},
    ]
    rf = {"type": "json_schema", "json_schema": {"name": "person", "schema": SCHEMA, "strict": True}}
    for attempt in range(1, max_attempts + 1):
        reply = chat(messages, rf if use_response_format else None, **kw)
        try:
            obj = json.loads(reply)  # strict parse: prose or code fences fail here
            errors = validate(obj)
        except json.JSONDecodeError as exc:
            errors = [f"not valid JSON ({exc.msg})"]
        print(f"  attempt {attempt}: {'OK' if not errors else errors}")
        if not errors:
            return obj, attempt
        # bounded retry: feed the bad answer and the exact problem back, then ask again
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": f"Invalid: {'; '.join(errors)}. Reply with ONLY the JSON object."}]
    raise ValueError(f"no valid JSON after {max_attempts} attempts")


if __name__ == "__main__":
    text = "Maria moved to Lisbon in 2019; she is 34 and works as a nurse."
    print("prompt-only (parse + validate + retry):")
    print("  result:", extract_person(text))
    print("with response_format json_schema:")
    print("  result:", extract_person(text, use_response_format=True))
