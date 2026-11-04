"""The replicated state machine of project 01 (helper for pqmsg.py). Every replica applies its committed Raft prefix
with this code; it never decrypts (replicas hold no keys) but reads the envelope HEADER - so it is a consumer of the
envelope contract too. Deterministic: the same committed prefix gives the same state on every replica, which is why
idempotency, epoch checks and the version gate live HERE and not in a leader's memory or a node's local config."""
import json

_PARSED = {}  # command string -> parsed entry: replicas and replays share one parse


class State:
    """Replicated state machine. Deterministic: the same committed prefix gives the same state on every replica."""
    def __init__(self, faults=(), local_accept=(1, 2)):
        self.epoch, self.members, self.accept, self.epoch_msgs, self.applied = 0, [], [1, 2], 0, 0
        self.seen, self.messages, self.epochs, self.rejected = {}, [], [], []
        self.faults, self.local_accept = set(faults), list(local_accept)

    def accepted(self) -> list:  # the fault reads a node-local setting instead of the replicated gate
        return self.local_accept if "local-contract-config" in self.faults else self.accept

    def apply(self, index: int, command: str) -> str:
        e, self.applied = _PARSED.get(command) or _PARSED.setdefault(command, json.loads(command)), index
        if e["type"] == "epoch":
            if e["epoch"] <= self.epoch:
                return "duplicate"  # a retried control entry
            self.epoch, self.members, self.epoch_msgs = e["epoch"], e["members"], 0
            self.epochs.append(e)
            return "epoch"
        if e["type"] == "contract":  # version gate: every replica switches at the same log index
            self.accept = e["accept"]
            return "contract"
        h = e["h"]
        verdict = ("unsupported_version" if h["v"] not in self.accepted() else
                   "stale_epoch" if h["epoch"] != self.epoch and "accept-stale-epoch" not in self.faults else
                   "not_a_member" if h["sender"] not in self.members else None)
        if verdict:
            self.rejected.append((index, h["ikey"], verdict))
            return verdict
        old = self.seen.get(h["ikey"])
        if old and "no-apply-dedupe" not in self.faults:  # idempotency lives in REPLICATED state, not leader memory
            return "conflict" if old[0] == h["epoch"] and old[1] != e["fp"] else "duplicate"
        self.seen.setdefault(h["ikey"], (h["epoch"], e["fp"], index))
        self.messages.append(e)
        self.epoch_msgs += 1
        return "accepted"
