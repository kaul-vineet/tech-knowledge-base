"""Shared plumbing for this lab (not the lesson's concept): a simulated clock so TTLs are reproducible."""


class SimClock:
    """Simulated seconds: the demo sets or advances time explicitly, so nothing sleeps for a TTL."""
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt
