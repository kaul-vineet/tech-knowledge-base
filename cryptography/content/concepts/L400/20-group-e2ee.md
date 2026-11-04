## Why it matters
End-to-end encryption means the relaying server cannot read messages. For two people the double ratchet solved this. For a 50-person room with weekly joins and leaves it gets hard: members agree on keys while some are offline, a removed member must stop reading at once, and a stolen phone must stop being useful after its owner's next update. MLS (RFC 9420, 2023) standardises a tree-based answer that scales from two to thousands of members. Its ideas (epochs, commits, fresh entropy, log-sized updates) are how you judge any group-encryption claim.

## Mental model
A **family tree of locks**. Every member sits at a leaf, and every parent node holds a key pair known only to the members below it. A change is a **Commit**: the committer creates fresh secrets along its path to the root and encrypts each one to the *other* half of the tree under that node, so about log₂(n) encryptions reach everyone. The root secret, mixed with the previous epoch's `init_secret`, gives the next **epoch secret**, from which message keys are derived.

```
              root            epoch_n+1 = KDF(init_n || commit_secret)
            /      \          app key   = KDF(epoch_n+1, "app")
         AB          CD       Remove(d): blank d AND its path, then commit
        /  \        /  \      → new secrets are encrypted only to keys d never knew
       a    b      c    d
```

## Design space
- **Pairwise fan-out.** Every message is encrypted once per recipient over pairwise channels. Removal is free (stop sending), but each message costs n−1 encryptions, and FS/PCS come from each pairwise ratchet.
- **Sender keys** (Signal groups, WhatsApp). Each member distributes a symmetric chain key once, and each message is one encryption with forward secrecy from a hash ratchet. After a removal, *every* remaining member must create and distribute a new sender key, which RFC 9420 notes scales with the square of the group size.
- **MLS-style tree.** One encryption per message, about log n per change, and forward secrecy plus post-compromise security through Commits. It needs ordered commits (a delivery service) and an authentication service for credentials.

## How to decide
Criteria: removal cost at your largest group, cost per message, immediate cut-off, recovery from compromise, and operational complexity.

Evidence from `compare_designs.py`, counting encryptions by the sender or committer (→ see lab step 3):

| Design | Per message (n=256) | Per removal n=8 / 64 / 256 | Bytes per removal (n=256) |
|---|---|---|---|
| Pairwise | 255 | 0 / 0 / 0 | 0 |
| Sender keys | 1 | 42 / 3,906 / 64,770 | ≈5.2 MB |
| Tree | 1 | 4 / 10 / 14 | 1,120 |

The tree removal at n=256 took about 90 ms in total in this Python toy, including all members processing.

Worked example from one lab run (→ see lab steps 1, 2 and 4). Eight members share epoch 0. Carol's update Commit costs 3 HPKE encryptions (log₂ 8), and all members agree on epoch 1. tryIt 1 shows post-compromise security: an attacker holding a copy of carol's state reads before her update (`True`) and not after it (`False`).

Then the fault. Frank removes dave, but the removed leaf's path is not blanked, so frank's fresh secret is encrypted to a parent key dave still knows: dave reads the post-removal message. Across all 56 (committer, removed) pairs the bug leaks in 48 (tryIt 2); only siblings are safe by accident. The fix blanks the whole direct path, as RFC 9420 §12.1.3 requires. The commit then costs 4 encryptions and dave reads nothing.

## Failure modes at scale
- **Forked epochs.** Two members commit at once and the group splits: decrypt failures cluster by epoch. Order commits per group in the delivery service.
- **Members who never update.** Post-compromise security only arrives when someone commits. RFC 9420 recommends regular updates and removing members who never update; track the age of each leaf's key.
- **Sender keys in big rooms**: removal storms grow quadratically (64,770 at n=256).
- **The toy is not MLS**: no signatures, credentials, tree hashes or Welcome. Use OpenMLS (pending CI).

## Common mistakes
- Rotating to a new epoch by ratcheting the old secret alone: a removed member can compute it. New epochs need fresh entropy that the removed member never receives.
- Forgetting to blank intermediate nodes on removal (the fault): the tests that check everyone stays in sync still pass.
- Assuming forward secrecy implies post-compromise security. FS protects the past; only a later update heals the future.
