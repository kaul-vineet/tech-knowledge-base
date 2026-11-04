"""An in-process MQTT-style broker for tests (CPython only). NOT MQTT on the wire.

Same contract the labs rely on from MQTT 5.0 (OASIS, 2019): topic names with "/" levels,
filters with "+" (one level) and "#" (rest, last), QoS 1 = at least once (a PUBACK per
publish; a retried publish may arrive twice), RETAIN = the broker keeps the last message per
topic and hands it to new subscribers. Real broker: Eclipse Mosquitto (CI job, pending-ci).
"""


def matches(topic_filter, topic):
    f, t = topic_filter.split("/"), topic.split("/")
    for i, part in enumerate(f):
        if part == "#":
            return True
        if i >= len(t) or (part != "+" and part != t[i]):
            return False
    return len(f) == len(t)


class MiniBroker:
    def __init__(self):
        self.subs = []            # (filter, callback)
        self.retained = {}
        self.stats = {"published": 0, "delivered": 0, "pubacks": 0}

    def subscribe(self, topic_filter, callback):
        self.subs.append((topic_filter, callback))
        for topic, payload in sorted(self.retained.items()):
            if matches(topic_filter, topic):
                callback(topic, payload)

    def publish(self, topic, payload, qos=1, retain=False):
        if "+" in topic or "#" in topic:
            raise ValueError("wildcards are not allowed in a topic name")
        self.stats["published"] += 1
        if retain:
            self.retained[topic] = payload
        for topic_filter, cb in self.subs:
            if matches(topic_filter, topic):
                cb(topic, payload)
                self.stats["delivered"] += 1
        if qos:
            self.stats["pubacks"] += 1
            return True           # PUBACK
        return None
