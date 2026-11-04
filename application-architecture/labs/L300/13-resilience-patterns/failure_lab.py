"""Lesson 13 failureLab: the catalogue hangs; 3 waves of 8 borrows arrive. Shared pool vs one bulkhead each.

Run: python failure_lab.py   (base loans_service.py first, then solution/loans_service.py)
"""
import importlib.util
import json
import pathlib
import threading
import time
from collections import Counter

import loans_service as base
from deps import Catalogue, Members

HERE = pathlib.Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_waves(module, catalogue, waves=3, per_wave=8, gap_s=0.25, log=lambda record: None):
    """Fire `per_wave` concurrent borrows every `gap_s` seconds; log one JSON record per request."""
    service = module.build_service(Members(), catalogue, log=log)
    records, lock = [], threading.Lock()

    def one(wave, i):
        started, error, result = time.perf_counter(), None, None
        try:
            result = service.borrow(f"m{i}", f"b{wave}-{i}")
        except Exception as exc:  # the request failed: record the error type, the log is the diagnosis
            error = f"{type(exc).__name__}: {exc}"
        record = {"evt": "request", "wave": wave, "ok": error is None, "error": error,
                  "degraded": bool(result and result["degraded"]),
                  "ms": round((time.perf_counter() - started) * 1000, 1), "pools": service.pools()}
        with lock:
            records.append(record)
        log(record)

    threads = []
    for wave in range(1, waves + 1):
        for i in range(per_wave):
            threads.append(threading.Thread(target=one, args=(wave, i)))
            threads[-1].start()
        time.sleep(gap_s)
    for thread in threads:
        thread.join()
    catalogue.release()
    service.close()
    return records


def summary(records):
    by_wave = Counter((r["wave"], "ok" if r["ok"] else r["error"].split(":")[0]) for r in records)
    return {wave: {k: v for (w, k), v in sorted(by_wave.items()) if w == wave} for wave in sorted({r["wave"] for r in records})}


def main():
    for label, module in [("base     (one shared pool of 8)", base),
                          ("solution (members 4 + catalogue bulkhead 4)",
                           load(HERE / "solution" / "loans_service.py", "loans_service_solution"))]:
        records = run_waves(module, Catalogue(mode="slow"))
        ok = sum(r["ok"] for r in records)
        print(f"{label}: {ok}/{len(records)} borrows ok, {sum(r['degraded'] for r in records)} with fallback title")
        print(f"    per wave: {summary(records)}")
        failed = next((r for r in records if not r["ok"]), None)
        if failed:
            print(f"    first failed request log: {json.dumps(failed, sort_keys=True)}")


if __name__ == "__main__":
    main()
