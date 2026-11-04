"""Recompute every calculation answer and execute every 'What does this print?' snippet in content/qbank/*.json
(L100-L400 and, since the L500 theory level, L500.json).
Run from the topic folder or kb/: python research/qbank_checks.py   -> prints OK and exits 0, or lists failures and exits 1.
Calculation answers come from running code here (cryptography 50.0.2), never from mental arithmetic."""
import base64
import json
import math
import os
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

from cryptography.hazmat.primitives import hpke, serialization as ser
from cryptography.hazmat.primitives.asymmetric import ed25519, mldsa, mlkem, x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.dont_write_bytecode = True  # do not leave .pyc files in lab folders
TOPIC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOPIC / "labs" / "L200" / "08-hybrid-encryption"))


def _ed():
    k = ed25519.Ed25519PrivateKey.generate()
    return k, k.sign(b"release manifest")


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def l100_022():  # nonce || AES-256-GCM(100-byte plaintext)
    k, n = AESGCM.generate_key(bit_length=256), os.urandom(12)
    return f"{len(n + AESGCM(k).encrypt(n, bytes(100), None))} bytes"


def l100_023():  # birthday bound: 2^32 random 96-bit nonces
    n = 2**32
    p = n * (n - 1) / 2 / 2**96
    return f"about 2^{round(math.log2(p))}"


def l100_024():  # messages for a 50 % collision chance among random 96-bit nonces
    n50 = math.sqrt(2 * math.log(2) * 2**96)
    return f"about 2^{round(math.log2(n50))}"


def l100_031():  # Argon2id memory_cost is in KiB
    return f"{19456 * 1024 / 2**20:g} MiB"


def l100_032():  # scrypt memory = 128 * N * r bytes (RFC 7914)
    return f"{128 * 2**17 * 8 // 2**20} MiB"


def l100_033():
    guesses = 10**7
    return f"{guesses / 10**10:g} s vs {guesses / 10**4:g} s"


def l200_003():
    k, sig = _ed()
    return (f"private {len(k.private_bytes_raw())} B, public {len(k.public_key().public_bytes_raw())} B, "
            f"signature {len(sig)} B")


def l200_004():
    k, _ = _ed()
    priv = k.private_bytes(ser.Encoding.PEM, ser.PrivateFormat.PKCS8, ser.NoEncryption())
    pub = k.public_key().public_bytes(ser.Encoding.PEM, ser.PublicFormat.SubjectPublicKeyInfo)
    return f"private {len(priv)} B, public {len(pub)} B"


def l200_009():
    import seal_box
    bob = x25519.X25519PrivateKey.generate()
    return f"{len(seal_box.seal(bob.public_key(), b'db password rotation at 02:00'))} bytes"


def l200_022():
    return f"{(date(2026, 11, 27) - date(2026, 10, 28)).days} days"


def l200_036():
    _, sig = _ed()
    return f"{len(_b64u(sig))} characters"


def l300_001():  # wrapped DEK = nonce || AESGCM(KEK).encrypt(nonce, 32-byte DEK, kid)
    kek, n = AESGCM.generate_key(bit_length=256), os.urandom(12)
    return f"{len(n + AESGCM(kek).encrypt(n, os.urandom(32), b'orders-kek:v1'))} bytes"


def l300_002():
    records, wrapped, record_mib = 2_000_000, 60, 1
    return f"about {records * wrapped / 2**20:.0f} MiB vs about {records * record_mib / 2**20:.1f} TiB"


def l300_010():
    life = 160
    return f"hour {0.60 * life:g} to hour {0.72 * life:g}"


def l300_011():
    return f"{sum(1 for h in range(192) if h >= 160)} hours"


def l300_012():
    return f"{0.25 * 160:g} hours left"


def l300_027():
    _, sig = _ed()
    return f"{40 * len(sig):,} B vs {len(sig)} B"


def l300_030():
    return f"1 in 2^{4 * 8}"


def l400_001():
    _, ed_sig = _ed()
    ml_sig = mldsa.MLDSA65PrivateKey.generate().sign(b"doc")
    return f"{len(ed_sig) + len(ml_sig):,} B"


def l400_002():
    aeads, sig_algs = 2 + 1, 2
    sig_phases = sig_algs + 1  # Ed25519 only, ML-DSA-65 only, both
    return f"{aeads * sig_phases} suite ids vs {aeads + sig_algs} algorithm ids"


def l400_008():
    _, ed_sig = _ed()
    dual = len(ed_sig) + len(mldsa.MLDSA65PrivateKey.generate().sign(b"r"))
    return f"about {dual / 200:.1f}x"


def l400_009():
    k = mlkem.MLKEM768PrivateKey.generate()
    _, ct = k.public_key().encapsulate()
    xpub = len(x25519.X25519PrivateKey.generate().public_key().public_bytes_raw())
    return f"client {len(k.public_key().public_bytes_raw()) + xpub:,} B, server {len(ct) + xpub:,} B"


