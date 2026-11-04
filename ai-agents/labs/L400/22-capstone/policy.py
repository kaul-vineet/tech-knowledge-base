"""Deterministic core of the capstone: severity and actions from metrics (lesson 20's rule, applied to incidents).

Thresholds: 14.4 = the SRE Workbook fast-burn paging rate (2 % of a 30-day budget in 1 h), as used in the
application-architecture SLO lesson. Nothing a model says is an input to these functions.
"""
ACTIONS = {"SEV1": ["page_oncall", "open_incident_doc"], "SEV2": ["page_oncall"], "SEV3": ["open_ticket"], "SEV4": []}
KNOWN_ACTIONS = {"page_oncall", "open_incident_doc", "open_ticket", "rollback_deploy"}
NEEDS_APPROVAL = {"rollback_deploy"}
SEVERITIES = ["SEV1", "SEV2", "SEV3", "SEV4"]


def severity(m):
    if m["users_affected_pct"] >= 25 or m["error_rate"] >= 20:
        return "SEV1"
    if m["users_affected_pct"] >= 5 or m["burn_rate"] >= 14.4:
        return "SEV2"
    if m["burn_rate"] >= 1 or m["error_rate"] >= 2:
        return "SEV3"
    return "SEV4"


def decide(metrics, deploy_age_min):
    sev = severity(metrics)
    actions = list(ACTIONS[sev])
    if sev in ("SEV1", "SEV2") and deploy_age_min <= 60:
        actions.append("rollback_deploy")  # proposed by code; a person must approve it
    return {"severity": sev, "actions": actions}
