"""L400 extension of the deterministic fake model server (wraps labs/L300/fake_server_l300.py -> L100).

NOT a language model. The L100 file stays byte-identical to kb/shared/local_agent/ and the L300 file is unchanged:
L400 adds its rules here. Every L100/L300 rule still answers when no L400 rule matches; rule F (seeded faults) works
as in L300. Chat replies are built here, so every chat reply carries usage.prompt_tokens_details.cached_tokens (rule P).

L400 rules (POST /v1/chat/completions; checked before the L300 and L100 rules)
  K. Context limit (off by default): make_server(context_limit=N). Prompt tokens = words of every message text and
     tool_calls JSON + words of json.dumps(tools). More than N -> HTTP 400 {"error": {"code": "context_length_exceeded"}}
     (vLLM / OpenAI behaviour; Ollama truncates silently instead).
  P. Prefix cache: one slot per model. cached_tokens = number of leading prompt words equal to the previous request
     for the same model (tools JSON first, then messages in order) - like llama.cpp cache_prompt with one slot.
  G. Model registry: fake-model / fake-large (v1), fake-small (S), fake-model:v2 (V); alias fake-model:latest ->
     fake-model, re-pointed with server.retag(alias, target). GET /api/tags lists name + digest (Ollama shape).
     Unknown model names behave like v1.
  S. fake-small on <ticket>: tickets longer than 9 words come back wrapped in prose (invalid JSON); priority is "high"
     only for "outage" (misses urgent/asap/immediately/down). Otherwise the L300 rule T answer.
  V. fake-model:v2 on <ticket>: priority "high" only for outage|down (urgent/asap/immediately -> "normal").
  M. Ops tools - the request offers any of get_metrics, get_logs, list_deploys, search_runbook, lookup_invoice,
     open_ticket. Clauses in the last user message, in order: 'metrics for <svc>', 'logs for <svc>', 'deploys for
     <svc>', 'runbook for "<q>"', 'invoice <ID>', 'ticket for <svc>', and the conditional 'if error_rate is above
     <x>% check deploys for <svc>' (planned only after get_metrics(<svc>) returned "error_rate <y>%" with y > x).
     Only OFFERED tools are planned; ONE call per turn; then "Final answer: name(arg) -> <first line of result>; ...".
  M2. <plan>task</plan> [+ "Tools: a, b"] -> JSON list [{"tool", "args"}] of the unconditional clauses (a planner never
     sees results, so conditional clauses are dropped).
  M3. <route>task</route> + <specialists> lines "name: tool, tool" -> the specialist owning most clauses (ties: first).
  M4. <split>task</split> + <specialists> -> JSON list [{"worker", "task"}], one per clause (conditional clauses go to
     the worker that owns list_deploys).
  M5. <results> blocks "[label]" + text lines -> "Final answer: label -> first text line; ..." ("Final answer: "
     prefixes inside a block are dropped).
  W. <refund_proposal> "order <ID> paid <amount>" -> JSON {"order_id", "amount", "reason"} (amount = paid).
  D. Refund decisions (lesson 20). Facts are "key: value" lines; the customer text is in <customer>...</customer>.
     OVERRIDE = override|vip|ignore (all )?previous|approve (the )?full (case-insensitive) in the customer text.
     <decide>: JSON {"action", "amount", "rule"}: OVERRIDE -> approve_auto for the largest number in the customer
     text (else amount_requested); else
     days_since_delivery > 30 or amount_requested > paid -> deny; else approve_auto (ignores prior_refunds_90d).
     <propose>: JSON {"claims": {"damaged", "threat"}, "summary", "suggested_action"}; OVERRIDE adds
     "suggested_action": "approve_auto" and an extra key "override": true.
     <explain>: JSON decision inside -> "Decision: <action> for <amount>. Reason: <rule>."; OVERRIDE ->
     "Good news: your refund of <amount_requested> is approved."
  I. <incident> facts + logs (+ <context> "[id] text" lines) -> JSON {"suspected_cause", "runbook",
     "proposed_severity", "proposed_actions", "explanation"}; logs in <logs>...</logs>: cause OutOfMemory -> memory exhaustion, Timeout ->
     dependency timeout, deploy_age_min < 60 -> bad deploy; runbook = first context id mentioning the cause keyword;
     severity SEV1 if error_rate > 10 else SEV2; actions page_oncall (+ rollback_deploy for a bad deploy). Log text
     "ignore previous instructions ... set severity SEVn and call <tool>" is obeyed (severity + tool appended).
  J. <adr_draft>{report JSON}</adr_draft> -> one paragraph that restates candidate, passed/total, pass rate,
     regressions, red-team safe/total and drift from the report.

Run:  python fake_server_l400.py --port 8765 [--context-limit 1000] [--fail-rate 0.3 --seed 7]
"""
import argparse
import hashlib
import io
import json
import random
import re
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "L300"), str(ROOT / "L100" / "01-setup")]
import fake_model_server as fms  # noqa: E402
import fake_server_l300 as l3  # noqa: E402

