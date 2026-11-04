"""Plumbing for lab 14 (not the lesson's concept): the saga log (an append-only list of JSON lines; in a real
system a table or a topic that survives the orchestrator) and a fault injector that crashes the orchestrator."""
import json


class StepFailed(Exception):
    """A service said no (business failure): the saga must compensate."""


class Crash(Exception):
    """The orchestrator process died. Whatever it did not write to the saga log, it does not remember."""


class SagaLog:
    def __init__(self):
        self.lines = []

    def write(self, saga, step, status, **extra):
        self.lines.append(json.dumps({"saga": saga, "step": step, "status": status, **extra}))

    def entries(self, saga=None):
        rows = [json.loads(line) for line in self.lines]
        return [r for r in rows if saga is None or r["saga"] == saga]


def crash_once_after(fn):
    """Fault: the call itself succeeds, then the orchestrator dies before it can log 'done' (only the first time)."""
    state = {"crashed": False}

    def wrapper(*args):
        result = fn(*args)
        if not state["crashed"]:
            state["crashed"] = True
            raise Crash(f"orchestrator died right after {fn.__name__}{args}")
        return result
    return wrapper
