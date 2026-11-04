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

Topic extension (application-architecture copy only; the shared original is unchanged):
  [[ADR-DRAFT]] marker       -> fills a Nygard ADR from the Number/Title/Context/Decision/Consequences
                                lines inside <brief>...</brief>. Scripted failure on purpose: the first
                                draft says 'Accepted.' (like copying ADR 1); a message that contains
                                'Problems:' gets 'Proposed.' so the lab can show check -> retry.
                                Avoid the words j-s-o-n / sentiment in that prompt (rules 2-3 win).
  [[EVENT-SCHEMA]] marker    -> (L200 lesson 9) builds an AsyncAPI 3 fragment (channels, operations,
                                components) from the Event/Channel/Address/Fields lines inside
                                <brief>...</brief>. Scripted failure on purpose: the first reply uses the
                                AsyncAPI 2 verb 'publish', omits 'required' and types integer fields as
                                string; a message that contains 'Problems:' gets a corrected fragment.
                                Same caveat: no j-s-o-n / sentiment words anywhere in that conversation.
  [[INCIDENT-SUMMARY]] marker -> (L300 lesson 15) writes a short incident summary from the key: value lines
                                inside <brief>...</brief> (evaluated_at, alert, windows, burn_rate, slow_since,
                                p99_ms, p95_ms, mean_ms, budget_used_1h, availability_3d). Scripted failure on
                                purpose: the first draft quotes the MEAN as the p99 and moves the burn rate's
                                decimal point; a message that contains 'Problems:' gets the correct numbers.
                                Same caveat: no j-s-o-n / sentiment words anywhere in that conversation.
  [[CAPACITY-MEMO]] marker   -> (L400 lesson 21) writes a capacity memo from the key: value lines inside
                                <brief>...</brief> (peak_rps, avg_rps, mean_service_ms, in_flight_at_peak,
                                capacity_rps, instances, p99_at_peak_ms, p99_one_down_ms, cost_per_million_usd,
                                email_senders, rejected_option, rejected_instances). Scripted failure on purpose:
                                the first draft sizes on the AVERAGE rate (quotes avg_rps as the peak, invents an
                                in-flight number and recommends 1 instance); 'Problems:' gets the correct memo.
  [[GO-NO-GO]] marker        -> (L400 capstone) explains a release scorecard from the key: value lines inside
                                <brief>...</brief> (passed, total, failed, verdict). Scripted failure on purpose:
                                the first draft says GO although criteria failed; 'Problems:' gets an honest summary.
                                Same caveat for both: no j-s-o-n / sentiment words anywhere in that conversation.

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


def _adr_draft(user_text):
    brief = dict(re.findall(r"^(Number|Title|Context|Decision|Consequences):\s*(.+)$", _delimited(user_text), re.M))
    status = "Proposed." if "Problems:" in user_text else "Accepted."
    return (f"# ADR {brief.get('Number', '?')}: {brief.get('Title', 'Untitled')}\n\n"
            f"## Context\n\n{brief.get('Context', '')}\n\n## Decision\n\n{brief.get('Decision', '')}\n\n"
            f"## Status\n\n{status}\n\n## Consequences\n\n{brief.get('Consequences', '')}\n")


EXTRA_RULES.append(("[[ADR-DRAFT]]", _adr_draft))


def _event_schema(user_text):
    brief = dict(re.findall(r"^(Event|Channel|Address|Fields):\s*(.+)$", _delimited(user_text), re.M))
    event, channel = brief.get("Event", "Unnamed"), brief.get("Channel", "unnamed")
    fixed = "Problems:" in user_text
    fields = [f.strip().split(":") for f in brief.get("Fields", "").split(",") if ":" in f]
    props = {}
    for name, kind in fields:
        if kind in ("uuid", "date-time"):
            props[name] = {"type": "string", "format": kind}
        elif kind == "integer" and not fixed:
            props[name] = {"type": "string"}  # scripted mistake: numbers typed as text
        else:
            props[name] = {"type": kind}
    schema = {"type": "object", "properties": props}
    if fixed:
        schema = {"type": "object", "additionalProperties": False, "required": [n for n, _ in fields],
                  "properties": props}
    fragment = {
        "channels": {channel: {"address": brief.get("Address", channel),
                               "messages": {event: {"$ref": f"#/components/messages/{event}"}}}},
        "operations": {f"send{event}": {"action": "send" if fixed else "publish",
                                        "channel": {"$ref": f"#/channels/{channel}"},
                                        "messages": [{"$ref": f"#/channels/{channel}/messages/{event}"}]}},
        "components": {"messages": {event: {"name": event, "payload": {"$ref": f"#/components/schemas/{event}Payload"}}},
                       "schemas": {f"{event}Payload": schema}}}
    return json.dumps(fragment, indent=1)


