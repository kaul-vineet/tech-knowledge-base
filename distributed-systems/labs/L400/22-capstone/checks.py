"""Capstone correctness checks: deterministic code decides pass/fail for every rubric criterion (no model involved).
Each check reads the services' own data, the outboxes, the consumers, the spans, the queue samples and the Raft log."""
from collections import Counter

from reuse import SAGA, TRACING

WAIT_BUDGET_TICKS = 6  # p99 time an accepted order waits in the bounded queue


def pct(values, p):
    values = sorted(values)
    return values[min(len(values) - 1, int(p / 100 * len(values)))] if values else 0


def evaluate(p):
    """Returns {criterion: (pass, measured value)} for one pipeline run."""
    orders = set(p.trace)
    final = {r["saga"] for r in p.log.entries() if r["step"] == "saga" and r["status"] in ("completed", "compensated")}
    rows = [r for db in p.dbs.values() for r in db.rows]
    created = Counter(r["saga"] for r in rows if r["type"] == "order.created")
    charges = Counter(s for s, amount in p.payments.ledger if amount > 0)
    audit = SAGA.audit(p.orders, p.payments, p.shipping)
    processed = [c.processed for c in p.bus.subscribers]
    by_saga = {}
    for s in p.spans:
        by_saga.setdefault(s["saga"], []).append(s)
    ids = {s["span_id"] for s in p.spans}
    orphans = sum(s["parent_id"] is not None and s["parent_id"] not in ids for s in p.spans)
    split = sum(len({s["trace_id"] for s in spans}) != 1 for spans in by_saga.values())
    bad_headers = sum(TRACING.parse_traceparent(r["traceparent"]) is None for r in rows)
    over = sum(q > bound for q, bound in p.queue_seen)
    live = [n for name, n in p.raft.nodes.items() if name not in p.raft.net.down]
    configs = {max((int(cmd.split(":")[0]) for _, cmd in n.log[:n.commit]), default=0) for n in live}
    seen = [v for _, v in p.config_seen]
    return {
        "money invariant (audit)": (not audit, f"{len(audit)} violations"),
        "no lost orders": (final == orders, f"{len(final)}/{len(orders)} final"),
        "one order and one charge per key": (all(created[k] == 1 for k in orders) and max(charges.values()) == 1,
                                             f"max created {max(created.values())}, max charges {max(charges.values())}"),
        "exactly-once effects": (all(v == 1 for v in p.emails.values()) and
                                 all(p.revenue[s] == p.payments.net(s) for s in orders),
                                 f"max emails per event {max(p.emails.values())}, "
                                 f"revenue mismatches {sum(p.revenue[s] != p.payments.net(s) for s in orders)}"),
        "outbox delivered": (all(r["sent"] for r in rows) and all({r['id'] for r in rows} <= ids_ for ids_ in processed),
                             f"{len(rows)} events, {p.bus.published} publishes"),
        "one trace per order": (split == 0 and orphans == 0 and bad_headers == 0,
                                f"split {split}, orphans {orphans}, bad headers {bad_headers}"),
        "bounded queue": (over == 0 and pct(p.waits, 99) <= WAIT_BUDGET_TICKS,
                          f"over bound {over}, p99 wait {pct(p.waits, 99)} ticks"),
        "config via Raft": (not p.raft.checker.violations and configs == {2} and seen == sorted(seen),
                            f"safety violations {len(p.raft.checker.violations)}, committed versions {sorted(configs)}"),
    }
