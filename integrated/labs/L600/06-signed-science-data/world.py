"""One seeded run of the whole system: 4 releases over 4 simulated hours, a key rotation before v4, 4 mirrors fed
only through mirror m0 + anti-entropy, m3 partitioned while v4 spreads (a snapshot of it is the 'lagging' mirror).
Faults (all off by default): float-format, drop-old-key, no-freshness, licence-drop."""
import copy

import canonical as C
import client as CL
import mirrors as MR
import publisher as P

SPACING = 1200  # a release every 20 simulated minutes


class World:
    def __init__(self, inject=None):
        self.inject = inject
        self.pub = P.Publisher(keep_retired=inject != "drop-old-key")
        enc = C.platform_dumps if inject == "float-format" else C.dumps  # m2 re-serialises JSON on ingest
        self.mirrors = [MR.Mirror("m0"), MR.Mirror("m1"), MR.Mirror("m2", encoder=enc), MR.Mirror("m3")]
        self.rounds, self.stale, self.now = {}, None, 0
        for v in (1, 2, 3, 4):
            self.now = SPACING * (v - 1)
            if v == 4:
                self.stale = copy.deepcopy(self.mirrors[3])  # m3 is partitioned for v4 and keeps serving v3
                self.stale.name = "m3-lagging"
                self.pub.rotate_release_keys(self.now - 600, last_old_version=3)
            self.objects = self.pub.publish(v, self.now)
            for key, raw in self.objects.items():
                self.mirrors[0].put(key, raw)  # the publisher uploads to ONE mirror; anti-entropy does the rest
            self.ts = self.pub.timestamp(self.now)
            self.mirrors[0].put_timestamp(self.ts)
            self.rounds[v] = MR.gossip(self.mirrors, seed=v, down_until={"m3": 3} if v == 4 else None)

    @property
    def root(self) -> dict:
        return self.pub.roots[-1]["signed"]

    def client(self) -> CL.Client:
        c = CL.Client(self.pub.roots[0], check_freshness=self.inject != "no-freshness")
        c.update_root(self.pub.roots)  # root v1 shipped with the client, v2 fetched and chained
        return c
