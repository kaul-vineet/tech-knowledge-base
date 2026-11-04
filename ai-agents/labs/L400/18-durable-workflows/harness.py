"""Helper for lesson 18: drive a workflow to the end through crashes, and sweep every crash point."""
import tempfile
from pathlib import Path

import requests

import durable
import payments_service
from naive_workflow import run_naive

HERE = Path(__file__).resolve().parent
CRASH_POINTS = [p for s in durable.STEPS for p in (f"before:{s}", f"after:{s}")] + ["after_model:propose", "after_effect:refund"]


def drive(make_engine, wf_id, crash_at=(), approver="alice"):
    """Run to the end like an operator would: restart after every crash, approve when the workflow waits."""
    engine, crashes = make_engine(crash_at), []
    for _ in range(20):
        try:
            status = engine.run(wf_id)
        except durable.Crash as c:
            crashes.append(str(c))
            engine.db.close()
            engine = make_engine(())  # a new process: same SQLite file, nothing in memory
            continue
        if status != "waiting":
            return status, crashes, engine
        engine.signal(wf_id, "approve", approver)
    raise RuntimeError("did not finish")


def sweep(variant, base_url, model="fake-model", server=None):
    """One row per crash point: refunds, notifications and model calls after recovery."""
    rows = []
    for point in CRASH_POINTS:
        pay, pay_url = payments_service.start_in_thread()
        before = server.stats["requests"] if server else 0
        if variant == "naive":
            run_naive("A-1001", pay_url, base_url, model, crash_at={point})
            status, notes = "done", None
        else:
            with tempfile.TemporaryDirectory(dir=HERE) as d:
                db = Path(d) / "wf.db"
                make = lambda crash: durable.Engine(db, pay_url, base_url, model, crash_at=crash, use_keys=(variant == "durable"))
                make(()).start("wf-1", "A-1001")
                status, _, eng = drive(make, "wf-1", crash_at={point})
                notes = eng.db.execute("SELECT COUNT(*) FROM outbox WHERE kind = 'refund_done'").fetchone()[0]
                eng.db.close()
        refunds = len(requests.get(f"{pay_url}/refunds", timeout=5).json())
        pay.shutdown()
        pay.server_close()
        rows.append({"variant": variant, "crash_at": point, "status": status, "refunds": refunds, "notifications": notes,
                     "model_calls": (server.stats["requests"] - before) if server else None})
    return rows
