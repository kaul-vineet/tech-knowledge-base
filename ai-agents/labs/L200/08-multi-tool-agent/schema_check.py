"""Tiny JSON Schema (2020-12) subset validator, stdlib only - enough for tool arguments.

Keywords: type, enum, minimum, maximum, minLength, maxLength, properties, required,
additionalProperties (false), items. Returns a list of "$.path: problem" strings (empty = valid).
Full validators (python-jsonschema, ajv) implement every keyword; see test_jsonschema_equivalent.py.
"""
TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "number": (int, float), "integer": (int, float)}


def _type_ok(value, kind):
    if kind in ("number", "integer") and isinstance(value, bool):
        return False  # JSON true/false are not numbers (Python bool is an int subclass)
    if kind == "integer":
        return isinstance(value, int) or (isinstance(value, float) and value.is_integer())  # 1.0 counts
    return isinstance(value, TYPES[kind])


def validate(value, schema, path="$"):
    kind = schema.get("type")
    if kind and not _type_ok(value, kind):
        return [f"{path}: expected {kind}, got {type(value).__name__}"]
    errors = []
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
    if "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{path}: {value} is less than the minimum of {schema['minimum']}")
    if "maximum" in schema and value > schema["maximum"]:
        errors.append(f"{path}: {value} is greater than the maximum of {schema['maximum']}")
    if "minLength" in schema and len(value) < schema["minLength"]:
        errors.append(f"{path}: is shorter than {schema['minLength']} characters")
    if "maxLength" in schema and len(value) > schema["maxLength"]:
        errors.append(f"{path}: is longer than {schema['maxLength']} characters")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        errors += [f"{path}.{k}: is required" for k in schema.get("required", []) if k not in value]
        for key, item in value.items():
            if key in props:
                errors += validate(item, props[key], f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}.{key}: additional property not allowed")
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors += validate(item, schema["items"], f"{path}[{i}]")
    return errors
