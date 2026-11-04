"""Plumbing for project 01 (not the lesson's concept): a faster cluster driver over lesson 12's helpers.Cluster,
the retrying client and the offline nonce audit (cryptography L300 #15 scan_for_reuse, run per epoch key)."""
import uuid

import group_crypto as gc
from _kb import load

helpers, guard = load("raft", "helpers"), load("misuse", "nonce_guard")


class FastCluster(helpers.Cluster):
    """helpers.Cluster minus the per-tick full safety scan (too slow for 10k entries); check() runs it on demand."""
    def run(self, ticks):
        for _ in range(ticks):
            self.net.now += 1
            for src, dst, msg in self.net.due():
                self.nodes[dst].receive(src, msg)
            for name, node in self.nodes.items():
                if name not in self.net.down:
                    node.tick()

    def check(self):
        self.checker.observe(self.net.now, self.nodes.values())
        return self.checker.violations


def send(svc, sender, text, rng, attempts=12):
    """Client: ONE key per logical message, created before the retry loop (DS lesson 5); retries only on 503."""
    key = f'"{uuid.UUID(int=rng.getrandbits(128), version=4)}"'  # production: uuid.uuid4(); seeded for replay
    for attempt in range(1, attempts + 1):
        status, body = svc.post(key, sender, text)
        if status != 503:
            return status, body, attempt
    return status, body, attempts


def nonce_reuse(wire) -> dict:
    """Lesson 15's offline scan, per epoch key: {epoch: {nonce_hex: [wire indexes]}} for nonces sealed twice."""
    by_epoch = {}
    for env in wire:
        by_epoch.setdefault(env["h"]["epoch"], []).append(gc.b64d(env["h"]["n"]) + gc.b64d(env["ct"]))
    return {e: hits for e, blobs in by_epoch.items() if (hits := guard.scan_for_reuse(blobs))}
