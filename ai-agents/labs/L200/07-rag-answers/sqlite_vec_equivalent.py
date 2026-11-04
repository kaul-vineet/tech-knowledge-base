"""Equivalent (pending-ci): the same cosine top-k inside SQLite with the sqlite-vec extension (pip install sqlite-vec==0.1.9)."""
import sqlite3

import numpy as np
import sqlite_vec


def top_k_sqlite_vec(chunks, vectors, query_vec, k=2):
    db = sqlite3.connect(":memory:")
    db.enable_load_extension(True)  # missing on some Python builds (e.g. macOS system Python) -> AttributeError
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    db.execute(f"create virtual table vec_chunks using vec0(chunk_id integer primary key, "
               f"embedding float[{vectors.shape[1]}] distance_metric=cosine)")
    for i, v in enumerate(vectors):
        db.execute("insert into vec_chunks(chunk_id, embedding) values (?, ?)", (i, v.astype(np.float32)))
    rows = db.execute(f"select chunk_id, distance from vec_chunks where embedding match ? and k = {int(k)}",
                      (query_vec.astype(np.float32),)).fetchall()
    db.close()
    return [(chunks[i][0], round(1 - d, 3)) for i, d in rows]  # cosine distance -> similarity
