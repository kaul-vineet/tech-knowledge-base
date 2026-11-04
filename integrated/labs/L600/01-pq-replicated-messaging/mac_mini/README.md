# 01 on the Mac mini — real crypto timings and real process failover

The lab proves nonce uniqueness across leader failover inside ONE Python process (a simulated Raft network, simulated
crashes). The Mac mini adds two things the sandbox cannot give you: **timings from Apple-silicon crypto** that turn the
rotation and per-key limits into numbers for your ADRs, and **three replicas as real OS processes** that are killed
with SIGKILL and restarted from their own disk, overnight, for 100,000+ messages.

Everything here also runs in the sandbox in a `--here` mode (small sizes). Nothing below is a Mac measurement: Mac
results are described as "what you should see", never as numbers.

| File | What it does |
|---|---|
| `bench_crypto.py` | X25519, ML-KEM-768/1024, HKDF, AES-256-GCM (64 B / 1 KiB / 64 KiB) and the lab's own `welcome` / `seal` → rotation budget and days to the 2^32 per-key cap |
| `replica.py` | one replica process: TCP on 127.0.0.1, append-only `log.jsonl` + `term.log` (fsync), `sealed.jsonl` = every envelope it ever put on the wire |
| `multiproc.py` | supervisor: starts 3 replicas, kills the leader at seeded points (half of them with a seal request in flight), elects the most up-to-date live replica in a higher term, restarts the dead one from disk, then re-runs F1/F2 on what the processes wrote |
| `ci.sh` | medium-size Mac runs for `.github/workflows/mac-mini.yml` (bench, 2,000 messages / 20 kills, failure lab must exit 1) |
| `_mac.py` | puts the lab on `sys.path`, loads `integrated/mac-mini/scripts/mac_profile.py` by path, JSONL output |
| `tests/test_mac_mini.py` | 7 tests: bench `--here`, log replay (truncate marker, torn last line after a kill), the three nonce sources across real processes, the track profile |

## Run
```bash
# macOS (zsh), from integrated/labs/L600/01-pq-replicated-messaging, in the venv of shared/WORKSTATION-SETUP.md
python mac_mini/bench_crypto.py --out ~/kb-runs/01-bench.jsonl
python mac_mini/multiproc.py --messages 2000 --kills 20                      # minutes
caffeinate -i python mac_mini/multiproc.py --messages 100000 --kills 400 --out ~/kb-runs/01-multiproc.jsonl   # overnight
python mac_mini/multiproc.py --here --nonce leader-counter                    # failure lab across processes: exit 1
python mac_mini/multiproc.py --here --nonce derived                           # build-task solution: exit 0
python -m unittest discover -s mac_mini/tests -t mac_mini/tests
```
Windows (PowerShell): the same `python` commands; `Popen.kill()` is `TerminateProcess` there (also an abrupt stop).

