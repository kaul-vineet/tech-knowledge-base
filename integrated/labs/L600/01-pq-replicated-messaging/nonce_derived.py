"""BUILD TASK (shipped, faulty on purpose): a deterministic nonce source for the sealer on the Raft leader.
It looks fine in a single-process test and is exactly the failure lab (`run_project.py --inject leader-counter`):
the counter lives in the sealer's memory, is not replicated and ignores the Raft term, so every new leader - and
every restarted one - starts again at 1 under the SAME epoch key. Fix it so test_build_task passes (see README)."""


class DerivedNonce:
    def __init__(self):
        self.counter = 0  # volatile: lost on restart, unknown to the other replicas

    def next(self, term: int) -> bytes:
        self.counter += 1
        return self.counter.to_bytes(12, "big")  # BUG on purpose: term ignored, counter restarts per leader
