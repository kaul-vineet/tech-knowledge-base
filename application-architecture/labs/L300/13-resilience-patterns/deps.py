"""Stand-in dependencies with switchable faults (in-process, deterministic). Not lesson code."""
import threading
import time


class Members:
    """Healthy, fast dependency: answers in about 1 ms."""

    def check(self, member_id):
        time.sleep(0.001)
        return not member_id.startswith("blocked")


class Catalogue:
    """mode 'up': 2 ms; 'down': raises ConnectionError at once; 'slow': hangs until release() or hang_s."""

    def __init__(self, mode="up", hang_s=1.0):
        self.mode, self.hang_s, self.calls = mode, hang_s, 0
        self._released = threading.Event()

    def title(self, book_id):
        self.calls += 1
        if self.mode == "down":
            raise ConnectionError("catalogue: connection refused")
        if self.mode == "slow":
            self._released.wait(self.hang_s)  # a stuck downstream call (lock, GC pause, dead socket)
        else:
            time.sleep(0.002)
        return f"Title of {book_id}"

    def release(self):
        self._released.set()
