"""Canonical bytes for anything we hash or sign: RFC 8785 JSON Canonicalization Scheme (JCS).
dumps(obj) = no whitespace, object keys sorted by UTF-16 code units, strings as ECMAScript JSON.stringify, numbers as
ECMAScript Number::toString (number formatter from solution/jcs_number.py, or build_task/ with BUILD_TARGET=mine).
platform_dumps() is the seeded fault: the same data written by a stack that prints doubles with '%.17g'
(what Python did before 3.1 and many C/C++ printf-based writers still do) - same VALUES, different BYTES."""
import importlib.util
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
_src = HERE / ("build_task" if os.environ.get("BUILD_TARGET") == "mine" else "solution") / "jcs_number.py"
_spec = importlib.util.spec_from_file_location("kb06_jcs_number", _src)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
jcs_number = _mod.number


class NotCanonical(ValueError):
    """Bytes parse as JSON but are not the canonical form of what they encode."""


def _string(s: str) -> str:
    if any(0xD800 <= ord(c) <= 0xDFFF for c in s):
        raise ValueError("lone surrogate: RFC 8785 3.2.2.2 requires an error")
    return json.dumps(s, ensure_ascii=False)  # same escapes as JSON.stringify: \b \t \n \f \r, \u00xx lowercase


def _encode(obj, number) -> str:
    if obj is None or obj is True or obj is False:
        return {None: "null", True: "true", False: "false"}[obj]
    if isinstance(obj, (int, float)):
        return number(obj)
    if isinstance(obj, str):
        return _string(obj)
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(_encode(v, number) for v in obj) + "]"
    if isinstance(obj, dict):
        keys = sorted(obj, key=lambda k: k.encode("utf-16-be"))  # UTF-16 code-unit order (RFC 8785 3.2.3)
        return "{" + ",".join(_string(k) + ":" + _encode(obj[k], number) for k in keys) + "}"
    raise TypeError(f"not JSON: {type(obj).__name__}")


def dumps(obj) -> bytes:
    return _encode(obj, jcs_number).encode("utf-8")


def platform_dumps(obj) -> bytes:
    """FAULT: sorted keys and no whitespace like JCS, but doubles printed with 17 significant digits."""
    return _encode(obj, lambda x: str(x) if isinstance(x, int) else format(x, ".17g")).encode("utf-8")


def loads_strict(raw: bytes):
    """Parse, then insist the bytes ARE the canonical form (RFC 8785 Appendix C: canonical JSON as wire format).
    Without this, 'E' for 'e' or an extra space changes the bytes but not the parsed value."""
    obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicates)
    if dumps(obj) != raw:
        raise NotCanonical("bytes are not the JCS form of their own content")
    return obj


def _no_duplicates(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate property name (I-JSON, RFC 7493)")
    return dict(pairs)
