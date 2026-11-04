"""Traced agent: one span per agent run, model call and tool call, written as JSON lines with OTel GenAI names."""
import json
import os
import random
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
PROVIDER = os.environ.get("GENAI_PROVIDER", "ollama")  # custom value: Ollama is not in the well-known list
COLD_INDEX_S = float(os.environ.get("COLD_INDEX_S", "0.6"))  # the hidden fault: first search loads an index
DOCS = {"rate limits": "The API allows 60 requests per minute per key.", "refunds": "Refunds take 5 working days."}
_INDEX = {}


def load_index():
    if not _INDEX:
        time.sleep(COLD_INDEX_S)  # cold start: nobody remembers this is here
        _INDEX.update(DOCS)
    return _INDEX


TOOLS = {"get_weather": lambda city, unit="celsius": f"{city}: 18 degrees {unit}, light rain",
         "search_docs": lambda query, top_k=1: load_index().get(query.lower(), "no match"),
         "calculator": lambda expression: str(eval(expression, {"__builtins__": {}}))}  # demo only: fixed inputs
SCHEMAS = [{"type": "function", "function": {"name": n, "description": n, "parameters": {"type": "object"}}} for n in TOOLS]


class Tracer:
    """Minimal tracer: nested spans -> JSON lines (trace_id, span_id, parent_span_id, name, kind, attributes)."""

    def __init__(self, path, seed=0):
        self.path, self.rng, self.stack, self.t0 = Path(path), random.Random(seed), [], time.perf_counter()
        self.trace_id = self._id(32)
        self.path.write_text("", encoding="utf-8")

    def _id(self, n):
        return "".join(self.rng.choice("0123456789abcdef") for _ in range(n))  # seeded: stable ids in tests

    @contextmanager
    def span(self, name, kind, **attributes):
        parent = self.stack[-1]["span_id"] if self.stack else None
        s = {"trace_id": self.trace_id, "span_id": self._id(16), "parent_span_id": parent, "name": name, "kind": kind,
             "status": "OK", "attributes": attributes}
        self.stack.append(s)
        start = time.perf_counter()
        try:
            yield attributes  # the caller adds response attributes (tokens, finish reason) inside the block
        except Exception as e:
            s["status"], attributes["error.type"] = "ERROR", type(e).__name__
            raise
        finally:
            self.stack.pop()
            s["start_ms"], s["duration_ms"] = round((start - self.t0) * 1000, 1), round((time.perf_counter() - start) * 1000, 1)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(s) + "\n")


def run(task, tracer, base_url=BASE_URL, model=MODEL, max_steps=6):
    url = urlparse(base_url)
    messages = [{"role": "user", "content": task}]
    with tracer.span("invoke_agent support-agent", "INTERNAL", **{"gen_ai.operation.name": "invoke_agent",
                     "gen_ai.provider.name": PROVIDER, "gen_ai.agent.name": "support-agent"}):
        for _ in range(max_steps):
            with tracer.span(f"chat {model}", "CLIENT", **{  # span per model call; name = "{operation} {model}"
                    "gen_ai.operation.name": "chat", "gen_ai.provider.name": PROVIDER, "gen_ai.request.model": model,
                    "server.address": url.hostname, "server.port": url.port}) as a:
                body = requests.post(f"{base_url}/chat/completions", timeout=60, json={
                    "model": model, "messages": messages, "tools": SCHEMAS, "temperature": 0}).json()
                a["gen_ai.response.model"] = body["model"]
                a["gen_ai.usage.input_tokens"] = body["usage"]["prompt_tokens"]  # token usage on the span
                a["gen_ai.usage.output_tokens"] = body["usage"]["completion_tokens"]
                a["gen_ai.response.finish_reasons"] = [c["finish_reason"] for c in body["choices"]]
            reply = body["choices"][0]["message"]
            messages.append(reply)
            if not reply.get("tool_calls"):
                return reply["content"]
            for call in reply["tool_calls"]:
                name = call["function"]["name"]
                with tracer.span(f"execute_tool {name}", "INTERNAL", **{"gen_ai.operation.name": "execute_tool",
                                 "gen_ai.tool.name": name, "gen_ai.tool.call.id": call["id"], "gen_ai.tool.type": "function"}):
                    result = TOOLS[name](**json.loads(call["function"]["arguments"]))  # span per tool call
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
        return "stopped: max_steps"


def summarize(path):
    """Group spans by name: count, total ms, share of the root span, tokens. Sorted slowest first."""
    spans = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    spans = [s for s in spans if "span_id" in s]  # plain log lines carry no spans
    root = next((s for s in spans if s["parent_span_id"] is None), None)
    rows = {}
    for s in spans:
        r = rows.setdefault(s["name"], {"name": s["name"], "count": 0, "ms": 0.0, "tokens": 0})
        r["count"] += 1
        r["ms"] = round(r["ms"] + s["duration_ms"], 1)
        r["tokens"] += s["attributes"].get("gen_ai.usage.input_tokens", 0) + s["attributes"].get("gen_ai.usage.output_tokens", 0)
    for r in rows.values():
        r["share"] = round(r["ms"] / root["duration_ms"], 2) if root else None
    return sorted(rows.values(), key=lambda r: -r["ms"])


def diagnose(path):
    """Name of the slowest operation below the root span, or None if the log cannot tell."""
    children = [r for r in summarize(path) if not r["name"].startswith("invoke_agent")]
    return children[0]["name"] if children else None


if __name__ == "__main__":
    task = 'What is the weather in Paris? Also search docs for "rate limits" and compute 17*23.'
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "trace.jsonl")
    print("answer:", run(task, Tracer(out)))
    for r in summarize(out):
        print(f"{r['name']:<28} x{r['count']}  {r['ms']:>7.1f} ms  share {r['share']:.0%}  tokens {r['tokens']}")
    print("slowest below the root:", diagnose(out))
