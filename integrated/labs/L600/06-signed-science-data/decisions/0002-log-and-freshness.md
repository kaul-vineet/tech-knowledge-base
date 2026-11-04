# 2. Untrusted mirrors: freshness from a short-lived signed timestamp, history from a transparency log

## Status
Accepted (2026-10-30)

## Context
Mirrors are run by other institutes and lag by design (anti-entropy every 60 s; m3 is partitioned for 3 rounds while
v4 spreads). A signature alone proves "the publisher signed this once", not "this is the newest" or "everyone sees the
same history". TUF names the attacks: rollback ("installing software that is older than that which the client
previously knew to be available") and indefinite freeze ("the same, outdated metadata without the client being
aware"). RFC 9162 adds append-only logs with inclusion and consistency proofs.

Options:
- A, signatures only: the lagging mirror's v3 and a frozen mirror both verify (`--inject no-freshness`: S3 and F3 fail,
  `lagging: ACCEPTED`).
- B, TUF-style timestamp (version + expiry, TTL 3600 s, online key) and a client that remembers the highest release
  and timestamp version it has seen.
- C, B plus a transparency log: every release.json hash is an entry; the client checks the signed tree head,
  an inclusion proof for the release and a consistency proof from the last tree head it saw.

## Decision
C. Order in the client: fixed start time, root chain (TUF 5.3), timestamp signature, expiry (freeze), version
monotonicity (rollback), release hash from the timestamp, release signatures, files, Merkle root, licence, log proofs.
On a refusal the client tries the next mirror; a bad mirror delays but cannot block or downgrade.

## Consequences
- Measured: the lagging mirror is refused (`offers v3, client has seen v4 (rollback)`), a frozen one is refused after
  6000 s (`timestamp expired`); F3 rejects replays of v1-v3; failover returns v4 from m1.
- TTL couples security to replication: TTL must exceed re-sign interval + worst replication lag + clock skew. With
  TTL 120 s and timestamps signed only at publish, every mirror is refused 300 s later (tryIt 2) - a self-inflicted
  freeze. F2 (convergence <= 4 rounds = 240 s) is therefore also a security budget.
- A first-time client has no "highest seen": it relies on expiry only. A single log can still show different views to
  different clients; detecting that needs witnesses/monitors (RFC 9162 11.3), not built here.
- Clients need a trustworthy clock; TUF 7.1 lists bogus clocks as an open problem.
