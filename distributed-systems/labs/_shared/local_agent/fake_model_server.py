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

Run:  python fake_model_server.py --port 8765   (base URL http://127.0.0.1:8765/v1)

Topic rule added in this copy (distributed-systems), registered in EXTRA_RULES:
  "[[RETRY-LOG-SUMMARY]]" -> reads `status=<code> latency_ms=<x>` log lines and answers
  attempts=/errors=/p50_ms=/p99_ms= lines plus a one-line summary. It deliberately makes two
  classic mistakes (p50 = the MEAN, p99 = the MAX) so lab 04's code checker has something to catch.
  "[[SHARD-LAYOUT]]" (L200 lab 09) -> reads `name@zone` nodes, "Place <N> shards" and "<R> replicas each",
  builds a zone-aware round-robin layout, then breaks it on purpose: shard 5's zone-b replica is swapped
  for a zone-a node (two replicas in one zone, and that node goes over capacity). One 'S<i>: a,b,c' line
  per shard plus a confident (wrong) summary line, so lab 09's checker has something to reject.
  "[[PARTITION-HISTORY]]" (L300 lab 13) -> reads "<node> acquired the lease" event lines and the history lines
  ({"process", "type", "f", "value", ...}), then explains them with two classic mistakes on purpose: it names the
  NEWEST lease holder as the stale leader and the FIRST acknowledged write as the lost one. It answers the
  linearizable question correctly ("no"). Lines: linearizable: / stale_leader: / lost_write: / summary:.
  "[[CHAOS-SCORECARD]]" (L400 capstone 22) -> reads the campaign's JSON lines ({"experiment", "held", "harmed_orders",
  "duplicates_absorbed", ...}), aggregates per experiment and answers one 'fault: <name> held=<yes|no> harmed=<n>' line
  each, a summary line and a 'verdict:' line. Mistakes on purpose: it reports relay-crash as NOT held and claims 3
  harmed orders for burst; it also volunteers a release verdict, which the capstone code must ignore.
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


def _retry_log_summary(text):
    rows = re.findall(r"status=(\d+) latency_ms=([\d.]+)", text)
    if not rows:
        return "I could not find any log lines."
    lat = [float(ms) for _, ms in rows]
    errors = sum(code != "200" for code, _ in rows)
    return (f"attempts={len(rows)}\nerrors={errors}\n"
            f"p50_ms={sum(lat) / len(lat):.1f}\n"  # mistake on purpose: mean, not median
            f"p99_ms={max(lat):.1f}\n"  # mistake on purpose: max, not 99th percentile
            f"summary: most requests succeed; about {round(100 * errors / len(rows))}% of attempts "
            f"fail with 503 and are retried, and a few slow calls stretch the latency tail.")


EXTRA_RULES.append(("[[RETRY-LOG-SUMMARY]]", _retry_log_summary))


def _shard_layout(text):
    nodes = re.findall(r"\b(\w+)@(\w+)\b", text)
    shards = int((re.search(r"Place (\d+) shards", text) or [0, 8])[1])
    zones = {}
    for name, zone in nodes:
        zones.setdefault(zone, []).append(name)
    if not zones:
        return "I could not find any nodes."
    groups = list(zones.values())
    layout = [[g[(i + z) % len(g)] for z, g in enumerate(groups)] for i in range(shards)]
    if shards > 5 and len(groups) > 1:  # mistake on purpose: 2nd replica of S5 taken from the 1st zone
        layout[5][1] = next(n for n in groups[0] if n not in layout[5])
    lines = [f"S{i}: {','.join(ns)}" for i, ns in enumerate(layout)]
    return "\n".join(lines) + "\nsummary: every shard spans all zones and every node holds the same number of replicas."


EXTRA_RULES.append(("[[SHARD-LAYOUT]]", _shard_layout))


def _partition_history(text):
    holders = re.findall(r"\b(n\d+) acquired the lease", text)
    writes = re.findall(r'"process": "(\w+)", "type": "ok", "f": "write", "value": (\d+)', text)
    if not holders or not writes:
        return "I could not find lease events or acknowledged writes."
    return (f"linearizable: no\nstale_leader: {holders[-1]}\n"  # mistake on purpose: newest holder, not the stale one
            f"lost_write: {writes[0][0]} write {writes[0][1]}\n"  # mistake on purpose: first acked write
            f"summary: during the partition {holders[-1]} kept writing with an old lease, so the first "
            f"acknowledged write was overwritten and later reads missed it.")


EXTRA_RULES.append(("[[PARTITION-HISTORY]]", _partition_history))


def _chaos_scorecard(text):
    rows = [json.loads(line) for line in re.findall(r'^\{.*"experiment".*\}$', text, re.M)]
    if not rows:
        return "I could not find any experiment results."
    agg = {}
    for r in rows:
        held, harmed = agg.get(r["experiment"], (True, 0))
        agg[r["experiment"]] = (held and r["held"], harmed + r["harmed_orders"])
    lines = []
    for name, (held, harmed) in agg.items():
        if name == "relay-crash":
            held = False  # mistake on purpose: a relay crash "looks" scary
        if name == "burst":
            harmed = 3  # mistake on purpose: an invented number
        lines.append(f"fault: {name} held={'yes' if held else 'no'} harmed={harmed}")
    absorbed = sum(r.get("duplicates_absorbed", 0) for r in rows)
    return "\n".join(lines) + (f"\nsummary: idempotent consumers absorbed {absorbed} duplicate deliveries; the relay "
                               f"crash is the weak spot.\nverdict: PASS - safe to release")


EXTRA_RULES.append(("[[CHAOS-SCORECARD]]", _chaos_scorecard))


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    port = parser.parse_args().port
    print(f"fake model server on http://127.0.0.1:{port}/v1 (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
