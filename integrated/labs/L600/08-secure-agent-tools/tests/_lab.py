"""Shared test setup: lab on sys.path, ONE shared fake model server and ONE verified registry per test process."""
import os
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
if str(LAB) not in sys.path:
    sys.path.insert(0, str(LAB))

import adapters  # noqa: E402
import scenarios  # noqa: E402

FAULTS = {os.environ["L600_08_INJECT"]} if os.environ.get("L600_08_INJECT") else set()  # failure-lab switch
_cache = {}


def url():
    if "url" not in _cache:
        _cache["server"], _cache["url"] = adapters.start_fake_model()
    return _cache["url"]


def registry():
    if "registry" not in _cache:
        _cache["registry"], rejected = scenarios.load_registry()
        assert not rejected, rejected
    return _cache["registry"]
