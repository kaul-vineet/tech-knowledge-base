# 20 – End-to-end encryption for groups: pairwise, sender keys and MLS-style epochs

Read first: `content/concepts/L400/20-group-e2ee.md`. Full lesson (steps, walkthrough, options, failure lab, trade-offs, sources): `content/L400.json` (lesson 20).

## Design brief
Project rooms of 8-256 members; people join and leave weekly; the relay server must not read messages; phones get lost.

Constraints:
- a removed member reads nothing sent after removal
- a member who updates after a compromise locks the attacker out (PCS)
- removal at n=256 costs <= 2*log2(n) public-key encryptions
- 1 encryption per application message

**Question:** Which group-key design meets removal and recovery requirements at 256 members?

**Decision:** `ADR-0020-group-key-design.md` (Nygard ADR in this folder).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python group_keys.py
python compare_designs.py
python -m unittest -v
python try_it.py
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2 (OpenSSL 4.0.3 wheel), Linux sandbox)
`python group_keys.py`:
```
1) group of 8 | epoch 0 | alice -> all: kick-off at 10
2) carol updates her path: HPKE encryptions: 3 | epoch 1 | all in sync: True
--- fault: frank removes dave; the removed leaf's parent keys are not blanked
commit HPKE encryptions: 3 | epoch 2 | can read post-removal message: {'alice': True, 'bob': True, 'carol': True, 'dave': True, 'erin': True, 'frank': True, 'grace': True, 'heidi': True}
```

`python compare_designs.py`:
```
{"design": "pairwise", "n": 8, "encryptions_per_message": 7, "encryptions_per_removal": 0, "bytes_per_removal": 0, "real_crypto": true}
{"design": "sender keys", "n": 8, "encryptions_per_message": 1, "encryptions_per_removal": 42, "bytes_per_removal": 3360, "real_crypto": true}
{"design": "MLS-style tree (toy)", "n": 8, "encryptions_per_message": 1, "encryptions_per_removal": 4, "bytes_per_removal": 320, "removed_can_read": false, "commit_and_process_ms": 1.7, "real_crypto": true}
{"design": "pairwise", "n": 64, "encryptions_per_message": 63, "encryptions_per_removal": 0, "bytes_per_removal": 0, "real_crypto": true}
{"design": "sender keys", "n": 64, "encryptions_per_message": 1, "encryptions_per_removal": 3906, "bytes_per_removal": 312480, "real_crypto": true}
{"design": "MLS-style tree (toy)", "n": 64, "encryptions_per_message": 1, "encryptions_per_removal": 10, "bytes_per_removal": 800, "removed_can_read": false, "commit_and_process_ms": 71.8, "real_crypto": true}
{"design": "pairwise", "n": 256, "encryptions_per_message": 255, "encryptions_per_removal": 0, "bytes_per_removal": 0, "real_crypto": false}
{"design": "sender keys", "n": 256, "encryptions_per_message": 1, "encryptions_per_removal": 64770, "bytes_per_removal": 5181600, "real_crypto": false}
{"design": "MLS-style tree (toy)", "n": 256, "encryptions_per_message": 1, "encryptions_per_removal": 14, "bytes_per_removal": 1120, "removed_can_read": false, "commit_and_process_ms": 89.5, "real_crypto": true}
```

Timings (µs/ms) are medians on the sandbox machine and differ on yours; sizes, counts and seeded results are exact. Keys, signatures and fingerprints are random per run.

Tests (`python -m unittest -v`, all test files in this folder):
```
Ran 9 tests in 3.823s
OK
```

## Options and evidence
| Option | Evidence (measured here) | Verdict |
|---|---|---|
| A: pairwise fan-out | per message: 255 encryptions at n=256; removal: 0. | Rejected for big rooms: per-message cost grows with n (fine below ~5 members). |
| B: sender keys | removal: 42 / 3,906 / 64,770 encryptions at n=8/64/256 (5,181,600 B at 256). | Rejected: removal and PCS scale quadratically (RFC 9420 introduction). |
| C: MLS-style tree with epochs | removal: 4 / 10 / 14 encryptions (1,120 B at 256); removed member can read: False. | Chosen (ADR-0020); production via a reviewed RFC 9420 implementation. |

## Failure lab: break it, then fix it
**Fault (seeded):** frank removes dave (both chosen by random.Random(20)); _remove blanks only dave's leaf, not its direct path.

**Symptom:** `commit HPKE encryptions: 3 | epoch 2 | can read post-removal message: {'alice': True, 'bob': True, 'carol': True, 'dave': True, 'erin': True, 'frank': True, 'grace': True, 'heidi': True}`

**Fix = build task:** Removal that excludes: blank the removed leaf and every node on its direct path before the Commit, so the fresh path secrets are encrypted only to keys the removed member never knew.

Hints: tree_math.direct_path(leaf) gives the parents up to the root. · Blank nodes make resolution() descend to the children, i.e. to keys of members who stay.

