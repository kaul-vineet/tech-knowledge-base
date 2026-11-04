"""Try it: two small experiments on the workbench (run: python try_it.py)."""
import hashlib

import sanity_check as lab

# 1) Version pinning: pretend requirements.txt pins an older release.
lab.PINNED = "49.0.0"
r = lab.run_checks()
ok = all(v for v in r.values() if isinstance(v, bool))
print("1) PINNED=49.0.0 -> cryptography_pinned:", r["cryptography_pinned"],
      "|", "WORKBENCH OK" if ok else "WORKBENCH NOT READY")

# 2) KAT input drift: `echo abc` hashes "abc\n", not "abc".
d = hashlib.sha256(b"abc\n").hexdigest()
print("2) sha256('abc\\n') =", d, "| matches NIST 'abc':", d == lab.NIST_ABC)
