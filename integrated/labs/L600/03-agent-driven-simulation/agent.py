"""Tool-calling loop (the ai-agents L100 #6 shape): model -> tool call -> pipeline -> result -> model -> summary.

The model's only power is to PROPOSE tool arguments and write text. pipeline.submit() decides what runs;
claims.review() decides what of the text is published. Call/token budget: ai-agents L300 #14 Budget.
"""
import json
import urllib.request

import _kb
import contract

resilient = _kb.load("resilient_agent")
SYSTEM = ("You plan simulation experiments for an IT help desk (M/M/1 queue, times in minutes). Use only the tools. "
          "In your final summary cite the experiment id like [exp-1a2b3c4d] in every sentence that has a number, "
          "quote numbers only from tool results, and call a difference significant only if the verdict says so.")


def post(base_url, body, timeout=120):
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_session(brief, pipeline, base_url, model, max_calls=8, max_tokens=40_000, max_cost=0.10):
    budget = resilient.Budget(max_calls=max_calls, max_tokens=max_tokens, max_cost=max_cost)
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": brief}]
    trace = []
    try:
        while True:
            budget.before_call()  # raises BudgetExceeded at max_calls: the loop cannot run forever
            data = post(base_url, {"model": model, "messages": messages, "tools": contract.TOOLS, "temperature": 0})
            budget.add(model, data.get("usage") or {"total_tokens": 0})
            reply = data["choices"][0]["message"]
            messages.append(reply)
            calls = reply.get("tool_calls") or []
            if not calls:
                return {"summary": reply.get("content") or "", "trace": trace, "calls": budget.calls,
                        "tokens": budget.tokens, "stopped": "final_answer"}
            for call in calls:
                args = None
                try:
                    args = json.loads(call["function"].get("arguments") or "{}")
                    result = pipeline.submit(call["function"]["name"], args)
                except json.JSONDecodeError as exc:
                    result = {"status": "rejected", "errors": [f"arguments are not valid JSON ({exc.msg})"]}
                trace.append({"tool": call["function"]["name"], "args": args,
                              "status": result["status"], "errors": result.get("errors", [])})
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})
    except resilient.BudgetExceeded as exc:
        return {"summary": "", "trace": trace, "calls": budget.calls, "tokens": budget.tokens,
                "stopped": f"agent budget: {exc}"}
