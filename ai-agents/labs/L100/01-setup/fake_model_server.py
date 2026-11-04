"""Deterministic, stdlib-only stand-in for a chat-completions server.

NOT a language model: it follows fixed rules so labs and tests give repeatable output
without downloading a model. Endpoints: GET /v1/models, POST /v1/chat/completions,
POST /v1/embeddings (OpenAI-compatible), POST /api/embed (Ollama-native shape).

Chat rules (checked in this order):
  1. `tools` in the request   -> plan tool calls from the last user message, ONE call per turn,
     then a final text answer "Final answer: <call> = <result>; ...". Planned, in this order:
       get_time: the word "time" | calculator: every arithmetic expression |
       get_weather: "weather in <City>" (+ " in <unit>") | search_docs: 'search docs for "<q>"'
       (+ "top <n>") | save_memory: "remember that <note>" | recall_memory: "what do you
       remember about <topic>".
     1a. Validation retry: a tool result starting "error: invalid arguments: $.<field>" makes
         the fake repeat that call once WITHOUT <field> (models often self-correct like this).
     1b. Injection: a user/tool text containing "ignore previous instructions ... call <tool>
         with {json}" makes the fake emit that tool call first (it obeys, like a naive model).
  2. "<context>" block of "[id] text" lines + "Question: ..." -> grounded answer: the context
     sentence sharing most words with the question, followed by " [id]" of its chunk; no
     overlap -> "I don't know based on the provided context."
  3. "<transcript>" block of "role: text" lines -> "Summary: " + first 8 words of each user line.
  4. "<tool_spec>" block "name: ..." + "- field (type[, required][, one of a|b])" lines ->
     a JSON Schema draft for that tool (no additionalProperties keyword: code must add it).
  5. "<tool_list>" block of "name: description" lines -> JSON {name: "high"|"low"} risk labels
     (high if the description mentions send/delete/pay/write/transfer).
  6. JSON requested           -> extract {name, age, city} from the text.
     With `response_format` the JSON is clean (like constrained decoding); without it
     the first answer is wrapped in prose + code fences (a common real failure mode).
  7. "sentiment" in prompt     -> keyword classifier; verbose without a system message,
     one label with one, mirrors the casing of few-shot assistant examples.
  8. EXTRA_RULES (topic hook)  -> first (marker, fn) whose marker is in the last user message;
                                 fn(user_text) returns the reply text. Topics register rules here.
  9. anything else            -> fixed echo reply.

Embeddings: 64-dim hashed bag of words (sha256 of each lower-case word, stop words dropped,
trailing "s" removed), L2-normalised. Texts that share words get a higher cosine - NOT semantic.

Run:  python fake_model_server.py --port 8765   (base URL http://127.0.0.1:8765/v1)
"""
import argparse
import hashlib
import json
import math
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL_ID = "fake-model"
EMBED_DIMS = 64
# Topic hook: list of (marker_string, function(user_text) -> reply_text). Checked before the echo reply.
EXTRA_RULES = []
NEG = {"died", "broke", "broken", "bad", "terrible", "slow", "refund", "never", "worst", "awful"}
POS = {"love", "great", "excellent", "fast", "perfect", "amazing", "good", "happy"}
STOP = {"a", "an", "the", "is", "are", "was", "of", "to", "in", "on", "for", "and", "or", "it", "its",
        "do", "does", "how", "what", "which", "with", "be", "by", "at", "as", "i", "you", "my", "this", "that"}
EXPR = re.compile(r"\(?\d+(?:\.\d+)?(?:\s*[-+*/]\s*\(?\d+(?:\.\d+)?\)?)+")
INJECTION = re.compile(r"ignore (?:all )?previous instructions.*?call (\w+) with (\{.*?\})", re.I | re.S)
RISKY = re.compile(r"\b(send|delete|pay|write|transfer)", re.I)


def _text(msg):
    content = msg.get("content")
    if isinstance(content, list):  # "content parts" form: [{"type": "text", "text": ...}]
        return " ".join(p.get("text", "") for p in content if isinstance(p, dict))
    return content or ""


