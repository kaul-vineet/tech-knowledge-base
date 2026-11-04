"""Crypto agility: a versioned, self-describing envelope. Each envelope names its AEAD and its signature
algorithms by identifier; the registry maps identifiers to code and the policy decides what is acceptable.
Swapping AES-GCM -> ChaCha20-Poly1305 or Ed25519 -> ML-DSA is a policy change, not a flag day."""
import base64
import json
import os
import random

import registry as reg

SEED = 17  # seeds the injected fault (which document the attacker forges)


class EnvelopeError(Exception):
    """Unknown format version, or a key used with an algorithm it is not bound to."""


class NoCommonAlgorithm(Exception):
    """Negotiation found no algorithm both sides support and policy allows: fail, never fall back."""


def b64e(b: bytes) -> str:
    return base64.b64encode(b).decode()


def b64d(s: str) -> bytes:
    return base64.b64decode(s)


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()  # one byte form for AAD and signatures


class Keyring:
    """Data keys by key id; every key is bound to exactly one algorithm (key + algorithm id, RFC 7696 2.1)."""

    def __init__(self):
        self.entries = {}

    def add(self, alg_id: str) -> str:
        kid = f"dk-{len(self.entries) + 1}"
        self.entries[kid] = (alg_id, reg.new_aead_key(alg_id))
        return kid

    def primary(self) -> str:
        default = reg.POLICY["aead_default"]
        return [k for k, (a, _) in self.entries.items() if a == default][-1]  # newest key for the policy default


def signed_bytes(env: dict) -> bytes:
    return canon(env["h"]) + b"." + env["ct"].encode()


def seal(ring: Keyring, kid: str, plaintext: bytes, ctx: str, signers: dict, sig_algs=None) -> dict:
    alg, key = ring.entries[kid]
    n = os.urandom(12)
    h = {"v": 2, "aead": alg, "kid": kid, "n": b64e(n), "ctx": ctx}  # algorithm identifier travels with the data
    ct = reg.aead(alg, key, for_new_data=True).encrypt(n, plaintext, canon(h))  # whole header is AAD
    env = {"h": h, "ct": b64e(ct), "sigs": []}
    for sig_alg in sig_algs or reg.signing_algorithms():  # dual-signing while the policy phase is "transition"
        env["sigs"].append({"alg": sig_alg, "sig": b64e(reg.sign(sig_alg, signers[sig_alg], signed_bytes(env)))})
    return env


def legacy_v1(ring: Keyring, kid: str, plaintext: bytes) -> dict:
    """What the old code wrote: no algorithm identifier, the format version implied AES-256-GCM."""
    n = os.urandom(12)
    return {"h": {"v": 1, "kid": kid, "n": b64e(n)}, "ct": b64e(reg.aead(reg.LEGACY_V1_AEAD, ring.entries[kid][1]).encrypt(n, plaintext, b"")), "sigs": []}


def open_(ring: Keyring, env: dict) -> bytes:
    h = env["h"]
    if h.get("v") == 1:
        alg, aad = reg.LEGACY_V1_AEAD, b""
    elif h.get("v") == 2:
        alg, aad = h["aead"], canon(h)
    else:
        raise EnvelopeError(f"unknown envelope version {h.get('v')!r}")
    key_alg, key = ring.entries[h["kid"]]
    if key_alg != alg:  # a header cannot make a key be used with a different algorithm
        raise EnvelopeError(f"key {h['kid']} is bound to {key_alg}, header says {alg}")
    return reg.aead(alg, key).decrypt(b64d(h["n"]), b64d(env["ct"]), aad)  # registry refuses disallowed algorithms


def verify(env: dict, pubkeys: dict) -> bool:
    data = signed_bytes(env)
    # BUG on purpose: any ONE valid signature is enough - the envelope, not the verifier's policy, decides what counts
    return any(reg.verify(s["alg"], pubkeys[s["alg"]], b64d(s["sig"]), data) for s in env["sigs"] if s["alg"] in pubkeys)


def negotiate(local_prefs: list, peer_offer: list) -> str:
    for alg in local_prefs:  # our preference order wins; only active algorithms qualify
        if alg in peer_offer and reg.REGISTRY.get(alg) and reg.REGISTRY[alg].status == "active":
            return alg
    raise NoCommonAlgorithm(f"no common active algorithm in {peer_offer}")


def migrate(ring: Keyring, env: dict, signers: dict) -> dict:
    """Lazy migration: re-seal only envelopes that are legacy or not on the policy default."""
    if env["h"].get("v") == 2 and env["h"]["aead"] == reg.POLICY["aead_default"]:
        return env
    return seal(ring, ring.primary(), open_(ring, env), env["h"].get("ctx", env["h"]["kid"]), signers)


def count_by_aead(store: dict) -> dict:
    algs = [e["h"].get("aead", f"v1:{reg.LEGACY_V1_AEAD}") for e in store.values()]
    return {"metric": "envelopes_by_aead", **{a: algs.count(a) for a in sorted(set(algs))}}  # observability


if __name__ == "__main__":
    rng = random.Random(SEED)
    ring = Keyring()
    ring.add(reg.POLICY["aead_default"])
    signers = {a: reg.new_signer(a) for a in reg.signing_algorithms()}
    pubs = {a: k.public_key() for a, k in signers.items()}
    store = {f"doc-{i}": seal(ring, ring.primary(), f"invoice {i}: amount={100 * i}".encode(), f"doc-{i}", signers) for i in range(1, 4)}
    e = store["doc-1"]
    print("1) sealed 3 docs | header:", {k: e["h"][k] for k in ("v", "aead", "kid")},
          "| ct bytes:", len(b64d(e["ct"])), "| sigs:", [(s["alg"], len(b64d(s["sig"]))) for s in e["sigs"]])
    reg.POLICY["aead_default"] = reg.POLICY["aead_prefs"][1]  # policy change only: new data uses the next preference
    ring.add(reg.POLICY["aead_default"])
    store["doc-4"] = seal(ring, ring.primary(), b"invoice 4: amount=400", "doc-4", signers)
    print("2) default ->", reg.POLICY["aead_default"], "| opened:", sum(1 for x in store.values() if open_(ring, x)), "of", len(store))
    print(json.dumps(count_by_aead(store)))
    prefs = reg.POLICY["aead_prefs"]
    try:
        negotiate(prefs, ["A128CBC"])  # an identifier the registry does not know
    except NoCommonAlgorithm as err:
        print("3) negotiate:", negotiate(prefs[::-1], [prefs[0], "A128CBC"]), "| only A128CBC offered ->", err)
    old = legacy_v1(ring, "dk-1", b"invoice 0: amount=0")
    new = migrate(ring, old, signers)
    print("4) legacy v1 opens:", open_(ring, old).decode(), "| migrate ->", {k: new["h"][k] for k in ("v", "aead", "kid")})
    print("--- fault: the Ed25519 key leaked; a co-tenant re-signs an edited document with Ed25519 only")
    victim = rng.choice(sorted(store))
    classic = reg.PHASES["classic"]
    forged = seal(ring, store[victim]["h"]["kid"], f"{victim}: amount={rng.randrange(1, 9)}".encode(), victim,
                  {a: signers[a] for a in classic}, sig_algs=classic)  # the ML-DSA signature is simply left out
    print("legit verify:", verify(store["doc-1"], pubs), "| forged", victim, "verify:", verify(forged, pubs),
          "| sigs on forged:", [s["alg"] for s in forged["sigs"]])
