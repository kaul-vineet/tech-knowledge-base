"""Deterministic, stdlib-only stand-in for a chat-completions server.

NOT a language model: it follows fixed rules so labs and tests give repeatable output
without downloading a model. Endpoints: GET /v1/models, POST /v1/chat/completions.

Rules (checked in this order):
  1. `tools` in the request   -> plan tool calls from the last user message
     (calculator: every arithmetic expression; get_time: the word "time"),
     return ONE tool call per turn, then a final text answer from the tool results.
  2. JSON requested           -> extract {name, age, city} from the text.
     With `response_format` the JSON is clean (like constrained decoding); without it
     the first answer is wrapped in prose + code fences (a common real failure mode).
  3. "sentiment" in prompt     -> keyword classifier; verbose without a system message,
     one label with one, mirrors the casing of few-shot assistant examples.
  4. EXTRA_RULES (topic hook)  -> first (marker, fn) whose marker is in the last user message;
                                 fn(user_text) returns the reply text. Topics register rules here.
  5. anything else            -> fixed echo reply.

Cryptography KB copy: the ONLY change to this vendored file is one EXTRA_RULES entry (see the end of
the file): marker "[[CRYPTO-REVIEW]]" -> _crypto_review(), a deliberately naive line-by-line regex
"reviewer" for labs/L100/06-encoding-hashing-encryption/agent_assist.py. It reports `random.*` calls
(CRY001) and EVERY hashlib call (CRY003, so it over-flags a legitimate SHA-256 file fingerprint) and
cannot see data flow, so it misses a constant nonce reused across AEAD calls (CRY002). Those mistakes
are on purpose: the lab's deterministic linter must catch them.
L200 addition (second EXTRA_RULES entry): marker "[[CERT-EXPLAIN]]" -> _cert_explain(), a naive
keyword reader of a certificate-verifier error for labs/L200/09-local-ca/agent_assist.py. It maps
"not valid at validation time" to EXPIRED even when the certificate is NOT YET valid (clock skew),
so one category is wrong on purpose: the lab's deterministic diagnose() must catch it.
L300 addition (third EXTRA_RULES entry): marker "[[SECRET-REVIEW]]" -> _secret_review(), a naive keyword
reviewer of an already-redacted log/config for labs/L300/16-secrets-handling/agent_assist.py. It flags every
line containing "password" or "token" (so it over-flags `token_ttl_seconds: 3600`) and misses leaks without
those words (an Authorization header, credentials inside a URL): the lab's deterministic scanner must judge.
L400 additions (fourth and fifth EXTRA_RULES entries):
- marker "[[THREAT-PROPOSE]]" -> _threat_propose(), a naive threat brainstormer for
  labs/L400/21-threat-model/agent_assist.py. From the element names inside <model>...</model> it proposes six fixed
  threats: two map to real controls, one is a real gap (no control), one uses a STRIDE letter that does not apply to
  the element, one names an element that does not exist and one invents a control. The lab's checker decides.
- marker "[[AUDIT-EXPLAIN]]" -> _audit_explain(), a naive explainer for labs/L400/22-capstone/agent_explain.py. It
  explains every "ANOMALY <id>" line it is given with a template, and also "explains" an anomaly id that the code never
  reported (A99), so the capstone must accept only explanations for anomalies its rules found.

Run:  python fake_model_server.py --port 8765   (base URL http://127.0.0.1:8765/v1)
"""
import argparse
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL_ID = "fake-model"
# Topic hook: list of (marker_string, function(user_text) -> reply_text). Checked before the echo reply.
EXTRA_RULES = []
NEG = {"died", "broke", "broken", "bad", "terrible", "slow", "refund", "never", "worst", "awful"}
POS = {"love", "great", "excellent", "fast", "perfect", "amazing", "good", "happy"}
EXPR = re.compile(r"\(?\d+(?:\.\d+)?(?:\s*[-+*/]\s*\(?\d+(?:\.\d+)?\)?)+")


def _text(msg):
    content = msg.get("content")
    if isinstance(content, list):  # "content parts" form: [{"type": "text", "text": ...}]
        return " ".join(p.get("text", "") for p in content if isinstance(p, dict))
    return content or ""


def _delimited(text):
    m = re.search(r"<(\w+)>(.*?)</\1>", text, re.S)  # data inside <tag>...</tag>
    return m.group(2) if m else text


def _sentiment(text):
    words = set(re.findall(r"[a-z]+", text.lower()))
    neg, pos = len(words & NEG), len(words & POS)
    return "negative" if neg > pos else "positive" if pos > neg else "neutral"


