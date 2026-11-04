"""Minimal provider-side contract check: does a real response match openapi.json?

Checks: path + method exist, status code is declared, JSON body has the schema's
required fields with the declared JSON types (and enum values). Not a full validator.
"""
import json
import pathlib
import re

JSON_TYPES = {"string": str, "integer": int, "boolean": bool, "object": dict, "array": list}


def load_spec(path=pathlib.Path(__file__).with_name("openapi.json")):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def find_operation(spec, method, path):
    for template, item in spec["paths"].items():
        # /loans/{loanId} -> ^/loans/[^/]+$ (concrete paths are tried in file order)
        pattern = "^" + re.sub(r"\{[^/]+\}", "[^/]+", template) + "$"
        if re.match(pattern, path) and method.lower() in item:
            return template, item[method.lower()]
    return None, None


def resolve(spec, schema):
    ref = schema.get("$ref", "")
    return spec["components"]["schemas"][ref.split("/")[-1]] if ref.startswith("#/components/schemas/") else schema


def check(spec, method, path, status, body):
    template, operation = find_operation(spec, method, path)
    if operation is None:
        return [f"{method} {path} is not in the spec"]
    response = operation["responses"].get(str(status))
    if response is None:
        return [f"{method} {template}: status {status} not declared"]
    media = response.get("content", {}).get("application/json")
    if media is None:
        return []
    schema, problems = resolve(spec, media["schema"]), []
    for field in schema.get("required", []):
        if field not in body:
            problems.append(f"{method} {template} {status}: missing required field '{field}'")
    for field, prop in schema.get("properties", {}).items():
        if field in body:
            expected = JSON_TYPES[prop["type"]]
            value = body[field]
            if not isinstance(value, expected) or (expected is int and isinstance(value, bool)):
                problems.append(f"{method} {template} {status}: '{field}' is not {prop['type']}")
            elif "enum" in prop and value not in prop["enum"]:
                problems.append(f"{method} {template} {status}: '{field}'={value!r} not in enum")
    return problems
