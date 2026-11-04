"""Signed tool manifests (Ed25519) and a verifying loader: the host loads a tool only if a trusted publisher signed
its manifest AND the implementation file still has the digest the manifest pins.

Reuses cryptography L300 #14 (key_id, digest) and L200 #7 (detached Ed25519 signatures over exact bytes).
"""
import base64
import hashlib
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import _kb

release_sign = _kb.load("release_sign")
HERE = Path(__file__).resolve().parent
TOOLS_DIR = HERE / "tools"
# DEMO ONLY: a seeded key makes signatures reproducible for the README. Real publishers keep a random key offline.
PUBLISHER_SEED = hashlib.sha256(b"L600-08 demo publisher - never seed a real key").digest()


class LoadError(Exception):
    pass


@dataclass
class Tool:
    manifest: dict
    fn: object

    @property
    def schema(self):
        return self.manifest["inputSchema"]


def publisher_key():
    return Ed25519PrivateKey.from_private_bytes(PUBLISHER_SEED)


def trusted_keys():
    pub = publisher_key().public_key()
    return {release_sign.key_id(pub): pub}  # the host's keyring: kid -> public key


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def publish(definitions, key, tools_dir=TOOLS_DIR):
    """Publisher side: pin each implementation's SHA-256 in the manifest, then sign the canonical bytes."""
    signed = []
    for d in definitions:
        m = {**d, "impl": f"{d['name']}.py", "impl_sha256": release_sign.digest(Path(tools_dir) / f"{d['name']}.py")}
        sig = base64.b64encode(key.sign(canonical(m))).decode()
        signed.append({"manifest": m, "kid": release_sign.key_id(key.public_key()), "sig": sig})
    return signed


def _import(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(f"tool_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run


def verify_one(entry, trusted, tools_dir=TOOLS_DIR):
    m = entry.get("manifest") or {}
    if entry.get("kid") not in trusted:
        raise LoadError(f"{m.get('name')}: unsigned or unknown signer {entry.get('kid')}")
    try:
        trusted[entry["kid"]].verify(base64.b64decode(entry.get("sig", "")), canonical(m))
    except (InvalidSignature, ValueError):
        raise LoadError(f"{m.get('name')}: manifest signature invalid") from None
    path = Path(tools_dir) / m["impl"]
    if path.name != m["impl"] or release_sign.digest(path) != m["impl_sha256"]:  # verify the code we will import
        raise LoadError(f"{m['name']}: implementation digest mismatch")
    return Tool(m, _import(path, m["name"]))


def load_tools(signed, trusted, tools_dir=TOOLS_DIR, verify=True):
    """Returns (registry, rejected). A bad tool is excluded and reported; the others still load (fail closed per tool)."""
    registry, rejected = {}, []
    for entry in signed:
        try:
            if verify:
                tool = verify_one(entry, trusted, tools_dir)
            else:  # the seeded fault 'skip-signature': trust whatever is on disk
                m = entry["manifest"]
                tool = Tool(m, _import(Path(tools_dir) / m["impl"], m["name"]))
            if tool.manifest["name"] in registry:
                raise LoadError(f"{tool.manifest['name']}: duplicate tool name")
            registry[tool.manifest["name"]] = tool
        except LoadError as err:
            rejected.append(str(err))
    return registry, rejected


def pin_check(registry, listed):
    """MCP tools/list must match the signed manifests exactly (name, description, inputSchema): no silent drift."""
    problems = []
    for t in listed:
        m = registry.get(t["name"])
        if m is None:
            problems.append(f"{t['name']}: not in a signed manifest")
        elif canonical([t.get("description"), t.get("inputSchema")]) != canonical(
                [m.manifest["description"], m.manifest["inputSchema"]]):
            problems.append(f"{t['name']}: definition differs from the signed manifest")
    return problems


if __name__ == "__main__":
    defs = json.loads((HERE / "fixtures" / "toolpack.json").read_text(encoding="utf-8"))
    signed = publish(defs, publisher_key())
    reg, bad = load_tools(signed, trusted_keys())
    print("loaded:", sorted(reg), "rejected:", bad)
    print("kid:", signed[0]["kid"], "| signature bytes:", len(base64.b64decode(signed[0]["sig"])))