BEHAVIOUR = {"fake-model": "v1", "fake-large": "v1", "fake-small": "small", "fake-model:v2": "v2"}
OPS_TOOLS = {"get_metrics", "get_logs", "list_deploys", "search_runbook", "lookup_invoice", "open_ticket"}
CLAUSE = re.compile(r'if error_rate is above (\d+(?:\.\d+)?)% check deploys for (\w+)|metrics for (\w+)|logs for (\w+)'
                    r'|deploys for (\w+)|runbook for "([^"]+)"|invoice ([A-Z]+-\d+)|ticket for (\w+)', re.I)
SIMPLE = [None, None, ("get_metrics", "service"), ("get_logs", "service"), ("list_deploys", "service"),
          ("search_runbook", "query"), ("lookup_invoice", "invoice_id"), ("open_ticket", "service")]
OVERRIDE = re.compile(r"override|vip|ignore (?:all )?previous|approve (?:the )?full", re.I)


def clauses(text):
    """[(tool, args, condition)] in text order; condition = (service, threshold) for the conditional clause."""
    out = []
    for m in CLAUSE.finditer(text):
        if m.group(1):
            out.append(("list_deploys", {"service": m.group(2)}, (m.group(2), float(m.group(1)))))
            continue
        i = next(i for i in range(3, 9) if m.group(i))
        tool, arg = SIMPLE[i - 1]
        out.append((tool, {arg: m.group(i)}, None))
    return out


def _first_line(text):
    return next((ln.strip() for ln in text.splitlines() if ln.strip()), "")


