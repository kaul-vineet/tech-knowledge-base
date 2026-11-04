"""Build task (lesson 14) - YOUR FILE. Shipped UNFIXED: BreakerClient accepts trip_after / cool_down but never
opens, so a dead primary costs 3 attempts (and budget) on every chat before the fallback answers.

TODO: override _call(base_url, model, messages, budget):
  - while the breaker for `model` is open: count down, raise Unavailable at once (no HTTP call, no budget);
  - on Unavailable from super()._call(): count it; after trip_after give-ups in a row, open for cool_down chats;
  - on success: reset the counter.
Check it: BUILD_TARGET=mine python -m unittest -v test_build_task
"""
from resilient_agent import Client, Unavailable  # noqa: F401  (Unavailable: raise it while the breaker is open)


class BreakerClient(Client):
    def __init__(self, endpoints, trip_after=2, cool_down=5, **kw):
        super().__init__(endpoints, **kw)
        self.trip_after, self.cool_down = trip_after, cool_down  # stored, not used yet
