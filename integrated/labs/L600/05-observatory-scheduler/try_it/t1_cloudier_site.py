"""Try it 1: the same two plans at a cloudier site (clear -> cloudy twice as likely per 10 min).
Predict first: does the optimised plan still beat greedy by >= 15 %? Which block suffers most?
python try_it/t1_cloudier_site.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scheduler  # noqa: E402
import weather  # noqa: E402

r = scheduler.build()
for a in (0.04, 0.08):
    clear = weather.clear_matrix(1000, len(r["slots"]), 7, a=a)
    g, lo = (weather.realised([(s, n, r["reqs"][i].priority) for s, n, i in r[k]], clear) for k in ("greedy", "local"))
    p_b = weather.p_complete(18, a=a)
    print(f"1. a={a:.2f} pi_clear={weather.pi_clear(a):.3f} | greedy {g.mean():.3f} local {lo.mean():.3f} "
          f"ratio {lo.mean() / g.mean():.3f} | Betelgeuse 180 min p={p_b:.3f} | greedy wins {(g > lo).mean():.3f}")