Reference solution: `solution_remove.py` → `python solution_remove.py` prints:
```
frank removes dave: commit HPKE encryptions 4 | can read post-removal message: {'alice': True, 'bob': True, 'carol': True, 'dave': False, 'erin': True, 'frank': True, 'grace': True, 'heidi': True}
```

**Proof** (`test_build_task.py`). Against the reference solution:
```
Ran 2 tests in 0.742s
OK
```

Against the shipped, unfixed lab file (observed — this is the "fails before"):
```
FAIL: test_every_committer_removed_pair (test_build_task.TestRemovalExcludes.test_every_committer_removed_pair)
FAIL: test_seeded_removal_from_the_lab (test_build_task.TestRemovalExcludes.test_seeded_removal_from_the_lab)
Ran 2 tests in 0.337s
FAILED (failures=2)
```

Test **your** `group_keys.py` (the shipped file is the unfixed one):

macOS (zsh): `BUILD_TARGET=mine python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_TARGET`  
(`BUILD_IMPL=<module>` still works, as in L200/L300.)

## Fitness function
Seeded random sequence of removals and updates in a 16-member group: after every change exactly the current members read the new epoch, and no commit exceeds the log budget.  
Test: `test_fitness_removal.py` · Threshold: 0 leaks to removed members; commit cost <= 2*log2(16) = 8 HPKE encryptions

## Scaling limits
- Concurrent commits: two committers in one epoch fork the group; signal = decrypt failures clustered by epoch - the delivery service must order commits per group.
- Very large groups (thousands): tree blanks from many removals push commit cost towards O(n); signal = commit size growing over time - re-key the whole path with periodic full updates.
- Idle members: PCS only arrives when members update; signal = age of each leaf key - require updates on a schedule and remove members who never update (RFC 9420 3.2).

## Try it (predict first)
1. Copy carol's whole key state (the attacker), then let carol send an update Commit. Can the attacker read before / after? *Predict:* Before yes, after no.
2. With the UNFIXED remove, try all 56 (committer, removed) pairs in a group of 8. In how many does the removed member still read? *Predict:* Most of them.

```bash
python try_it.py
```
Observed locally:
```
1) attacker with carol's stolen state reads: before update True, after carol's update False
2) unfixed remove leaks in 48 of 56 pairs; safe only when the committer is the removed member's sibling: [('alice', 'bob'), ('bob', 'alice'), ('carol', 'dave'), ('dave', 'carol')] ...
```

## Equivalents (pending CI)
OpenMLS (Rust, MIT) implements RFC 9420: remove_members(...) returns a Commit; the removed member's group becomes inactive after merge_staged_commit. CI clones openmls and runs its remove-related tests.

macOS (zsh):
```zsh
brew install rustup && export PATH="$(brew --prefix rustup)/bin:$PATH" && rustup default stable
git clone --depth 1 https://github.com/openmls/openmls && cd openmls && cargo test -p openmls remove
```
Windows (PowerShell):
```powershell
winget install -e --id Rustlang.Rustup
git clone --depth 1 https://github.com/openmls/openmls; cd openmls; cargo test -p openmls remove
```

## Learning tool: CyberChef (pending a manual run)
Run `python tool_check.py`. In CyberChef use Derive HKDF key (or HKDF): hash SHA256, salt empty, info 'kb-l20 epoch', length 32, input = the printed IKM hex (init_secret || commit_secret).

Expected: Should match the lab's printed value: 1c797e51158e809b97b7aa54052e0aaf0b78d2067ce913dfbde8183b9ae38781 (expected epoch secret). If your CyberChef build lacks an HKDF operation, note it - the catalog lists 'Derive HKDF key' but its exact parameters were not checked. Demo values only. Pending a manual run: the tool was not run in the sandbox; the value comes from the lab's printed output.

Install — macOS: Open the CyberChef web app linked from github.com/gchq/CyberChef, or the offline release zip from https://github.com/gchq/CyberChef/releases (runs fully client-side); Docker ghcr.io/gchq/cyberchef · Windows: Same: web app or the offline release zip from https://github.com/gchq/CyberChef/releases (runs fully client-side) · Licence: Apache-2.0 (OSI) · https://github.com/gchq/CyberChef

`python tool_check.py` (fixed demo values for the tool check):
```
IKM (hex):       11111111111111111111111111111111111111111111111111111111111111112222222222222222222222222222222222222222222222222222222222222222
Salt:            (empty)
Info (UTF8):     kb-l20 epoch
Hash / length:   SHA256 / 32 bytes
expected (hex):  1c797e51158e809b97b7aa54052e0aaf0b78d2067ce913dfbde8183b9ae38781
app key (info 'kb-l20 app' over that epoch secret): c0348d2c0afd21c955b5fc40fbcd5b32cea268401abdbe3cc5e210a170f85acf
```

## If it fails
| Symptom | Action |
|---|---|
| InvalidTag while processing a commit | A member tried a stale key for a re-keyed node; _process skips it. If it happens for a current member, the tree views diverged. |
| Members end in different epochs | Two commits were applied in different orders - commits must be totally ordered per group. |
