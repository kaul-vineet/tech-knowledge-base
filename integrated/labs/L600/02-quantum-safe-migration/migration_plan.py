"""Milestone 4 - risk with Mosca's inequality and a prioritised migration plan (code decides the order).

x = years the data must stay secret, y = years the migration takes (both per service, services.json),
z = years until a cryptographically relevant quantum computer - a LABELLED planning assumption, never a number derived
from the simulator. Key establishment protecting data with x + y > z is exposed to harvest-now-decrypt-later today.
"""
from dataclasses import dataclass

import inventory

SOURCES = {"planning-assumption", "policy-date: NIST IR 8547 disallowed after 2035"}
ORDER = ["P1-review", "P1", "P2-kex", "P2-sig", "done", "none"]
ACTION = {
    "P1-review": "no owner in services.json: assign one, then classify (never drop a finding)",
    "P1": "hybrid X25519MLKEM768 now: harvest-now-decrypt-later exposure (x + y > z)",
    "P2-kex": "ML-KEM or hybrid before 2030 (NIST IR 8547: deprecated after 2030, disallowed after 2035)",
    "P2-sig": "ML-DSA-65 before 2030 (signatures are not exposed to HNDL; deprecated after 2030)",
    "done": "post-quantum via the registry; remove the classical fallback when pq_required is on",
    "none": "no change: symmetric (AES-256) is not broken by Shor",
}


@dataclass(frozen=True)
class Horizon:
    z_years: int
    source: str
    note: str

    def __post_init__(self):
        if self.source not in SOURCES:
            raise ValueError(f"z must come from {sorted(SOURCES)}, not {self.source!r}")


HORIZON = Horizon(10, "planning-assumption", "team planning value for 2026, not a forecast; try_it varies it 5..15")


def exposed(x, y, horizon):
    if not isinstance(horizon, Horizon):
        raise TypeError("z must be a labelled Horizon (planning assumption or policy date), not a simulator result")
    return x + y > horizon.z_years


def classify(finding, svc, horizon):
    if svc is None:
        return "P1-review"
    if finding["usage"] == "symmetric":
        return "none"
    if finding["pq"]:
        return "done"
    if finding["usage"] == "key-establishment":
        return "P1" if exposed(svc["secrecy_years"], svc["migration_years"], horizon) else "P2-kex"
    return "P2-sig"


def plan(findings, horizon=HORIZON, services=None):
    services = services or inventory.SERVICES
    rows = []
    for f in findings:
        svc = services.get(f["service"])
        x, y = (svc["secrecy_years"], svc["migration_years"]) if svc else (None, None)
        prio = classify(f, svc, horizon)
        rows.append({"priority": prio, "service": f["service"], "file": f["file"], "line": f["line"],
                     "algorithm": f["algorithm"], "usage": f["usage"], "x": x, "y": y, "z": horizon.z_years,
                     "slack": None if svc is None else x + y - horizon.z_years, "action": ACTION[prio]})
    return sorted(rows, key=lambda r: (ORDER.index(r["priority"]), -(r["slack"] or 0), r["file"], r["line"]))


def summary(rows):
    return {p: sum(1 for r in rows if r["priority"] == p) for p in ORDER if any(r["priority"] == p for r in rows)}


if __name__ == "__main__":
    import json
    for stage in ("before", "after"):
        rows = plan(inventory.scan(stage))
        print(json.dumps({"stage": stage, "summary": summary(rows)}))
        for r in rows:
            print(json.dumps(r))
