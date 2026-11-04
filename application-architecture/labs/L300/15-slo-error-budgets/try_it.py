"""Try it (lesson 15): when does the latency page fire, and what does a smaller tail do? Run: python try_it.py"""
from datetime import datetime, timezone

from failure_lab import HERE, load
from traffic import END, INCIDENT_START, lines

slo = load(HERE / "solution" / "slo.py", "slo_solution")


def try_1_time_to_page():
    records = slo.parse(lines())
    now = INCIDENT_START.timestamp()
    while now <= END.timestamp() and not slo.alerts(records, now):
        now += 60
    fired = slo.alerts(records, now)
    at = datetime.fromtimestamp(now, timezone.utc).strftime("%H:%M")
    print(f"[1] incident starts 10:30 -> first alert at {at} UTC "
          f"({(now - INCIDENT_START.timestamp()) / 60:.0f} min later): {fired}")


def try_2_smaller_tail():
    records = slo.parse(lines(slow_share=0.05))
    now = END.timestamp()
    burns = {slo.label(s): round(slo.burn_rate(records, "latency", now, s), 1) for s in (300, 3600, 21600, 259200)}
    print(f"[2] 5% slow instead of 20%: latency burn rates {burns}; alerts {slo.alerts(records, now) or 'none'}")


if __name__ == "__main__":
    try_1_time_to_page()
    try_2_smaller_tail()
