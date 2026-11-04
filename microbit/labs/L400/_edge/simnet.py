"""L400 network helpers (CPython only, never flashed to a board).

LinkAir     the stub radio "air" with a seeded loss probability PER LINK (sensor <-> relay),
            optionally changing over time (loss_fn) - the L300 Air has one global loss.
percentile  nearest-rank percentile, so p95 is a value that was really observed.
reuse(...)  import an earlier lab's file under a unique module name (labs share file names).
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABS = HERE.parent.parent
STUB = LABS / "sim_stub"
if str(STUB) not in sys.path:
    sys.path.insert(0, str(STUB))
import radio as radio_stub  # noqa: E402  (the stub)

SERIAL_BAUD = 115200            # micro:bit USB serial default used by the labs (10 bits per byte on the wire)


class LinkAir(radio_stub.Air):
    """Per-link loss. loss: {board name: p}; a link's loss applies in both directions.

    loss_fn(sender, receiver, now_ms) -> p overrides the table (drift scenarios).
    The relay hears everything; sensors also hear each other (broadcast radio), and
    other sensors' frames fill their receive queue exactly like on a real group.
    """

    def __init__(self, loss=None, default_loss=0.0, seed=0, loss_fn=None):
        super().__init__(seed=seed)
        self.link_loss, self.default_loss, self.loss_fn = dict(loss or {}), default_loss, loss_fn
        self.now = 0
        self.per_link = {}

    def p_loss(self, a, b):
        if self.loss_fn:
            return self.loss_fn(a, b, self.now)
        return max(self.link_loss.get(a, self.default_loss), self.link_loss.get(b, self.default_loss))

    def _fault_deliver(self, ep, sender, payload):
        key = (sender.name, ep.name)
        st = self.per_link.setdefault(key, [0, 0])
        st[0] += 1
        if self.rng.random() < self.p_loss(sender.name, ep.name):
            self.faults["lost"] += 1
            st[1] += 1
            return
        ep._deliver(sender, payload)


def percentile(values, q):
    """Nearest-rank percentile (q in 0..100); None for no values."""
    if not values:
        return None
    s = sorted(values)
    k = max(1, -(-q * len(s) // 100))       # ceil(q/100 * n), at least 1
    return s[int(k) - 1]


def serial_ms(nbytes, baud=SERIAL_BAUD):
    """Time to push nbytes over a UART at baud (8N1 = 10 bits per byte)."""
    return nbytes * 10 * 1000.0 / baud


def reuse(rel_path, name):
    """Load labs/<rel_path> as module `name` (its folder goes on sys.path for its own imports)."""
    path = LABS / rel_path
    if name in sys.modules:
        return sys.modules[name]
    folder = str(path.parent)
    sys.path.insert(0, folder)                 # only while it loads: its test_*.py must not shadow ours
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(folder)
    return mod
