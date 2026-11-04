"""The deterministic core (lesson 20): refund decisions as a pure function of facts from systems of record.

No model output is an input here. Rules are checked in order; the first match decides.
"""
ALLOWED_ACTIONS = ("approve_auto", "escalate", "deny")
AUTO_LIMIT, WINDOW_DAYS, MAX_PRIOR = 50.0, 30, 3


def decide(f):
    """f: paid, amount_requested, delivered, days_since_delivery, prior_refunds_90d (from the order system)."""
    if f["amount_requested"] > f["paid"]:
        return {"action": "deny", "amount": 0.0, "rule": "R1 more than was paid"}
    if not f["delivered"]:
        return {"action": "escalate", "amount": 0.0, "rule": "R2 not delivered yet: carrier check"}
    if f["days_since_delivery"] > WINDOW_DAYS:
        return {"action": "deny", "amount": 0.0, "rule": "R3 outside the 30-day window"}
    if f["prior_refunds_90d"] >= MAX_PRIOR:
        return {"action": "escalate", "amount": 0.0, "rule": "R4 3+ refunds in 90 days"}
    if f["amount_requested"] <= AUTO_LIMIT:
        return {"action": "approve_auto", "amount": float(f["amount_requested"]), "rule": f"R5 up to {AUTO_LIMIT:.2f} within policy"}
    return {"action": "escalate", "amount": 0.0, "rule": f"R6 over {AUTO_LIMIT:.2f} needs a person"}


def combine(decision, claims):
    """Model claims are untrusted: they may only move approve_auto -> escalate (towards a human), never away."""
    if decision["action"] == "approve_auto" and claims and claims.get("threat") is True:
        return {"action": "escalate", "amount": 0.0, "rule": "R7 customer threatens a chargeback: a person replies"}
    return decision
