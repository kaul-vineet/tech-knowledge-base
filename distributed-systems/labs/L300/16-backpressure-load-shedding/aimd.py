"""An adaptive concurrency limit on the CALLER's side, AIMD style (the TCP congestion-window idea that libraries
such as Netflix concurrency-limits apply to requests): additive increase while answers come back, multiplicative
decrease on a 503. Requests above the limit fail locally - they never reach the overloaded server."""


class AIMDLimit:
    def __init__(self, initial=20.0, minimum=1.0, maximum=200.0, backoff=0.9):
        self.limit, self.minimum, self.maximum, self.backoff, self.in_flight = initial, minimum, maximum, backoff, 0

    def allow(self):
        if self.in_flight >= self.limit:
            return False
        self.in_flight += 1
        return True

    def on_success(self):
        self.in_flight -= 1
        self.limit = min(self.maximum, self.limit + 1 / self.limit)  # about +1 per limit's worth of answers

    def on_drop(self):
        self.in_flight -= 1
        self.limit = max(self.minimum, self.limit * self.backoff)  # back off fast when the server sheds
