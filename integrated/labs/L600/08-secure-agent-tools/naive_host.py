"""The anti-pattern, kept in its own file: a host that runs whatever tool the model asks for.

No capability, no policy, no approval, no output tagging; it offers every loaded tool and logs raw arguments.
This is the 'before' of the failure lab (run_project.py --inject naive-host).
"""
import json


class NaiveHost:
    def __init__(self, registry, model, world):
        self.registry, self.model, self.world, self.calls, self.log = registry, model, world, [], []

    def run(self, task, token=None, max_steps=6):
        tools = [{"type": "function", "function": {"name": n, "description": t.manifest["description"],
                                                   "parameters": t.schema}} for n, t in self.registry.items()]
        messages = [{"role": "user", "content": task}]
        for _ in range(max_steps):
            reply = self.model.propose(messages, tools)
            messages.append(reply)
            if not reply.get("tool_calls"):
                return reply.get("content") or ""
            for call in reply["tool_calls"]:
                name, args = call["function"]["name"], json.loads(call["function"]["arguments"] or "{}")
                self.log.append(json.dumps({"tool": name, "args": args, "token": token}))  # raw args + token: a leak
                tool = self.registry.get(name)
                try:
                    result = tool.fn(self.world, **args) if tool else f"error: unknown tool {name}"
                except Exception as exc:
                    result = f"error: {type(exc).__name__}"
                self.calls.append({"tool": name, "args": args, "side_effect": bool(tool and tool.manifest["sideEffect"]),
                                   "scope_ok": False, "allowed": True, "executed": tool is not None})
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": str(result)})
        return "stopped: max_steps"
