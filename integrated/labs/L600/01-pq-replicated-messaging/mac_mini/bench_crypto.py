"""Experiment 1 - what does the crypto cost on THIS machine? (Mac mini: Apple silicon; --here: a few iterations.)

python mac_mini/bench_crypto.py            full run (about a minute on a Mac mini)
python mac_mini/bench_crypto.py --here     tiny iteration counts: proves the script works, the numbers mean nothing
python mac_mini/bench_crypto.py --out runs/bench.jsonl   also append the JSON lines to a file

Times the primitives the project uses (cryptography 50.x, OpenSSL/BoringSSL backend of the wheel), then the project's
own operations (group_crypto.welcome / seal), and turns them into the two budgets the project depends on:
  rotation budget  - a rotation seals one hybrid welcome per member: max members that fit ROTATE_BUDGET_MS
  per-key budget   - AES-GCM with random 96-bit nonces is capped at 2^32 messages per key (SP 800-38D 8.3):
                     how long one saturated sealer at the measured rate needs to reach that cap
Timing rule: median of `rounds` batches of `n` calls, in microseconds per call (perf_counter). Nothing is asserted on
the numbers; the decision lines say what changes if they come out one way or the other.
"""
import argparse
import os
import platform
import statistics
import sys
import time

import _mac
import cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import mlkem, x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

ROTATE_BUDGET_MS = 100.0      # ASSUMPTION: a rotation should not stall the leader longer than ~one election timeout
MSG_LIMIT_PER_KEY = 2 ** 32   # NIST SP 800-38D 8.3, random 96-bit IVs (same constant as pqmsg.MAX_MSGS_PER_EPOCH)


def per_call_us(fn, n, rounds):
    fn()  # warm-up (first call loads the backend's tables)
    times = []
    for _ in range(rounds):
        t0 = time.perf_counter()
        for _ in range(n):
            fn()
        times.append((time.perf_counter() - t0) / n * 1e6)
    return round(statistics.median(times), 2)


def primitives(n, rounds):
    rows = []
    x_priv, x_peer = x25519.X25519PrivateKey.generate(), x25519.X25519PrivateKey.generate().public_key()
    k768 = mlkem.MLKEM768PrivateKey.generate()
    pub768 = k768.public_key()
    _, ct768 = pub768.encapsulate()
    k1024 = mlkem.MLKEM1024PrivateKey.generate()
    _, ct1024 = k1024.public_key().encapsulate()
    ops = {
        "x25519 keygen": lambda: x25519.X25519PrivateKey.generate(),
        "x25519 exchange": lambda: x_priv.exchange(x_peer),
        "ml-kem-768 keygen": lambda: mlkem.MLKEM768PrivateKey.generate(),
        "ml-kem-768 encapsulate": lambda: pub768.encapsulate(),
        "ml-kem-768 decapsulate": lambda: k768.decapsulate(ct768),
        "ml-kem-1024 encapsulate": lambda: k1024.public_key().encapsulate(),
        "ml-kem-1024 decapsulate": lambda: k1024.decapsulate(ct1024),
        "hkdf-sha256 32 B": lambda: HKDF(hashes.SHA256(), 32, None, b"app").derive(b"k" * 32),
    }
    for name, fn in ops.items():
        rows.append({"op": name, "us_per_call": per_call_us(fn, n, rounds)})
    gcm, nonce = AESGCM(os.urandom(32)), os.urandom(12)
    for size in (64, 1024, 65536):
        data = os.urandom(size)
        us = per_call_us(lambda: gcm.encrypt(nonce, data, b"hdr"), max(1, n // (1 + size // 4096)), rounds)
        rows.append({"op": f"aes-256-gcm encrypt {size} B", "us_per_call": us, "MB_per_s": round(size / us, 1)})
    return rows


def project_ops(n, rounds):
    import group_crypto as gc  # the lab's own welcome / seal (imports the reused crypto labs)
    member, secret = gc.Device("bob"), os.urandom(32)
    text = "msg 00042 from alice: status green"
    nonce = os.urandom(12)
    return [
        {"op": "project welcome (hybrid KEM + HKDF + AES-GCM wrap)",
         "us_per_call": per_call_us(lambda: gc.welcome(member.key_package, secret, 2, "bob"), max(1, n // 4), rounds)},
        {"op": "project seal (envelope + AES-256-GCM + fingerprint)",
         "us_per_call": per_call_us(lambda: gc.seal(secret, 2, "alice", "k1", text, nonce), n, rounds)},
    ]


def budgets(rows):
    us = {r["op"]: r["us_per_call"] for r in rows}
    welcome_us = us["project welcome (hybrid KEM + HKDF + AES-GCM wrap)"]
    seal_us = us["project seal (envelope + AES-256-GCM + fingerprint)"]
    seals_per_s = 1e6 / seal_us
    return {
        "budget": "rotation + per-key",
        "rotate_ms_for_members": {g: round(g * welcome_us / 1000, 2) for g in (3, 100, 1000, 10000)},
        "max_members_in_rotate_budget": int(ROTATE_BUDGET_MS * 1000 // welcome_us),
        "rotate_budget_ms": ROTATE_BUDGET_MS,
        "seals_per_s_one_core": round(seals_per_s),
        "days_to_2^32_at_that_rate": round(MSG_LIMIT_PER_KEY / seals_per_s / 86400, 1),
        "reading": "max_members < your group size -> rotations must be batched/async (ADR change); "
                   "days_to_2^32 shorter than your rotation period -> a timer alone is unsafe at full load, "
                   "keep the counter rule (F4: 409 rotation_required)",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true", help="tiny counts for the sandbox; numbers are not Mac numbers")
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--rounds", type=int, default=7)
    ap.add_argument("--out", help="append JSON lines to this file")
    args = ap.parse_args(argv)
    n, rounds = (20, 3) if args.here else (args.n, args.rounds)
    m = _mac.mac_profile().detect()
    _mac.emit({"experiment": "01 crypto benchmark", "mode": "here" if args.here else "mac", "at": _mac.stamp(),
               "system": m["system"], "arch": m["arch"], "macos": m["macos"], "apple_silicon": m["apple_silicon"],
               "python": platform.python_version(), "cryptography": cryptography.__version__, "n": n,
               "rounds": rounds}, args.out)
    rows = primitives(n, rounds) + project_ops(n, rounds)
    for r in rows:
        _mac.emit(r, args.out)
    _mac.emit(budgets(rows), args.out)
    if args.here:
        print("here mode: timings come from the sandbox, not from a Mac mini - do not copy them into an ADR",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
