# L600 #01 - Post-quantum secure messaging over a replicated log

**Combines:** cryptography · distributed-systems · application-architecture

A small group-messaging service. Each epoch secret reaches the members in a **hybrid X25519+ML-KEM-768 welcome**
(cryptography L400 #18). Messages are sealed under that key with AES-256-GCM, inside a **versioned envelope** (L400 #17).
The API takes **Idempotency-Keys** (distributed-systems L100 #5) and writes to a **transactional outbox**
(application-architecture L200 #9). A relay proposes each row onto a **3-node Raft log** (distributed-systems L300 #12,
in-process network, seeded crashes). A deterministic state machine on every replica dedupes, enforces epochs and gates
envelope versions. Replicas only store and order ciphertext.

Everything runs locally with Python 3.12 and `cryptography` 50.0.2. Nothing is installed and there is no network.

## Files
| File | Purpose |
|---|---|
| `pqmsg.py` | **Main file**: `Service` = API (`post`), sealer, outbox + relay, Raft driver, rotation, replay |
| `replicated_state.py` | `State.apply`: the deterministic replicated state machine (dedupe, epoch check, version gate) |
| `group_crypto.py` | Key packages, hybrid welcomes, `seal` / `open_msg`, keyed fingerprint, reader contract |
| `harness.py` | `FastCluster` (lesson 12's cluster without the per-tick full scan), retrying client `send`, `nonce_reuse` audit |
| `_kb.py` | Loads the reused labs by path. Never edits or copies them; same-name modules do not clash |
| `nonce_derived.py` | **Build task (shipped faulty)**: leader-local counter nonce = the failure lab |
| `solution/nonce_derived.py` | Reference: term (4 B) ‖ per-term counter (8 B) |
| `scenarios.py` | Seeded milestones, seams and fitness functions (shared by the scorecard and the tests) |
| `run_project.py` | Scorecard: JSON lines, exit 1 on any failure; `--inject <fault>` reproduces a seam failure |
| `tests/` | 24 unittest tests (milestones, seams, failure lab, fitness, build task, end to end) |
| `try_it/` | tryIt 1 (AES-GCM vs AES-GCM-SIV under nonce reuse), tryIt 2 (rotation cost vs group size) |
| `decisions/` | 4 ADRs (Nygard format) |
| `architecture.mmd` | Mermaid diagram |

Reused (imported, never edited): `cryptography/labs/L400/18-post-quantum` (pq_hybrid, solution_strict),
`L400/17-crypto-agility` (registry, agile_envelope), `L400/20-group-e2ee` (group_keys.kdf), `L300/15-testable-misuse`
(nonce_guard.scan_for_reuse), `L500/24-probability` (prob_tools); `distributed-systems/labs/L300/12-raft-replicated-log`
(solution_raft, helpers), `L100/05-idempotency-keys` (KEY_RE); `application-architecture/labs/L200/09-event-driven-integration`
(outbox.SCHEMA, Relay), `L300/14-consumer-driven-contracts` (like, _example).

## Run
```bash
# macOS (zsh)                                   # Windows (PowerShell): same commands, with py -3.12 / $env:PYTHONUTF8="1"
cd integrated/labs/L600/01-pq-replicated-messaging
python run_project.py                           # all lines PASS, exit 0 (about 1-3 minutes; the 10k-message run dominates)
python run_project.py --inject leader-counter   # the failure lab: exit 1
python -m unittest discover -s tests -t tests   # 24 tests
python try_it/try_it_1.py; python try_it/try_it_2.py
```
`--messages N` shortens the F1/F2 traffic run (the tests use 300 for the end-to-end check).

## Real output (2026-10-30, Linux, Python 3.12, cryptography 50.0.2)
```
$ python run_project.py
{"milestone": "M1 hybrid X25519MLKEM768 welcomes", "members_with_same_epoch_secret": 3, "distinct_secrets": 1, "key_package_B": 1216, "welcome_B": 1180, "epoch_entry_json_B": 6577, "downgraded_32B_share": "refused (HandshakeError)", "pass": true}
{"milestone": "M2 sealed envelopes on a 3-node Raft log", "messages": 30, "leader_crashed": "n1", "committed_per_replica": [31, 31, 31], "committed_logs_identical": true, "plaintext_in_any_log": 0, "safety_violations": 0, "alice_reads_per_replica": {"n1": 30, "n2": 30, "n3": 30}, "pass": true}
{"milestone": "M3 Idempotency-Key + transactional outbox", "status_codes": {"no key": 400, "first": 201, "retry": 200, "same key, new text": 422}, "crash_after_outbox_write": 503, "client_retry": 201, "sealed_ciphertexts_for_key": 2, "messages_shown_for_key": 1, "pass": true}
{"milestone": "M4 key rotation vs log replay", "epochs": 2, "late_epoch1_post": 503, "stale_epoch_rejected": 1, "carol_send_after_removal": 409, "replay_from_index_1": {"alice": "20/20", "bob": "20/20", "carol": "10/20"}, "carol_reads_after_removal": 0, "replicas_agree": true, "pass": true}
{"milestone": "M5 versioned envelope contract + crypto agility", "v2_contract_problems": [], "renamed_field_problems": ["missing n"], "v3_before_gate": 409, "v3_after_gate": 201, "v3_aead": "C20P1305", "readable_per_replica": {"n1": 4, "n2": 4, "n3": 4}, "unknown_version_9": "refused (EnvelopeError)", "pass": true}
{"seam": "crypto <-> distributed: nonce uniqueness vs leader failover", "messages": 1500, "failovers": 49, "reused_nonces": 0, "guard_proven_leader_counter_reuses": 109, "pass": true}
{"seam": "crypto <-> distributed: key rotation vs log replay", "stale_epoch_rejected": 1, "carol_reads_after_removal": 0, "guard_proven_accept_stale_epoch_carol_reads": 1, "pass": true}
{"seam": "application-architecture <-> distributed: idempotent retries vs duplicate ciphertexts", "messages": 300, "ciphertexts_sealed": 316, "duplicates_shown": 0, "every_acked_shown_once": true, "guard_proven_no_apply_dedupe_duplicates": 32, "pass": true}
{"seam": "application-architecture <-> crypto: envelope contract versioning across replicas", "readable_per_replica": {"n1": 4, "n2": 4, "n3": 4}, "guard_proven_local_config_readable": {"n1": 3, "n2": 5, "n3": 3}, "pass": true}
{"fitness": "F1 no nonce reuse across 10k messages with random failovers", "messages": 10000, "failovers": 205, "ciphertexts_sealed": 10101, "reused_nonces": 0, "birthday_bound_per_epoch": "4.0e-23", "pass": true}
{"fitness": "F2 all replicas decrypt identical plaintexts", "replicas": 3, "identical": true, "shown": 10000, "acked": 10000, "match_acked": true, "safety_violations": 0, "pass": true}
{"fitness": "F3 handshake size budget", "key_package_B": 1216, "welcome_B": 1180, "total_B": 2396, "budget": "welcome <= 1200 B, key package + welcome <= 2400 B", "pass": true}
{"fitness": "F4 rotate before the random-nonce limit (2^32 messages per epoch key)", "limit_in_test": 5, "codes": [201, 201, 201, 201, 201, 409], "after_rotation": 201, "pass": true}
{"scorecard": "L600-01 pq-replicated-messaging", "injected": null, "passed": 13, "total": 13, "decided_by": "code"}
```

## Failure lab: nonce reuse after leader failover
```
$ python run_project.py --inject leader-counter --messages 2000     (abridged: the lines that change)
{"seam": "crypto <-> distributed: nonce uniqueness vs leader failover", "messages": 1500, "failovers": 49, "reused_nonces": 109, "guard_proven_leader_counter_reuses": 109, "pass": false}
{"fitness": "F1 no nonce reuse across 10k messages with random failovers", "messages": 2000, "failovers": 43, "ciphertexts_sealed": 2022, "reused_nonces": 96, "birthday_bound_per_epoch": "1.6e-24", "pass": false}
{"failure_lab": "leader-counter", "messages": 1500, "failovers": 49, "reused_nonces": 109, "smallest_reused_nonce_values": [1, 2, 3, 4, 5], "keystream_reuse": {"nonce": "AAAAAAAAAAAAAAAB", "known_plaintext": "msg 00000 from alice: status green", "recovered": "msg 00010 from bob: status green", "actual": "msg 00010 from bob: status green"}}
{"scorecard": "L600-01 pq-replicated-messaging", "injected": "leader-counter", "passed": 11, "total": 13, "decided_by": "code"}
```
- **Inject:** the sealer's nonce is a counter in the leader's memory (`nonce_derived.py`). It is not replicated and
  ignores the Raft term.
- **Symptom:** lesson 15's offline scan finds 109 reused (epoch, nonce) pairs after 49 failovers. A known plaintext
  ("msg 00000 from alice ...") XORed with the two ciphertexts reveals bob's message.
- **Diagnose:** the reused nonce values are 1, 2, 3, ...: every new leader restarted the counter under the SAME epoch key.
- **Fix:** random 96-bit nonces (`RandomNonce`, ADR-01-1, the default) or term ‖ counter (`solution/nonce_derived.py`).
- **Test:** `tests/test_p01_failure_lab.py`; `tests/test_p01_build_task.py` fails on the shipped file and passes on the solution.

Other seeded faults (`--inject`): `no-apply-dedupe`, `accept-stale-epoch` and `local-contract-config` each break
their seam line.

## Build task
Make `nonce_derived.py` safe across failovers. It must use 12 bytes, never repeat a nonce across leaders or restarts
under one epoch key, and refuse a term that goes backwards. Keep `next(term)` as the interface.
```
macOS    BUILD_TARGET=mine python -m unittest -v test_p01_build_task      (run inside tests/)
Windows  $env:BUILD_TARGET="mine"; python -m unittest -v test_p01_build_task; Remove-Item Env:BUILD_TARGET
```
Observed: shipped file `Ran 5 tests in 1.594s | FAILED (failures=4)`; reference solution `OK`.

## Tests
```
$ python -m unittest discover -s tests -t tests
........................
Ran 24 tests in 246.586s
OK
```
(Wall time on the shared sandbox, where CPU time was 13 s. The 10k-message fitness test and the two end-to-end runs dominate. There are no wall-clock assertions.)

## tryIt
```
$ python try_it/try_it_1.py
AES-256-GCM      recovered == secret: True | repeat of the same message is identical: True
AES-256-GCM-SIV  recovered == secret: False | repeat of the same message is identical: True
$ python try_it/try_it_2.py
   3 members: welcomes 4,720 B raw, log entry 6,563 B JSON, x3 replicas
  30 members: welcomes 36,580 B raw, log entry 50,559 B JSON, x3 replicas
 100 members: welcomes 119,180 B raw, log entry 164,659 B JSON, x3 replicas
random 96-bit nonces: collision risk 2^-32 after 6.074e+09 messages per epoch key (NIST SP 800-38D caps random-IV use at 2^32 = 4,294,967,296)
```

## Simulator vs real
- The Raft cluster is lesson 12's in-process simulation: no disk, no snapshots, no membership change, ticks instead
  of time. Crashes are seeded. A restart rebuilds the state machine by replaying the log.
- The sealer runs on the service side as an "encryption gateway" identity with its own key package. In a pure E2EE app
  the sender's device seals. The nonce lesson transfers directly: two devices of one sender sharing a key with
  independent counters is the same bug.
- The welcome is a teaching construction modelled on lesson 18's hybrid exchange. Production would use HPKE with a
  PQ/T KEM or MLS (RFC 9420).
