"""Encrypted document service: per-document data keys (DEKs) in lesson 17's versioned envelope, DEKs wrapped by the
KMS over mTLS, document signatures and audit entries made through non-exportable token handles (lesson 19), PQ-hybrid
sharing with external recipients (HPKE, lesson 18), secrets from files with redacted JSON logs (lesson 16)."""
import base64
import json
import os

import paths  # noqa: F401  (reused labs on sys.path)
import agile_envelope as ae
import registry as reg
import solution_agile
import solution_nonexportable as tok
from cryptography.hazmat.primitives import serialization as ser

ACL_CACHE_S = 300  # the ACL cache refreshes every 5 minutes: revocation is not instant (a seeded weakness the audit catches)


class TokenSigner:
    """Duck-typed private key for the registry: .sign(data) goes through the token handle, never through key bytes."""

    def __init__(self, session, handle):
        self.session, self.handle = session, handle

    def sign(self, data: bytes) -> bytes:
        return self.session.sign(self.handle, tok.CKM_EDDSA, data)


def open_token(pin) -> dict:
    token = tok.SoftToken("capstone", so_pin=base64.b64encode(os.urandom(12)).decode(), user_pin=pin.reveal())
    s = token.open_session()
    s.login("USER", pin.reveal())
    keys = {}
    for label in ("doc-signing", "audit-log"):
        pub, priv = s.generate_key_pair(tok.CKM_EDDSA, label)  # non-exportable: the token enforces it
        keys[label] = (TokenSigner(s, priv), ser.load_der_public_key(s.get_attribute_value(pub, tok.CKA_VALUE)))
    return {"token": token, "session": s, "keys": keys}


class DocService:
    def __init__(self, kms, keys, audit, clock, log):
        self.kms, self.audit, self.clock, self.log = kms, audit, clock, log
        self.signer, self.pub = keys["doc-signing"]
        self.docs, self.acl, self.revoked, self._cache, self.primary = {}, {}, set(), (None, -1e18), None

    def _signers(self):
        return {alg: self.signer for alg in reg.signing_algorithms()}

    def put(self, user: str, doc_id: str, data: bytes, readers=()):
        alg = reg.POLICY["aead_default"]
        dek = reg.new_aead_key(alg)
        ring = ae.Keyring()
        ring.entries[doc_id] = (alg, dek)
        env = ae.seal(ring, doc_id, data, doc_id, self._signers())  # header names the AEAD; signed via the token
        w = self.kms.call("wrap", dek=base64.b64encode(dek).decode(), on_behalf=user, doc=doc_id)
        self.docs[doc_id] = {"env": env, "kek": w["kid"], "wdek": w["wdek"]}
        self.primary = self.primary or w["kid"]
        self.acl[doc_id] = {user, *readers}
        self.audit.append(f"doc-service/{user}", "doc.put", doc_id, aead=alg)
        self.log.info("document stored", extra={"ctx": {"doc": doc_id, "user": user, "bytes": len(data)}})

    def _allowed(self, user: str, doc_id: str) -> bool:
        if self.clock.now() - self._cache[1] >= ACL_CACHE_S:  # refresh the cached revocation list
            self._cache = (set(self.revoked), self.clock.now())
        return user in self.acl.get(doc_id, ()) and user not in self._cache[0]

    def get(self, user: str, doc_id: str) -> bytes:
        if not self._allowed(user, doc_id):
            self.audit.append(f"doc-service/{user}", "doc.get", doc_id, result="denied")
            raise PermissionError(f"{user} may not read {doc_id}")
        rec = self.docs[doc_id]
        dek = base64.b64decode(self.kms.call("unwrap", kid=rec["kek"], wdek=rec["wdek"], on_behalf=user, doc=doc_id)["dek"])
        if not solution_agile.verify(rec["env"], {alg: self.pub for alg in reg.required_signatures()}):
            raise ValueError(f"{doc_id}: signature policy not met")
        ring = ae.Keyring()
        ring.entries[doc_id] = (rec["env"]["h"]["aead"], dek)
        self.audit.append(f"doc-service/{user}", "doc.get", doc_id, result="ok")
        return ae.open_(ring, rec["env"])

    def revoke(self, admin: str, user: str):
        self.revoked.add(user)
        self.audit.append(f"doc-service/{admin}", "doc.revoke", user)

    def share(self, user: str, doc_id: str, recipient_pub) -> dict:
        """PQ-hybrid option: the DEK goes to an external recipient through HPKE with the policy's sharing KEM."""
        kem = reg.POLICY["share_kem"]
        rec = self.docs[doc_id]
        dek = base64.b64decode(self.kms.call("unwrap", kid=rec["kek"], wdek=rec["wdek"], on_behalf=user, doc=doc_id)["dek"])
        blob = reg.share_seal(kem, recipient_pub, dek, info=doc_id.encode())
        self.audit.append(f"doc-service/{user}", "doc.share", doc_id, kem=kem)
        return {"kem": kem, "blob": base64.b64encode(blob).decode(), "env": rec["env"]}

    def records_by_kid(self) -> dict:
        kids = [r["kek"] for r in self.docs.values()]
        return {k: kids.count(k) for k in sorted(set(kids))}

    def rotate_kek(self) -> str:
        self.primary = self.kms.call("rotate")["primary"]
        return self.primary

    def rewrap(self, crash_after=None) -> int:
        moved = 0
        for doc_id, rec in self.docs.items():
            if rec["kek"] == self.primary:
                continue  # idempotent: a rerun resumes where a crash stopped
            if crash_after is not None and moved == crash_after:
                raise RuntimeError(f"rewrap job crashed after {moved} records")
            w = self.kms.call("rewrap", kid=rec["kek"], wdek=rec["wdek"], doc=doc_id)  # only the wrapped DEK changes
            rec["kek"], rec["wdek"] = w["kid"], w["wdek"]
            moved += 1
        self.log.info("rewrap done", extra={"ctx": {"metric": "records_by_kid", **self.records_by_kid()}})
        return moved

    def retire(self, version: int) -> dict:
        return self.kms.call("retire", version=version, records_by_kid=self.records_by_kid())


def open_shared(package: dict, recipient_priv) -> bytes:
    """What the external recipient runs: unwrap the DEK with its own private key, then open the envelope."""
    env = package["env"]
    dek = reg.share_open(package["kem"], recipient_priv, base64.b64decode(package["blob"]), info=env["h"]["ctx"].encode())
    ring = ae.Keyring()
    ring.entries[env["h"]["kid"]] = (env["h"]["aead"], dek)
    return ae.open_(ring, env)


def dump(obj) -> str:
    return json.dumps(obj, sort_keys=True)
