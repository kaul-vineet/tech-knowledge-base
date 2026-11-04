"""Build-task solution (lesson 11): per-session rate limit - at most max_calls_per_tool calls to each tool."""
from collections import Counter

from guarded_agent import Session


class RateLimitedSession(Session):
    def __init__(self, allowed, max_calls_per_tool=2, **kwargs):
        super().__init__(allowed, **kwargs)
        self.max_calls, self.calls = max_calls_per_tool, Counter()

    def execute(self, name, args):
        self.calls[name] += 1  # counted even when later checks refuse: a looping model still hits the limit
        if self.calls[name] > self.max_calls:
            return f"error: rate limit: {name} called more than {self.max_calls} times in this session"
        return super().execute(name, args)
