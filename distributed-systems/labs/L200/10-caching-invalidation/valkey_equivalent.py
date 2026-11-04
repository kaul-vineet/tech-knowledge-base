"""Same lesson on a shared cache server: cache-aside in Valkey with SET ... EX (TTL), DEL on write
(invalidate) and SET ... NX EX as a cross-process "only one loader" lock. Stdlib RESP2 client.
Needs Valkey on 127.0.0.1:6379, e.g. `podman run -d -p 6379:6379 docker.io/valkey/valkey:9.1.3`.
Run: python valkey_equivalent.py   (pending-ci: Valkey runs only in the CI job; the client is unit-tested locally)."""
import os, socket


class Valkey:
    """Minimal RESP2 client: a command is an array of bulk strings; replies are + - : $ or *."""
    def __init__(self, host="127.0.0.1", port=6379):
        self.sock = socket.create_connection((host, port), timeout=2)
        self.reader = self.sock.makefile("rb")

    def cmd(self, *args):
        parts = [str(a).encode("utf-8") for a in args]
        self.sock.sendall(b"*%d\r\n" % len(parts) + b"".join(b"$%d\r\n%s\r\n" % (len(p), p) for p in parts))
        return self._reply()

    def _reply(self):
        line = self.reader.readline()
        kind, rest = line[:1], line[1:-2].decode("utf-8")
        if kind == b"+":
            return rest
        if kind == b"-":
            raise RuntimeError(rest)
        if kind == b":":
            return int(rest)
        if kind == b"$":  # bulk string; $-1 = nil (key missing)
            return None if int(rest) < 0 else self.reader.read(int(rest) + 2)[:-2].decode("utf-8")
        if kind == b"*":
            return None if int(rest) < 0 else [self._reply() for _ in range(int(rest))]
        raise RuntimeError(f"unexpected reply {line!r}")

    def close(self):
        self.reader.close()
        self.sock.close()


DB = {"apple": "5"}  # the source of truth (a dict stands in for the database)


def get_price(v, sku, ttl=30):
    cached = v.cmd("GET", f"price:{sku}")
    if cached is not None:
        return cached, "hit"
    if v.cmd("SET", f"lock:{sku}", "me", "NX", "EX", 5) != "OK":  # someone else is loading: use DB once more
        return DB[sku], "miss (another loader holds the lock)"
    v.cmd("SET", f"price:{sku}", DB[sku], "EX", ttl)  # fill with a TTL
    v.cmd("DEL", f"lock:{sku}")
    return DB[sku], "miss -> filled"


def set_price(v, sku, price):
    DB[sku] = str(price)
    v.cmd("DEL", f"price:{sku}")  # invalidate-on-write


if __name__ == "__main__":
    v = Valkey(port=int(os.environ.get("VALKEY_PORT", 6379)))
    print("PING ->", v.cmd("PING"))
    v.cmd("DEL", "price:apple", "lock:apple")
    print("read 1 ->", get_price(v, "apple"), "| TTL", v.cmd("TTL", "price:apple"))
    print("read 2 ->", get_price(v, "apple"))
    set_price(v, "apple", 9)
    print("write 9, read ->", get_price(v, "apple"))
    assert get_price(v, "apple") == ("9", "hit")
    v.close()
    print("valkey equivalent OK")
