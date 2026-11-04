"""tryIt experiments for lesson 8 (run: python try_it.py)."""
import mmc_queue as mq

# 1. Pooling: three desks with their OWN lines (3 x M/M/1, each gets 1/3 of the patients) vs one shared line.
separate = mq.simulate(200_000, c=1, lam=mq.LAM / 3)["Wq"]
shared = mq.simulate(200_000)["Wq"]
print(f"3 separate lines: Wq={separate:.2f} min | 1 shared line, 3 desks: Wq={shared:.2f} min | "
      f"formula {mq.erlang_c(1, mq.LAM / 3)['Wq']:.2f} vs {mq.erlang_c()['Wq']:.2f}")

# 2. 10% more patients (lam 2.4 -> 2.64) with the same 3 desks. Predict: Wq +10%?
for lam in (2.4, 2.64):
    print(f"lam={lam}: utilisation {lam / 3:.0%}, simulated Wq={mq.simulate(200_000, lam=lam)['Wq']:.2f} min, "
          f"Erlang C Wq={mq.erlang_c(lam=lam)['Wq']:.2f} min")
