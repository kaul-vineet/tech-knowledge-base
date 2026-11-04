"""Build task (lesson 21): data retention that keeps the audit trail verifiable.

Shipped UNFIXED: deletes old AUDIT rows - the hash chain breaks (verify() fails) and the old prompt text stays in
the content table. Make purge() delete only CONTENT older than keep_days (unless a newer audit row still points at
it) and never touch audit rows. Return the number of content rows removed.
"""


def purge(db, today, keep_days=30):
    with db:
        cur = db.execute("DELETE FROM audit WHERE day < ?", (today - keep_days,))
    return cur.rowcount
