"""Toy MLS-style group key (RFC 9420 ideas, NOT the MLS wire protocol): a ratchet tree of X25519 node keys,
epochs, and Commits that inject fresh entropy. A Commit encrypts new path secrets (HPKE) to the resolution of each
copath node - about log2(n) encryptions - so only current members can compute the next epoch secret."""
import os
import random

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, hpke
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

import tree_math as tm

SEED = 20  # seeds the injected fault (who is removed, who commits)
SUITE = hpke.Suite(hpke.KEM.X25519, hpke.KDF.HKDF_SHA256, hpke.AEAD.AES_128_GCM)


def kdf(secret: bytes, label: bytes) -> bytes:
    return HKDF(hashes.SHA256(), 32, salt=None, info=b"kb-l20 " + label).derive(secret)


def node_key(path_secret: bytes) -> x25519.X25519PrivateKey:
    return x25519.X25519PrivateKey.from_private_bytes(kdf(path_secret, b"node"))  # key pair derived from the path secret


class Member:
    def __init__(self, name: str):
        self.name, self.privs, self.epoch, self.epoch_secret, self.init_secret = name, {}, 0, None, None


class Group:
    def __init__(self, names: list):
        self.n = len(names)  # power of two in this toy (no tree growth)
        self.members = {name: Member(name) for name in names}
        self.index = {name: i for i, name in enumerate(names)}
        self.nodes, self.encryptions = {}, 0
        privs = {x: x25519.X25519PrivateKey.generate() for x in range(1, 2 * self.n)}  # creator builds the tree
        self.nodes = {x: k.public_key() for x, k in privs.items()}
        first, init = os.urandom(32), os.urandom(32)
        for name, m in self.members.items():  # "Welcome": each member learns keys on its own direct path only
            x = tm.leaf(self.n, self.index[name])
            m.privs = {y: privs[y] for y in [x] + tm.direct_path(x)}
            m.epoch_secret, m.init_secret = first, init

    def _remove(self, name: str):
        self.nodes[tm.leaf(self.n, self.index.pop(name))] = None
        # BUG on purpose: RFC 9420 12.1.3 also blanks the removed leaf's direct path; here those parent keys stay

    def commit(self, committer: str, remove: str = None):
        if remove:
            self._remove(remove)
        c, x = self.members[committer], tm.leaf(self.n, self.index[committer])
        ps = os.urandom(32)  # fresh entropy: the heart of post-compromise security
        c.privs[x] = node_key(ps)
        self.nodes[x] = c.privs[x].public_key()
        sent = []
        for parent, sibling in zip(tm.direct_path(x), tm.copath(x)):
            ps = kdf(ps, b"path")
            c.privs[parent] = node_key(ps)
            self.nodes[parent] = c.privs[parent].public_key()
            for target in tm.resolution(self.nodes, sibling, self.n):  # everyone under the sibling, as few keys as possible
                sent.append((parent, target, SUITE.encrypt(ps, self.nodes[target], info=b"kb-l20 path")))
                self.encryptions += 1
        receivers = [m for name, m in self.members.items() if name != committer]
        for m in receivers:  # removed members try too: they keep whatever keys they had
            self._process(m, sent, x)
        self._advance(c, kdf(ps, b"commit"))
        return len(sent)

    def _process(self, m: Member, sent: list, committer_leaf: int):
        for parent, target, ct in sent:
            if target in m.privs:
                try:
                    ps = SUITE.decrypt(ct, m.privs[target], info=b"kb-l20 path")
                except InvalidTag:  # a stale key for a node that has since been re-keyed
                    continue
                for node in tm.direct_path(committer_leaf)[tm.direct_path(committer_leaf).index(parent):]:
                    m.privs[node] = node_key(ps)
                    last, ps = ps, kdf(ps, b"path")
                return self._advance(m, kdf(last, b"commit"))

    @staticmethod
    def _advance(m: Member, commit_secret: bytes):
        m.epoch_secret = kdf(m.init_secret + commit_secret, b"epoch")  # new epoch = old init secret + fresh commit
        m.init_secret, m.epoch = kdf(m.epoch_secret, b"init"), m.epoch + 1

    def send(self, sender: str, text: str) -> dict:
        m, n = self.members[sender], os.urandom(12)
        return {"epoch": m.epoch, "n": n, "ct": AESGCM(kdf(m.epoch_secret, b"app")).encrypt(n, text.encode(), b"%d" % m.epoch)}

    def read(self, reader: str, msg: dict):
        m = self.members[reader]
        if m.epoch != msg["epoch"]:
            return None
        try:
            return AESGCM(kdf(m.epoch_secret, b"app")).decrypt(msg["n"], msg["ct"], b"%d" % m.epoch).decode()
        except Exception:
            return None


if __name__ == "__main__":
    rng = random.Random(SEED)
    names = ["alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi"]
    g = Group(names)
    print("1) group of", g.n, "| epoch", g.members["alice"].epoch, "| alice -> all:", g.read("heidi", g.send("alice", "kick-off at 10")))
    sent = g.commit("carol")  # an empty Commit = key update (post-compromise security for carol's old keys)
    print("2) carol updates her path: HPKE encryptions:", sent, "| epoch", g.members["bob"].epoch, "| all in sync:",
          len({m.epoch_secret for m in g.members.values()}) == 1)
    removed, committer = rng.choice(names[1:4]), rng.choice(names[4:])
    print(f"--- fault: {committer} removes {removed}; the removed leaf's parent keys are not blanked")
    sent = g.commit(committer, remove=removed)
    msg = g.send(committer, "new launch date: 1 March")
    readers = {name: g.read(name, msg) is not None for name in names}
    print(f"commit HPKE encryptions: {sent} | epoch {g.members[committer].epoch} | can read post-removal message:", readers)
