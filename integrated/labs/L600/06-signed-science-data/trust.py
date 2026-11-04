"""Signing and the root of trust (cryptography): TUF-style signed envelopes {"signed": ..., "signatures": [...]} over
JCS bytes. Algorithms come from cryptography L400 #17's registry (Ed25519 + ML-DSA-65; the 'transition' phase
requires both on a release), key ids from L300 #14 (first 16 hex of SHA-256 of the raw public key).
Key rotation keeps retired release keys with a validity window (valid_through_version) so old releases still verify
but a retired key cannot sign anything new. DEMO keys are derived from fixed seeds so output is reproducible."""
import hashlib

from cryptography.hazmat.primitives.asymmetric import ed25519, mldsa

import canonical as C
from _kb import REGISTRY as REG, SUPPLY

Rejected = SUPPLY.Rejected  # one exception type for every refusal, as in the supply-chain lab
PUBLIC = {"Ed25519": ed25519.Ed25519PublicKey, "ML-DSA-65": mldsa.MLDSA65PublicKey}


class Signer:
    def __init__(self, alg: str, seed: str):
        s = hashlib.sha256(seed.encode()).digest()  # demo only: real keys come from a CSPRNG / HSM (crypto L400 #19)
        self.alg = alg
        self.priv = (ed25519.Ed25519PrivateKey.from_private_bytes(s) if alg == "Ed25519"
                     else mldsa.MLDSA65PrivateKey.from_seed_bytes(s))
        self.public = self.priv.public_key().public_bytes_raw()
        self.kid = hashlib.sha256(self.public).hexdigest()[:16]

    def entry(self) -> dict:
        return {"alg": self.alg, "public": self.public.hex()}


def sign(signed: dict, signers: list) -> dict:
    raw = C.dumps(signed)
    return {"signed": signed, "signatures": [{"keyid": s.kid, "alg": s.alg, "sig": REG.sign(s.alg, s.priv, raw).hex()}
                                             for s in signers]}


def valid_kids(env: dict, keys: dict) -> dict:
    """keyid -> alg for every signature that verifies with the listed key (one per keyid, TUF section 5.3)."""
    raw, ok = C.dumps(env["signed"]), {}
    for s in env["signatures"]:
        k = keys.get(s["keyid"])
        if k is None or k["alg"] != s["alg"] or s["keyid"] in ok:
            continue
        pub = PUBLIC[k["alg"]].from_public_bytes(bytes.fromhex(k["public"]))
        if REG.verify(s["alg"], pub, bytes.fromhex(s["sig"]), raw):
            ok[s["keyid"]] = s["alg"]
    return ok


def require_role(env: dict, root: dict, role: str) -> None:
    good = valid_kids(env, root["keys"])
    n = sum(1 for kid in root["roles"][role]["keyids"] if kid in good)
    if n < root["roles"][role]["threshold"]:
        raise Rejected(f"{role}: {n} valid signature(s), threshold {root['roles'][role]['threshold']}")


def require_release(env: dict, root: dict, honour_retired: bool = True) -> None:
    """Every algorithm the policy phase requires must be covered by a release key that was valid for THIS version."""
    version = env["signed"]["version"]
    allowed = set(root["roles"]["release"]["keyids"])
    if honour_retired:
        allowed |= {kid for kid, r in root.get("retired", {}).items() if version <= r["valid_through_version"]}
    good = {kid: alg for kid, alg in valid_kids(env, root["keys"]).items() if kid in allowed}
    for alg in REG.required_signatures():  # ["Ed25519", "ML-DSA-65"] in the 'transition' phase
        if alg not in good.values():
            raise Rejected(f"release v{version}: no valid {alg} signature from a key trusted for v{version}")


def make_root(version: int, expires: int, signers: dict, retired: dict = None) -> dict:
    """signers: role -> list of Signer. Retired release keys stay listed so old signatures can still be checked."""
    keys = {s.kid: s.entry() for group in signers.values() for s in group}
    for kid, r in (retired or {}).items():
        keys[kid] = r["key"]
    return {"_type": "root", "version": version, "expires": expires, "keys": keys,
            "roles": {role: {"keyids": [s.kid for s in group], "threshold": len(group)} for role, group in signers.items()},
            "retired": {kid: {"role": r["role"], "valid_through_version": r["valid_through_version"]}
                        for kid, r in (retired or {}).items()}}


def next_root(trusted: dict, env: dict) -> dict:
    """TUF section 5.3: root N+1 must be signed by a threshold of root N AND of root N+1, version exactly N+1."""
    new = env["signed"]
    if new["version"] != trusted["version"] + 1:
        raise Rejected(f"root rollback/skip: have v{trusted['version']}, got v{new['version']}")
    require_role(env, trusted, "root")
    require_role(env, new, "root")
    return new