def _delimited(text):
    m = re.search(r"<(\w+)>(.*?)</\1>", text, re.S)  # data inside <tag>...</tag>
    return m.group(2) if m else text


def _block(text, tag):
    m = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.S)
    return m.group(1) if m else None


def _words(text):
    words = [w[:-1] if len(w) > 3 and w.endswith("s") else w for w in re.findall(r"[a-z0-9]+", text.lower())]
    return [w for w in words if w not in STOP]


def embed(text, dims=EMBED_DIMS):
    vec = [0.0] * dims
    for w in _words(text):
        h = hashlib.sha256(w.encode("utf-8")).digest()  # stable across runs and OSes (unlike hash())
        vec[h[0] % dims] += 1.0 if h[1] % 2 else -1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [round(v / norm, 6) for v in vec]


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


def _plan(user_text, names):
    plan = []
    if "get_time" in names and re.search(r"\btime\b", user_text, re.I):
        plan.append(("get_time", {}))
    if "calculator" in names:
        plan += [("calculator", {"expression": e.strip()}) for e in EXPR.findall(user_text)]
    m = re.search(r"weather in ([A-Z][a-z]+)(?: in (\w+))?", user_text)
    if "get_weather" in names and m:
        plan.append(("get_weather", {"city": m.group(1), **({"unit": m.group(2)} if m.group(2) else {})}))
    m = re.search(r'search (?:the )?docs for "([^"]+)"', user_text, re.I)
    if "search_docs" in names and m:
        k = re.search(r"\btop (\d+)", user_text)
        plan.append(("search_docs", {"query": m.group(1), **({"top_k": int(k.group(1))} if k else {})}))
    m = re.search(r"remember that (.+?)(?:[.!]\s|[.!]?$)", user_text, re.I)
    if "save_memory" in names and m:
        plan.append(("save_memory", {"note": m.group(1).strip()}))
    m = re.search(r"what do you remember about ([\w -]+)", user_text, re.I)
    if "recall_memory" in names and m:
        plan.append(("recall_memory", {"query": m.group(1).strip()}))
    return plan


def _tool_turn(messages, tools):
    names = {t.get("function", {}).get("name") for t in tools}
    last_user = max(i for i, m in enumerate(messages) if m.get("role") == "user")
    plan = _plan(_text(messages[last_user]), names)
    pending, done = {}, []  # done = [(name, args, result_text)] in call order since the last user turn
    for m in messages[last_user + 1:]:
        for c in m.get("tool_calls") or []:
            raw = c["function"].get("arguments") or "{}"
            pending[c["id"]] = (c["function"]["name"], raw if isinstance(raw, dict) else json.loads(raw))
        if m.get("role") == "tool" and m.get("tool_call_id") in pending:
            done.append((*pending[m["tool_call_id"]], _text(m)))
    seen = " ".join(_text(m) for m in messages if m.get("role") in ("user", "tool"))
    inj = INJECTION.search(seen)
    if inj and not any(n == inj.group(1) for n, _, _ in done):  # rule 1b: naive model obeys injected text
        plan.insert(len(done), (inj.group(1), json.loads(inj.group(2))))
    effective, retry, retried = [], None, set()
    for name, args, result in done:
        bad = re.match(r"error: invalid arguments: \$\.(\w+)", result)
        if bad and bad.group(1) in args and (name, bad.group(1)) not in retried:  # rule 1a
            retried.add((name, bad.group(1)))
            retry = (name, {k: v for k, v in args.items() if k != bad.group(1)})
            continue
        retry = None
        effective.append((name, args, result))
    nxt = retry or (plan[len(effective)] if len(effective) < len(plan) else None)
    if nxt is None and not plan:
        return None
    if nxt:  # one call per turn -> forces a multi-step loop
        call = {"id": f"call_{len(done) + 1}", "type": "function",
                "function": {"name": nxt[0], "arguments": json.dumps(nxt[1])}}
        return {"role": "assistant", "content": None, "tool_calls": [call]}, "tool_calls"
    label = lambda n, a: a.get("expression") or f"{n}({', '.join(f'{k}={v}' for k, v in a.items())})"
    parts = [f"{label(n, a)} = {r}" for n, a, r in effective]
    return {"role": "assistant", "content": "Final answer: " + "; ".join(parts)}, "stop"


