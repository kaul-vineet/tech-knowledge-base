"""Experiment 2 - post-quantum algorithm cost on THIS machine, turned into the numbers the ADRs depend on.

python mac_mini/pq_bench.py              full run (Mac mini; about a minute)
python mac_mini/pq_bench.py --here       tiny counts: proves the script works; the timings are not Mac timings
python mac_mini/pq_bench.py --out runs/pq.jsonl

Measures keygen / encapsulate / decapsulate (ML-KEM-768, ML-KEM-1024) and keygen / sign / verify (ML-DSA-44/65/87),
next to the classical primitives they replace (X25519, Ed25519, ECDSA P-256, RSA-2048). Sizes come from the library
(raw public keys, ciphertexts, signatures), never from a table. ML-KEM-512 is reported as unavailable when the
installed `cryptography` has no class for it (50.x ships 768 and 1024 only).

Two decisions read the output:
  ADR-0001 bytes  client flight = ML-KEM ek + X25519 share (+ framing), checked against fitness.BUDGET (1,400 B)
  ADR-0001 CPU    server CPU per hybrid handshake (X25519 keygen + exchange, ML-KEM encapsulate, ML-DSA sign) ->
                  handshakes/s per core and cores needed at PEAK_HANDSHAKES_PER_S (an ASSUMPTION, printed)
"""
import argparse
import platform
import statistics
import sys
import time

import _mac
import cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, mldsa, mlkem, padding, rsa, x25519

PEAK_HANDSHAKES_PER_S = 500   # ASSUMPTION for the messaging service's busiest minute; change it to yours
X25519_SHARE = 32
MSG = b"transcript-hash-" + b"x" * 48


def us(fn, n, rounds):
    fn()
    t = []
    for _ in range(rounds):
        t0 = time.perf_counter()
        for _ in range(n):
            fn()
        t.append((time.perf_counter() - t0) / n * 1e6)
    return round(statistics.median(t), 2)


def kem_rows(n, rounds):
    rows = []
    for level in (512, 768, 1024):
        cls = getattr(mlkem, f"MLKEM{level}PrivateKey", None)
        if cls is None:
            rows.append({"alg": f"ML-KEM-{level}", "available": False,
                         "note": f"cryptography {cryptography.__version__} has no MLKEM{level}PrivateKey"})
            continue
        sk = cls.generate()
        pk = sk.public_key()
        ss, ct = pk.encapsulate()
        rows.append({"alg": f"ML-KEM-{level}", "available": True, "ek_B": len(pk.public_bytes_raw()), "ct_B": len(ct),
                     "ss_B": len(ss), "keygen_us": us(cls.generate, n, rounds), "encaps_us": us(pk.encapsulate, n, rounds),
                     "decaps_us": us(lambda: sk.decapsulate(ct), n, rounds)})
    return rows


