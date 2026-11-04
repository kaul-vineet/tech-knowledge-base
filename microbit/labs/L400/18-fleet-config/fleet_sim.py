"""Run a fleet rollout on stub boards (CPython only, simulated time, seeded 10 % loss per link).

Scenario: at t = 0 roll out v2 (good: i=500;th=28;g=18); at t = 15 s roll out v3 (bad: g=99, a radio
group the gateway is not on - the device goes deaf). Every tick checks the fitness invariant: each
device runs a version the gateway holds an acknowledgement for.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_edge"))
sys.path.insert(0, str(HERE))
from simnet import LinkAir  # noqa: E402
from labtest import load_boards  # noqa: E402
import radio as radio_stub  # noqa: E402
from fleet import Fleet  # noqa: E402

DEVICES = ["n%d" % i for i in range(1, 7)]
GOOD, BAD = (2, "i=500;th=28;g=18"), (3, "i=500;th=28;g=99")


def run(filename="solution.py", strategy="staged", loss=0.10, seed=18, end_ms=40000, plan=None, sources=None):
    air = LinkAir(default_loss=loss, seed=seed)
    boards = load_boards(str(HERE), names=DEVICES, filename=filename, air=air, sources=sources)
    gw_clock = [0]
    gw = radio_stub.Endpoint(air, "gw", lambda: gw_clock[0])
    gw.config(group=18, queue=30)
    lab = boards[0].lab
    fleet = Fleet(gw, DEVICES, strategy, encode=lab.encode, decode=lab.decode)
    states = [b.lab.new_state(b.name) for b in boards]
    plan = plan or {0: GOOD, 15000: BAD}
    m = {"unacked_ticks": 0, "deaf_device_ms": 0, "max_on_bad": 0, "jobs": []}
    for t in range(0, end_ms, 10):
        air.now = gw_clock[0] = t
        if t in plan:
            if fleet.job:
                m["jobs"].append(dict((k, fleet.job[k]) for k in ("ver", "status", "start", "end")))
            fleet.rollout(plan[t][0], plan[t][1], t)
        fleet.step(t)
        for b, st in zip(boards, states):
            b.lab.step(st, t)
            b.mb.sleep(10)
            v = st["cfg"]["v"]
            if v not in fleet.acked[b.name]:
                m["unacked_ticks"] += 1                   # the fitness function counts these
            if st["cfg"]["g"] != 18:
                m["deaf_device_ms"] += 10
        m["max_on_bad"] = max(m["max_on_bad"], sum(st["cfg"]["v"] == BAD[0] for st in states))
    m["jobs"].append(dict((k, fleet.job[k]) for k in ("ver", "status", "start", "end")))
    m["final"] = dict((b.name, st["cfg"]["v"]) for b, st in zip(boards, states))
    m["final_group"] = dict((b.name, st["cfg"]["g"]) for b, st in zip(boards, states))
    m["gw_sent"] = fleet.sent
    return m, fleet


def line(filename, strategy, m):
    jobs = ", ".join("v%(ver)d %(status)s @%(end)s" % j for j in m["jobs"])
    return json.dumps({"device": filename, "strategy": strategy, "unacked_ticks": m["unacked_ticks"],
                       "max_on_bad": m["max_on_bad"], "deaf_device_ms": m["deaf_device_ms"],
                       "jobs": jobs, "final": "".join(str(v) for v in m["final"].values()),
                       "gw_sent": m["gw_sent"]})


if __name__ == "__main__":
    for f, s in (("config_agent.py", "push-all"), ("solution.py", "push-all"), ("solution.py", "staged")):
        m, fleet = run(f, s)
        print(line(f, s, m))
