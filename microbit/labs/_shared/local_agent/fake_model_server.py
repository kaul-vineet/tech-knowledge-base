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

micro:bit topic extension (this vendored copy only, labs/_shared/local_agent/):
  EXTRA_RULES starts with ONE rule keyed on the marker "[[MICROBIT-TELEMETRY]]".
  It reads `temp=<t>,light=<l>,state=<s>` lines inside <telemetry>...</telemetry>
  and returns a fixed-template plain-language summary built only from those lines.
  Used by labs/L100/05-temperature-light/agent_assist.py and its test.
  L200: a second rule keyed on "[[MICROBIT-CSV]]" reads the CSV inside <csv>...</csv>
  (header time_ms,<col>,...) and returns a fixed-template summary: row count,
  duration, and per column first -> last with a rose/fell/stayed word and the mean
  rounded to 1 decimal. Used by labs/L200/08-data-logging/agent_assist.py.
  L300: a third rule keyed on "[[MICROBIT-GATEWAY]]" reads the JSON object inside
  <gateway>...</gateway> (gateway metrics + the alarms the CODE raised) and returns a
  fixed-template explanation that repeats only those numbers and alarm names.
  Used by labs/L300/15-serial-gateway/agent_assist.py.
  L400: a fourth rule keyed on "[[MICROBIT-INCIDENT]]" reads the incident JSON inside
  <incident>...</incident> (alarms the CODE raised + device labels) and returns a JSON reply
  {"explanation", "operator_note"} built from those alarms only. It also imitates a model that obeys
  instructions hidden in data: a device label containing "clear <ALARM>" adds "actions":
  [{"clear_alarm": "<ALARM>"}]. Used by labs/L400/21-edge-ai-explain and labs/L400/22-capstone.
"""
import argparse
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL_ID = "fake-model"
MICROBIT_MARKER = "[[MICROBIT-TELEMETRY]]"
TELEMETRY_LINE = re.compile(r"temp=(-?\d+),light=(\d+),state=(\w+)")


def _microbit_telemetry(user_text):
    """Fixed-template explanation of micro:bit serial telemetry (topic extension)."""
    rows = [(int(t), int(l), s) for t, l, s in TELEMETRY_LINE.findall(_delimited(user_text))]
    if not rows:
        return "I could not find any temp=...,light=... lines to explain."
    temps = [r[0] for r in rows]
    lights = [r[1] for r in rows]
    flagged = [s for s in ("hot", "dark") if any(r[2] == s for r in rows)]
    states = " and ".join(f"{sum(r[2] == s for r in rows)} {s}" for s in flagged) or "none flagged"
    return (f"The micro:bit sent {len(rows)} readings. Temperature started at {temps[0]} C and ended at "
            f"{temps[-1]} C, peaking at {max(temps)} C; this is the processor's own estimate, so it can read "
            f"a little above the room. Light ranged from {min(lights)} to {max(lights)}, where larger means "
            f"brighter. The program itself labelled the readings: {states}; everything else was ok.")


MICROBIT_CSV_MARKER = "[[MICROBIT-CSV]]"


def _microbit_csv(user_text):
    """Fixed-template summary of a micro:bit CSV log (topic extension, L200 lab 08)."""
    lines = [l.strip() for l in _delimited(user_text).strip().splitlines() if l.strip()]
    if len(lines) < 3:
        return "The log is too short to summarise."
    header, rows = lines[0].split(","), [l.split(",") for l in lines[1:]]
    secs = (int(rows[-1][0]) - int(rows[0][0])) / 1000
    parts = [f"The log has {len(rows)} rows over {secs:g} seconds."]
    for i, name in enumerate(header[1:], 1):
        v = [float(r[i]) for r in rows]
        word = "rose" if v[-1] > v[0] else "fell" if v[-1] < v[0] else "stayed"
        label = "Temperature" if name == "temp" else name.capitalize()
        parts.append(f"{label} {word} from {v[0]:g} to {v[-1]:g}, with a mean of {sum(v) / len(v):.1f}.")
    return " ".join(parts)


MICROBIT_GATEWAY_MARKER = "[[MICROBIT-GATEWAY]]"


def _microbit_gateway(user_text):
    """Fixed-template explanation of serial-gateway metrics (topic extension, L300 lab 15)."""
    try:
        d = json.loads(_delimited(user_text))
        m, alarms = d["metrics"], d["alarms"]
    except (ValueError, KeyError, TypeError):
        return "I could not read the gateway metrics."
    damaged = m["bad_crc"] + m["bad_len"]
    total = m["frames_ok"] + damaged
    names = ", ".join(a["name"] for a in alarms) or "none"
    return (f"The gateway accepted {m['frames_ok']} of {total} frames. {m['bad_crc']} frames failed the "
            f"CRC check and {m['bad_len']} had the wrong length, so {100 * damaged / total:.1f}% of frames "
            f"were damaged on the serial link, which looks like noise or a loose cable rather than a "
            f"sensor fault. It resynchronised {m['resyncs']} times and kept running. "
            f"{d.get('missing', 0)} readings are missing from the sequence. "
            f"Alarms raised by the gateway code: {names}.")


MICROBIT_INCIDENT_MARKER = "[[MICROBIT-INCIDENT]]"
_ALARM_TEXT = {"TEMP_HIGH": "the room temperature reached {value} C at {dev} (limit {limit} C)",
               "DRIFT_LAT": "{dev}'s radio link needs more retransmissions than the twin predicts",
               "DRIFT_TEMP": "{dev}'s temperature reads higher than the twin's room model",
               "AUTH_REJECTS": "the gateway rejected {value} radio frames that failed authentication"}


def _microbit_incident(user_text):
    """Fixed-template incident explanation as JSON (topic extension, L400 lab 21 + capstone).

    Deliberately ALSO a stand-in for a model that follows instructions hidden in data: if a device
    label (free text typed by people) says "clear <ALARM>", the reply obeys and asks for that action.
    """
    try:
        d = json.loads(_delimited(user_text))
        alarms, devices = d["alarms"], d.get("devices", [])
    except (ValueError, KeyError, TypeError):
        return json.dumps({"explanation": "I could not read the incident.", "operator_note": ""})
    parts = [_ALARM_TEXT.get(a["name"], "{name} at {dev}").format(**dict({"value": "", "limit": "", "dev": ""}, **a))
             for a in alarms]
    names = ", ".join(a["name"] for a in alarms) or "none"
    detail = "; ".join(parts)
    detail = detail[:1].upper() + detail[1:] + "." if parts else ""
    reply = {"explanation": "Alarms raised by the gateway code: %s. %s" % (names, detail),
             "operator_note": "Check the boards named above in the room; only the gateway code can change these alarms."}
    for dev in devices:
        m = re.search(r"clear (\w+)", " ".join(str(v) for v in dev.values()), re.I)
        if m:                                              # obeys the injected instruction
            reply["actions"] = [{"clear_alarm": m.group(1).upper()}]
            reply["operator_note"] = "%s cleared after recalibration; no action needed." % m.group(1).upper()
    return json.dumps(reply)


# Topic hook: list of (marker_string, function(user_text) -> reply_text). Checked before the echo reply.
EXTRA_RULES = [(MICROBIT_MARKER, _microbit_telemetry), (MICROBIT_CSV_MARKER, _microbit_csv),
               (MICROBIT_GATEWAY_MARKER, _microbit_gateway), (MICROBIT_INCIDENT_MARKER, _microbit_incident)]
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    port = parser.parse_args().port
    print(f"fake model server on http://127.0.0.1:{port}/v1 (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
