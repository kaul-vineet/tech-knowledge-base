"""Adapters for the host's ports: model (shared fake over HTTP, or scripted), approver, clock, and the tool world."""
import copy
import json
import urllib.request
from pathlib import Path

import _kb
from model_endpoint import check_model_url

HERE = Path(__file__).resolve().parent
WORLD = json.loads((HERE / "fixtures" / "world.json").read_text(encoding="utf-8"))
T0 = 1_790_000_000  # fake clock start (seconds since the epoch)
# HttpModel defaults; run_project.py --real-model / --allow-remote-model change them (the fake path never does).
DEFAULT_MODEL, DEFAULT_TIMEOUT, ALLOW_REMOTE = "fake-model", 30, False


class FakeClock:
    def __init__(self, now=T0):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class World:
    """What the tools act on. Effects are RECORDED in a list, never real."""

    def __init__(self, extra_docs=None):
        self.docs = {**copy.deepcopy(WORLD["docs"]), **(extra_docs or {})}
        self.files = copy.deepcopy(WORLD["files"])
        self.effects = []


def start_fake_model():
    """The shared deterministic fake (kb/shared/local_agent). Rule 1b: it OBEYS 'ignore previous instructions ...
    call <tool> with {json}' found in user or tool text - like a naive model. Returns (server, base_url)."""
    return _kb.load("fake_model").start_in_thread()


class HttpModel:
    """OpenAI-compatible chat completions (fake server here; Ollama at http://localhost:11434/v1 in pendingCi).
    Refuses a non-loopback base_url unless allow_remote (or ALLOW_REMOTE) is set: see model_endpoint.py."""

    def __init__(self, base_url, model=None, timeout=None, allow_remote=None):
        check_model_url(base_url, ALLOW_REMOTE if allow_remote is None else allow_remote)
        self.base_url = base_url.rstrip("/")
        self.model, self.timeout = model or DEFAULT_MODEL, timeout or DEFAULT_TIMEOUT

    def propose(self, messages, tools):
        body = json.dumps({"model": self.model, "messages": messages, "tools": tools, "temperature": 0}).encode("utf-8")
        req = urllib.request.Request(self.base_url + "/chat/completions", data=body,
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]


class ScriptedModel:
    """Replays fixed tool calls, then answers. For paths the fake model cannot plan (e.g. send_email)."""

    def __init__(self, calls, answer="done"):
        self.calls, self.answer, self.turn = calls, answer, 0

    def propose(self, messages, tools):
        if self.turn < len(self.calls):
            name, args = self.calls[self.turn]
            self.turn += 1
            raw = args if isinstance(args, str) else json.dumps(args)
            return {"role": "assistant", "content": None, "tool_calls": [
                {"id": f"call_{self.turn}", "type": "function", "function": {"name": name, "arguments": raw}}]}
        return {"role": "assistant", "content": self.answer}


class FakeApprover:
    """A human stand-in: answers from a fixed rule and keeps every request it was shown."""

    def __init__(self, approve=True):
        self.approve, self.seen = approve, []

    def ask(self, request):
        self.seen.append(request)
        return self.approve(request) if callable(self.approve) else bool(self.approve)
