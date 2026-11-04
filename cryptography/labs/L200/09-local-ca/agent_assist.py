"""Agent assist: a local model EXPLAINS a certificate validation failure; code is the judge.

The verifier (local_ca.verify) decides pass/fail. diagnose() derives the true category from the
certificate's public fields. The agent's CATEGORY is CONFIRMED only if it equals diagnose(); otherwise
REJECTED. Only public certificate facts are sent: never private keys (a guard refuses them).
Default: deterministic fake model server. --real: Ollama/llama.cpp at LOCAL_MODEL_URL.
"""
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))  # labs/_shared/local_agent
from local_agent import fake_model_server  # noqa: E402
from local_agent.client import chat  # noqa: E402

from cryptography import x509  # noqa: E402
from cryptography.exceptions import InvalidSignature  # noqa: E402
import local_ca  # noqa: E402

SYSTEM = ("You explain X.509 certificate validation failures to a developer. Answer in exactly three lines: "
          "CATEGORY: one of HOSTNAME_MISMATCH, EXPIRED, NOT_YET_VALID, UNTRUSTED_ISSUER | WHY: one sentence | "
          "FIX: one sentence.")
SECRET = re.compile("|".join([  # key material never leaves the process (the report holds public fields only)
    r"PRIVATE KEY",                                                      # PEM private key header
    r"\b[0-9a-fA-F]{64,}\b",                                             # raw key/secret as long hex
    r"[A-Za-z0-9+/]{40,}={0,2}",                                         # base64: a 32-byte key is 44 chars
    r"(?<![\w-])(?=[\w-]*\d)(?=[\w-]*[A-Z])(?=[\w-]*[a-z])[A-Za-z0-9_-]{43,}",  # base64url, unpadded (43 chars)
    r'"(?:d|p|q|dp|dq|qi|k)"\s*:\s*"[A-Za-z0-9_-]{16,}',                  # JWK private members
]))


def diagnose(leaf, roots, hostname, at):  # deterministic ground truth from public fields
    if not any(r.subject == leaf.issuer and _signed_by(leaf, r) for r in roots):
        return "UNTRUSTED_ISSUER"
    if at < leaf.not_valid_before_utc:
        return "NOT_YET_VALID"
    if at > leaf.not_valid_after_utc:
        return "EXPIRED"
    sans = leaf.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName)
    return "OK" if hostname in sans else "HOSTNAME_MISMATCH"


def _signed_by(leaf, root):
    try:
        leaf.verify_directly_issued_by(root)
        return True
    except (ValueError, TypeError, InvalidSignature):  # different issuer name or bad signature
        return False


def report(leaf, hostname, at, error):
    sans = [str(n.value) for n in leaf.extensions.get_extension_for_class(x509.SubjectAlternativeName).value]
    return (f"ERROR: {error}\nhostname requested: {hostname}\ncheck time: {at:%Y-%m-%d %H:%M}Z\n"
            f"subject: {leaf.subject.rfc4514_string()}\nissuer: {leaf.issuer.rfc4514_string()}\nSAN: {sans}\n"
            f"notBefore: {leaf.not_valid_before_utc:%Y-%m-%d}\nnotAfter: {leaf.not_valid_after_utc:%Y-%m-%d}")


def ask_agent(text, base_url=None, model=None):
    if SECRET.search(text):  # deterministic gate before anything leaves the process
        raise ValueError("refusing to send: looks like key material")
    return chat([{"role": "system", "content": SYSTEM},
                 {"role": "user", "content": f"[[CERT-EXPLAIN]] Explain this failure:\n<report>{text}</report>"}],
                base_url=base_url, model=model)


def scenarios():
    ca_key, ca = local_ca.make_root()
    _, leaf = local_ca.issue_server(ca_key, ca)
    _, future = local_ca.issue_server(ca_key, ca, not_before=local_ca.NOW + dt.timedelta(days=2))
    other = local_ca.make_root("Some Other Root")[1]
    now = local_ca.NOW
    return [("wrong host", leaf, [ca], "example.com", now), ("expired", leaf, [ca], "localhost", now + dt.timedelta(days=31)),
            ("clock skew", future, [ca], "localhost", now), ("untrusted CA", leaf, [other], "localhost", now)]


def run(base_url=None, model=None):
    rows = []
    for label, leaf, roots, host, at in scenarios():
        try:
            local_ca.verify(leaf, roots, host, at=at)
            error = None
        except x509.verification.VerificationError as e:
            error = str(e).split(" (encountered")[0]
        truth = diagnose(leaf, roots, host, at)
        reply = ask_agent(report(leaf, host, at, error), base_url, model)
        m = re.search(r"CATEGORY:\s*([A-Z_]+)", reply)
        claimed = m.group(1) if m else "NONE"
        why = next((ln[4:].strip() for ln in reply.splitlines() if ln.startswith("WHY:")), "")
        rows.append((label, "FAIL" if error else "PASS", truth, claimed,
                     "CONFIRMED" if claimed == truth else "REJECTED", why))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true", help="use LOCAL_MODEL_URL / LOCAL_MODEL (e.g. Ollama)")
    args = ap.parse_args(argv)
    server, base_url, model = None, None, None
    if not args.real:
        server, base_url = fake_model_server.start_in_thread()
        model = fake_model_server.MODEL_ID
    try:
        rows = run(base_url, model)
    finally:
        if server:
            server.shutdown()
            server.server_close()
    for label, verdict, truth, claimed, status, why in rows:
        print(f"{label:<13} verifier={verdict}  code says {truth:<17} agent says {claimed:<17} {status}")
        if status == "CONFIRMED":
            print(f"{'':<13} agent explains: {why}")
    print("VERDICTS come from the verifier; categories from diagnose(); the agent only explains.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
