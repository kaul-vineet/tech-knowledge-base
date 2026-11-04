"""Agent assist: a local model reviews a log/config for leaked secrets; the deterministic scanner decides.
Pipeline: scan -> redact -> secret gate (must find nothing) -> model -> compare every claim with the scanner.
The model never sees a secret value: the gate reuses lesson 9's SECRET regex plus this lesson's scanner.
Default: deterministic fake model server. --real: Ollama/llama.cpp at LOCAL_MODEL_URL / LOCAL_MODEL."""
import argparse
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "_shared"))  # labs/_shared/local_agent
sys.path.append(str(HERE.parents[1] / "L200" / "09-local-ca"))  # local_ca, needed by lesson 9's module
from local_agent import fake_model_server  # noqa: E402
from local_agent.client import chat  # noqa: E402

from secrets_app import PATTERNS, SENSITIVE_KEY, scan_log  # noqa: E402

_spec = importlib.util.spec_from_file_location("l200_agent_assist", HERE.parents[1] / "L200" / "09-local-ca" / "agent_assist.py")
_l200 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_l200)
SECRET_GATE = _l200.SECRET  # the topic's secret gate: PEM keys, long hex, base64/base64url keys, JWK private members

SYSTEM = ("You review application logs and config for leaked credentials. Values are already redacted. "
          "For each line that leaked a credential answer 'LEAK line N: reason'. If none, answer 'No leaks found.'")
MASK = "[REDACTED]"


def redact(text: str) -> str:
    for kind, rx in PATTERNS.items():
        text = rx.sub(f"://{MASK}@" if kind == "URL_CREDENTIALS" else MASK, text)
    return re.sub(r'("?)([\w-]+)("?\s*[:=]\s*)"?[^",}\s]+"?',
                  lambda m: m.group(0) if not SENSITIVE_KEY.search(m.group(2)) else f'{m.group(1)}{m.group(2)}{m.group(3)}"{MASK}"',
                  text)


def gate(text: str) -> str:
    if scan_log(text) or SECRET_GATE.search(text):  # deterministic: refuse rather than hope
        raise ValueError("refusing to send: secret-like content survived redaction")
    return text


def review(text: str, base_url=None, model=None):
    truth = {n for n, _, _ in scan_log(text)}  # ground truth: lines the scanner flags
    reply = chat([{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": f"[[SECRET-REVIEW]] Review this:\n<log>{gate(redact(text))}</log>"}],
                 base_url=base_url, model=model)
    claimed = {int(n): why.strip() for n, why in re.findall(r"LEAK line (\d+):?(.*)", reply)}
    rows = [(n, f"CONFIRMED - agent explains: {claimed[n][:58]}" if n in truth else "REJECTED (scanner: no leak)")
            for n in sorted(claimed)]
    rows += [(n, "MISSED by agent (scanner found it)") for n in sorted(truth - set(claimed))]
    return sorted(rows), truth


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true", help="use LOCAL_MODEL_URL / LOCAL_MODEL (e.g. Ollama)")
    ap.add_argument("file", nargs="?", default=str(HERE / "review_me.log"))
    args = ap.parse_args(argv)
    text = Path(args.file).read_text(encoding="utf-8")
    server, base_url, model = None, None, None
    if not args.real:
        server, base_url = fake_model_server.start_in_thread()
        model = fake_model_server.MODEL_ID
    try:
        rows, truth = review(text, base_url, model)
    finally:
        if server:
            server.shutdown()
            server.server_close()
    print("sent to the model (redacted):")
    print("\n".join("  " + line for line in redact(text).splitlines()))
    for n, verdict in rows:
        print(f"line {n}: {verdict}")
    print(f"LEAKS = {sorted(truth)} (decided by scan_log); the agent only proposes and explains.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
