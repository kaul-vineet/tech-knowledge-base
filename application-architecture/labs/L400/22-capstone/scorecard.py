"""Capstone milestones as measured criteria. Every number comes from running the system; nothing is asserted by hand.

build(fault) wires the system (optionally with one seeded fault), runs a seeded workload and returns the evidence;
criteria(evidence) turns it into rubric rows {milestone, criterion, measure, value, threshold, pass}.
"""
import ast
import json
import pathlib
import random
import re
from datetime import datetime, timedelta, timezone

import loans_service
from http_api import start
from reuse import (POLICY_BUGGY, POLICY_FIXED, bus, capacity, consumers, contract, fines_buggy, fines_fixed,
                   fines_traffic, fitness_capacity, fitness_legacy, fitness_policy, fitness_tenant, outbox, rego_lite,
                   slo, strangler)

HERE = pathlib.Path(__file__).resolve().parent
FAULTS = ("fines-rounding", "cross-tenant-policy", "unscoped-query", "duplicate-delivery")
TENANTS = [f"lib{i:02d}" for i in range(5)]
START = datetime(2026, 10, 28, 9, 0, tzinfo=timezone.utc)
MEMBER_LOANS = loans_service.MEMBER_LOANS
MEMBER_LOANS_UNSCOPED = "SELECT id, book_id FROM loans WHERE member_id = :member AND returned = 0 ORDER BY id"  # fault


class NotIdempotent(consumers.ActiveLoansProjection):  # seeded fault: forgets the eventId check
    def __call__(self, event):
        self.handle(event)


def build(fault=None, out=HERE / "out"):
    out.mkdir(exist_ok=True)
    ticks = iter(range(10 ** 6))
    clock = lambda: (START + timedelta(seconds=next(ticks))).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: E731
    policy = rego_lite.load_policy(POLICY_BUGGY if fault == "cross-tenant-policy" else POLICY_FIXED)
    decision_log = []  # collected in memory, written once (one open per decision is slow on network drives)
    pdp = rego_lite.DecisionPoint(policy, log_path=decision_log, clock=clock)
    # M1: shadow the extracted fines service on 2,000 seeded requests, then cut over only if the criteria pass
    candidate = fines_buggy if fault == "fines-rounding" else fines_fixed
    facade = strangler.Facade(strangler.LegacyFines(), strangler.ServiceFines(fn=candidate.fine_for), mode="shadow")
    strangler.replay(facade, list(fines_traffic.requests()))
    decision = strangler.cutover_decision(facade.shadow.stats)
    facade.mode = "service" if decision["ready"] else "shadow"
    loans_service.MEMBER_LOANS = MEMBER_LOANS_UNSCOPED if fault == "unscoped-query" else MEMBER_LOANS
    service = loans_service.LoansService(pdp, facade, clock=clock)
    evidence = {"fault": fault, "cutover": decision, "facade_mode": facade.mode, "service": service,
                "probes": workload(service)}
    evidence["events"] = relay_and_consume(service, idempotent=fault != "duplicate-delivery")
    evidence["decision_log"] = decision_log
    (out / "decisions.jsonl").write_text("\n".join(decision_log) + "\n", encoding="utf-8")
    (out / "requests.jsonl").write_text("\n".join(service.request_log) + "\n", encoding="utf-8")
    return evidence


