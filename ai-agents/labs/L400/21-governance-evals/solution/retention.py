"""Solution (lesson 21 build task): delete the content, keep the chain of hashes (who / what / when)."""


def purge(db, today, keep_days=30):
    cutoff = today - keep_days
    with db:
        cur = db.execute("DELETE FROM content WHERE day < ? AND hash NOT IN "
                         "(SELECT content_hash FROM audit WHERE day >= ?)", (cutoff, cutoff))
    return cur.rowcount
