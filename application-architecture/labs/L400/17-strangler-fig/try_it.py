"""Try it (lesson 17): plant a new caller of the monolith; try to cut over on too little evidence.

Run: python try_it.py   (scratch copy in .tryit-work/, deleted after)
"""
import shutil
import time

import fitness_legacy
from app import HERE, load
from strangler import Facade, LegacyFines, ServiceFines, cutover_decision, replay
from traffic import requests

WORK = HERE / ".tryit-work"


def try_1_new_legacy_caller():
    WORK.mkdir(exist_ok=True)
    for path in list(HERE.glob("*.py")) + [HERE / "legacy_callers.json"]:
        shutil.copy(path, WORK / path.name)
    (WORK / "new_feature.py").write_text(
        "from legacy_monolith import calculate_fine  # 'just reuse the old rule'\n", encoding="utf-8")
    print(f"[1] new_feature.py imports the monolith -> {fitness_legacy.gate(WORK, WORK / 'legacy_callers.json')}")


def try_2_too_little_evidence():
    solution = load(HERE / "solution" / "fines_service.py", "fines_solution")
    facade = Facade(LegacyFines(), ServiceFines(fn=solution.fine_for), mode="shadow")
    replay(facade, list(requests(n=300)))
    print(f"[2] fixed service, 300 shadow requests -> {cutover_decision(facade.shadow.stats)}")


if __name__ == "__main__":
    try:
        try_1_new_legacy_caller()
        try_2_too_little_evidence()
    finally:
        for _ in range(5):  # retry: some network mounts need a second pass
            shutil.rmtree(WORK, ignore_errors=True)
            if not WORK.exists():
                break
            time.sleep(0.5)
