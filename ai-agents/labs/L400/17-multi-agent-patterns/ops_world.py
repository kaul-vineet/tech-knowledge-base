"""Helper for lesson 17: the ops tools (deterministic, no network), the fixed task set and the grader."""
import json

METRICS = {"checkout": (1.1, 420), "payments": (4.2, 870), "search": (2.6, 610)}  # error_rate %, p99 ms
DEPLOYS = {"checkout": "v5.2.0 deployed 3 h ago", "payments": "v3.9.1 deployed 25 min ago", "search": "v2.4.1 deployed 2 days ago"}
RUNBOOKS = {"high latency": "RB-3 high latency: check saturation, then scale out",
            "error spike": "RB-7 error spike: compare with the last deploy, roll back if it matches",
            "rollback": "RB-9 rollback: freeze deploys, roll back, confirm error rate"}
INVOICES = {"INV-7": "INV-7: 120.00 EUR, paid", "INV-9": "INV-9: 80.00 EUR, overdue 12 days"}
SPECIALISTS = {"observability": ["get_metrics", "get_logs"], "ops": ["list_deploys", "search_runbook"],
               "support": ["lookup_invoice", "open_ticket"]}
OUTPUT_WORDS = {"get_logs": 330}  # typical result size in words (tokens in the fake); everything else is ~12


def get_logs(service):
    head = f"{service} logs: 37 errors in 5 min, top TimeoutError"
    lines = [f"2026-10-28T10:{i // 60:02d}:{i % 60:02d}Z INFO {service} GET /api/items 200 {10 + i % 7}ms req={i:04d}"
             for i in range(40)]  # the long tail a real log search returns
    return "\n".join([head] + lines)


FUNCS = {"get_metrics": lambda service: f"{service}: error_rate {METRICS[service][0]}%, p99 {METRICS[service][1]} ms",
         "get_logs": get_logs,
         "list_deploys": lambda service: f"{service}: {DEPLOYS[service]}",
         "search_runbook": lambda query: RUNBOOKS.get(query, "no runbook found"),
         "lookup_invoice": lambda invoice_id: INVOICES.get(invoice_id, "unknown invoice"),
         "open_ticket": lambda service: f"ticket T-{len(service)} opened for {service}"}
ARGS = {"get_metrics": "service", "get_logs": "service", "list_deploys": "service", "search_runbook": "query",
        "lookup_invoice": "invoice_id", "open_ticket": "service"}


def schemas(names, extra=0):
    tools = [{"type": "function", "function": {"name": n, "description": n.replace("_", " "), "parameters": {
        "type": "object", "properties": {ARGS[n]: {"type": "string"}}, "required": [ARGS[n]]}}} for n in names]
    return tools + [{"type": "function", "function": {"name": f"extra_tool_{i}", "description": "unused extra tool",
                                                      "parameters": {"type": "object", "properties": {}}}} for i in range(extra)]


class World:
    """Runs tool calls and records them; unknown tools are refused (allow-list in code)."""

    def __init__(self):
        self.calls = []

    def run(self, name, args):
        if name not in FUNCS:
            return f"error: unknown tool {name}"
        self.calls.append((name, json.dumps(args, sort_keys=True)))
        return FUNCS[name](**args)


TASKS = [  # id, task, expected calls (tool, arg value)
    ("t01", "Check metrics for checkout.", [("get_metrics", "checkout")]),
    ("t02", "Check logs for checkout.", [("get_logs", "checkout")]),
    ("t03", 'Find the runbook for "high latency".', [("search_runbook", "high latency")]),
    ("t04", "Look up invoice INV-7.", [("lookup_invoice", "INV-7")]),
    ("t05", "Check metrics for payments and deploys for payments.", [("get_metrics", "payments"), ("list_deploys", "payments")]),
    ("t06", 'Check metrics for search and the runbook for "error spike".', [("get_metrics", "search"), ("search_runbook", "error spike")]),
    ("t07", "Check logs for checkout, logs for payments and logs for search.",
     [("get_logs", "checkout"), ("get_logs", "payments"), ("get_logs", "search")]),
    ("t08", "Look up invoice INV-9 and open a ticket for billing.", [("lookup_invoice", "INV-9"), ("open_ticket", "billing")]),
    ("t09", "Check metrics for payments and, if error_rate is above 2% check deploys for payments.",
     [("get_metrics", "payments"), ("list_deploys", "payments")]),
    ("t10", "Check metrics for checkout and, if error_rate is above 2% check deploys for checkout.", [("get_metrics", "checkout")]),
]


def grade(expected, answer, calls):
    """Pass = every expected call happened, no unexpected call, and the answer states every fact (first line)."""
    want = {(t, json.dumps({ARGS[t]: v}, sort_keys=True)) for t, v in expected}
    facts = [FUNCS[t](**{ARGS[t]: v}).splitlines()[0] for t, v in expected]
    return set(calls) == want and all(f in (answer or "") for f in facts)