def _extract_person(text):
    text = _delimited(text)
    name = re.search(r"\b([A-Z][a-z]+)\b", text)
    age = re.search(r"\b(\d{1,3})\b", text)
    city = re.search(r"\b(?:in|to|from)\s+([A-Z][a-z]+)", text)
    return {"name": name.group(1) if name else None,
            "age": int(age.group(1)) if age else None,
            "city": city.group(1) if city else None}


def _tool_turn(messages, tools):
    names = {t.get("function", {}).get("name") for t in tools}
    last_user = max(i for i, m in enumerate(messages) if m.get("role") == "user")
    user_text = _text(messages[last_user])
    results = [m for m in messages[last_user + 1:] if m.get("role") == "tool"]
    plan = []
    if "get_time" in names and re.search(r"\btime\b", user_text, re.I):
        plan.append(("get_time", {}))
    if "calculator" in names:
        plan += [("calculator", {"expression": e.strip()}) for e in EXPR.findall(user_text)]
    if not plan:
        return None
    if len(results) < len(plan):  # one call per turn -> forces a multi-step loop
        name, args = plan[len(results)]
        call = {"id": f"call_{len(results) + 1}", "type": "function",
                "function": {"name": name, "arguments": json.dumps(args)}}
        return {"role": "assistant", "content": None, "tool_calls": [call]}, "tool_calls"
    parts = [f"{args.get('expression', name + '()')} = {_text(r)}" for (name, args), r in zip(plan, results)]
    return {"role": "assistant", "content": "Final answer: " + "; ".join(parts)}, "stop"


def _reply(req):
    messages = req["messages"]
    tools = req.get("tools") or []
    if tools:
        turn = _tool_turn(messages, tools)
        if turn:
            return turn
    all_text = " ".join(_text(m) for m in messages)
    user_texts = [_text(m) for m in messages if m.get("role") == "user"]
    user_text = user_texts[-1]
    rf = (req.get("response_format") or {}).get("type")
    if rf in ("json_object", "json_schema") or "json" in all_text.lower():
        # extract from the latest user message that carries delimited data (skips retry notes)
        data = next((t for t in reversed(user_texts) if _delimited(t) != t), user_text)
        body = json.dumps(_extract_person(data))
        retried = any(m.get("role") == "assistant" for m in messages)
        if rf or retried:
            return {"role": "assistant", "content": body}, "stop"
        return {"role": "assistant", "content": f"Sure! Here is the JSON:\n```json\n{body}\n```"}, "stop"
    if "sentiment" in all_text.lower():
        label = _sentiment(_delimited(user_text))
        examples = [_text(m) for m in messages if m.get("role") == "assistant"]
        if examples and examples[-1].isupper():
            label = label.upper()
        if any(m.get("role") == "system" for m in messages):
            return {"role": "assistant", "content": label}, "stop"
        return {"role": "assistant", "content": f"Sure! Reading the review carefully, I would say the "
                f"overall sentiment is {label}. Let me know if you want a more detailed analysis."}, "stop"
    for marker, fn in EXTRA_RULES:
        if marker in user_text:
            return {"role": "assistant", "content": fn(user_text)}, "stop"
    return {"role": "assistant", "content": f"Hello from {MODEL_ID}! You said: {user_text[:80]!r}"}, "stop"


def _validate(req):
    if not isinstance(req.get("model"), str) or not isinstance(req.get("messages"), list) or not req["messages"]:
        return "'model' (string) and non-empty 'messages' (list) are required"
    if not any(m.get("role") == "user" for m in req["messages"]):
        return "at least one 'user' message is required"
    call_ids = {c["id"] for m in req["messages"] for c in (m.get("tool_calls") or [])}
    for m in req["messages"]:
        if m.get("role") == "tool" and m.get("tool_call_id") not in call_ids:
            return "tool message has unknown or missing 'tool_call_id'"
    return None


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.rstrip("/") == "/v1/models":
            return self._send(200, {"object": "list", "data": [{"id": MODEL_ID, "object": "model", "owned_by": "local"}]})
        self._send(404, {"error": {"message": "not found", "type": "invalid_request_error"}})

    def do_POST(self):
        if self.path.rstrip("/") != "/v1/chat/completions":
            return self._send(404, {"error": {"message": "not found", "type": "invalid_request_error"}})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": {"message": "body is not valid JSON", "type": "invalid_request_error"}})
        problem = _validate(req)
        if problem:
            return self._send(400, {"error": {"message": problem, "type": "invalid_request_error"}})
        message, finish = _reply(req)
        prompt_tokens = sum(len(_text(m).split()) for m in req["messages"])
        completion_tokens = len((message.get("content") or "").split())
        self._send(200, {
            "id": "chatcmpl-fake", "object": "chat.completion", "created": 0, "model": req["model"],
            "choices": [{"index": 0, "message": message, "finish_reason": finish}],
            "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
                      "total_tokens": prompt_tokens + completion_tokens}})

    def log_message(self, *args):  # keep test output quiet
        pass


