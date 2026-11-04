"""Domain events: facts in the past tense, described in asyncapi.json (AsyncAPI 3.1.0)."""
import uuid
from datetime import datetime, timezone

CHANNEL = {"LoanCreated": "loanCreated", "LoanReturned": "loanReturned", "LoanOverdue": "loanOverdue"}


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_event(event_type, data, occurred_at=None, event_id=None):
    # eventId lets consumers drop duplicates (the relay delivers at least once)
    return {"eventId": event_id or str(uuid.uuid4()), "eventType": event_type,
            "occurredAt": occurred_at or utc_now(), **data}
