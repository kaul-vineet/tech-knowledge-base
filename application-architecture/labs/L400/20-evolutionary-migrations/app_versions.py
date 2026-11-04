"""Three versions of the members code that run side by side during a rolling deploy (not lesson code).

v1: reads/writes name only. v2: dual-writes name + new columns; reads new columns when the release flag is on.
v3: new columns only (safe after the contract step).
"""
from migrations import split


def create(db, version, full_name):
    if version == 1:
        return db.execute("INSERT INTO members (name) VALUES (?)", (full_name,)).lastrowid
    given, family = split(full_name)
    if version == 2:  # dual write: old readers and new readers both see the member
        return db.execute("INSERT INTO members (name, given_name, family_name) VALUES (?, ?, ?)",
                          (full_name, given, family)).lastrowid
    return db.execute("INSERT INTO members (given_name, family_name) VALUES (?, ?)", (given, family)).lastrowid


def read(db, version, member_id, flags):
    if version == 1 or (version == 2 and not flags.enabled("read_split_name")):
        (name,) = db.execute("SELECT name FROM members WHERE id = ?", (member_id,)).fetchone()
        return split(name)
    return db.execute("SELECT given_name, family_name FROM members WHERE id = ?", (member_id,)).fetchone()
