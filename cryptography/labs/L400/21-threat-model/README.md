# 21 – Threat modelling cryptographic systems: STRIDE, attack trees and tests

Read first: `content/concepts/L400/21-threat-modelling.md`. Full lesson (steps, walkthrough, options, failure lab, trade-offs, sources): `content/L400.json` (lesson 21).

## Design brief
The topic now has envelopes + rotation (12, 17), token-based signing (14, 19), TLS and PQ key exchange (10, 18), group keys (20) and secret handling (16). A threat-model document written once would drift within weeks.

Constraints:
- every element has >= 1 threat; every boundary-crossing flow has T and I threats
- every threat has a control or an acceptance that names an ADR
- every control names tests that exist and pass (run in CI)
- an agent may propose threats but never change the model by itself

**Question:** How do we keep the threat model honest as the code changes?

**Decision:** `ADR-0021-threat-model-as-code.md` (Nygard ADR in this folder).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python threat_model.py
python agent_assist.py
python -m unittest -v
python try_it.py
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2 (OpenSSL 4.0.3 wheel), Linux sandbox)
`python threat_model.py`:
```
1) elements 11 (flows 5, crossing a boundary 4) | STRIDE-per-element candidates 41 | threats 18 | controls 12
2) checker problems: [] | controls whose tests exist: 12/12
3) cheapest open attack path: cost 9 via ['phish an authorised user']
--- fault: model drift (a test is deleted in a refactor; a SIEM export flow is added)
control C-NO-FALLBACK now points at a missing test: True | checker problems: [] | new flow app-log->siem threats: []
```

`python agent_assist.py`:
```
doc-api->envelope-db T (an attacker swaps a stored envelope for ) -> CONFIRMED - C-DUAL-SIG proven by TestPolicyDecidesSignatures::test_stripped_envelope_rejected_in_transition
app-log I (bearer tokens end up in the application ) -> CONFIRMED - C-REDACT proven by TestNoSecretsInLogs::test_seeded_request_mix_leaves_clean_logs
signer R (nobody can prove which operator signed a) -> GAP - valid threat with no control: triage it (not added automatically)
client->doc-api E (privilege escalation over the wire) -> REJECTED - E does not apply to a flow
blockchain-ledger T (the ledger is rewritten) -> REJECTED - unknown element
envelope-db I (database backups are readable by the bac) -> REJECTED - control C-QUANTUM-SHIELD does not exist
verdicts {'CONFIRMED': 2, 'GAP': 1, 'REJECTED': 3}; the model only proposes - the checker decides, and nothing is merged automatically.
```

Timings (µs/ms) are medians on the sandbox machine and differ on yours; sizes, counts and seeded results are exact. Keys, signatures and fingerprints are random per run.

Tests (`python -m unittest -v`, all test files in this folder):
```
Ran 14 tests in 182.982s
OK
```

## Options and evidence
| Option | Evidence (measured here) | Verdict |
|---|---|---|
| A: STRIDE per element | 1) elements 11 (flows 5, crossing a boundary 4) | STRIDE-per-element candidates 41 | threats 18 | controls 12 | Kept as the coverage backbone (rules in the checker). |
| B: attack tree over verified controls | 3) cheapest open attack path: cost 9 via ['phish an authorised user']; after the drift: cheapest open attack path with only VERIFIED controls: cost 8 via ['record traffic on path', 'client accepts classical-only share', 'wait for a quantum computer'] | Kept for prioritisation: shows which deleted test matters. |
| C: agent brainstorming | verdicts {'CONFIRMED': 2, 'GAP': 1, 'REJECTED': 3}; the model only proposes - the checker decides, and nothing is merged automatically. | Kept as an aid only; proposals never merge automatically. |

## Failure lab: break it, then fix it
**Fault (seeded):** inject_drift() with random.Random(21): the test behind C-NO-FALLBACK is 'deleted in a refactor' and an app-log -> siem flow (crossing to the internet zone) is added without threats.

**Symptom:** `control C-NO-FALLBACK now points at a missing test: True | checker problems: [] | new flow app-log->siem threats: []`

**Fix = build task:** Verified model checker: a control counts only if every test it names exists; every element has >= 1 threat; every boundary-crossing flow has T and I threats; verified_controls() returns only controls with existing tests (and run_control_tests() runs them).

Hints: Reuse test_exists() for every reference in model['controls'][cid]['tests']. · Collect covered STRIDE letters per element with a defaultdict(set).

Reference solution: `solution_verified.py` → `python solution_verified.py` prints:
```
clean model problems: [] | verified controls: 12 of 12
after drift:
  - C-NO-FALLBACK: test missing labs/L400/18-post-quantum/test_build_task.py::TestNoSilentFallback::test_removed_in_refactor
  - siem: no threats modelled
  - app-log->siem: no threats modelled
  - app-log->siem: boundary-crossing flow lacks T
  - app-log->siem: boundary-crossing flow lacks I
cheapest open attack path with only VERIFIED controls: cost 8 via ['record traffic on path', 'client accepts classical-only share', 'wait for a quantum computer']
```

**Proof** (`test_build_task.py`). Against the reference solution:
```
Ran 4 tests in 4.843s
OK
```

