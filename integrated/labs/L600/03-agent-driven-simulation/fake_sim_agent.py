"""Deterministic stand-in for a tool-calling model that plans simulation experiments (NOT a language model).

Wraps kb/shared/local_agent/fake_model_server.py without editing it: requests that offer the tool `run_experiment`
get the rule below; everything else is passed unchanged to the shared rules.
Rule SIM (keyed on the offered tool name run_experiment):
  plan, in the order they appear in the last user message:
    'screen with <morris|sobol> <n>'                         -> run_screening {method, size, seed}
    'compare mu <a> vs <b> at lam <l> with <r> replications' -> run_experiment {baseline, candidate, replications, seed}
    ('seed <s>' anywhere sets the seed). ONE call per turn, like the shared rule 1.
  then a final summary that behaves like a naive model:
    - always calls a lower candidate mean "a significant improvement", whatever the verdict says;
    - for a REJECTED experiment it still states a textbook number (M/M/1 formula) without a citation;
    - cites [exp-...] for results it did receive.
"""
import io
import json
import re

import _kb

fms = _kb.load("fake_model_server")
SCREEN = re.compile(r"screen with (morris|sobol) (\d+)", re.I)
COMPARE = re.compile(r"compare mu ([\d.]+) vs ([\d.]+) at lam ([\d.]+) with (\d+) replications", re.I)


def plan(text):
    seed = re.search(r"\bseed (\d+)", text)
    extra = {"seed": int(seed.group(1))} if seed else {}
    steps = [(m.start(), "run_screening", {"method": m.group(1).lower(), "size": int(m.group(2)), **extra})
             for m in SCREEN.finditer(text)]
    steps += [(m.start(), "run_experiment", {"baseline": {"lam": float(m.group(3)), "mu": float(m.group(1))},
                                             "candidate": {"lam": float(m.group(3)), "mu": float(m.group(2))},
                                             "replications": int(m.group(4)), **extra})
              for m in COMPARE.finditer(text)]
    return [(name, args) for _, name, args in sorted(steps, key=lambda s: s[0])]


def summary(done):
    out = []
    for name, args, raw in done:
        res = json.loads(raw)
        if res["status"] != "ok" and name == "run_screening":
            out.append(f"The {args['method']} screening was skipped because the run budget did not allow it.")
        elif res["status"] != "ok":
            lam, mu = args["baseline"]["lam"], args["baseline"]["mu"]
            out.append(f"At lam {lam} the mean wait would be about {lam / (mu * (mu - lam)):.1f} min.")
        elif name == "run_screening":
            key = "mu_star" if res["method"] == "morris" else "ST"
            first, last = res["ranking"][0], res["ranking"][-1]
            out.append(f"Screening ranks {first} first ({key} {res[key][first]:.2f}) and {last} last "
                       f"({key} {res[key][last]:.2f}) [{res['experiment_id']}].")
        else:
            a, b = res["baseline"]["mean"], res["candidate"]["mean"]
            word = "a significant improvement" if b < a else "a significant slowdown"
            out.append(f"Faster service (mu {args['candidate']['mu']}) cut the mean wait from {a:.2f} to {b:.2f} min "
                       f"({res['percent_change']:.0f}%), {word} with {res['replications']} replications "
                       f"[{res['experiment_id']}].")
    return " ".join(out)


def sim_turn(messages):
    last_user = max(i for i, m in enumerate(messages) if m.get("role") == "user")
    steps, pending, done = plan(fms._text(messages[last_user])), {}, []
    for m in messages[last_user + 1:]:
        for c in m.get("tool_calls") or []:
            pending[c["id"]] = (c["function"]["name"], json.loads(c["function"]["arguments"] or "{}"))
        if m.get("role") == "tool" and m.get("tool_call_id") in pending:
            done.append((*pending[m["tool_call_id"]], fms._text(m)))
    if len(done) < len(steps):
        name, args = steps[len(done)]
        call = {"id": f"call_{len(done) + 1}", "type": "function",
                "function": {"name": name, "arguments": json.dumps(args)}}
        return {"role": "assistant", "content": None, "tool_calls": [call]}, "tool_calls"
    return {"role": "assistant", "content": summary(done)}, "stop"


class Handler(fms.Handler):
    def do_POST(self):
        if self.path.rstrip("/") == "/v1/chat/completions":
            raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            try:
                req = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                req = {}
            offered = {t.get("function", {}).get("name") for t in req.get("tools") or []}
            if "run_experiment" in offered and not fms._validate(req):
                message, finish = sim_turn(req["messages"])
                words = sum(len(fms._text(m).split()) for m in req["messages"])
                done = len((message.get("content") or "").split())
                return self._send(200, {"id": "chatcmpl-fake-sim", "object": "chat.completion", "created": 0,
                                        "model": req["model"], "choices": [{"index": 0, "message": message,
                                                                            "finish_reason": finish}],
                                        "usage": {"prompt_tokens": words, "completion_tokens": done,
                                                  "total_tokens": words + done}})
            self.rfile = io.BytesIO(raw)  # not ours: hand the untouched body to the shared rules
        return super().do_POST()


def start_in_thread(port=0):
    """Same contract as the shared start_in_thread(): (server, base_url) on 127.0.0.1."""
    import threading
    server = fms.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/v1"
