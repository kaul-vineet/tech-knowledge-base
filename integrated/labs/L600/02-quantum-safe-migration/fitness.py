"""Fitness functions that keep the migration decisions true (each returns ok + the measured value)."""
import json
from datetime import date

import _kb  # noqa: F401
import agility_lint  # cryptography L400 #17: AST check for hard-coded algorithms outside the registry
import crypto_registry as registry
import inventory
import migration_plan

BUDGET = {"client_flight_bytes": 1400, "handshake_bytes": 6144}      # team budget (see the design brief)
BASELINE = json.loads((registry.HERE / "migration_baseline.json").read_text(encoding="utf-8"))["accepted"]


def f1_no_classical_kex_for_exposed_data(findings, horizon=migration_plan.HORIZON, today=registry.TODAY):
    """No classical-only key establishment for data with x + y > z, except baseline entries that are not overdue."""
    accepted = {(b["file"], b["algorithm"]): b for b in BASELINE}
    violations, used = [], []
    for f in findings:
        svc = inventory.SERVICES.get(f["service"])
        if f["usage"] != "key-establishment" or f["pq"] or svc is None:
            continue
        if not migration_plan.exposed(svc["secrecy_years"], svc["migration_years"], horizon):
            continue
        entry = accepted.get((f["file"], f["algorithm"]))
        if entry and date.fromisoformat(entry["due"]) >= today:
            used.append(f"{f['file']}:{f['line']}")
        else:
            violations.append(f"{f['service']} {f['file']}:{f['line']} {f['algorithm']}" + (" (baseline overdue)" if entry else ""))
    return {"ok": not violations, "violations": violations, "baseline_used": len(used), "threshold": "0 outside baseline"}


def f2_handshake_budget(tap):
    hellos = [f for f in tap.flights if f["t"] in ("client_hello", "server_hello")]
    client = max(f["bytes"] for f in hellos if f["t"] == "client_hello")
    pairs = [a["bytes"] + b["bytes"] for a, b in zip(hellos[::2], hellos[1::2])]
    total = max(pairs)
    return {"ok": client <= BUDGET["client_flight_bytes"] and total <= BUDGET["handshake_bytes"],
            "client_flight_bytes": client, "handshake_bytes": total, "threshold": BUDGET}


def f3_registry_only(channel_path, tap, service="messaging"):
    """Static: no algorithm named in the service (lint). Runtime: one client registry resolution per handshake."""
    ids = set(registry.KEX) | set(registry.SIG) | set(registry.AEAD)
    static = agility_lint.scan_source(channel_path.read_text(encoding="utf-8"), channel_path.name, ids=ids)
    handshakes = sum(1 for f in tap.flights if f["t"] == "client_hello" and f["service"] == service)
    resolved = sum(1 for a in registry.AUDIT if a["service"] == service and a["kind"] == "kex" and a["role"] == "client")
    return {"ok": not static and resolved >= handshakes, "static_violations": len(static),
            "handshakes": handshakes, "client_kex_resolutions": resolved, "threshold": "0 static; resolutions >= handshakes"}


def f4_flags_owned_and_live(flags=registry.FLAGS):
    gate = registry.gate_flags(flags)
    unowned = sorted(n for n, f in flags.flags.items() if not f.get("owner"))
    return {"ok": gate["ok"] and not unowned, "expired": gate["value"], "unowned": unowned, "threshold": "0 expired, 0 unowned"}