Against the shipped, unfixed lab file (observed — this is the "fails before"):
```
FAIL: test_deleted_test_is_reported (test_build_task.TestModelDriftIsCaught.test_deleted_test_is_reported)
FAIL: test_unmodelled_boundary_flow_is_reported (test_build_task.TestModelDriftIsCaught.test_unmodelled_boundary_flow_is_reported)
FAIL: test_unverified_control_does_not_close_the_attack_tree (test_build_task.TestModelDriftIsCaught.test_unverified_control_does_not_close_the_attack_tree)
Ran 4 tests in 0.065s
FAILED (failures=3)
```

Test **your** `threat_model.py` (the shipped file is the unfixed one):

macOS (zsh): `BUILD_TARGET=mine python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_TARGET`  
(`BUILD_IMPL=<module>` still works, as in L200/L300.)

## Fitness function
The checker finds 0 problems in model.json and every referenced control test passes when run (one unittest process per test file).  
Test: `test_fitness_threat_model.py` · Threshold: 0 checker problems; 12/12 control tests pass

## Scaling limits
- Model size: hundreds of elements make STRIDE-per-element candidates explode (41 for 11 elements here); signal = triage backlog of unjudged candidates - split the model per component with shared boundary flows.
- Test runtime: running every control test on each change gets slow (~100-180 s on the sandbox's slow file mount, ~6 s CPU); signal = fitness job time - run it in CI on model or control-test changes only.
- Agent noise: more proposals than reviewers; signal = GAP/REJECTED ratio rising - tighten the prompt or rate-limit proposals; never auto-merge.

## Try it (predict first)
1. Delete threat T3 ('request modified in transit') because 'TLS handles that'. What does the fixed checker say? *Predict:* It notices the boundary-crossing flow has no Tampering threat.
2. Point C-NONEXPORT at a missing test. Which attack path becomes cheapest? *Predict:* Stealing the key from the host.

```bash
python try_it.py
```
Observed locally:
```
1) without T3: ['client->doc-api: boundary-crossing flow lacks T']
2) C-NONEXPORT unverified -> cheapest path cost 6 via ['compromise the app host', 'read key bytes out of the token'] (was 9 via ['phish an authorised user'])
```

## Agent assist (fake model server by default; `--real` uses LOCAL_MODEL_URL / LOCAL_MODEL)
A local model proposes STRIDE threats for the model's elements; deterministic code classifies each proposal against the model and the existing tests.

Check: judge(): REJECTED if the element is unknown, the STRIDE letter does not apply to its type, or the control is invented/unverified; GAP if the threat is valid but has no control (triage, never auto-merged); CONFIRMED only if the control exists and its tests exist. The prompt carries no secrets and passes lesson 9's SECRET gate.

`python agent_assist.py` (observed):
```
doc-api->envelope-db T (an attacker swaps a stored envelope for ) -> CONFIRMED - C-DUAL-SIG proven by TestPolicyDecidesSignatures::test_stripped_envelope_rejected_in_transition
app-log I (bearer tokens end up in the application ) -> CONFIRMED - C-REDACT proven by TestNoSecretsInLogs::test_seeded_request_mix_leaves_clean_logs
signer R (nobody can prove which operator signed a) -> GAP - valid threat with no control: triage it (not added automatically)
client->doc-api E (privilege escalation over the wire) -> REJECTED - E does not apply to a flow
blockchain-ledger T (the ledger is rewritten) -> REJECTED - unknown element
envelope-db I (database backups are readable by the bac) -> REJECTED - control C-QUANTUM-SHIELD does not exist
verdicts {'CONFIRMED': 2, 'GAP': 1, 'REJECTED': 3}; the model only proposes - the checker decides, and nothing is merged automatically.
```

--real uses Ollama (default qwen2.5:1.5b; Metal on the Mac mini, CUDA/CPU on Windows); wording and proposals vary, verdicts still come from judge(). Not run in the sandbox (no model).

## Learning tool: Wireshark (pending a manual run)
Prove a control instead of trusting it: capture lesson 10's localhost TLS run (SSLKEYLOGFILE as in lesson 10) and confirm the client->doc-api flow (threats T2/T3) carries no readable application data without the key log.

Expected: Without the key log only TLS records are visible; with it Wireshark decrypts 'hello over TLS' - the evidence behind control C-MTLS / C-NO-FALLBACK for that flow. Compare with model.json's flow labels (step 2). Pending a manual run: the tool was not run in the sandbox; the value comes from the lab's printed output.

Install — macOS: brew install --cask wireshark-app (or the official universal .dmg) · Windows: Official x64/Arm64 installer from wireshark.org (bundles Npcap) · Licence: GPL-2.0 (OSI) · https://www.wireshark.org/download.html

## If it fails
| Symptom | Action |
|---|---|
| test_fitness_threat_model is slow | It runs 12 control tests in subprocesses; on a normal disk it takes seconds, on the sandbox mount minutes. |
| A control test fails in the fitness run | The control is broken: fix the code it protects (do not remove the mapping). |
| agent_assist refuses to send | Something secret-like reached the prompt; only element names and control ids belong there. |
