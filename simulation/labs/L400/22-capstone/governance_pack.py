"""Capstone milestone 6a: the governance pack - model card claims checked against this run's evidence.

Reuses L400 lesson 21's line-ending-safe sha256(). Claims that are wider or better than the evidence block
publication; a recommendation outside the validated envelope is published only with a REVIEW flag.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent / "21-governance-vv"))
from governance import sha256  # noqa: E402  (lesson 21)

CARD = HERE / "model_card.json"
VERSIONED = ("centre.py", "pipeline.py", "data/history_kpis.jsonl")


def evidence_hashes():
    return {name: sha256(HERE / name) for name in VERSIONED}


def check(card, ev):
    findings = []
    if card["inputs"]["service_distribution"] != ev["inputs"]["service_dist"]:
        findings.append("service distribution claim differs from the fitted one")
    for key in ("sl_mae_pp", "abandon_mae_pp"):
        if card["validation"][key] < ev["validation"][key]:
            findings.append(f"claims {key} {card['validation'][key]}, holdout shows {ev['validation'][key]}")
    if card["validity_envelope"]["max_rate_per_min"] > max(ev["inputs"]["rates"]) * 1.05:
        findings.append("envelope claims rates the history never showed")
    for name, digest in evidence_hashes().items():
        if card["versions"].get(name) != digest:
            findings.append(f"{name} changed since the card was written: re-run and bump model_version")
    return findings


def review_flags(card, recommended_rates):
    """Not a failure: the decision stands, but a human must sign off anything outside the envelope."""
    limit = card["validity_envelope"]["max_rate_per_min"]
    return [f"hour {8 + h}:00 plans for {r:.2f} calls/min > validated {limit}" for h, r in enumerate(recommended_rates)
            if r > limit]


def load_card():
    return json.loads(CARD.read_text(encoding="utf-8"))
