"""The simulation the agent may experiment on: the L200 #10 help desk (M/M/1 with a Monday backlog).

One run = waits(customers) from warmup.py with a seed derived from (root seed, arm, replication) through a
SeedSequence spawn key (the L400 #20 pattern): replication i of arm k always gets the same stream, so a run can be
re-created from its registry record alone, and extending 3 -> 40 replications re-uses the first 3 unchanged.
"""
import hashlib
import math
import platform

import numpy as np

import _kb

warmup = _kb.load("warmup")
NAME = "helpdesk-mm1"
VERSION = hashlib.sha256(_kb.source_path("warmup").read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:12]
DEFAULTS = {"backlog": 30, "customers": 2000, "warmup": 200}  # warm-up 200 > the 169 that L200 #10's Welch plot proposes
ENVIRONMENT = f"python {platform.python_version()} numpy {np.__version__} {platform.machine()}"


def seed_for(root, arm, rep):
    return int(np.random.SeedSequence(root, spawn_key=(arm, rep)).generate_state(1)[0])


def run_once(params, seed):
    """Mean wait (minutes) after deleting the warm-up. math.fsum: the result does not depend on summation order."""
    p = {**DEFAULTS, **params}
    w = warmup.waits(int(p["customers"]), seed, lam=p["lam"], mu=p["mu"], backlog=int(p["backlog"]))
    tail = w[int(p["warmup"]):]
    return math.fsum(tail.tolist()) / len(tail)


def cost(params):
    """Budget unit = simulated customers (the loop count; run time is proportional to it)."""
    return int({**DEFAULTS, **params}["customers"])


def mm1_wq(lam, mu):
    return _kb.load("vv").formula(lam, mu)  # L100 #6: Wq = lam / (mu (mu - lam))
