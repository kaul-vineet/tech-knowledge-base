"""Alert packet schema (ZTF/Rubin-inspired field names, JSON form) and a minimal validator.

Real brokers serialise with Apache Avro (schema in JSON); fastavro.validation.validate is the pending-ci
equivalent (alert_avro.py). Supported here: type, required, properties, enum, minimum, maximum, items.
"""
SCHEMA = {
    "type": "object",
    "required": ["schemavsn", "candid", "objectId", "candidate", "prv_candidates"],
    "properties": {
        "schemavsn": {"type": "string", "enum": ["astro-kb-1.0"]},
        "candid": {"type": "integer", "minimum": 0},
        "objectId": {"type": "string"},
        "candidate": {
            "type": "object",
            "required": ["mjd", "x", "y", "flux", "sigmaflux", "isdiffpos", "rb", "fwhm"],
            "properties": {"mjd": {"type": "number"}, "x": {"type": "number", "minimum": 0, "maximum": 128},
                           "y": {"type": "number", "minimum": 0, "maximum": 128}, "flux": {"type": "number"},
                           "sigmaflux": {"type": "number", "minimum": 0}, "isdiffpos": {"type": "string", "enum": ["t", "f"]},
                           "rb": {"type": "number", "minimum": 0, "maximum": 1}, "fwhm": {"type": "number", "minimum": 0}}},
        "prv_candidates": {"type": "array", "items": {"type": "object"}},
    },
}
TYPES = {"object": dict, "string": str, "integer": int, "number": (int, float), "array": list}


def validate(value, schema=SCHEMA, path="$"):
    """Returns a list of error strings (empty = valid)."""
    errors = []
    if not isinstance(value, TYPES[schema["type"]]) or (schema["type"] == "integer" and isinstance(value, bool)):
        return [f"{path}: expected {schema['type']}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in {schema['enum']}")
    if "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{path}: {value} < {schema['minimum']}")
    if "maximum" in schema and value > schema["maximum"]:
        errors.append(f"{path}: {value} > {schema['maximum']}")
    for key in schema.get("required", []):
        if key not in value:
            errors.append(f"{path}.{key}: missing")
    for key, sub in schema.get("properties", {}).items():
        if isinstance(value, dict) and key in value:
            errors += validate(value[key], sub, f"{path}.{key}")
    if schema["type"] == "array":
        for i, item in enumerate(value):
            errors += validate(item, schema["items"], f"{path}[{i}]")
    return errors
