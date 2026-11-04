"""Capstone milestone 5a: parallel, checkpointed replications (the pattern of L400 lesson 20, generalised).

Each task is identified by a key; its random stream is SeedSequence(ROOT, spawn_key=key) - a function of WHAT is
computed, so a crashed and resumed run, or a different worker count, stores exactly the same results.
"""
import hashlib
import json
import multiprocessing as mp
import sqlite3

import numpy as np

import centre

ROOT, BATCH = 22, 8


class Crash(Exception):
    pass


def day_replication(task):
    """Worker (top level, picklable for spawn): one simulated day for one staffing plan."""
    key, rates, staff, mean_service, cv, patience = task
    seed = int(np.random.SeedSequence(ROOT, spawn_key=key).generate_state(1)[0])
    hours = centre.simulate(rates, staff, mean_service, cv, patience, seed=seed)
    return json.dumps(list(key)), json.dumps([[round(h["sl"], 6), round(h["abandon"], 6)] for h in hours])


def run(db, tasks, workers=2, crash_after=None):
    con = sqlite3.connect(db)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("CREATE TABLE IF NOT EXISTS results (key TEXT PRIMARY KEY, value TEXT)")
    done = {row[0] for row in con.execute("SELECT key FROM results")}
    todo = [t for t in tasks if json.dumps(list(t[0])) not in done]
    batch, stored = [], 0
    try:
        with mp.get_context("spawn").Pool(workers) as pool:
            for row in pool.imap_unordered(day_replication, todo, chunksize=2):
                batch.append(row)
                if crash_after is not None and stored + len(batch) > crash_after:
                    raise Crash(f"crashed after {stored} stored replications")
                if len(batch) == BATCH:
                    with con:
                        con.executemany("INSERT OR IGNORE INTO results VALUES (?, ?)", batch)
                    stored, batch = stored + len(batch), []
            with con:
                con.executemany("INSERT OR IGNORE INTO results VALUES (?, ?)", batch)
    finally:
        con.close()


def load(db):
    con = sqlite3.connect(db)
    rows = sorted(con.execute("SELECT key, value FROM results"))
    con.close()
    return rows


def checksum(db):
    return hashlib.sha256(repr(load(db)).encode("utf-8")).hexdigest()[:16]


def hourly_summary(db, t975=2.023):
    """Mean service level, its lower 95% bound and mean abandonment per hour, over all stored days."""
    values = np.array([json.loads(v) for _, v in load(db)])  # shape (reps, hours, 2)
    sl, ab = values[:, :, 0], values[:, :, 1]
    low = sl.mean(0) - t975 * sl.std(0, ddof=1) / np.sqrt(len(values))
    return sl.mean(0), low, ab.mean(0)
