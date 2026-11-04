"""tryIt for the capstone (one star each, a few seconds).
1. Detrend with a 0.25-day window instead of 0.75 d: what happens to S03's 4.2-hour transits?
2. Switch the odd/even test off (threshold = infinity): does the eclipsing binary S05 slip through?
"""
import run_capstone  # noqa: F401  (makes sure data/ exists)
import make_data
import pipeline

if __name__ == "__main__":
    if not (run_capstone.DATA / "S12.csv").exists():
        make_data.write(run_capstone.DATA)
    t, f, _ = pipeline.load(run_capstone.DATA / "S03.csv")
    for w in (0.75, 0.25):
        _, c = pipeline.bls(t, pipeline.detrend(t, f, window=w))
        print(f"1. S03 window {w} d: period {c['period_d']:.4f} d, depth {c['depth'] * 1e6:.0f} ppm, SNR {c['snr']}")
    t, f, _ = pipeline.load(run_capstone.DATA / "S05.csv")
    _, c = pipeline.bls(t, pipeline.detrend(t, f))
    flat = pipeline.detrend(t, f, mask=pipeline.in_transit(t, c))
    for sig in (3.0, float("inf")):
        pipeline.ODD_EVEN_SIG = sig
        print(f"2. S05 odd/even threshold {sig} sigma ->", pipeline.vet(t, flat, c))
