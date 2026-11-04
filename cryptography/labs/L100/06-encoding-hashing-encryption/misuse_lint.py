"""Deterministic crypto-misuse linter (the judge for agent_assist.py). Reads code, never runs it."""
import ast
import sys
from pathlib import Path
from typing import NamedTuple

PRNG_FUNCS = {"choice", "choices", "randint", "randrange", "random", "getrandbits", "sample", "randbytes"}
FAST_HASHES = {"md5", "sha1", "sha224", "sha256", "sha384", "sha512", "blake2b", "blake2s", "new",
               "sha3_224", "sha3_256", "sha3_384", "sha3_512"}
PASSWORD_HINTS = ("pass", "pw", "pwd")


class Finding(NamedTuple):
    rule: str
    line: int
    why: str


def _arg_names(call):
    return {n.id.lower() for a in call.args + [k.value for k in call.keywords]
            for n in ast.walk(a) if isinstance(n, ast.Name)}


def lint(source: str) -> list:
    tree = ast.parse(source)
    module_consts = {t.id for s in tree.body if isinstance(s, ast.Assign) for t in s.targets
                     if isinstance(t, ast.Name)}
    found = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        owner = node.func.value.id if isinstance(node.func.value, ast.Name) else None
        attr = node.func.attr
        # CSPRNG vs PRNG: the random module is seedable and predictable -> never for tokens/keys
        if owner == "random" and attr in PRNG_FUNCS:
            found.append(Finding("CRY001", node.lineno, f"random.{attr}() is a predictable PRNG"))
        # nonce reuse: a literal or module-level nonce is the SAME value on every encrypt call
        if attr == "encrypt" and node.args:
            nonce = node.args[0]
            if isinstance(nonce, (ast.Constant, ast.BinOp)) or (
                    isinstance(nonce, ast.Name) and nonce.id in module_consts):
                found.append(Finding("CRY002", node.lineno, "AEAD nonce is a constant (reused per key)"))
        # password storage: fast hashes are cheap to brute-force -> use Argon2id/scrypt
        if owner == "hashlib" and attr in FAST_HASHES and any(
                h in name for name in _arg_names(node) for h in PASSWORD_HINTS):
            found.append(Finding("CRY003", node.lineno, f"hashlib.{attr}() used on a password"))
    return sorted(found)


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("review_me.txt")
    findings = lint(path.read_text(encoding="utf-8"))
    for f in findings:
        print(f"{f.rule} line {f.line}: {f.why}")
    print(f"{len(findings)} finding(s) in {path.name}")
