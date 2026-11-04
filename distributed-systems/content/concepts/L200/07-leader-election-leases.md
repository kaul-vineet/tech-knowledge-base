## Why it matters
A nightly billing job runs on three replicas but must run on exactly one. A hand-picked leader stops the job when its machine dies; three running copies bill customers three times.

## Mental model
A lease is a parking permit with an expiry time: the holder may act, must renew before it runs out, and permit numbers only go up.

```
t=0  n1 creates "leader" (TTL 3 s) -> token 1
t=2  n1's last renewal; t=3 n1 pauses
t=5  lease expired, n2 creates     -> token 4
t=7  n1 wakes, writes with token 1 -> REJECTED (1 < 4)
```

## How it works
1. **Acquire with compare-and-swap.** Create the key only if absent (`expect: 0`); one CAS wins, the rest get 409. → see lab step 1
2. **Renew well before the TTL** with CAS on your own revision; a failed renewal means step down. → see lab step 2
3. **Failover is the TTL.** Nobody detects the crash: the lease expires and the next candidate's CAS succeeds. → see lab step 2
4. **Fencing tokens stop zombies.** Revisions only grow, so each new holder gets a higher token; storage rejects tokens below the highest seen. A paused process cannot know its lease expired: the check must live in the resource. → see lab step 3
5. **Hand over early.** A clean shutdown deletes the key (CAS on its revision), so nobody waits for the TTL. → see lab step 5

Worked example (demo output): n1 last renews at t=2, so its lease ends at 2 + 3 = t=5; n2 takes over with token 4 (revisions 1-3 were n1's). n1's write at t=7 carries token 1: rejected.

## Trade-offs
| Use it when | Avoid it when |
|---|---|
| One worker must own a job or shard at a time | Every replica could safely do the work (make it idempotent) |
| The store has atomic CAS + TTL (etcd, ZooKeeper, a database row) | The protected resource cannot check a token |

Short TTL: faster failover, more false failovers. Long TTL: the reverse (tryIt 2).

## Common mistakes
- Checking "am I still leader?" before writing: the pause can follow the check.
- A random lock value as token; it must grow with every new holder.
- Renewing at the last moment instead of at a fraction of the TTL.
