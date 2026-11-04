"""The 'before' picture: the same agent with tracing switched off, logging one line per run (the usual setup)."""
import json
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import traced_agent


class NoSpans:
    @contextmanager
    def span(self, name, kind, **attributes):
        yield attributes  # same interface, nothing recorded


def run_with_log(task, log_path, **kw):
    start = time.perf_counter()
    answer = traced_agent.run(task, NoSpans(), **kw)
    line = {"event": "agent_run", "duration_ms": round((time.perf_counter() - start) * 1000, 1), "answer_chars": len(answer)}
    Path(log_path).write_text(json.dumps(line) + "\n", encoding="utf-8")
    return answer


if __name__ == "__main__":
    task = 'What is the weather in Paris? Also search docs for "rate limits" and compute 17*23.'
    run_with_log(task, sys.argv[1] if len(sys.argv) > 1 else "run.log.jsonl")
    print(Path(sys.argv[1] if len(sys.argv) > 1 else "run.log.jsonl").read_text(encoding="utf-8").strip())
    print("slowest below the root:", traced_agent.diagnose(sys.argv[1] if len(sys.argv) > 1 else "run.log.jsonl"))