def sig_rows(n, rounds):
    rows = []
    for level in (44, 65, 87):
        cls = getattr(mldsa, f"MLDSA{level}PrivateKey")
        sk = cls.generate()
        pk, sig = sk.public_key(), sk.sign(MSG)
        rows.append({"alg": f"ML-DSA-{level}", "pk_B": len(pk.public_bytes_raw()), "sig_B": len(sig),
                     "keygen_us": us(cls.generate, max(1, n // 2), rounds), "sign_us": us(lambda: sk.sign(MSG), n, rounds),
                     "verify_us": us(lambda: pk.verify(sig, MSG), n, rounds)})
    ed = ed25519.Ed25519PrivateKey.generate()
    esig = ed.sign(MSG)
    rows.append({"alg": "Ed25519", "pk_B": 32, "sig_B": len(esig), "keygen_us": us(ed25519.Ed25519PrivateKey.generate, n, rounds),
                 "sign_us": us(lambda: ed.sign(MSG), n, rounds),
                 "verify_us": us(lambda: ed.public_key().verify(esig, MSG), n, rounds)})
    p256 = ec.generate_private_key(ec.SECP256R1())
    psig = p256.sign(MSG, ec.ECDSA(hashes.SHA256()))
    rows.append({"alg": "ECDSA P-256", "sig_B_max": 72, "sign_us": us(lambda: p256.sign(MSG, ec.ECDSA(hashes.SHA256())), n, rounds),
                 "verify_us": us(lambda: p256.public_key().verify(psig, MSG, ec.ECDSA(hashes.SHA256())), n, rounds)})
    r = rsa.generate_private_key(65537, 2048)
    pss = padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.MAX_LENGTH)
    rsig = r.sign(MSG, pss, hashes.SHA256())
    rows.append({"alg": "RSA-2048 PSS", "sig_B": len(rsig), "sign_us": us(lambda: r.sign(MSG, pss, hashes.SHA256()), max(1, n // 4), rounds),
                 "verify_us": us(lambda: r.public_key().verify(rsig, MSG, pss, hashes.SHA256()), n, rounds)})
    xk = x25519.X25519PrivateKey.generate()
    xp = x25519.X25519PrivateKey.generate().public_key()
    rows.append({"alg": "X25519", "share_B": X25519_SHARE, "keygen_us": us(x25519.X25519PrivateKey.generate, n, rounds),
                 "exchange_us": us(lambda: xk.exchange(xp), n, rounds)})
    return rows


def decisions(kems, sigs, budget):
    k = {r["alg"]: r for r in kems if r.get("available")}
    s = {r["alg"]: r for r in sigs}
    x = s["X25519"]
    out = {"decision": "ADR-0001 budgets", "client_flight_budget_B": budget["client_flight_bytes"],
           "peak_handshakes_per_s_assumed": PEAK_HANDSHAKES_PER_S, "options": []}
    for kem in ("ML-KEM-768", "ML-KEM-1024"):
        for sig in ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87"):
            if kem not in k:
                continue
            share = k[kem]["ek_B"] + X25519_SHARE
            server_us = x["keygen_us"] + x["exchange_us"] + k[kem]["encaps_us"] + s[sig]["sign_us"]
            client_us = k[kem]["keygen_us"] + x["keygen_us"] + x["exchange_us"] + k[kem]["decaps_us"] + s[sig]["verify_us"]
            out["options"].append({"kem": kem, "sig": sig, "client_key_share_B": share,
                                   "share_fits_client_flight": share < budget["client_flight_bytes"],
                                   "server_us": round(server_us, 1), "client_us": round(client_us, 1),
                                   "handshakes_per_s_per_core": int(1e6 // server_us),
                                   "cores_at_peak": round(PEAK_HANDSHAKES_PER_S * server_us / 1e6, 3)})
    out["reading"] = ("share_fits_client_flight=false rules an option out by BYTES whatever its speed; among the rest, "
                      "cores_at_peak > 1 means the handshake needs its own capacity line in the ADR")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--here", action="store_true")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--rounds", type=int, default=7)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    n, rounds = (8, 3) if a.here else (a.n, a.rounds)
    import fitness  # the lab's budget constants (1,400 B client flight, 6,144 B handshake)
    m = _mac.mac_profile().detect()
    _mac.emit({"experiment": "02 PQ algorithm benchmark", "mode": "here" if a.here else "mac", "at": _mac.stamp(),
               "system": m["system"], "arch": m["arch"], "apple_silicon": m["apple_silicon"], "macos": m["macos"],
               "python": platform.python_version(), "cryptography": cryptography.__version__, "n": n, "rounds": rounds},
              a.out)
    kems, sigs = kem_rows(n, rounds), sig_rows(n, rounds)
    for r in kems + sigs:
        _mac.emit(r, a.out)
    _mac.emit(decisions(kems, sigs, fitness.BUDGET), a.out)
    if a.here:
        print("here mode: timings are from the sandbox, not a Mac mini; sizes are exact", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