def workload(service, seed=22):
    """Seeded traffic: members borrow/return/view in 5 libraries; probes try to cross library lines."""
    rng, open_loans, probes = random.Random(seed), [], {"cross_rows": 0, "cross_allowed": 0, "attempts": 0}
    for i in range(600):
        tenant, member = rng.choice(TENANTS), f"m{rng.randrange(20)}"
        subject = {"id": member, "tenant": tenant, "roles": ["member"], "email": f"{member}@{tenant}.example"}
        try:
            if rng.random() < 0.5 or not open_loans:
                kind = "student" if rng.random() < 0.3 else "adult"
                open_loans.append((tenant, member, service.borrow(subject, tenant, member, kind, f"b{i}")))
            elif rng.random() < 0.6:
                t, m, loan = open_loans.pop(rng.randrange(len(open_loans)))
                owner = {"id": m, "tenant": t, "roles": ["member"], "email": f"{m}@{t}.example"}
                service.give_back(owner, t, loan, rng.choice([0, 3, 5, 7, 12, 40]))
            else:
                service.loans_of(subject, tenant, member)
        except loans_service.Forbidden:
            pass  # loan limit reached: the policy said no (403), not an error
    for t in TENANTS:  # probes: a librarian of another library, and a member of t asking for its own id elsewhere
        other = TENANTS[(TENANTS.index(t) + 1) % len(TENANTS)]
        for who in ({"id": "s9", "tenant": other, "roles": ["librarian"]}, {"id": "m1", "tenant": t, "roles": ["member"]}):
            probes["attempts"] += 1
            target = t if who["roles"] == ["librarian"] else other
            try:
                rows = service.loans_of(who, target, "m1")
                probes["cross_allowed"] += who["tenant"] != target
                probes["cross_rows"] += sum(1 for _ in rows) if who["tenant"] != target else 0
            except loans_service.Forbidden:
                pass
        own = service.loans_of({"id": "m1", "tenant": t, "roles": ["member"]}, t, "m1")
        expected = service.db.execute("SELECT COUNT(*) FROM loans WHERE tenant_id = ? AND member_id = 'm1' AND "
                                      "returned = 0", (t,)).fetchone()[0]
        probes["cross_rows"] += max(0, len(own) - expected)  # rows that belong to another library
    return probes


def relay_and_consume(service, idempotent=True):
    """Relay the outbox at least once: publish everything, then redeliver everything (a crash before marking)."""
    events_bus, projection = bus.InProcessBus(), (consumers.ActiveLoansProjection() if idempotent else NotIdempotent())
    for channel in ("loanCreated", "loanReturned"):
        events_bus.subscribe(channel, projection)
    published = outbox.Relay(service.db, events_bus).publish_pending()  # system process: all tenants, by design
    for _, channel, payload in service.db.execute("SELECT seq, channel, payload FROM outbox ORDER BY seq").fetchall():
        events_bus.publish(channel, json.loads(payload))  # redelivery
    active = dict(service.db.execute("SELECT member_id || '@' || tenant_id, COUNT(*) FROM loans WHERE returned = 0 "
                                     "GROUP BY tenant_id, member_id").fetchall())
    seen = {k.split("@")[0] for k in active}
    wrong = sum(1 for m, n in projection.active.items() if n != sum(v for k, v in active.items() if k.startswith(m + "@")))
    committed = service.db.execute("SELECT COUNT(*) + (SELECT COUNT(*) FROM loans WHERE returned = 1) FROM loans"
                                   ).fetchone()[0]
    rows = service.db.execute("SELECT COUNT(*), SUM(published_at IS NULL) FROM outbox").fetchone()
    return {"committed_changes": committed, "outbox_rows": rows[0], "unpublished": rows[1] or 0,
            "published": published, "projection_mismatches": wrong + len(seen - set(projection.active))}


def unscoped_sql(module=loans_service):
    """Static gate (lesson 18 rule) over the SQL the service actually holds, including injected strings."""
    found = []
    for name, value in vars(module).items():
        if isinstance(value, str) and fitness_tenant.TENANT_TABLES.search(value) and \
                value.lstrip().upper().startswith(("SELECT", "UPDATE", "DELETE")) and \
                not re.search(r"\bWHERE\s+tenant_id\s*=\s*(\?|:tenant)", value, re.I):
            found.append(name)
    return found


def pep_gaps(path=HERE / "loans_service.py"):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "LoansService")
    return [f.name for f in cls.body if isinstance(f, ast.FunctionDef) and not f.name.startswith("_") and
            not any(isinstance(c, ast.Attribute) and c.attr == "_authorize" for c in ast.walk(f))]


ADR_SECTIONS = ["## Status", "## Context", "## Decision", "## Consequences"]  # Title first, then these, in order


def adr_problems(text):
    positions = [text.find(s) for s in ADR_SECTIONS]
    ok = re.match(r"# ADR \d+: \S", text) and -1 not in positions and positions == sorted(positions)
    return [] if ok else ["not Nygard: title, Status, Context, Decision, Consequences"]