def l400_010():
    _, ed_sig = _ed()
    return f"about {len(mldsa.MLDSA65PrivateKey.generate().sign(b'm')) / len(ed_sig):.0f}x"


def l400_023():
    return f"about {1e6 / 40.1:,.0f} vs about {1e6 / 5001.5:,.0f}"


def l400_026():
    n = 64
    return f"{(n - 1) * (n - 2):,}"


def l400_027():
    n = 256
    return f"{n - 1} and {int(math.log2(n))}"


def l400_041():
    suite = hpke.Suite(hpke.KEM.MLKEM768_X25519, hpke.KDF.HKDF_SHA256, hpke.AEAD.AES_256_GCM)
    rk = hpke.MLKEM768X25519PrivateKey(mlkem.MLKEM768PrivateKey.generate(), x25519.X25519PrivateKey.generate())
    return f"{len(suite.encrypt(os.urandom(32), rk.public_key(), info=b'doc-share')):,} bytes"


def l100_007():
    return f"{2**30 // (64 * 1024):,} calls"


def l100_016():
    t = int(time.time())
    return f"{len(range(t - 3600, t + 3600 + 1)):,} seeds"


def l100_039():
    return f"{len(base64.b64encode(os.urandom(32)))} characters"


# ---------------- L500 (lessons 23-27): theory answers recomputed from first principles ----------------
def l500_002():  # 17^-1 mod 3120 by extended Euclid (pow(x, -1, m) uses the same algorithm)
    return str(pow(17, -1, 3120))


def l500_009():  # integer cube root of 42^3 (no modular wrap-around)
    c = 42 ** 3
    r = round(c ** (1 / 3))
    assert r ** 3 == c
    return str(r)


def l500_010():  # union bound for 2^40 random 96-bit nonces
    q, n = 2**40, 2**96
    return f"about 2^{round(math.log2(q * (q - 1) / (2 * n)))}"


def l500_011():  # smallest q with P[shared birthday] >= 1/2 (exact product)
    none, q = 1.0, 0
    while 1 - none < 0.5:
        none *= (365 - q) / 365
        q += 1
    return str(q)


def l500_021():  # advantage = |Pr[1 | exp 1] - Pr[1 | exp 0]|
    return f"{abs(7400 - 2600) / 10000:g}"


def l500_024():  # baby-step giant-step: about sqrt(q) operations for q ~ 2^256
    return f"about 2^{math.isqrt(2**256).bit_length() - 1}"


def l500_034():  # entropy of a uniform 6-digit passcode
    return f"about {math.log2(10**6):.1f} bits"


def l500_042():  # Shannon's H(K) for simple substitution, decimal digits
    return f"{math.log10(math.factorial(26)):.1f}"


CALC = {f"cr-{name[:4].upper()}-{name[5:]}": fn for name, fn in list(globals().items())
        if callable(fn) and name[:4] in ("l100", "l200", "l300", "l400", "l500") and name[4] == "_"}


def run_snippet(code: str) -> str:
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120, cwd=TOPIC)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip().splitlines()[-1] if r.stderr.strip() else f"exit {r.returncode}")
    return r.stdout.strip()


def is_output_question(q: dict) -> bool:
    return q["type"] == "code-reading" and "What does this print?" in q["question"]


def main() -> int:
    fails, n_calc, n_run, n_compiled, seen_calc = [], 0, 0, 0, set()
    for lv in ("L100", "L200", "L300", "L400", "L500"):
        for q in json.loads((TOPIC / "content" / "qbank" / f"{lv}.json").read_text(encoding="utf-8")):
            qid, shown = q["id"], q["options"][q["answer"]]
            if q["type"] == "calculation":
                if qid not in CALC:
                    fails.append(f"{qid}: calculation without a recompute function")
                    continue
                got = CALC[qid]()
                seen_calc.add(qid)
                n_calc += 1
                if got != shown:
                    fails.append(f"{qid}: computed {got!r}, keyed answer {shown!r}")
                if sum(o == got for o in q["options"]) != 1:
                    fails.append(f"{qid}: computed value must match exactly one option")
            if q.get("code"):
                try:
                    compile(q["code"], qid, "exec")
                    n_compiled += 1
                except SyntaxError as e:
                    fails.append(f"{qid}: snippet does not compile: {e}")
                    continue
                if is_output_question(q):
                    try:
                        out = run_snippet(q["code"])
                    except Exception as e:  # noqa: BLE001 - report any snippet failure
                        fails.append(f"{qid}: snippet failed: {e}")
                        continue
                    n_run += 1
                    if out != shown:
                        fails.append(f"{qid}: snippet printed {out!r}, keyed answer {shown!r}")
            elif is_output_question(q):
                fails.append(f"{qid}: output question without code")
    for qid in sorted(set(CALC) - seen_calc):
        fails.append(f"{qid}: recompute function has no calculation question")
    print(f"recomputed {n_calc} calculation answers; executed {n_run} output snippets; compiled {n_compiled} snippets")
    for f in fails:
        print("FAIL", f)
    if fails:
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
