"""Evidence for the decision: X25519 vs ML-KEM-768 vs hybrid X25519MLKEM768, plus ML-DSA vs Ed25519 sizes/costs.
Sizes are exact (FIPS 203/204, RFC 10024); timings are medians on THIS machine in microseconds (vary by CPU)."""
import json
import statistics
import time

from cryptography.hazmat.primitives import hpke
from cryptography.hazmat.primitives.asymmetric import ed25519, mldsa, mlkem, x25519

import pq_hybrid as pq


def median_us(fn, reps=200):
    runs = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        runs.append((time.perf_counter() - t) * 1e6)
    return round(statistics.median(runs), 1)


def x25519_only():
    a, b = x25519.X25519PrivateKey.generate(), x25519.X25519PrivateKey.generate()
    return a.exchange(b.public_key()) == b.exchange(a.public_key())


def mlkem_only():
    k = mlkem.MLKEM768PrivateKey.generate()
    ss, ct = k.public_key().encapsulate()
    return k.decapsulate(ct) == ss


def hybrid():
    st, ch = pq.client_hello()
    sh, ks = pq.server_respond(ch)
    return pq.client_finish(st, sh)[0] == ks


def main():
    s = pq.sizes()
    for name, fn, quantum_safe, classical_safe in (("X25519", x25519_only, False, True), ("ML-KEM-768", mlkem_only, True, "new"),
                                                   (pq.GROUP, hybrid, True, True)):
        print(json.dumps({"option": name, "on_wire_bytes": s[name]["client_share"] + s[name]["server_share"],
                          "handshake_us": median_us(fn), "safe_if_CRQC_exists": quantum_safe,
                          "safe_if_lattice_break": classical_safe if name != "ML-KEM-768" else False}))
    sigs = {"Ed25519": ed25519.Ed25519PrivateKey, "ML-DSA-44": mldsa.MLDSA44PrivateKey,
            "ML-DSA-65": mldsa.MLDSA65PrivateKey, "ML-DSA-87": mldsa.MLDSA87PrivateKey}
    for name, cls in sigs.items():
        key = cls.generate()
        pub, sig = key.public_key(), key.sign(b"release manifest")
        print(json.dumps({"signature": name, "public_key_bytes": len(pub.public_bytes_raw()), "signature_bytes": len(sig),
                          "sign_us": median_us(lambda: key.sign(b"release manifest")),
                          "verify_us": median_us(lambda: pub.verify(sig, b"release manifest"))}))
    suite = hpke.Suite(hpke.KEM.MLKEM768_X25519, hpke.KDF.HKDF_SHA256, hpke.AEAD.AES_256_GCM)
    rk = hpke.MLKEM768X25519PrivateKey(mlkem.MLKEM768PrivateKey.generate(), x25519.X25519PrivateKey.generate())
    ct = suite.encrypt(b"k" * 32, rk.public_key(), info=b"kb-l18")
    print(json.dumps({"hpke": "MLKEM768_X25519 (X-Wing)", "enc_bytes": hpke.KEM.MLKEM768_X25519.enc_length(),
                      "wrapped_32B_key_bytes": len(ct), "classic_X25519_enc_bytes": hpke.KEM.X25519.enc_length(),
                      "seal_us": median_us(lambda: suite.encrypt(b"k" * 32, rk.public_key(), info=b"kb-l18"), 100)}))


if __name__ == "__main__":
    main()