## Real output here (Linux sandbox, 2026-11-02 — sandbox numbers, NOT Mac numbers)
```
$ python mac_mini/multiproc.py --here
{"experiment": "01 multi-process failover", "nonce": "random", "messages": 300, "kills": 4, "kills_with_request_in_flight": 2, "failovers": 4, "restarts": 4, "acked": 300, "client_retries": 0, "fsync": true, ...}
{"fitness": "F1 no nonce reuse across real process failover", "ciphertexts_on_wire": 301, "reused_nonces": 0, "pass": true}
{"fitness": "F2 every acked message exactly once on every replica's disk", "acked": 300, "log_lengths": {"r1": 300, "r2": 300, "r3": 300}, "logs_identical": true, "duplicates_in_log": 0, "acked_missing": 0, "pass": true}
$ python mac_mini/multiproc.py --here --nonce leader-counter --no-fsync
{"fitness": "F1 no nonce reuse across real process failover", "ciphertexts_on_wire": 300, "reused_nonces": 62, "pass": false, "example_reused_nonce_hex": "000000000000000000000001"}
$ python mac_mini/multiproc.py --here --nonce derived --no-fsync
{"fitness": "F1 no nonce reuse across real process failover", "ciphertexts_on_wire": 302, "reused_nonces": 0, "pass": true}
$ python mac_mini/bench_crypto.py --here      (last line)
{"budget": "rotation + per-key", "rotate_ms_for_members": {"3": 0.5, "100": 16.56, "1000": 165.61, "10000": 1656.1}, "max_members_in_rotate_budget": 603, "rotate_budget_ms": 100.0, "seals_per_s_one_core": 41186, "days_to_2^32_at_that_rate": 1.2, ...}
```
`ciphertexts_on_wire` 301 for 300 messages: one request was in flight when its leader was killed; the old leader had
sealed it but not replicated it, the client retried with the same Idempotency-Key on the new leader, which sealed it
again under a fresh nonce. The uncommitted copy is still "on the wire" (it reached a follower's socket or the old
leader's disk), so the audit counts it — exactly the case a nonce scheme must survive.

## Experiments (what you should see on the Mac and how to read it)
1. **Crypto budget** (`bench_crypto.py`). Expect every `us_per_call` to be lower than the sandbox's; ML-KEM
   encapsulate/decapsulate in tens of µs, AES-GCM at 64 KiB in GB/s. Read the last line: if
   `max_members_in_rotate_budget` is below your largest group, a synchronous rotation in the request path breaks the
   100 ms budget (ADR change: rotate asynchronously or in batches). If `days_to_2^32_at_that_rate` is shorter than your
   planned rotation period, a timer-based rotation is unsafe under full load: keep F4's counter rule (409
   `rotation_required`). The sandbox already shows ~1 day at one saturated core.
2. **Real process failover** (`multiproc.py`). Expect F1 and F2 to pass for `random` and `derived` at any size, and
   `leader-counter` to fail F1 after the first failover (nonce `...01` sealed twice under the same epoch key). With
   fsync on, `msgs_per_s` is bounded by three fsyncs per message on APFS; compare with `--no-fsync` to see the cost of
   durability. A nonzero `acked_missing` would mean an acknowledged message was lost: a real bug, not noise.
3. **Latency and loss with containers (optional, Colima)**. Run the same experiment inside one Linux container and put
   `tc netem` on the container's loopback, so the 127.0.0.1 traffic between the three replicas is delayed and lossy:
   ```bash
   brew install colima docker            # or MacPorts: sudo port install colima  (Colima: MIT; docker CLI: Apache-2.0)
   colima start --cpu 4 --memory 4
   docker run --rm --cap-add NET_ADMIN -v "$PWD/../../../..":/kb -w /kb/integrated/labs/L600/01-pq-replicated-messaging \
     python:3.12-slim bash -c "apt-get update -qq && apt-get install -y -qq iproute2 && pip install -q numpy cryptography==50.0.2 \
     && tc qdisc add dev lo root netem delay 5ms 2ms loss 1% && python mac_mini/multiproc.py --messages 2000 --kills 20 --no-fsync"
   ```
   Without the docker CLI: `colima start --runtime containerd`, `colima nerdctl install`, then `nerdctl run` with the
   same flags (Colima README).
   Expect `client_retries` > 0 and a much lower `msgs_per_s`; F1/F2 must still pass — loss and delay may cost
   availability, never nonce uniqueness or acknowledged messages. `tc` needs `NET_ADMIN`, hence `--cap-add`.

## Overnight
`caffeinate -i python mac_mini/multiproc.py --messages 100000 --kills 400` (about 3 × 100,000 fsyncs plus 400
restarts). It reveals what the in-process lab cannot: a crash between `term.log` and the first seal of a new term, a
truncate marker replayed after a torn write, or a follower that was down for several failovers and needs a long log
repair. Pass = F1 and F2 pass. The nightly runner (`integrated/mac-mini/scripts/nightly.sh`) collects the JSONL.

## Limits (stated, not hidden)
The supervisor elects leaders (highest term + most up-to-date log, Raft's two rules that matter here); it is not a
full Raft (no heartbeats or timeouts between the processes — the in-process lab uses lesson 12's Raft for that). The
epoch secret is read from a file written by the supervisor; in `pqmsg.py` it arrives in a hybrid welcome.

Sources and verification notes: `integrated/research/mac-mini-evidence.md`, section 01.
