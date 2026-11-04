"""Structural checks for an AsyncAPI 3.x document + payload validation (a small JSON Schema subset).

Not a full validator: CI also runs the official AsyncAPI CLI. Run: python asyncapi_check.py [asyncapi.json]
"""
import json
import pathlib
import re
import sys
import uuid
from datetime import datetime

HERE = pathlib.Path(__file__).resolve().parent
TYPES = {"object": dict, "string": str, "integer": int, "boolean": bool, "array": list}


def load(path=HERE / "asyncapi.json"):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def resolve(doc, ref):
    node = doc
    for part in ref.removeprefix("#/").split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def deref(doc, node):
    return resolve(doc, node["$ref"]) if isinstance(node, dict) and "$ref" in node else node


def check_document(doc):
    problems = []
    if not re.fullmatch(r"3\.\d+\.\d+", str(doc.get("asyncapi", ""))):
        problems.append(f"asyncapi must be a 3.x.y version, got {doc.get('asyncapi')!r}")
    if not all(isinstance(doc.get("info", {}).get(k), str) for k in ("title", "version")):
        problems.append("info.title and info.version are required strings")
    for cid, channel in doc.get("channels", {}).items():
        for mid, ref in channel.get("messages", {}).items():
            try:
                message = deref(doc, ref)
                schema = deref(doc, message["payload"])
            except (KeyError, TypeError):
                problems.append(f"channels.{cid}.messages.{mid}: unresolvable message or payload")
                continue
            where = message["payload"].get("$ref", f"#/channels/{cid}/messages/{mid}/payload")
            if not schema.get("required"):  # house rule: a contract without required fields promises nothing
                problems.append(f"{where[2:].replace('/', '.')}: house rule - payload schema must list 'required' fields")
    for oid, op in doc.get("operations", {}).items():
        if op.get("action") not in ("send", "receive"):
            problems.append(f"operations.{oid}: action must be 'send' or 'receive' (AsyncAPI 3), got {op.get('action')!r}")
        cref = (op.get("channel") or {}).get("$ref", "")
        cid = cref.removeprefix("#/channels/")
        if not cref.startswith("#/channels/") or cid not in doc.get("channels", {}):
            problems.append(f"operations.{oid}: channel must be a $ref to a root channel, got {cref!r}")
            continue
        for mref in op.get("messages", []):
            if not mref.get("$ref", "").startswith(f"#/channels/{cid}/messages/"):
                problems.append(f"operations.{oid}: message {mref.get('$ref')!r} is not in channel {cid}")
    return problems


def validate(schema, value, doc, path="payload"):
    schema = deref(doc, schema)
    expected = TYPES.get(schema.get("type"))
    if expected and (not isinstance(value, expected) or (expected is int and isinstance(value, bool))):
        return [f"{path}: expected {schema['type']}, got {type(value).__name__} {value!r}"]
    problems = []
    if "const" in schema and value != schema["const"]:
        problems.append(f"{path}: must be {schema['const']!r}, got {value!r}")
    if schema.get("format") == "uuid" and not _parses(uuid.UUID, value):
        problems.append(f"{path}: not a uuid: {value!r}")
    if schema.get("format") == "date-time" and not _parses(lambda v: datetime.fromisoformat(v.replace("Z", "+00:00")), value):
        problems.append(f"{path}: not a date-time: {value!r}")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        problems += [f"{path}: missing required field {k!r}" for k in schema.get("required", []) if k not in value]
        if schema.get("additionalProperties") is False:
            problems += [f"{path}: unexpected field {k!r}" for k in value if k not in props]
        for key, sub in props.items():
            if key in value:
                problems += validate(sub, value[key], doc, f"{path}.{key}")
    return problems


def validate_event(doc, channel_id, event):
    """An event must be valid against exactly one message of its channel (AsyncAPI 3 Channel Object)."""
    results = [validate(deref(doc, ref)["payload"], event, doc)
               for ref in doc["channels"][channel_id]["messages"].values()]
    return [] if sum(not r for r in results) == 1 else results[0] or ["matches more than one message"]


def _parses(fn, value):
    try:
        fn(value)
        return True
    except (ValueError, TypeError, AttributeError):
        return False


if __name__ == "__main__":
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "asyncapi.json")
    doc = load(path)
    problems = check_document(doc)
    for problem in problems:
        print("PROBLEM", problem)
    print(f"{path.name}: AsyncAPI {doc.get('asyncapi')}, {len(doc.get('channels', {}))} channels, "
          f"{len(doc.get('operations', {}))} operations: {'OK' if not problems else 'FAILED'}")
    sys.exit(1 if problems else 0)
