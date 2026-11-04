"""The shared lease store: a stdlib HTTP key-value store with TTL + compare-and-swap (this lab's etcd).
  POST /get    {key}                     -> 200 {value, rev, created, ttl_left} | 404 {rev: 0}
  POST /cas    {key, expect, value, ttl} -> 200 {rev, created} | 409 {rev}   expect = current rev (0 = absent)
  POST /delete {key, expect}             -> 200 {rev} | 409 {rev}
Every successful write takes the next value of ONE store-wide counter that only grows (like etcd's revision);
`created` is the revision at which the key was created and stays fixed while the lease is renewed."""
import threading

from helpers import QuietHandler, SimClock


class KVStore(QuietHandler):
    clock, lock, data, revision = SimClock(), threading.Lock(), {}, 0

    @classmethod
    def reset(cls, clock):
        cls.clock, cls.data, cls.revision = clock, {}, 0

    def _live(self, key):  # TTL: a key whose time has run out no longer exists
        entry = self.data.get(key)
        if entry and self.clock() >= entry["expires"]:
            del self.data[key]
            entry = None
        return entry

    def do_POST(self):
        req, cls = self.read_json(), type(self)
        with self.lock:  # the store applies one request at a time: CAS is atomic
            entry = self._live(req["key"])
            current = entry["rev"] if entry else 0
            if self.path == "/get":
                if not entry:
                    return self.reply(404, {"rev": 0})
                return self.reply(200, {"value": entry["value"], "rev": current, "created": entry["created"],
                                        "ttl_left": round(entry["expires"] - self.clock(), 3)})
            if req["expect"] != current:  # compare-and-swap failed: someone else changed the key
                return self.reply(409, {"rev": current})
            if self.path == "/delete":
                self.data.pop(req["key"], None)
                return self.reply(200, {"rev": current})
            cls.revision += 1
            created = entry["created"] if entry else cls.revision
            self.data[req["key"]] = {"value": req["value"], "rev": cls.revision, "created": created,
                                     "expires": self.clock() + req["ttl"]}
            self.reply(200, {"rev": cls.revision, "created": created})
