"""In-process event bus: channel -> list of handlers, called synchronously, in subscription order."""
from collections import defaultdict


class InProcessBus:
    def __init__(self):
        self._handlers = defaultdict(list)
        self.delivered = []  # (channel, eventType) log, handy for demos and tests

    def subscribe(self, channel, handler):
        self._handlers[channel].append(handler)

    def publish(self, channel, event):
        for handler in self._handlers[channel]:
            handler(event)  # an exception propagates: the relay then keeps the event pending
        self.delivered.append((channel, event["eventType"]))
