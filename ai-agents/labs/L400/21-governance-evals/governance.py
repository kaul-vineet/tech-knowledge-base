"""Governance for a model in production: pin by digest, gate upgrades on evals + red team, watch drift,
keep a tamper-evident audit trail, and write the upgrade decision record from measured numbers."""
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
L300 = HERE.parent.parent / "L300"
_saved = list(sys.path)
sys.path[:0] = [str(HERE), str(L300 / "12-eval-golden-set"), str(L300 / "16-red-team-injection")]
import eval_gate  # noqa: E402  (lesson 12: golden set + regression gate)
import run_suite  # noqa: E402  (lesson 16: red-team suite)
sys.path[:] = _saved  # do not leak other labs' folders: their test files share names with ours

CRITICAL_99 = {1: 6.635, 4: 13.277}  # chi-square critical values, alpha = 0.01 (NIST/SEMATECH e-Handbook table)
GENESIS = "0" * 64


def pin_check(base_url, lock):
    """Refuse to start if a pinned model name now points at different weights (a silent re-tag or re-pull)."""
    tags = requests.get(base_url.removesuffix("/v1") + "/api/tags", timeout=10).json()["models"]
    digests = {m["name"]: m["digest"] for m in tags}
    return [f"{name}: pinned {d[:12]}, server has {(digests.get(name) or 'missing')[:12]}"
            for name, d in lock.items() if digests.get(name) != d]


def classify(tickets, base_url, model):
    prompt = (L300 / "12-eval-golden-set" / "prompts" / "v1.txt").read_text(encoding="utf-8")
    seen = {}
    for t in set(tickets):  # production replay: one call per distinct ticket
        seen[t] = json.loads(eval_gate.run_case(prompt, {"ticket": t}, base_url, model))
    return [seen[t] for t in tickets]


def chi_square(baseline, window, keys):
    """Goodness of fit of the window's counts against the baseline proportions; alarm if > critical (df = k - 1)."""
    n, total = len(window), len(baseline)
    b, w = Counter(baseline), Counter(window)
    stat = sum((w[k] - n * b[k] / total) ** 2 / (n * b[k] / total) for k in keys if b[k])
    df = sum(1 for k in keys if b[k]) - 1
    return round(stat, 2), df, stat > CRITICAL_99[df]


def category_drift(base_url, model, baseline_tickets, window_tickets):
    """Input drift without labels: compare the category mix the pinned model assigns this week with the baseline."""
    keys = sorted(eval_gate.FIELDS["category"])
    old = [o["category"] for o in classify(baseline_tickets, base_url, model)]
    return chi_square(old, [o["category"] for o in classify(window_tickets, base_url, model)], keys)


class AuditLog:
    """Hash-chained, append-only audit trail. Content (prompts, answers) lives in its own table so retention can
    delete it while the chain of hashes - who did what, when - stays verifiable."""

    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.executescript("""CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY, day REAL, actor TEXT,
            event TEXT, content_hash TEXT, prev_hash TEXT, hash TEXT);
            CREATE TABLE IF NOT EXISTS content (hash TEXT PRIMARY KEY, day REAL, text TEXT);""")

    def append(self, day, actor, event, content=""):
        day = float(day)  # hashed exactly as SQLite returns it (REAL)
        prev = (self.db.execute("SELECT hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone() or [GENESIS])[0]
        seq = self.db.execute("SELECT COALESCE(MAX(seq), 0) + 1 FROM audit").fetchone()[0]
        chash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        row_hash = hashlib.sha256((prev + json.dumps([seq, day, actor, event, chash])).encode("utf-8")).hexdigest()
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO content VALUES (?, ?, ?)", (chash, day, content))
            self.db.execute("INSERT INTO audit VALUES (?, ?, ?, ?, ?, ?, ?)", (seq, day, actor, event, chash, prev, row_hash))

    def verify(self):
        """(ok, first bad seq): recompute every link; any edited, deleted or reordered row breaks the chain."""
        prev = GENESIS
        for seq, day, actor, event, chash, stored_prev, stored in self.db.execute("SELECT * FROM audit ORDER BY seq"):
            expect = hashlib.sha256((prev + json.dumps([seq, day, actor, event, chash])).encode("utf-8")).hexdigest()
            if stored_prev != prev or stored != expect:
                return False, seq
            prev = stored
        return True, None


def evaluate_candidate(base_url, pinned, candidate, stream):
    report = eval_gate.evaluate(L300 / "12-eval-golden-set" / "prompts" / "v1.txt", None, base_url, candidate)
    base = eval_gate.evaluate(L300 / "12-eval-golden-set" / "prompts" / "v1.txt", None, base_url, pinned)
    reasons = eval_gate.gate(report, base)
    red = [r for r in run_suite.run_all(base_url=base_url, model=candidate) if r["mode"] == "protected"]
    old = [o["priority"] for o in classify(stream, base_url, pinned)]
    new = [o["priority"] for o in classify(stream, base_url, candidate)]
    stat, df, alarm = chi_square(old, new, ["high", "normal"])
    regressions = [cid for cid, r in report["results"].items() if base["results"][cid]["pass"] and not r["pass"]]
    return {"pinned": pinned, "candidate": candidate, "passed": report["passed"], "total": report["total"],
            "pass_rate": report["pass_rate"], "regressions": regressions, "gate_reasons": reasons,
            "redteam_safe": sum(r["safe"] for r in red), "redteam_total": len(red),
            "drift_chi2": stat, "drift_df": df, "drift_alarm": alarm}


def decide_upgrade(r):
    """The decision is code: every check must pass. The model may draft prose, never this line."""
    ok = not r["gate_reasons"] and r["redteam_safe"] == r["redteam_total"] and not r["drift_alarm"]
    return "ACCEPT" if ok else "REJECT"


def fill_record(r, context=None, template=HERE / "MODEL-UPGRADE-TEMPLATE.md"):
    values = {**{k: str(v) for k, v in r.items()}, "decision": decide_upgrade(r),
              "pass_pct": f"{r['pass_rate']:.0%}", "regression_count": str(len(r["regressions"])),
              "context": context or f"Candidate {r['candidate']} was compared with the pinned {r['pinned']}."}
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], template.read_text(encoding="utf-8"))


if __name__ == "__main__":
    sys.path.insert(0, str(HERE.parent))
    import fake_server_l400  # the demo runs its own fake server so it can re-tag a model
    server, url = fake_server_l400.start_in_thread()
    lock = json.loads((HERE / "models.lock.json").read_text(encoding="utf-8"))
    print("pin check at start   :", pin_check(url, lock) or "OK")
    server.retag("fake-model:latest", "fake-model:v2")  # someone ran a pull: same name, new weights
    print("pin check after pull :", pin_check(url, lock))
    stream = [c["ticket"] for c in eval_gate.load_cases()] * 10
    report = evaluate_candidate(url, "fake-model", "fake-model:v2", stream)
    print(json.dumps(report))
    print("decision:", decide_upgrade(report))
    shipping = [c["ticket"] for c in eval_gate.load_cases() if c["expect"]["category"] == "shipping"]
    print("input drift, same mix      (chi2, df, alarm):", category_drift(url, "fake-model", stream, stream[:100]))
    print("input drift, shipping surge (chi2, df, alarm):", category_drift(url, "fake-model", stream, stream[:100] + shipping * 10))
    (HERE / "upgrade-record.md").write_text(fill_record(report), encoding="utf-8")
    print("decision record written: upgrade-record.md")
