"""tryIt experiments for lesson 2 (python try_it.py). Prints what actually happens."""
import socket, time
from urllib.error import URLError

import two_services as ts

# tryIt 1: point A at a port where nothing listens (B is down)
s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
try:
    ts.call_b(f"http://127.0.0.1:{port}", "pear")
except URLError as e:
    print(f"tryIt 1: {type(e).__name__} -> {type(e.reason).__name__}: {e.reason.strerror}")


# tryIt 2: make B take 50 ms per request, then make 3 calls one after another
class SlowServiceB(ts.ServiceB):
    def do_GET(self):
        time.sleep(0.050)
        super().do_GET()


b = ts.serve(SlowServiceB)
url = f"http://127.0.0.1:{b.server_port}"
t0 = time.perf_counter()
lat = [ts.call_b(url, item)[1] for item in ("apple", "pear", "plum")]
total = (time.perf_counter() - t0) * 1000
print(f"tryIt 2: every call >= 50 ms: {all(ms >= 50 for ms in lat)}; "
      f"3 sequential calls >= 150 ms: {total >= 150} (total {total:.0f} ms)")
b.shutdown()
