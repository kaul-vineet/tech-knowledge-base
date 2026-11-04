"""Writes promptfoo_tests.jsonl from golden.jsonl, so promptfoo checks the same cases as eval_gate.py.

Run: python make_promptfoo_tests.py   (then: npx promptfoo@0.125.1 eval -c promptfooconfig.yaml --no-cache)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def promptfoo_case(case):
    js = lambda expr: {"type": "javascript", "value": expr}
    return {"description": case["id"], "vars": {"ticket": case["ticket"]}, "assert": [
        {"type": "is-json"},  # structural
        js(f"JSON.parse(output).category === '{case['expect']['category']}'"),  # exact
        js(f"JSON.parse(output).priority === '{case['expect']['priority']}'"),
        js(f"JSON.parse(output).summary.toLowerCase().includes('{case['rubric']['mentions'].lower()}')"),  # rubric item
    ]}


def build():
    cases = [json.loads(l) for l in (HERE / "golden.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return "".join(json.dumps(promptfoo_case(c)) + "\n" for c in cases)


if __name__ == "__main__":
    (HERE / "promptfoo_tests.jsonl").write_text(build(), encoding="utf-8")
    print("wrote promptfoo_tests.jsonl")
