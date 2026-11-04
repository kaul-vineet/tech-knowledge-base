"""Build-task solution: the verifier's POLICY decides which signatures are required, not the envelope.
During the "transition" phase every envelope must carry a valid Ed25519 AND a valid ML-DSA-65 signature;
an envelope that drops one (signature stripping) is rejected. Phases move by policy: classic -> transition -> pq-only."""
import random

import registry as reg
from agile_envelope import (EnvelopeError, Keyring, NoCommonAlgorithm, b64d, legacy_v1, migrate,  # noqa: F401
                            negotiate, open_, seal, signed_bytes)


def verify(env: dict, pubkeys: dict) -> bool:
    data, have = signed_bytes(env), {s["alg"]: s for s in env["sigs"]}
    for alg in reg.required_signatures():  # policy-required set; extra signatures are ignored, missing ones fail
        s = have.get(alg)
        if s is None or alg not in pubkeys or not reg.verify(alg, pubkeys[alg], b64d(s["sig"]), data):
            return False
    return True


if __name__ == "__main__":
    rng = random.Random(17)
    ring = Keyring()
    ring.add(reg.POLICY["aead_default"])
    signers = {a: reg.new_signer(a) for a in reg.signing_algorithms()}
    pubs = {a: k.public_key() for a, k in signers.items()}
    good = seal(ring, ring.primary(), b"invoice 1: amount=100", "doc-1", signers)
    classic = reg.PHASES["classic"]
    forged = seal(ring, ring.primary(), f"doc-1: amount={rng.randrange(1, 9)}".encode(), "doc-1",
                  {a: signers[a] for a in classic}, sig_algs=classic)
    print("phase:", reg.POLICY["phase"], "| required:", reg.required_signatures())
    print("legit verify:", verify(good, pubs), "| stripped (Ed25519 only) verify:", verify(forged, pubs))
    reg.POLICY["phase"] = "pq-only"  # later: Ed25519 no longer required (and may become deprecated)
    print("phase:", reg.POLICY["phase"], "| legit verify:", verify(good, pubs), "| stripped verify:", verify(forged, pubs))
