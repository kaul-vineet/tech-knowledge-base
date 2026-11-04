"""Rolling-deploy simulation: 4 instances serve seeded traffic while the schema changes (not lesson code).

Each phase sends 100 requests round-robin (half create, half read). Instances are upgraded one at a time.
After every phase one JSON line of fitness metrics is appended: the history the dashboard reads.
"""
import json
import random
import sqlite3

import app_versions
from flags import Flags

NAMES = ["Ada Lovelace", "Alan Turing", "Grace Hopper", "Edsger Dijkstra", "Barbara Liskov", "Prince"]


class Rollout:
    def __init__(self, migrations, history=None, seed=20):
        self.m, self.history, self.rng = migrations, history, random.Random(seed)
        self.db, self.flags, self.fleet = migrations.connect(), Flags(), [1, 1, 1, 1]
        self.ids, self.errors, self.log = [], 0, []
        for i in range(200):
            self.ids.append(app_versions.create(self.db, 1, NAMES[i % len(NAMES)]))

    def traffic(self, n=100, upgrade_to=None):
        """Serve n requests; if upgrade_to is set, replace one instance every n // 4 requests."""
        phase_errors = 0
        for i in range(n):
            if upgrade_to and i % (n // 4) == 0:
                self.fleet[self.fleet.index(min(self.fleet))] = upgrade_to
            version = self.fleet[i % len(self.fleet)]
            try:
                if i % 2:
                    app_versions.read(self.db, version, self.rng.choice(self.ids), self.flags)
                else:
                    self.ids.append(app_versions.create(self.db, version, self.rng.choice(NAMES)))
            except sqlite3.Error as exc:  # an old instance meets a schema it does not understand
                phase_errors += 1
                self.log.append(f"v{version}: {exc}")
        self.errors += phase_errors
        return phase_errors

    def record(self, step, errors):
        row = {"step": step, "errors": errors, "columns": self.m.columns(self.db),
               "fleet": "".join(f"v{v}" for v in self.fleet), "unbackfilled": self.m.missing_new_values(self.db),
               "flags_on": sum(self.flags.enabled(n) for n in self.flags.flags), "flags_expired": len(self.flags.expired())}
        if self.history:
            with open(self.history, "a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
        return row


def big_bang(migrations, history=None):
    """Change the schema in one step, then roll out v3."""
    r = Rollout(migrations, history)
    migrations.expand(r.db), migrations.backfill(r.db), migrations.contract(r.db)
    rows = [r.record("migrate all at once", 0), r.record("deploy v3", r.traffic(upgrade_to=3))]
    return r, rows


def expand_contract(migrations, history=None):
    """Expand -> deploy v2 -> backfill -> flag on -> try contract -> deploy v3 -> contract."""
    r, rows = Rollout(migrations, history), []
    migrations.expand(r.db)
    rows.append(r.record("expand", r.traffic()))
    rows.append(r.record("deploy v2 (dual write)", r.traffic(upgrade_to=2)))
    migrations.backfill(r.db)
    rows.append(r.record("backfill", r.traffic()))
    r.flags.set("read_split_name", True)
    rows.append(r.record("flag read_split_name on", r.traffic()))
    for step in ("try contract", "deploy v3 (new columns only)", "contract"):
        if step.startswith("deploy"):
            rows.append(r.record(step, r.traffic(upgrade_to=3)))
            continue
        ok, reasons = migrations.can_contract(r.db, r.fleet)  # the guard decides, not the calendar
        if ok:
            migrations.contract(r.db)
        rows.append(r.record(f"{step}: {'dropped name' if ok else 'refused (' + '; '.join(reasons) + ')'}",
                             r.traffic()))
    return r, rows
