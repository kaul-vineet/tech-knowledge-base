"""Lesson 17 demo: strangle the fines module. Shadow (parallel run) -> cut-over decision -> canary -> service.

Run: python app.py            (extracted service over HTTP on 127.0.0.1, base fines_service.py)
     python app.py --solution (the fixed service)
"""
import argparse
import importlib.util
import pathlib

import fines_service
from strangler import Facade, LegacyFines, ServiceFines, cutover_decision, replay
from traffic import requests

HERE = pathlib.Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution", action="store_true")
    service_module = load(HERE / "solution" / "fines_service.py", "fines_solution") \
        if parser.parse_args(argv).solution else fines_service
    (HERE / "out").mkdir(exist_ok=True)
    log = HERE / "out" / "mismatches.jsonl"
    log.write_text("", encoding="utf-8")
    server, url = service_module.start()
    try:
        facade = Facade(LegacyFines(), ServiceFines(base_url=url), mode="shadow", log_path=log)
        seconds = replay(facade, list(requests()))
        decision = cutover_decision(facade.shadow.stats)
        print(f"shadow : {facade.shadow.stats} in {seconds:.1f} s over HTTP")
        print(f"cutover: {decision}")
        if decision["ready"]:
            for pct in (10, 50):
                canary = Facade(LegacyFines(), ServiceFines(base_url=url), mode="canary", canary_pct=pct)
                replay(canary, list(requests(n=500, seed=170)))
                print(f"canary {pct}%: routed {canary.routed}")
            print("service: all fine calls go to the extracted service; legacy fine code can be deleted next")
        else:
            print(f"mismatch log: out/mismatches.jsonl ({len(facade.shadow.mismatches)} lines); first: "
                  f"{facade.shadow.mismatches[0]}")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