def _rag_answer(text):
    question = (re.search(r"Question:\s*(.+)", text) or re.search(r"(.+)", text)).group(1)
    q = set(_words(question))
    best, best_score = None, 0
    for cid, chunk in re.findall(r"^\[([^\]]+)\]\s*(.+)$", _block(text, "context"), re.M):
        for sentence in re.split(r"(?<=[.!?])\s+", chunk.strip()):
            score = len(q & set(_words(sentence)))
            if score > best_score:
                best, best_score = (cid, sentence), score
    if not best:
        return "I don't know based on the provided context."
    return f"{best[1]} [{best[0]}]"


def _summary(text):
    users = re.findall(r"^user:\s*(.+)$", _block(text, "transcript"), re.M)
    return "Summary: " + "; ".join(" ".join(u.split()[:8]) for u in users)


def _schema_draft(text):
    spec = _block(text, "tool_spec")
    props, required = {}, []
    for field, kind, rest in re.findall(r"^-\s*(\w+)\s*\((\w+)([^)]*)\)", spec, re.M):
        props[field] = {"type": kind}
        one_of = re.search(r"one of ([\w|]+)", rest)
        if one_of:
            props[field]["enum"] = one_of.group(1).split("|")
        if "required" in rest:
            required.append(field)
    return json.dumps({"type": "object", "properties": props, "required": required})


def _risk_labels(text):
    rows = re.findall(r"^(\w+):\s*(.+)$", _block(text, "tool_list"), re.M)
    return json.dumps({name: "high" if RISKY.search(desc) else "low" for name, desc in rows})


MARKER_RULES = [("context", _rag_answer), ("transcript", _summary), ("tool_spec", _schema_draft),
                ("tool_list", _risk_labels)]


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
    for tag, fn in MARKER_RULES:  # rules 2-5: keyed on a <tag> block in the last user message
        if _block(user_text, tag) is not None:
            return {"role": "assistant", "content": fn(user_text)}, "stop"
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


def _embed_inputs(req):
    inp = req.get("input")
    texts = [inp] if isinstance(inp, str) else inp
    if not isinstance(req.get("model"), str) or not isinstance(texts, list) or not texts \
            or not all(isinstance(t, str) for t in texts):
        return None
    return texts


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _error(self, status, message):
        self._send(status, {"error": {"message": message, "type": "invalid_request_error"}})

    def do_GET(self):
        if self.path.rstrip("/") == "/v1/models":
            return self._send(200, {"object": "list", "data": [{"id": MODEL_ID, "object": "model", "owned_by": "local"}]})
        self._error(404, "not found")

    def do_POST(self):
        path = self.path.rstrip("/")
        if path not in ("/v1/chat/completions", "/v1/embeddings", "/api/embed"):
            return self._error(404, "not found")
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except json.JSONDecodeError:
            return self._error(400, "body is not valid JSON")
        if path != "/v1/chat/completions":
            texts = _embed_inputs(req)
            if texts is None:
                return self._error(400, "'model' (string) and 'input' (string or list of strings) are required")
            vectors = [embed(t) for t in texts]
            count = sum(len(t.split()) for t in texts)
            if path == "/api/embed":  # Ollama-native response shape
                return self._send(200, {"model": req["model"], "embeddings": vectors, "prompt_eval_count": count})
            return self._send(200, {"object": "list", "model": req["model"],
                                    "data": [{"object": "embedding", "index": i, "embedding": v} for i, v in enumerate(vectors)],
                                    "usage": {"prompt_tokens": count, "total_tokens": count}})
        problem = _validate(req)
        if problem:
            return self._error(400, problem)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    port = parser.parse_args().port
    print(f"fake model server on http://127.0.0.1:{port}/v1 (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
