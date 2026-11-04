"""Evidence for the design decision: three ways to make an encrypted, signed format swappable.
A) one true algorithm, no identifier (v1)  B) per-algorithm identifiers + registry (v2)  C) one suite identifier.
Sizes and counts are exact; timings depend on the machine (median of repeated runs, microseconds)."""
import itertools
import json
import statistics
import time

import agile_envelope as ae
import registry as reg

N_DOCS, DOC = 1000, b"x" * 1024


def median_us(fn, reps=200):
    runs = []
    for _ in range(reps):
        t = time.perf_counter()
        fn()
        runs.append((time.perf_counter() - t) * 1e6)
    return round(statistics.median(runs), 1)


def main():
    ring = ae.Keyring()
    old_kid = ring.add("A256GCM")
    signers = {a: reg.new_signer(a) for a in reg.signing_algorithms()}
    v1 = [ae.legacy_v1(ring, old_kid, DOC) for _ in range(N_DOCS)]
    v2 = ae.seal(ring, old_kid, DOC, "doc-1", signers)
    header_v1, header_v2 = len(ae.canon(v1[0]["h"])), len(ae.canon(v2["h"]))
    sig_bytes = {s["alg"]: len(ae.b64d(s["sig"])) for s in v2["sigs"]}

    # A) swap the cipher in a format WITHOUT identifiers: every reader must guess (trial decryption) or all data is
    #    rewritten before the switch (flag day). Count what a new reader faces after the switch.
    new_kid = ring.add("C20P1305")
    guesses = 0
    for env in v1:
        for alg_id, kid in (("C20P1305", new_kid), ("A256GCM", old_kid)):  # new default tried first
            guesses += 1
            try:
                reg.aead(alg_id, ring.entries[kid][1]).decrypt(ae.b64d(env["h"]["n"]), ae.b64d(env["ct"]), b"")
                break
            except Exception:
                continue
    t_rewrite = median_us(lambda: ae.legacy_v1(ring, old_kid, DOC), 50) * N_DOCS / 1e6
    print(json.dumps({"option": "A one algorithm, no id", "header_bytes": header_v1, "swap_rewrites_before_switch": N_DOCS,
                      "trial_decryptions_per_read": guesses / N_DOCS, "rewrite_all_seconds_est": round(t_rewrite, 3)}))

    # B) identifiers + registry: readers dispatch on the header, so the switch is a policy change and old data stays.
    reg.POLICY["aead_default"] = "C20P1305"
    readable = sum(1 for env in [v2] * N_DOCS if ae.open_(ring, env))
    print(json.dumps({"option": "B per-algorithm ids + registry", "header_bytes": header_v2,
                      "extra_header_bytes_vs_A": header_v2 - header_v1, "swap_rewrites_before_switch": 0,
                      "old_docs_readable_after_switch": f"{readable}/{N_DOCS}", "dual_signature_bytes": sum(sig_bytes.values())}))

    # C) one identifier per complete suite: every combination needs its own id and code path.
    aeads = [a for a in reg.REGISTRY.values() if a.kind == "aead"]
    suites = list(itertools.product(aeads, reg.PHASES))
    print(json.dumps({"option": "C suite ids", "ids_needed_for_suites": len(suites), "ids_needed_per_algorithm": len(reg.REGISTRY),
                      "after_adding_one_aead": (len(aeads) + 1) * len(reg.PHASES)}))

    # Per-algorithm costs that the policy trades off (machine-dependent timings).
    costs = {}
    for alg_id in ("A256GCM", "C20P1305"):
        box, n = reg.aead(alg_id, reg.new_aead_key(alg_id)), b"\x00" * 12
        costs[alg_id] = {"seal_4KiB_us": median_us(lambda: box.encrypt(n, b"x" * 4096, b"h"))}
    for alg_id, key in signers.items():
        sig, pub = key.sign(b"m"), key.public_key()
        costs[alg_id] = {"sig_bytes": len(sig), "sign_us": median_us(lambda: key.sign(b"m")),
                         "verify_us": median_us(lambda: pub.verify(sig, b"m"))}
    print(json.dumps({"per_algorithm": costs}))


if __name__ == "__main__":
    main()
