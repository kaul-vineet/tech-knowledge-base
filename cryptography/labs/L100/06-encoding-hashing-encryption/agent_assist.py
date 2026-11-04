"""Agent assist: a local model reviews a snippet for crypto misuse; misuse_lint.py is the judge.

The agent only proposes and explains. Every claim is checked against the deterministic linter:
CONFIRMED (both agree), MISSED (linter only), REJECTED (agent only). The verdict comes from code.
Default: the deterministic fake model server (no download). --real: Ollama/llama.cpp at LOCAL_MODEL_URL.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))  # labs/_shared/local_agent
from local_agent import fake_model_server  # noqa: E402
from local_agent.client import chat  # noqa: E402

from misuse_lint import lint  # noqa: E402

SYSTEM = ("You review Python code for cryptography misuse. Report only these rules: "
          "CRY001 = random module used for a token/secret; CRY002 = AEAD nonce constant or reused; "
          "CRY003 = fast hash (MD5/SHA-x) used to store a password. "
          "Output one line per finding, exactly: CRYxxx line N: reason. If none, output: No findings.")
CLAIM = re.compile(r"\b(CRY00[1-3])\b\D{0,12}?(\d+)")
SECRET_PATTERNS = {  # guard: never send real keys/secrets to a model
    "PEM private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "long hex string": re.compile(r"\b[0-9a-fA-F]{32,}\b"),
    "long base64 string": re.compile(r"[A-Za-z0-9+/]{40,}={0,2}"),
    "AWS access key id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    # base64url (JWK/JWT alphabet, no padding): a 32-byte key is 43 chars; mixed case + digit avoids long identifiers
    "long base64url string": re.compile(r"(?<![\w-])(?=[\w-]*\d)(?=[\w-]*[A-Z])(?=[\w-]*[a-z])[A-Za-z0-9_-]{43,}"),
    "JWK private member": re.compile(r'"(?:d|p|q|dp|dq|qi|k)"\s*:\s*"[A-Za-z0-9_-]{16,}'),
}


def find_secrets(text: str) -> list:
    return [name for name, rx in SECRET_PATTERNS.items() if rx.search(text)]


def ask_agent(snippet: str, base_url=None, model=None) -> str:
    leaks = find_secrets(snippet)
    if leaks:  # deterministic gate before anything leaves the process
        raise ValueError(f"refusing to send snippet to a model: looks like it contains {leaks}")
    numbered = "\n".join(f"{n:>3}| {line}" for n, line in enumerate(snippet.splitlines(), start=1))
    user = f"[[CRYPTO-REVIEW]] Review this code (line numbers on the left):\n<code>{numbered}</code>"
    return chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                base_url=base_url, model=model)


def judge(snippet: str, reply: str) -> dict:
    truth = {(f.rule, f.line): f.why for f in lint(snippet)}  # deterministic judge
    claims = {}
    for raw in reply.splitlines():
        m = CLAIM.search(raw)
        if m:
            claims[(m.group(1), int(m.group(2)))] = raw.split(":", 1)[-1].strip()
    return {"confirmed": {k: claims[k] for k in sorted(claims.keys() & truth.keys())},
            "missed": {k: truth[k] for k in sorted(truth.keys() - claims.keys())},
            "rejected": {k: claims[k] for k in sorted(claims.keys() - truth.keys())},
            "linter_findings": len(truth)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", default=str(Path(__file__).with_name("review_me.txt")))
    ap.add_argument("--real", action="store_true", help="use LOCAL_MODEL_URL / LOCAL_MODEL (e.g. Ollama)")
    args = ap.parse_args(argv)
    snippet = Path(args.file).read_text(encoding="utf-8")
    server = None
    if args.real:
        base_url, model = None, None  # client.py reads LOCAL_MODEL_URL / LOCAL_MODEL
    else:
        server, base_url = fake_model_server.start_in_thread()  # binds 127.0.0.1, random free port
        model = fake_model_server.MODEL_ID
    try:
        result = judge(snippet, ask_agent(snippet, base_url, model))
    finally:
        if server:
            server.shutdown()
            server.server_close()
    for (rule, line), text in result["confirmed"].items():
        print(f"CONFIRMED {rule} line {line:<3} agent explains: {text}")
    for (rule, line), why in result["missed"].items():
        print(f"MISSED    {rule} line {line:<3} linter: {why} (agent did not report it)")
    for (rule, line), text in result["rejected"].items():
        print(f"REJECTED  {rule} line {line:<3} agent claim not backed by the linter: {text}")
    n = result["linter_findings"]
    print(f"VERDICT (from linter, not agent): {'FAIL' if n else 'PASS'} - {n} misuse(s)")
    return 0  # demo snippet is meant to fail; exit 0 so CI can run the script


if __name__ == "__main__":
    sys.exit(main())
