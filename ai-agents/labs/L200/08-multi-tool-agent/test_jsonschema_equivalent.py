"""Equivalent check (pending-ci): python-jsonschema must agree with schema_check.validate on every case.

CI installs jsonschema==4.26.0; locally (no package) this test is skipped.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import multi_tool_agent as agent  # noqa: E402
from schema_check import validate  # noqa: E402

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - depends on the environment
    Draft202012Validator = None

CASES = [
    ("get_weather", {"city": "Paris"}), ("get_weather", {"city": "Paris", "unit": "kelvin"}),
    ("get_weather", {}), ("get_weather", {"city": "Oslo", "x": 1}), ("get_weather", {"city": 5}),
    ("search_docs", {"query": "tokens", "top_k": 5}), ("search_docs", {"query": "tokens", "top_k": 6}),
    ("search_docs", {"query": "t"}), ("search_docs", {"query": "tokens", "top_k": 2.0}),
    ("search_docs", {"query": "tokens", "top_k": True}), ("calculator", {"expression": "1" * 101}),
]


@unittest.skipIf(Draft202012Validator is None, "jsonschema not installed (CI installs jsonschema==4.26.0)")
class JsonschemaAgrees(unittest.TestCase):
    def test_same_verdicts(self):
        for name, args in CASES:
            schema = agent.REGISTRY[name]["schema"]
            Draft202012Validator.check_schema(schema)  # our schemas are valid 2020-12 schemas
            with self.subTest(name=name, args=args):
                self.assertEqual(Draft202012Validator(schema).is_valid(args), not validate(args, schema))


if __name__ == "__main__":
    unittest.main()
