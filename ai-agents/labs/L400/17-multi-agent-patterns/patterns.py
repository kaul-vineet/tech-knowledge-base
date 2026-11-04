"""One fixed task set, five designs: one agent + tools, router, planner/executor, supervisor/worker, hybrid.

Measures success, model calls and tokens per task (usage from the server). Run against fake_server_l400.py
started with --context-limit 1000 (a small context window, like a 1-4k num_ctx on a small local model).
"""
import json
import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ops_world as ow  # noqa: E402

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")
CONTEXT_LIMIT = int(os.environ.get("CONTEXT_LIMIT", "1000"))
SPECS = "\n".join(f"{name}: {', '.join(tools)}" for name, tools in ow.SPECIALISTS.items())
KEYWORDS = {"get_logs": "logs for", "get_metrics": "metrics for", "list_deploys": "deploys for",
            "search_runbook": "runbook for", "lookup_invoice": "invoice ", "open_ticket": "ticket for"}


class ContextOverflow(Exception):
    pass


class Run:
    """Cost meter for ONE task: every model call and its tokens are counted here."""

    def __init__(self, base_url=BASE_URL, model=MODEL):
        self.base_url, self.model, self.calls, self.tokens, self.world = base_url, model, 0, 0, ow.World()

    def chat(self, content_or_messages, tools=None):
        messages = content_or_messages if isinstance(content_or_messages, list) else [{"role": "user", "content": content_or_messages}]
        self.calls += 1
        r = requests.post(f"{self.base_url}/chat/completions", timeout=60, json={
            "model": self.model, "messages": messages, **({"tools": tools} if tools else {}), "temperature": 0})
        if r.status_code == 400 and "context_length_exceeded" in r.text:
            raise ContextOverflow(r.json()["error"]["message"])  # the context window is a hard limit
        r.raise_for_status()
        body = r.json()
        self.tokens += body["usage"]["total_tokens"]
        return body["choices"][0]["message"]


def loop(run, task, names, max_steps=8, extra_tools=0, trim=None):
    """ONE agent (ReAct style): a model call per step; every tool result stays in the context."""
    messages = [{"role": "user", "content": task}]
    for _ in range(max_steps):
        reply = run.chat(messages, ow.schemas(names, extra_tools))
        messages.append(reply)
        if not reply.get("tool_calls"):
            return reply["content"]
        for call in reply["tool_calls"]:
            name, args = call["function"]["name"], json.loads(call["function"]["arguments"])
            result = run.world.run(name, args) if name in names else f"error: tool {name} is not offered"
            result = trim(result) if trim else result  # optional tool-result budget (build task)
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    return "stopped: max_steps"


def single(run, task, extra_tools=0, trim=None):
    return loop(run, task, list(ow.FUNCS), extra_tools=extra_tools, trim=trim)


def router(run, task):
    """One routing call, then ONE specialist with only its own tools (fewer schemas per call)."""
    name = run.chat(f"<specialists>\n{SPECS}\n</specialists>\nPick one specialist.\n<route>{task}</route>")["content"].strip()
    return loop(run, task, ow.SPECIALISTS.get(name, []))  # code validates the route; unknown name -> no tools


def planner(run, task):
    """Planner/executor (ReWOO style): one planning call, code runs the plan, one call writes the answer."""
    plan = json.loads(run.chat(f"Plan the tool calls as JSON.\nTools: {', '.join(ow.FUNCS)}\n<plan>{task}</plan>")["content"])
    blocks = [f"[{s['tool']}({next(iter(s['args'].values()))})]\n{run.world.run(s['tool'], s['args'])}"
              for s in plan if s.get("tool") in ow.FUNCS]  # allow-list: the plan is data, not code
    return run.chat("Answer from these results.\n<results>\n" + "\n".join(blocks) + "\n</results>")["content"]


def supervisor(run, task):
    """Supervisor/worker: split, one worker loop per sub-task (own context), then one summarising call."""
    jobs = json.loads(run.chat(f"<specialists>\n{SPECS}\n</specialists>\nSplit the task.\n<split>{task}</split>")["content"])
    answers = [f"[{j['worker']}]\n{loop(run, j['task'], ow.SPECIALISTS.get(j['worker'], []))}" for j in jobs]
    return run.chat("Combine the worker answers.\n<results>\n" + "\n".join(answers) + "\n</results>")["content"]


def estimate(task):
    """Peak prompt of ONE agent ~ all tool schemas + task + every expected tool result (the last turn re-sends all)."""
    words = len(json.dumps(ow.schemas(list(ow.FUNCS))).split()) + len(task.split())
    for tool, keyword in KEYWORDS.items():
        words += task.lower().count(keyword) * (ow.OUTPUT_WORDS.get(tool, 12) + 25)  # result + call/reply overhead
    return words


def hybrid(run, task):
    """Decision under test: one agent by default; supervisor/worker only when the estimate would not fit."""
    return (supervisor if estimate(task) > 0.9 * CONTEXT_LIMIT else single)(run, task)


PATTERNS = {"single": single, "router": router, "planner": planner, "supervisor": supervisor, "hybrid": hybrid}


def evaluate(pattern, base_url=BASE_URL, model=MODEL, tasks=None, fn=None):
    rows = []
    for tid, task, expected in tasks or ow.TASKS:
        run = Run(base_url, model)
        try:
            answer, error = (fn or PATTERNS[pattern])(run, task), None
        except ContextOverflow as e:
            answer, error = None, f"context_length_exceeded: {e}"
        rows.append({"pattern": pattern, "task": tid, "pass": ow.grade(expected, answer, run.world.calls),
                     "model_calls": run.calls, "tokens": run.tokens, "error": error})
    return rows


def summary(rows):
    return {"pattern": rows[0]["pattern"], "passed": sum(r["pass"] for r in rows), "tasks": len(rows),
            "model_calls": sum(r["model_calls"] for r in rows), "tokens": sum(r["tokens"] for r in rows),
            "failed": [r["task"] for r in rows if not r["pass"]]}


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "patterns.jsonl"
    lines = []
    for name in PATTERNS:
        rows = evaluate(name)
        lines += [json.dumps(r) for r in rows]
        s = summary(rows)
        print(f"{s['pattern']:<10} {s['passed']}/{s['tasks']} passed  model calls {s['model_calls']:>3}  "
              f"tokens {s['tokens']:>6}  failed {s['failed']}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"per-task rows: {out.name}")
