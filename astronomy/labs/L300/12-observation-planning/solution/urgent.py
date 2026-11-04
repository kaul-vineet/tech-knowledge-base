"""Stretch solution (lesson 12): urgency-first scheduling.

The greedy 'lowest airmass now' rule spends 18:50 on Deneb (it stays up all evening) while Vega, Altair and
Fomalhaut set. Urgency first: at each free step pick the valid target with the FEWEST remaining valid start steps
(it is about to become unobservable); break ties by airmass. python solution/urgent.py
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("plan_fixed", HERE / "plan.py")
plan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(plan)


def block_ok(name, k, g, n_block):
    return all(plan.observable(name, k + j, g)[0] for j in (0, n_block // 2, n_block))


def schedule_urgent(site=plan.SITE, start=plan.NIGHT):
    g = plan.grid(site, start)
    n_block, n = plan.BLOCK_MIN // plan.STEP_MIN, len(g[0])
    valid = {t: [block_ok(t, k, g, n_block) if k + n_block < n else False for k in range(n)] for t in plan.TARGETS}
    k, out, todo = 0, [], set(plan.TARGETS)
    while k + n_block < n and todo:
        ready = [t for t in sorted(todo) if valid[t][k]]
        if not ready:
            k += 1
            continue
        name = min(ready, key=lambda t: (sum(valid[t][k:]), plan.observable(t, k, g)[2]))  # urgency, then airmass
        ok, alt, x, sep = plan.observable(name, k, g)
        out.append({"target": name, "start": g[0][k].strftime("%H:%M"), "alt_deg": round(alt, 1),
                    "airmass": round(x, 2), "moon_sep_deg": round(sep, 1)})
        todo.discard(name)
        k += n_block
    return out, sorted(todo)


if __name__ == "__main__":
    rows, left = schedule_urgent()
    for r in rows:
        print(json.dumps(r))
    print("unscheduled:", left)
