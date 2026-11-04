"""Strangler-fig decomposition of the fines module (lesson 17 lab code).

Branch by abstraction: callers depend on FinesPort, never on the monolith. A facade routes each call to the
legacy code, to the extracted service, or to both (parallel run: legacy answers, the service is compared).
cutover_decision() turns the measured mismatch rate into a go/no-go. Run the demo: python app.py
"""
import hashlib
import json
import time
import urllib.parse
import urllib.request
from typing import Protocol

import legacy_monolith  # the ONLY new-code import of the monolith (fitness: legacy_callers.json)

CUTOVER = {"min_comparisons": 1000, "max_mismatch_rate": 0.001, "max_candidate_errors": 0}


class FinesPort(Protocol):  # branch by abstraction: the seam every caller uses
    def fine(self, days_late: int, member_type: str) -> str: ...


class LegacyFines:
    def fine(self, days_late, member_type):
        return legacy_monolith.calculate_fine(days_late, member_type)


class ServiceFines:
    """Calls the extracted service: over HTTP (base_url) or in-process (fn) for fast tests."""

    def __init__(self, base_url=None, fn=None, timeout=2.0):
        self.base_url, self.fn, self.timeout = base_url, fn, timeout

    def fine(self, days_late, member_type):
        if self.fn:
            return self.fn(days_late, member_type)
        query = urllib.parse.urlencode({"days_late": days_late, "member_type": member_type})
        with urllib.request.urlopen(f"{self.base_url}/fines?{query}", timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))["fine"]


class ParallelRun:
    """Run control (legacy) and candidate (service); ALWAYS return the control; record every difference."""

    def __init__(self, control, candidate, log_path=None):
        self.control, self.candidate, self.log_path = control, candidate, log_path
        self.stats = {"comparisons": 0, "mismatches": 0, "candidate_errors": 0}
        self.mismatches = []

    def fine(self, days_late, member_type):
        expected = self.control.fine(days_late, member_type)
        try:
            actual = self.candidate.fine(days_late, member_type)
        except Exception as exc:  # a broken candidate must never break the member's request
            self.stats["candidate_errors"] += 1
            self._record({"days_late": days_late, "member_type": member_type, "error": repr(exc)})
            return expected
        self.stats["comparisons"] += 1
        if actual != expected:
            self.stats["mismatches"] += 1
            self._record({"days_late": days_late, "member_type": member_type, "control": expected,
                          "candidate": actual})
        return expected  # users only ever see the legacy answer while we compare

    def _record(self, row):
        self.mismatches.append(row)
        if self.log_path:  # JSON lines: one mismatch per line, for diagnosis
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")

    def mismatch_rate(self):
        return self.stats["mismatches"] / self.stats["comparisons"] if self.stats["comparisons"] else 0.0


def bucket(member_id):
    """Stable 0-99 bucket per member: a canary member stays in the canary on every request."""
    return int(hashlib.sha256(member_id.encode("utf-8")).hexdigest(), 16) % 100


class Facade:
    """The strangler facade. mode: legacy | shadow (parallel run) | canary (pct % to service) | service."""

    def __init__(self, legacy, service, mode="legacy", canary_pct=0, log_path=None):
        self.legacy, self.service, self.mode, self.canary_pct = legacy, service, mode, canary_pct
        self.shadow = ParallelRun(legacy, service, log_path)
        self.routed = {"legacy": 0, "service": 0}

    def fine(self, member_id, days_late, member_type):
        if self.mode == "service" or (self.mode == "canary" and bucket(member_id) < self.canary_pct):
            self.routed["service"] += 1
            return self.service.fine(days_late, member_type)
        self.routed["legacy"] += 1
        if self.mode == "shadow":
            return self.shadow.fine(days_late, member_type)
        return self.legacy.fine(days_late, member_type)


def cutover_decision(stats, criteria=CUTOVER):
    """Cut-over criteria as code: enough evidence, mismatch rate under budget, no candidate errors."""
    rate = stats["mismatches"] / stats["comparisons"] if stats["comparisons"] else 1.0
    reasons = []
    if stats["comparisons"] < criteria["min_comparisons"]:
        reasons.append(f"only {stats['comparisons']} comparisons (< {criteria['min_comparisons']})")
    if rate > criteria["max_mismatch_rate"]:
        reasons.append(f"mismatch rate {rate:.2%} > {criteria['max_mismatch_rate']:.2%}")
    if stats["candidate_errors"] > criteria["max_candidate_errors"]:
        reasons.append(f"{stats['candidate_errors']} candidate errors")
    return {"ready": not reasons, "mismatch_rate": round(rate, 4), "reasons": reasons}


def replay(facade, requests):
    """Send seeded traffic through the facade; returns elapsed seconds (informational only)."""
    start = time.perf_counter()
    for r in requests:
        facade.fine(r["member_id"], r["days_late"], r["member_type"])
    return time.perf_counter() - start
