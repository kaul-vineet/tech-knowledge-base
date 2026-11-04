"""Build task (lesson 13): a latency budget per operation, checked from the trace, plus the fix (warm-up)."""
import json
from pathlib import Path

BUDGET_MS = {"chat": 500, "execute_tool": 200}  # per span, by gen_ai.operation.name


def check_budgets(path, budgets=BUDGET_MS):
    """Return one line per span over its budget (empty list = within budget)."""
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        s = json.loads(line)
        limit = budgets.get(s["attributes"].get("gen_ai.operation.name"))
        if limit is not None and s["duration_ms"] > limit:
            out.append(f"{s['name']}: {s['duration_ms']:.0f} ms > {limit} ms")
    return out


def warm_up(agent_module):
    """Pay the cold-start cost at process start, not inside the first user request."""
    agent_module.load_index()
