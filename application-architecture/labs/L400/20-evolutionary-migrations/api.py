"""Backward-compatible API versions over the migrated schema (not lesson code).

/v2/members/{id} -> {"id", "givenName", "familyName"}
/v1/members/{id} -> {"id", "name"} rebuilt from the new columns, plus Deprecation (RFC 9745), Sunset (RFC 8594)
                    and a Link to the migration guide. Old consumers keep working after the contract step.
"""
from datetime import datetime, timezone

DEPRECATED_AT = datetime(2026, 11, 1, tzinfo=timezone.utc)
SUNSET = "Tue, 30 Mar 2027 00:00:00 GMT"


def get_member(db, member_id, version):
    given, family = db.execute("SELECT given_name, family_name FROM members WHERE id = ?", (member_id,)).fetchone()
    if version == 2:
        return {"id": member_id, "givenName": given, "familyName": family}, {}
    headers = {"Deprecation": f"@{int(DEPRECATED_AT.timestamp())}", "Sunset": SUNSET,
               "Link": '<https://library.example/docs/v2-migration>; rel="deprecation"'}
    return {"id": member_id, "name": f"{given} {family}".strip()}, headers
