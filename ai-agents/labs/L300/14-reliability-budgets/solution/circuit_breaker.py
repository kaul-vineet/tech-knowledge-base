"""Build task (lesson 14): a circuit breaker - after N give-ups in a row, skip that endpoint for the next M chats."""
from resilient_agent import Client, Unavailable


class BreakerClient(Client):
    def __init__(self, endpoints, trip_after=2, cool_down=5, **kw):
        super().__init__(endpoints, **kw)
        self.trip_after, self.cool_down = trip_after, cool_down
        self.failures = {model: 0 for _, model in endpoints}
        self.skip = {model: 0 for _, model in endpoints}  # chats left while the breaker is open

    def _call(self, base_url, model, messages, budget):
        if self.skip[model] > 0:
            self.skip[model] -= 1
            raise Unavailable(f"{model}: breaker open")  # no HTTP call, no budget spent
        try:
            message = super()._call(base_url, model, messages, budget)
        except Unavailable:
            self.failures[model] += 1
            if self.failures[model] >= self.trip_after:
                self.skip[model], self.failures[model] = self.cool_down, 0
                self.log("breaker_open", model=model, chats=self.cool_down)
            raise
        self.failures[model] = 0
        return message