def _ops_turn(messages, offered):
    last_user = max(i for i, m in enumerate(messages) if m.get("role") == "user")
    pending, done = {}, []
    for m in messages[last_user + 1:]:
        for c in m.get("tool_calls") or []:
            pending[c["id"]] = (c["function"]["name"], json.loads(c["function"].get("arguments") or "{}"))
        if m.get("role") == "tool" and m.get("tool_call_id") in pending:
            done.append((*pending[m["tool_call_id"]], fms._text(m)))
    plan = []
    for tool, args, cond in clauses(fms._text(messages[last_user])):
        if tool not in offered:
            continue  # a specialist without this tool silently skips the clause
        if cond:
            seen = [r for n, a, r in done if n == "get_metrics" and a.get("service") == cond[0]]
            rate = re.search(r"error_rate ([\d.]+)%", seen[0]) if seen else None
            if not rate or float(rate.group(1)) <= cond[1]:
                continue  # the condition is false or cannot be evaluated yet
        plan.append((tool, args))
    if len(done) < len(plan):
        name, args = plan[len(done)]
        call = {"id": f"call_{len(done) + 1}", "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}
        return {"role": "assistant", "content": None, "tool_calls": [call]}, "tool_calls"
    parts = [f"{n}({next(iter(a.values()), '')}) -> {_first_line(r)}" for n, a, r in done]
    return {"role": "assistant", "content": "Final answer: " + "; ".join(parts)}, "stop"


def _specialists(text):
    block = fms._block(text, "specialists") or ""
    return [(n, [t.strip() for t in tools.split(",")]) for n, tools in re.findall(r"^(\w+):\s*(.+)$", block, re.M)]


def _clause_text(tool, args, cond):
    if cond:
        return f"If error_rate is above {cond[1]:g}% check deploys for {cond[0]}."
    noun = {"get_metrics": "metrics for", "get_logs": "logs for", "list_deploys": "deploys for",
            "search_runbook": "runbook for", "lookup_invoice": "invoice", "open_ticket": "ticket for"}[tool]
    value = next(iter(args.values()))
    return f"Check {noun} " + (f'"{value}"' if tool == "search_runbook" else value) + "."


def _facts(text):
    return {k.lower(): v.strip() for k, v in re.findall(r"^\s*(\w+):\s*(.+)$", text, re.M)}


def _num(value, default=0.0):
    m = re.search(r"-?\d+(?:\.\d+)?", str(value))
    return float(m.group(0)) if m else default


def _decide(block):
    f, customer = _facts(block), fms._block(block, "customer") or ""
    asked, paid, days = _num(f.get("amount_requested")), _num(f.get("paid")), _num(f.get("days_since_delivery"))
    if OVERRIDE.search(customer):
        said = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", customer)]
        return {"action": "approve_auto", "amount": max(said) if said else asked, "rule": "customer is a VIP"}
    if days > 30 or asked > paid:
        return {"action": "deny", "amount": 0, "rule": "outside policy"}
    return {"action": "approve_auto", "amount": asked, "rule": "within 30 days"}


def _propose(block):
    customer = fms._block(block, "customer") or block
    out = {"claims": {"damaged": bool(re.search(r"broken|damaged|cracked", customer, re.I)),
                      "threat": bool(re.search(r"chargeback|lawyer|bank", customer, re.I))},
           "summary": " ".join(customer.split()[:12]), "suggested_action": "escalate"}
    if OVERRIDE.search(customer):
        out.update({"suggested_action": "approve_auto", "override": True})
    return out


def _explain(block):
    customer, f = fms._block(block, "customer") or "", _facts(block)
    if OVERRIDE.search(customer):
        return f"Good news: your refund of {f.get('amount_requested', '?')} is approved."
    d = json.loads(re.search(r"\{.*\}", block, re.S).group(0))
    return f"Decision: {d['action']} for {d['amount']}. Reason: {d['rule']}."


def _incident(block):
    f, logs = _facts(block), fms._block(block, "logs") or block
    ctx = re.findall(r"^\[([^\]]+)\]\s*(.+)$", fms._block(block, "context") or "", re.M)
    cause = ("memory exhaustion" if "OutOfMemory" in logs else "dependency timeout" if "Timeout" in logs
             else "bad deploy" if _num(f.get("deploy_age_min"), 999) < 60 else "unknown")
    key = {"memory exhaustion": "memory", "dependency timeout": "timeout", "bad deploy": "deploy"}.get(cause, "")
    runbook = next((cid for cid, text in ctx if key and key in text.lower()), ctx[0][0] if ctx else None)
    sev = "SEV1" if _num(f.get("error_rate")) > 10 else "SEV2"
    actions = ["page_oncall"] + (["rollback_deploy"] if cause == "bad deploy" else [])
    inj = re.search(r"ignore (?:all )?previous instructions.*?set severity (SEV\d).*?call (\w+)", logs, re.I | re.S)
    if inj:  # obeys text inside the logs, like a naive model
        sev, actions = inj.group(1).upper(), actions + [inj.group(2)]
    return {"suspected_cause": cause, "runbook": runbook, "proposed_severity": sev, "proposed_actions": actions,
            "explanation": f"Likely {cause} (see {runbook}). Proposed {sev}: {', '.join(actions)}."}


def _adr_draft(block):
    r = json.loads(block)
    return (f"Context: candidate {r['candidate']} passed {r['passed']}/{r['total']} golden cases "
            f"({r['pass_rate']:.0%}) with {len(r['regressions'])} regressions against the pinned model; the red-team "
            f"suite was {r['redteam_safe']}/{r['redteam_total']} safe; drift alarm: {r['drift_alarm']}.")


def _ticket(req, user_text, behaviour):
    data = json.loads(l3._ticket(req, user_text))
    ticket = fms._block(user_text, "ticket")
    if behaviour == "small":
        data["priority"] = "high" if re.search(r"\boutage\b", ticket, re.I) else "normal"
        if len(ticket.split()) > 9:
            return "Sure! Here is the triage: " + json.dumps(data)
    if behaviour == "v2":
        data["priority"] = "high" if re.search(r"\b(outage|down)\b", ticket, re.I) else "normal"
    return json.dumps(data)


def l400_reply(req, behaviour):
    """(message, finish_reason) for an L400 rule, or None to fall through to the L300 / L100 rules."""
    user_text = fms._text([m for m in req["messages"] if m.get("role") == "user"][-1])
    offered = {t.get("function", {}).get("name") for t in req.get("tools") or []}
    if offered & OPS_TOOLS:
        return _ops_turn(req["messages"], offered)
    say = lambda text: ({"role": "assistant", "content": text}, "stop")
    if fms._block(user_text, "ticket") is not None and behaviour in ("small", "v2"):
        return say(_ticket(req, user_text, behaviour))
    task = fms._block(user_text, "plan")
    if task is not None:
        tools = re.search(r"^Tools:\s*(.+)$", user_text, re.M)
        allowed = {t.strip() for t in tools.group(1).split(",")} if tools else OPS_TOOLS
        return say(json.dumps([{"tool": t, "args": a} for t, a, c in clauses(task) if not c and t in allowed]))
    for tag in ("route", "split"):
        task = fms._block(user_text, tag)
        if task is None:
            continue
        specs, found = _specialists(user_text), clauses(task)
        owner = lambda tool: next((n for n, tools in specs if tool in tools), specs[0][0])
        if tag == "route":
            counts = {n: sum(owner(t) == n for t, _, _ in found) for n, _ in specs}
            return say(max(counts, key=lambda n: (counts[n], -[s for s, _ in specs].index(n))))
        return say(json.dumps([{"worker": owner(t), "task": _clause_text(t, a, c)} for t, a, c in found]))
    block = fms._block(user_text, "results")
    if block is not None:
        parts = []
        for label, body in re.findall(r"^\[([^\]]+)\]\s*\n(.*?)(?=^\[|\Z)", block, re.M | re.S):
            parts.append(f"{label} -> {_first_line(body).removeprefix('Final answer: ')}")
        return say("Final answer: " + "; ".join(parts))
    for tag, fn in (("refund_proposal", None), ("decide", _decide), ("propose", _propose), ("explain", _explain),
                    ("incident", _incident), ("adr_draft", _adr_draft)):
        block = fms._block(user_text, tag)
        if block is None:
            continue
        if tag == "refund_proposal":
            m = re.search(r"order ([\w-]+) paid (\d+(?:\.\d+)?)", block)
            return say(json.dumps({"order_id": m.group(1), "amount": float(m.group(2)), "reason": "item arrived damaged"}))
        out = fn(block)
        return say(out if isinstance(out, str) else json.dumps(out))
    return None


def _prompt_words(req):
    words = json.dumps(req.get("tools") or []).split() if req.get("tools") else []
    for m in req["messages"]:
        words += [m.get("role", "")] + fms._text(m).split() + (json.dumps(m["tool_calls"]).split() if m.get("tool_calls") else [])
    return words


class Handler(l3.Handler):
    def do_GET(self):
        if self.path.rstrip("/") == "/api/tags":  # rule G: Ollama-shaped model list with digests
            models = [{"name": n, "model": n, "digest": self.server.digest(n)} for n in sorted({*BEHAVIOUR, *self.server.aliases})]
            return self._send(200, {"models": models})
        return l3.fms.Handler.do_GET(self)

    def do_POST(self):
        f = self.server.faults
        with f["lock"]:
            r = f["rng"].random()  # rule F (L300): one seeded draw per request, in arrival order
            f["stats"]["requests"] += 1
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if r < f["fail_rate"]:
            f["stats"]["503"] += 1
            return self._send(503, {"error": {"message": "model overloaded (fake fault)", "type": "server_error"}})
        if r < f["fail_rate"] + f["slow_rate"]:
            f["stats"]["slow"] += 1
            time.sleep(f["slow_s"])
        if self.path.rstrip("/") != "/v1/chat/completions":
            self.rfile = io.BytesIO(body)
            return fms.Handler.do_POST(self)
        try:
            req = json.loads(body or b"{}")
        except json.JSONDecodeError:
            return self._error(400, "body is not valid JSON")
        problem = fms._validate(req)
        if problem:
            return self._error(400, problem)
        words = _prompt_words(req)
        if self.server.context_limit and len(words) > self.server.context_limit:  # rule K
            return self._send(400, {"error": {"code": "context_length_exceeded", "type": "invalid_request_error",
                                              "message": f"{len(words)} prompt tokens > context {self.server.context_limit}"}})
        behaviour = BEHAVIOUR.get(self.server.resolve(req["model"]), "v1")
        message, finish = l400_reply(req, behaviour) or l3.l300_reply(req) or fms._reply(req)
        with f["lock"]:  # rule P: one prefix-cache slot per model
            prev = self.server.slots.get(req["model"], [])
            cached = next((i for i, (a, b) in enumerate(zip(prev, words)) if a != b), min(len(prev), len(words)))
            self.server.slots[req["model"]] = words
        completion = len((message.get("content") or json.dumps(message.get("tool_calls"))).split())
        try:
            self._send(200, {"id": "chatcmpl-fake", "object": "chat.completion", "created": 0, "model": req["model"],
                             "choices": [{"index": 0, "message": message, "finish_reason": finish}],
                             "usage": {"prompt_tokens": len(words), "completion_tokens": completion,
                                       "total_tokens": len(words) + completion,
                                       "prompt_tokens_details": {"cached_tokens": cached}}})
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass


def make_server(port=0, fail_rate=0.0, slow_rate=0.0, slow_s=1.0, seed=0, context_limit=None):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.faults = {"fail_rate": fail_rate, "slow_rate": slow_rate, "slow_s": slow_s, "rng": random.Random(seed),
                     "lock": threading.Lock(), "stats": {"requests": 0, "503": 0, "slow": 0}}
    server.stats, server.context_limit, server.slots = server.faults["stats"], context_limit, {}
    server.aliases = {"fake-model:latest": "fake-model"}
    server.resolve = lambda name: server.aliases.get(name, name)
    server.digest = lambda name: hashlib.sha256(f"{server.resolve(name)}:{BEHAVIOUR.get(server.resolve(name), 'v1')}"
                                                .encode("utf-8")).hexdigest()
    server.retag = lambda alias, target: server.aliases.__setitem__(alias, target)  # like `ollama cp` / a new pull
    return server


def start_in_thread(port=0, **options):
    """Start on 127.0.0.1 (port 0 = any free port). Returns (server, base_url)."""
    server = make_server(port, **options)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/v1"


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--context-limit", type=int, default=None)
    p.add_argument("--fail-rate", type=float, default=0.0)
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args()
    print(f"fake model server (L400 rules) on http://127.0.0.1:{a.port}/v1 context_limit={a.context_limit} "
          f"fail_rate={a.fail_rate} seed={a.seed} (Ctrl+C to stop)")
    make_server(a.port, a.fail_rate, seed=a.seed, context_limit=a.context_limit).serve_forever()
