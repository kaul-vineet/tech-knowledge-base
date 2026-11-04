"""L600 #01 (main file): post-quantum secure group messaging over a replicated log.
Members get each epoch secret in a hybrid X25519+ML-KEM-768 welcome (group_crypto.py); messages are sealed under it,
written to a transactional outbox, relayed onto a 3-node Raft log (in-process network, crashes) and applied by a
deterministic state machine that dedupes Idempotency-Keys, enforces epochs and gates envelope versions. Replicas
only store and order ciphertext. Seeded faults: leader-counter, no-apply-dedupe, accept-stale-epoch, local-contract-config."""
import json
import os
import random
import sqlite3

import group_crypto as gc
import nonce_derived
from _kb import load
from harness import FastCluster
from replicated_state import State

raft = load("raft", "solution_raft")  # Raft WITH the election restriction (lesson 12 build task)
idem, outbox = load("idem", "idempotency"), load("outbox", "outbox")
MAX_MSGS_PER_EPOCH = 2**32  # NIST SP 800-38D 8.3: random 96-bit IVs -> at most 2^32 encryptions per key
FAULTS = ("leader-counter", "no-apply-dedupe", "accept-stale-epoch", "local-contract-config")


class RandomNonce:  # ADR-01-1: 96 random bits, nothing to replicate, safe up to the per-epoch message limit
    def next(self, term: int) -> bytes:
        return os.urandom(12)


class NotCommitted(Exception):
    """Outcome unknown (leader lost or no commit in time): the client retries with the SAME Idempotency-Key."""


