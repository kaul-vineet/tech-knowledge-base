"""Fitness function: private signing keys never leave the token.
1) Static: outside the token implementation, no module reads private key bytes (private_bytes*, CKA_VALUE on a
   private handle, wrap_key). 2) Inventory: every private key on the deployed token is ALWAYS_SENSITIVE and
   NEVER_EXTRACTABLE. Threshold: 0 violations. Reused by the capstone."""
import ast
import unittest
from pathlib import Path

import solution_nonexportable as tok

HERE = Path(__file__).resolve().parent
TOKEN_IMPL = {"soft_token.py", "solution_nonexportable.py", "key_storage_options.py", "pkcs11_softhsm.py", "try_it.py"}
FORBIDDEN_CALLS = {"private_bytes", "private_bytes_raw", "wrap_key"}


def key_export_calls(paths) -> list:
    found = []
    for path in paths:
        for f in sorted(Path(path).rglob("*.py")):
            if f.name in TOKEN_IMPL or f.name.startswith("test_") or "__pycache__" in f.parts:
                continue
            for node in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in FORBIDDEN_CALLS:
                    found.append(f"{f.name}:{node.lineno}: {node.func.attr}")
    return found


def inventory(token) -> list:
    bad = []
    for h, o in token._objects.items():
        a = o["attrs"]
        if a[tok.st.CKA_CLASS] == "CKO_PRIVATE_KEY" and not (a[tok.CKA_ALWAYS_SENSITIVE] and a[tok.CKA_NEVER_EXTRACTABLE]):
            bad.append((h, a[tok.st.CKA_LABEL]))
    return bad


class TestNoKeyExport(unittest.TestCase):
    def test_no_module_reads_private_key_bytes(self):
        self.assertEqual(key_export_calls([HERE]), [])

    def test_token_inventory_is_non_exportable(self):
        token = tok.SoftToken("prod", so_pin="so", user_pin="pin")
        s = token.open_session()
        s.login("USER", "pin")
        for label in ("release-signing", "audit-log"):
            s.generate_key_pair(tok.CKM_EDDSA, label)
        self.assertEqual(inventory(token), [])

    def test_check_catches_a_leaky_token(self):
        token = tok.st.SoftToken("old", so_pin="so", user_pin="pin")  # unfixed defaults
        s = token.open_session()
        s.login("USER", "pin")
        s.generate_key_pair(tok.CKM_EDDSA, "legacy")
        self.assertEqual(len(inventory(token)), 1)


if __name__ == "__main__":
    unittest.main()
