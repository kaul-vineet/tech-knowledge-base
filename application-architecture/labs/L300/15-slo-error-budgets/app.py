"""Lesson 15 demo: write 3 days of request logs, compute SLIs, error budget and burn-rate alerts at 12:00 UTC.

Run: python app.py   (the log goes to out/requests.jsonl - one JSON object per request)
"""
import pathlib

import slo
from traffic import END, write_log

HERE = pathlib.Path(__file__).resolve().parent
LOG = HERE / "out" / "requests.jsonl"


def main(module=slo, log=LOG):
    log.parent.mkdir(exist_ok=True)
    write_log(log)
    records = module.parse(log.read_text(encoding="utf-8").splitlines())
    now = END.timestamp()
    print(f"log        : out/requests.jsonl, {len(records)} requests, {records[0]['ts']} .. {records[-1]['ts']}")
    for sli, target in module.SLOS.items():
        sli_3d = 1 - module.bad_ratio(module.window(records, now, 3 * 86400), sli)
        burns = {module.label(s): round(module.burn_rate(records, sli, now, s), 1) for s in (300, 3600, 21600, 259200)}
        print(f"{sli:<11}: SLI 3d {sli_3d:.4%} vs SLO {target:.1%}; budget used in 3d: "
              f"{module.budget_consumed(records, sli, now):.1%} of 30 days; burn rates {burns}")
    print(f"latency 1h : {module.latency_report(records, now)}")
    print(f"mean check : {module.latency_problems(records, now) or 'OK'}")
    print(f"alerts     : {module.alerts(records, now) or 'none'}")
    return records


if __name__ == "__main__":
    main()