class Service:
    def __init__(self, members, seed=1, nonce_factory=RandomNonce, faults=(), local_accept=None, chaos=0.0):
        self.faults, self.local_accept, self.version = set(faults), local_accept or {}, 2
        self.nonce_factory = nonce_derived.DerivedNonce if "leader-counter" in self.faults else nonce_factory
        self.cluster, self.rng, self.chaos, self.chaos_on = FastCluster(raft.Node, seed), random.Random(seed), chaos, False
        self.sealer, self.devices = gc.Device("svc"), {m: gc.Device(m) for m in members}  # svc: key in every node's keystore
        self.rt = {n: self._fresh(n) for n in self.cluster.nodes}
        self.dbs = {n: sqlite3.connect(":memory:") for n in self.cluster.nodes}  # each node's local disk
        for db in self.dbs.values():
            db.executescript(outbox.SCHEMA)  # lesson 9's schema; Relay reads its outbox table
        self.wire, self.failovers, self.to_drain = [], 0, []  # wire: every envelope any sealer ever produced
        self.rotate(list(members))

    def _fresh(self, name):  # volatile runtime of one node: rebuilt by replaying the log after a restart
        return {"state": State(self.faults, self.local_accept.get(name, (1, 2))), "nonce": self.nonce_factory(),
                "sealer": self.sealer.fork()}

    def sync(self, name):
        node, rt = self.cluster.nodes[name], self.rt[name]
        for i in range(rt["state"].applied + 1, node.commit + 1):
            if rt["state"].apply(i, node.log[i - 1][1]) == "epoch":
                rt["sealer"].learn(rt["state"].epochs[-1])  # the sealer learns epoch keys from the log, like members
        return rt

    def leader(self):
        return self.cluster.run_until_leader()

    def crash_leader(self):
        for n in list(self.cluster.net.down):
            self.restart(n)  # at most one node down: a majority stays up
        self.cluster.crash(self.leader().name)
        self.failovers += 1

    def restart(self, name):
        self.cluster.restart(name)
        self.rt[name], self.to_drain = self._fresh(name), self.to_drain + [name]

    def publish(self, channel, payload):
        """The 'bus' lesson 9's Relay hands rows to: propose on the leader and wait for the commit."""
        leader = self.leader()
        leader.propose(json.dumps(payload))
        index = len(leader.log)
        if self.chaos_on and self.rng.random() < self.chaos:
            self.crash_leader()  # after propose, before commit: the entry may or may not survive
        for _ in range(40):
            self.cluster.run(1)
            if leader.name in self.cluster.net.down or leader.role != "leader":
                raise NotCommitted("leader lost")
            if leader.commit >= index:
                return self.sync(leader.name)
        raise NotCommitted("not committed in time")

    def relay(self, name):
        try:
            outbox.Relay(self.dbs[name], self).publish_pending()  # at-least-once: re-sends rows not marked published
        except NotCommitted:
            return False
        return True

    def post(self, key_header, sender, text):
        """POST /groups/g/messages. 201 created, 200 replay, 400 bad key, 409 refused, 422 key reuse, 503 retry."""
        if not (m := idem.KEY_RE.match(key_header or "")):
            return 400, {"title": "Idempotency-Key is missing or malformed"}
        ikey = m.group(1)
        while self.to_drain:
            self.relay(self.to_drain.pop())  # a restarted node relays rows stuck in its outbox
        leader = self.leader()
        rt = self.sync(leader.name)
        st, keys = rt["state"], rt["sealer"].keys
        if ikey in st.seen:
            epoch, fp, index = st.seen[ikey]
            if fp != gc.fingerprint(keys[epoch], sender, text):
                return 422, {"title": "Idempotency-Key already used for another message"}
            return 200, {"msg_id": ikey, "index": index, "epoch": epoch}
        if self.version not in st.accepted() or st.epoch_msgs >= MAX_MSGS_PER_EPOCH:
            return 409, {"title": "envelope version not accepted yet" if self.version not in st.accepted() else "rotation_required"}
        env = gc.seal(keys[st.epoch], st.epoch, sender, ikey, text, rt["nonce"].next(leader.term), self.version)
        self.wire.append(env)
        with self.dbs[leader.name] as db:  # outbox: store the sealed envelope (never plaintext), then relay it
            db.execute("INSERT INTO outbox (channel, payload) VALUES (?, ?)", ("group-messages", json.dumps(env)))
        self.chaos_on = True
        if self.chaos and self.rng.random() < self.chaos:
            self.crash_leader()  # crash after the outbox write, before the relay: the row is stuck on that disk
            ok = False
        else:
            ok = self.relay(leader.name)
        self.chaos_on = False
        st = self.sync(self.leader().name)["state"] if ok else None
        if st and ikey in st.seen:
            epoch, fp, index = st.seen[ikey]
            return (201, {"msg_id": ikey, "index": index, "epoch": epoch}) if fp == env["fp"] else (422, {"title": "key reused"})
        return (409, {"title": next((v for _, k, v in st.rejected[::-1] if k == ikey), "rejected")}) if st else (503, {"title": "retry"})

    def control(self, entry):  # epoch and contract entries: no outbox, retried until applied (apply is idempotent)
        for _ in range(10):
            try:
                return self.publish("control", entry)
            except NotCommitted:
                continue
        raise NotCommitted("control entry not committed")

    def rotate(self, members):
        st = self.sync(self.leader().name)["state"]
        epoch, secret = st.epoch + 1, os.urandom(32)
        to = {**{m: self.devices[m].key_package for m in members}, "svc": self.sealer.key_package}
        entry = {"type": "epoch", "epoch": epoch, "members": sorted(members),
                 "welcomes": {n: gc.welcome(kp, secret, epoch, n) for n, kp in to.items()}}
        self.control(entry)
        return entry

    def settle(self, ticks=60):
        for n in list(self.cluster.net.down):
            self.restart(n)
        while self.to_drain:
            self.relay(self.to_drain.pop())
        self.cluster.run(ticks)
        return self.cluster.check()  # lesson 12's State Machine Safety checker over all replicas

    def replay(self, reader, replica):
        """What `reader`'s fresh device shows after replaying `replica`'s committed log from index 1."""
        node, st = self.cluster.nodes[replica], State(self.faults, self.local_accept.get(replica, (1, 2)))
        for i in range(1, node.commit + 1):
            st.apply(i, node.log[i - 1][1])
        dev = (self.sealer if reader == "svc" else self.devices[reader]).fork()
        for e in st.epochs:
            dev.learn(e)
        return [(m["h"]["ikey"], m["h"]["sender"], gc.open_msg(dev.keys, m)) for m in st.messages]


