"""Build task (lesson 13) - YOUR FILE. Shipped UNFIXED: one budget for the whole run (2 s), so a 600 ms
cold tool hides inside a 'fast enough' total, and nothing warms the index.

TODO 1: check_budgets() - check EVERY span against a budget looked up by attributes["gen_ai.operation.name"]
        (chat <= 500 ms, execute_tool <= 200 ms); one line per violation, e.g.
        "execute_tool search_docs: 600 ms > 200 ms".
TODO 2: warm_up() - call agent_module.load_index() at process start.
Check it: BUILD_TARGET=mine python -m unittest -v test_build_task
"""
import json
from pathlib import Path

RUN_BUDGET_MS = 2000  # whole-run budget only


def check_budgets(path, budgets=None):
    """Return one line per span over its budget (empty list = within budget)."""
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        s = json.loads(line)
        if s["parent_span_id"] is None and s["duration_ms"] > RUN_BUDGET_MS:  # only the root span is checked
            out.append(f"{s['name']}: {s['duration_ms']:.0f} ms > {RUN_BUDGET_MS} ms")
    return out


def warm_up(agent_module):
    """Nothing is warmed: the first user request pays the cold start."""
