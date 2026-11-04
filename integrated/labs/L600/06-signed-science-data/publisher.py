"""The release side: process -> licence gate -> content-addressed files -> Merkle manifest -> dual-signed release
-> transparency log -> short-lived timestamp. Licence rule and citation file come from astronomy L400 #21
(solution: keep every input restriction, so Gaia's NonCommercial makes the derived release CC-BY-NC-4.0)."""
import hashlib

import canonical as C
import merkle
import science
import tlog
import trust
from _kb import INPUTS, OPEN_DATA

NAME = "kb-gaia-like-distances"
TTL = 3600  # timestamp lifetime (s): must exceed mirror lag, or slow-but-honest mirrors look like a freeze attack
ROOT_TTL = 365 * 86400


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class Refused(Exception):
    """The licence gate refused to sign (a human must review)."""


def licence_problems(lic: str) -> list:
    return [f"licence {lic} drops the {r} condition of input {i['name']} ({i['licence']})"
            for i in INPUTS.INPUTS for r in OPEN_DATA.RESTRICTIVE
            if r in i["family"].split("-") and f"-{r}" not in lic]


def build_files(version: int, licence_fn=OPEN_DATA.release_licence) -> dict:
    lic = licence_fn(INPUTS.INPUTS)
    problems = licence_problems(lic)
    if problems:
        raise Refused("; ".join(problems))
    ack = ("\n\n".join(i["credit"] for i in INPUTS.INPUTS) + "\n").encode("utf-8")
    prov = {"inputs": [{k: i[k] for k in ("name", "licence")} for i in INPUTS.INPUTS], "seed": 21,
            "steps": ["astronomy L400 #21 inputs.rows", "inverse parallax if parallax/error >= 5 (L100 #4 units)"],
            "note": "rows are SYNTHETIC stand-ins; licences and credit lines are the providers' real texts"}
    return {"catalogue.json": C.dumps(science.catalogue(version)), "LICENSE.txt": f"{lic}\n".encode("utf-8"),
            "ACKNOWLEDGEMENTS.md": ack, "CITATION.cff": OPEN_DATA.citation_cff(lic).encode("utf-8"),
            "provenance.json": C.dumps(prov)}


def leaves(files_meta: dict) -> list:
    return [C.dumps([p, m["sha256"], m["length"]]) for p, m in sorted(files_meta.items())]


def manifest(version: int, now: int, files: dict) -> dict:
    meta = {p: {"sha256": sha(b), "length": len(b)} for p, b in files.items()}
    return {"_type": "release", "name": NAME, "version": version, "created": now,
            "licence": files["LICENSE.txt"].decode("utf-8").strip(), "files": meta,
            "attribution_sha256": meta["ACKNOWLEDGEMENTS.md"]["sha256"], "merkle_root": merkle.mth(leaves(meta)).hex()}


class Publisher:
    def __init__(self, keep_retired=True):
        self.root_key = trust.Signer("Ed25519", "demo-root")
        self.release = [trust.Signer("Ed25519", "demo-release-1"), trust.Signer("ML-DSA-65", "demo-release-1")]
        self.ts_key, self.log_key = trust.Signer("Ed25519", "demo-timestamp"), trust.Signer("Ed25519", "demo-log")
        self.log, self.keep_retired, self.ts_version, self.latest = tlog.Log(self.log_key), keep_retired, 0, None
        self.retired = {}
        self.roots = [trust.sign(self._root(1, 0), [self.root_key])]

    def _root(self, version, now):
        roles = {"root": [self.root_key], "release": self.release, "timestamp": [self.ts_key], "log": [self.log_key]}
        return trust.make_root(version, now + ROOT_TTL, roles, self.retired)

    def publish(self, version: int, now: int, licence_fn=OPEN_DATA.release_licence) -> dict:
        files = build_files(version, licence_fn)
        rel = C.dumps(trust.sign(manifest(version, now, files), self.release))
        self.log.add(tlog.entry(NAME, version, sha(rel)))
        self.latest = (version, sha(rel))
        out = {f"releases/v{version}/{p}": b for p, b in files.items()}
        out[f"releases/v{version}/release.json"] = rel
        return out

    def timestamp(self, now: int) -> bytes:
        self.ts_version += 1
        v, h = self.latest
        return C.dumps(trust.sign({"_type": "timestamp", "version": self.ts_version, "expires": now + TTL,
                                   "release": {"version": v, "sha256": h}}, [self.ts_key]))

    def rotate_release_keys(self, now: int, last_old_version: int) -> None:
        """Rotate: new release keys; old ones retired with a window (or dropped: the seeded seam fault)."""
        if self.keep_retired:
            for s in self.release:
                self.retired[s.kid] = {"role": "release", "key": s.entry(), "valid_through_version": last_old_version}
        self.release = [trust.Signer("Ed25519", "demo-release-2"), trust.Signer("ML-DSA-65", "demo-release-2")]
        new = self._root(len(self.roots) + 1, now)
        self.roots.append(trust.sign(new, [self.root_key]))  # same root key signs as old and new root (TUF section 5.3)
