"""Deterministic fake-model rule for lab 21's agent_assist.py (tests and --fake; NOT a model).

Registers ONE route in the vendored fake server (labs/_shared/local_agent/fake_model_server.py) through its
EXTRA_RULES hook, keyed on the marker "[[PQC-NOTES]]". The vendored server is unchanged. Replies imitate a small model:
  "Draft"     -> correct notes for every quantum-vulnerable item (should be accepted)
  "Summarise" -> drops the P1 sync.py ECDH item and tells you to replace AES-GCM (should be rejected)
  "Creative"  -> invents toy_app/payments.py, maps ECDSA to ML-KEM and quotes a 2029 deadline (should be rejected)
"""
MARKER = "[[PQC-NOTES]]"

GOOD = """- toy_app/billing.py:7 | RSA-3072 | ML-KEM-768 | P1
- toy_app/sync.py:7 | ECDH P-384 | ML-KEM-768 | P1
- toy_app/api_client.py:11 | X25519 | ML-KEM-768 | P2
- toy_app/auth.py:11 | ECDSA P-256 | ML-DSA-65 | P2
- toy_app/config/tls.toml:3 | RSA-2048 | ML-DSA-65 | P2
- toy_app/config/tls.toml:4 | ECDHE X25519/P-256 | ML-KEM-768 | P2"""

REPLIES = {
    "Draft": "Migration notes (NIST IR 8547: deprecated after 2030, disallowed after 2035):\n" + GOOD +
             "\nAES-GCM at rest stays as is.",
    "Summarise": "Short version:\n- toy_app/billing.py:7 | RSA-3072 | ML-KEM-768 | P1\n"
                 "- toy_app/storage.py:10 | AES-GCM | ML-KEM-768 | P2\nEverything else can wait.",
    "Creative": "Notes:\n- toy_app/payments.py:12 | RSA-2048 | ML-KEM-512 | P1\n" + GOOD.replace(
        "toy_app/auth.py:11 | ECDSA P-256 | ML-DSA-65", "toy_app/auth.py:11 | ECDSA P-256 | ML-KEM-768") +
                "\nAll of this must be finished by 2029.",
}


def reply(user_text):
    for key, text in REPLIES.items():
        if key in user_text:
            return text
    return "I am not sure what to migrate."


def register(fake_server_module):
    if all(marker != MARKER for marker, _ in fake_server_module.EXTRA_RULES):
        fake_server_module.EXTRA_RULES.append((MARKER, reply))
