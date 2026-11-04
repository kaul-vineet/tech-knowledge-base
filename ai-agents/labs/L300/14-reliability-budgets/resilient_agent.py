"""Hardened agent loop: per-call timeout, retry with backoff (5xx/timeouts only), budgets, fallback, cache."""
import hashlib
import json
import os
import random
import time

import requests

PRICE_PER_1K = {"fake-model": 0.002, "fake-small": 0.0005}  # illustrative $ per 1k tokens; local models cost 0
CANNED = "Sorry - the assistant is busy right now. Your question is saved and a person will reply."
TOOLS = [{"type": "function", "function": {"name": "calculator", "description": "evaluate arithmetic",
                                           "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}}}}]


class BudgetExceeded(Exception):
    pass


class Unavailable(Exception):
    pass


class Budget:
    """Per-question spend limits: model calls (steps + retries), tokens and cost. Checked by code, every call."""

    def __init__(self, max_calls=8, max_tokens=1500, max_cost=0.01):
        self.max_calls, self.max_tokens, self.max_cost = max_calls, max_tokens, max_cost
        self.calls, self.tokens, self.cost = 0, 0, 0.0

    def before_call(self):
        if self.calls >= self.max_calls:
            raise BudgetExceeded(f"calls {self.calls} >= {self.max_calls}")
        self.calls += 1

    def add(self, model, usage):
        self.tokens += usage["total_tokens"]
        self.cost += usage["total_tokens"] / 1000 * PRICE_PER_1K.get(model, 0.0)
        if self.tokens > self.max_tokens or self.cost > self.max_cost:
            raise BudgetExceeded(f"tokens {self.tokens} / cost ${self.cost:.4f}")


class Client:
    def __init__(self, endpoints, timeout=0.5, retries=2, backoff=0.05, cap=0.4, seed=7, events=None):
        self.endpoints = endpoints  # [(base_url, model), ...]: primary first, then the fallback (smaller) model
        self.timeout, self.retries, self.backoff, self.cap = timeout, retries, backoff, cap
        self.rng, self.cache, self.events = random.Random(seed), {}, events if events is not None else []

    def log(self, event, **fields):
        self.events.append({"event": event, **fields})  # JSON-lines-ready structured log

    def chat(self, messages, budget):
        key = hashlib.sha256(json.dumps(messages, sort_keys=True).encode("utf-8")).hexdigest()
        if key in self.cache:  # response cache: same request -> no call, no tokens
            self.log("cache_hit", key=key[:12])
            return self.cache[key]
        for base_url, model in self.endpoints:
            try:
                self.cache[key] = self._call(base_url, model, messages, budget)
                return self.cache[key]
            except Unavailable as e:
                self.log("fallback", reason=str(e))  # try the next endpoint in the chain
        raise Unavailable("all endpoints failed")

    def _call(self, base_url, model, messages, budget):
        for attempt in range(self.retries + 1):
            budget.before_call()  # retries spend the same budget as steps
            start = time.perf_counter()
            try:
                r = requests.post(f"{base_url}/chat/completions", timeout=self.timeout,  # per-call timeout
                                  json={"model": model, "messages": messages, "tools": TOOLS, "temperature": 0})
                error = f"http_{r.status_code}" if r.status_code >= 500 else None
            except (requests.Timeout, requests.ConnectionError) as e:
                error = "timeout" if isinstance(e, requests.Timeout) else "connection"
            ms = round((time.perf_counter() - start) * 1000)
            if error is None:
                r.raise_for_status()  # 4xx = a bug in OUR request: never retried
                body = r.json()
                budget.add(model, body["usage"])
                self.log("call", model=model, attempt=attempt, ms=ms, tokens=body["usage"]["total_tokens"])
                return body["choices"][0]["message"]
            if attempt == self.retries:
                self.log("give_up", model=model, attempt=attempt, error=error, ms=ms)
                break
            delay = min(self.cap, self.backoff * 2 ** attempt) * self.rng.uniform(0.5, 1.0)  # backoff + jitter
            self.log("retry", model=model, attempt=attempt, error=error, ms=ms, sleep_s=round(delay, 3))
            time.sleep(delay)
        raise Unavailable(f"{model}: {error} after {self.retries + 1} attempts")


def answer(question, client, max_steps=4, budget=None):
    """Agent loop with a step budget; any exhausted budget or outage ends in the canned answer."""
    budget = budget or Budget()
    messages = [{"role": "user", "content": question}]
    try:
        for _ in range(max_steps):
            reply = client.chat(messages, budget)
            messages.append(reply)
            if not reply.get("tool_calls"):
                return reply["content"]
            for call in reply["tool_calls"]:
                expr = json.loads(call["function"]["arguments"])["expression"]
                result = str(eval(expr, {"__builtins__": {}}))  # demo calculator; fixed inputs only
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
        client.log("step_budget", max_steps=max_steps)
    except (BudgetExceeded, Unavailable) as e:
        client.log("canned", reason=str(e))
    return CANNED


if __name__ == "__main__":
    primary = (os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1"),
               os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b"))
    fallback = (os.environ.get("FALLBACK_MODEL_URL", primary[0]), os.environ.get("FALLBACK_MODEL", "qwen2.5:0.5b"))
    client = Client([primary, fallback])
    print(answer("What is 12*7?", client))
    print("\n".join(json.dumps(e) for e in client.events))