EXTRA_RULES.append(("[[EVENT-SCHEMA]]", _event_schema))


def _incident_summary(user_text):
    f = dict(re.findall(r"^(\w+):\s*(.+)$", _delimited(user_text), re.M))
    get = lambda key: f.get(key, "?")  # noqa: E731
    if "Problems:" not in user_text:  # scripted mistakes: mean reported as p99, burn rate off by 10x
        burn = get("burn_rate")
        wrong_burn = f"{float(burn) / 10:.2f}" if burn.replace(".", "", 1).isdigit() else burn
        return (f"Incident summary: the {get('alert')} fired at {get('evaluated_at')} ({get('windows')} windows, "
                f"burn rate {wrong_burn}). POST /loans slowed down from {get('slow_since')}. "
                f"The p99 latency was {get('mean_ms')} ms, so most members were not affected. "
                f"Availability stayed at {get('availability_3d')}.")
    return (f"Incident summary: the {get('alert')} fired at {get('evaluated_at')} ({get('windows')} windows, "
            f"burn rate {get('burn_rate')}). From {get('slow_since')} some POST /loans requests took seconds: "
            f"p99 {get('p99_ms')} ms in the last hour, while the mean was {get('mean_ms')} ms and "
            f"p95 {get('p95_ms')} ms. The last hour used {get('budget_used_1h')} of the 30-day latency error budget. "
            f"Availability stayed at {get('availability_3d')}.")


EXTRA_RULES.append(("[[INCIDENT-SUMMARY]]", _incident_summary))


def _capacity_memo(user_text):
    f = dict(re.findall(r"^(\w+):\s*(.+)$", _delimited(user_text), re.M))
    get = lambda key: f.get(key, "?")  # noqa: E731
    if "Problems:" not in user_text:  # scripted mistakes: average used as the peak, invented numbers
        return (f"Capacity memo: plan for a peak of {get('avg_rps')} req/s. Little's law gives 1.8 requests in "
                f"flight. One instance handles {get('capacity_rps')} req/s, so we recommend 1 instances at "
                f"{get('cost_per_million_usd')} USD per million requests.")
    return (f"Capacity memo: plan for a peak of {get('peak_rps')} req/s (average {get('avg_rps')} req/s). "
            f"With a mean service time of {get('mean_service_ms')} ms, Little's law gives {get('in_flight_at_peak')} "
            f"requests in flight at peak. One instance meets the p99 SLO up to a capacity of {get('capacity_rps')} req/s, "
            f"so we recommend {get('instances')} instances (N+1): p99 {get('p99_at_peak_ms')} ms at peak and "
            f"{get('p99_one_down_ms')} ms with one instance down, at a cost of {get('cost_per_million_usd')} USD per "
            f"million requests. Confirmation emails move to the outbox with {get('email_senders')} sender slots; the "
            f"{get('rejected_option')} option would need {get('rejected_instances')} instances.")


EXTRA_RULES.append(("[[CAPACITY-MEMO]]", _capacity_memo))


def _go_no_go(user_text):
    f = dict(re.findall(r"^(\w+):\s*(.+)$", _delimited(user_text), re.M))
    get = lambda key: f.get(key, "?")  # noqa: E731
    if "Problems:" not in user_text:  # scripted mistake: optimistic GO regardless of the verdict
        return f"Release summary: GO. {get('passed')} of {get('total')} criteria passed; the rest looks minor."
    if get("verdict") == "GO":
        return f"Release summary: GO. All {get('total')} criteria passed."
    return (f"Release summary: NO-GO. {get('passed')} of {get('total')} criteria passed; failed: {get('failed')}. "
            f"Fix these before the release.")


EXTRA_RULES.append(("[[GO-NO-GO]]", _go_no_go))


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
