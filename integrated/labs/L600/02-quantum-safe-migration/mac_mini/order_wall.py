"""Experiment 3 - where is the memory wall for order finding on THIS machine? (numpy statevector, shor_sim.py)

python mac_mini/order_wall.py --here            N = 15, 21, 35 (12-18 qubits) + the predicted wall for 16/24/32/64 GB
python mac_mini/order_wall.py                   run every N that fits this Mac's RAM budget, stop before the wall
python mac_mini/order_wall.py --ram 24          predict for a 24 GB Mac (simulated RAM; runs only what fits here too)
python mac_mini/order_wall.py --max-n 143       CI size: run N <= 143 only (24 qubits)

Order finding for an n-bit N uses t = 2n counting + n work qubits = 3n qubits, so every extra bit of N multiplies the
state by 2^3 = 8. The script MEASURES what shor_sim really allocates per amplitude (tracemalloc peak / 2^qubits at the
small sizes: the state, the index arrays and the permuted copy of controlled_mult) and computes the wall from that
figure and the RAM budget of integrated/mac-mini/scripts/mac_profile.py - not from the 16 B/amplitude textbook value.
Scope (estimates.py rule): these are claims about toy N on a classical simulator only, never about RSA-2048.
"""
import argparse
import math
import resource
import sys
import time
import tracemalloc

import _mac
import shor_sim

SEMIPRIMES = [15, 21, 35, 77, 143, 323, 899, 1763, 3599]   # n = 4..12 bits (products of two odd primes)


def bits(modulus):
    return math.ceil(math.log2(modulus))


def qubits(modulus):
    return 3 * bits(modulus)


def pick_a(modulus):
    """Smallest a whose order is even and a^(r/2) != -1 mod N (so a successful run can split N)."""
    for a in range(2, modulus):
        if math.gcd(a, modulus) != 1:
            continue
        r = shor_sim.l25.order(a, modulus)
        if r % 2 == 0 and pow(a, r // 2, modulus) != modulus - 1:
            return a
    raise ValueError(f"no usable a for {modulus}")


def max_rss_bytes():
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss if sys.platform == "darwin" else rss * 1024   # macOS reports bytes, Linux kilobytes


def run_one(modulus):
    a = pick_a(modulus)
    tracemalloc.start()
    t0 = time.perf_counter()
    r = shor_sim.shor(modulus, a)
    secs = time.perf_counter() - t0
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    q = qubits(modulus)
    return {"N": modulus, "a": a, "bits": bits(modulus), "qubits": q, "order_r": r["order_r"],
            "p_success_per_run": r["p_success_per_run"], "factors": r["factors"], "seconds": round(secs, 2),
            "peak_traced_B": peak, "bytes_per_amplitude": round(peak / 2 ** q, 1), "max_rss_B": max_rss_bytes()}


def wall(bytes_per_amp, budget_gb):
    """Largest semiprime in the list whose measured memory fits the budget, and the first one that does not."""
    fits = [m for m in SEMIPRIMES if bytes_per_amp * 2 ** qubits(m) <= budget_gb * 1e9]
    last = fits[-1] if fits else None
    nxt = next((m for m in SEMIPRIMES if m not in fits), None)
    return {"largest_N": last, "qubits": qubits(last) if last else None,
            "need_GB": round(bytes_per_amp * 2 ** qubits(last) / 1e9, 3) if last else None,
            "next_N": nxt, "next_need_GB": round(bytes_per_amp * 2 ** qubits(nxt) / 1e9, 2) if nxt else None}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true", help="N = 15, 21, 35 only")
    ap.add_argument("--ram", type=float, help="simulate this RAM (GiB) for the prediction")
    ap.add_argument("--max-n", type=int, help="run no N above this (CI: bounded time); the prediction is unchanged")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    rows = []
    calibrate = [15, 21, 35]
    for m in calibrate:
        rows.append(run_one(m))
        _mac.emit({"run": "order finding", **rows[-1]}, a.out)
    k = max(r["bytes_per_amplitude"] for r in rows if r["qubits"] >= 15)   # small sizes are dominated by overhead
    pred = {g: wall(k, _mac.mac_profile().recommend(_mac.mac_profile().ram_from_gib(g))["budget_gb"])
            for g in (16, 24, 32, 64)}
    _mac.emit({"wall": "predicted from measured bytes/amplitude", "bytes_per_amplitude": k,
               "textbook_bytes_per_amplitude": 16, "by_ram_GB": pred,
               "maths": "need(N) = bytes_per_amplitude x 2^(3 x ceil(log2 N)); fits if need <= mac_profile budget_gb"},
              a.out)
    if not a.here:
        prof = _mac.profile(a.ram)  # --ram predicts for another Mac, but never runs past THIS machine's budget
        target = wall(k, min(prof["budget_gb"], _mac.profile(None)["budget_gb"]))
        for m in SEMIPRIMES:
            if m in calibrate or target["largest_N"] is None or m > target["largest_N"] or (a.max_n and m > a.max_n):
                continue
            rows.append(run_one(m))
            _mac.emit({"run": "order finding", **rows[-1]}, a.out)
        _mac.emit({"wall": "this machine", "ram_gb": prof["ram_gb"], "budget_gb": prof["budget_gb"], **target,
                   "stopped_before": target["next_N"]}, a.out)
    else:
        print("here mode: ran N = 15, 21, 35 only; the by-RAM prediction uses mac_profile's simulated budgets",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