def start_in_thread(port=0):
    """Start the server on 127.0.0.1 (port 0 = any free port). Returns (server, base_url)."""
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/v1"


def _crypto_review(user_text):
    """Naive reviewer: regex per line of the <code> block; no data-flow analysis (see header)."""
    findings = []
    for n, line in enumerate(_delimited(user_text).splitlines(), start=1):
        if re.search(r"\brandom\.(choice|choices|randint|randrange|random|getrandbits|sample)\(", line):
            findings.append(f"CRY001 line {n}: the random module is a predictable PRNG; "
                            "use secrets.token_urlsafe() or secrets.token_hex() for tokens.")
        if re.search(r"\bhashlib\.\w+\(", line):
            findings.append(f"CRY003 line {n}: fast hash applied to a secret; "
                            "store passwords with Argon2id (or scrypt), never MD5/SHA-x.")
    return "\n".join(findings) or "No findings."


EXTRA_RULES.append(("[[CRYPTO-REVIEW]]", _crypto_review))


def _cert_explain(user_text):
    """Naive explainer: keywords in the ERROR line only; it never compares dates (see header)."""
    err = next((l for l in _delimited(user_text).splitlines() if l.startswith("ERROR:")), "").lower()
    if "subjectaltname" in err:
        return ("CATEGORY: HOSTNAME_MISMATCH\nWHY: the name the client asked for is not in the certificate's SAN list."
                "\nFIX: reissue the certificate with that DNS name in subjectAltName, or connect with a listed name.")
    if "validation time" in err:
        return ("CATEGORY: EXPIRED\nWHY: the certificate's validity period has ended.\nFIX: renew the certificate.")
    if "candidates exhausted" in err:
        return ("CATEGORY: UNTRUSTED_ISSUER\nWHY: no trusted root signed this chain.\n"
                "FIX: add the issuing CA to the client's trust store (or present the missing intermediate).")
    return "CATEGORY: UNKNOWN\nWHY: not enough information.\nFIX: inspect the certificate."


EXTRA_RULES.append(("[[CERT-EXPLAIN]]", _cert_explain))


def _secret_review(user_text):
    """Naive reviewer: keyword match per line of the <log> block; no understanding of values (see header)."""
    found = [f"LEAK line {n}: a credential appears to be logged here; remove it or log a reference instead."
             for n, line in enumerate(_delimited(user_text).splitlines(), start=1)
             if re.search(r"(?i)password|token", line)]
    return "\n".join(found) or "No leaks found."


EXTRA_RULES.append(("[[SECRET-REVIEW]]", _secret_review))


def _threat_propose(user_text):
    """Naive brainstormer: fixed proposals keyed on element names it can see (see header)."""
    seen = _delimited(user_text)
    ideas = [("doc-api->envelope-db", "T", "an attacker swaps a stored envelope for a forged one", "C-DUAL-SIG"),
             ("app-log", "I", "bearer tokens end up in the application log", "C-REDACT"),
             ("signer", "R", "nobody can prove which operator signed a release", "NONE"),
             ("client->doc-api", "E", "privilege escalation over the wire", "C-MTLS"),
             ("blockchain-ledger", "T", "the ledger is rewritten", "C-LEDGER"),
             ("envelope-db", "I", "database backups are readable by the backup operator", "C-QUANTUM-SHIELD")]
    lines = [f"THREAT {el} {s}: {what} | CONTROL {c}" for el, s, what, c in ideas if el in seen or el == "blockchain-ledger"]
    return "\n".join(lines) or "No threats proposed."


def _audit_explain(user_text):
    """Naive explainer: one template sentence per ANOMALY line, plus one invented anomaly (see header)."""
    ids = re.findall(r"ANOMALY (\w+) (\w+)", _delimited(user_text))
    out = [f"EXPLAIN {i}: rule {rule} fired; check who triggered it and whether it was expected." for i, rule in ids]
    return "\n".join(out + ["EXPLAIN A99: entry 3 also looks suspicious to me."])


EXTRA_RULES.append(("[[THREAT-PROPOSE]]", _threat_propose))
EXTRA_RULES.append(("[[AUDIT-EXPLAIN]]", _audit_explain))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    port = parser.parse_args().port
    print(f"fake model server on http://127.0.0.1:{port}/v1 (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
