# Lab 17 – Strangler-fig decomposition: facade, branch by abstraction, parallel run, cut-over

The monolith's fine rule (`legacy_monolith.calculate_fine`) moves into its own **fines service**. Callers depend on a seam (`FinesPort`, **branch by abstraction**), a **strangler facade** routes each call (`legacy → shadow → canary → service`), and a **parallel run** returns the legacy answer while it compares the service's answer and logs every difference as a JSON line. `cutover_decision()` turns the measured **mismatch rate** into go/no-go. A **fitness function** fails the build if new code imports the legacy module. The shipped service has a seeded rounding bug; the parallel run finds it before any member is charged.

## Files
| File | Purpose |
|---|---|
| `strangler.py` | `FinesPort`, adapters, `ParallelRun`, `Facade`, `cutover_decision` (lesson code) |
| `legacy_monolith.py` / `monolith_reports.py` | The monolith's fine rule and an old caller (on the baseline) |
| `fines_service.py` | Extracted service, in-process or HTTP on 127.0.0.1; **seeded fault**: `round()` is half-to-even |
| `traffic.py` | 2,000 seeded fine requests (30 % students) |
| `fitness_legacy.py` + `legacy_callers.json` | Fitness function: no new legacy callers (ratchet) |
| `app.py` | Shadow over HTTP → cut-over decision → canary 10 % / 50 % |
| `failure_lab.py` | Big bang vs shadow, base vs solution |
| `adr/0001-strangle-fines-behind-a-facade.md` | Decision record |
| `test_strangler.py` | Parallel run, facade, criteria, HTTP, fitness |
| `test_build_task.py` / `solution/fines_service.py` | Build task check / solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L400/17-strangler-fig
python app.py                 # shadow mode over HTTP with the shipped (buggy) service
python failure_lab.py
python app.py --solution      # fixed service: cut-over, canary
python fitness_legacy.py      # exit 0 = no new legacy callers
python -m unittest -v
```

## Expected output (observed 2026-10-28, Python 3.12.15, Linux)
Counts and decisions are seeded and repeat exactly. The HTTP time varies with host load (3.0–26.6 s for 2,000 calls on this shared, network-mounted host).
```
$ python app.py
shadow : {'comparisons': 2000, 'mismatches': 108, 'candidate_errors': 0} in 26.6 s over HTTP
cutover: {'ready': False, 'mismatch_rate': 0.054, 'reasons': ['mismatch rate 5.40% > 0.10%']}
mismatch log: out/mismatches.jsonl (108 lines); first: {'days_late': 7, 'member_type': 'student', 'control': '0.63', 'candidate': '0.62'}
$ python app.py --solution
shadow : {'comparisons': 2000, 'mismatches': 0, 'candidate_errors': 0} in 15.5 s over HTTP
cutover: {'ready': True, 'mismatch_rate': 0.0, 'reasons': []}
canary 10%: routed {'legacy': 466, 'service': 34}
canary 50%: routed {'legacy': 255, 'service': 245}
service: all fine calls go to the extracted service; legacy fine code can be deleted next
$ head -2 out/mismatches.jsonl
{"candidate": "0.62", "control": "0.63", "days_late": 7, "member_type": "student"}
{"candidate": "0.12", "control": "0.13", "days_late": 3, "member_type": "student"}
$ python fitness_legacy.py
{"budget": "<= 2 known callers, no new ones", "gate": "no-new-legacy-callers", "ok": true, "value": {"callers": 2, "migrated": [], "new": []}}
```
Canary buckets are per member (a SHA-256 hash of the member id mod 100), so 10 % of *members*, not of requests: 34 of 500 requests here.

## failureLab: a rounding difference nobody wrote down
```
$ python failure_lab.py
base    : big-bang would charge 108 of 2000 wrong; shadow found 108 mismatches, members saw 0; cutover ready False ['mismatch rate 5.40% > 0.10%']
solution: big-bang would charge 0 of 2000 wrong; shadow found 0 mismatches, members saw 0; cutover ready True []
mismatching (type, days late), first 6: [('student', 3), ('student', 7), ('student', 11), ('student', 15), ('student', 19), ('student', 23)]
```
Students pay half of 0.25 per chargeable day, so every odd number of chargeable days ends in half a cent. The monolith rounds it up (0.125 → 0.13); Python's `round()` rounds half to even (0.12) for 1, 5, 9 … chargeable days.

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_cap_and_grace_days (test_build_task.ExtractedServiceTest.test_cap_and_grace_days) ... ok
test_half_cent_rounds_up_like_the_monolith (test_build_task.ExtractedServiceTest.test_half_cent_rounds_up_like_the_monolith) ... ok
test_parallel_run_allows_cutover (test_build_task.ExtractedServiceTest.test_parallel_run_allows_cutover) ... ok
test_criteria (test_strangler.CutoverTest.test_criteria) ... ok
test_canary_is_sticky_per_member (test_strangler.FacadeTest.test_canary_is_sticky_per_member) ... ok
test_over_http (test_strangler.FacadeTest.test_over_http) ... ok
test_symptom_base_service_mismatch_rate (test_strangler.FacadeTest.test_symptom_base_service_mismatch_rate) ... ok
test_no_new_legacy_callers (test_strangler.FitnessTest.test_no_new_legacy_callers) ... ok
test_planted_caller_fails (test_strangler.FitnessTest.test_planted_caller_fails) ... ok
test_candidate_error_never_reaches_the_member (test_strangler.ParallelRunTest.test_candidate_error_never_reaches_the_member) ... ok
test_mismatches_are_logged_as_json_lines (test_strangler.ParallelRunTest.test_mismatches_are_logged_as_json_lines) ... ok
test_returns_control_and_counts_mismatch (test_strangler.ParallelRunTest.test_returns_control_and_counts_mismatch) ... ok

----------------------------------------------------------------------
Ran 12 tests in 1.870s

OK
```

## Build task (the hardening change)
Make `fine_for()` in `fines_service.py` match the monolith exactly: `Decimal` arithmetic and `ROUND_HALF_UP`.
- Solution: `solution/fines_service.py`.
- Check (solution by default; YOUR file with `CHECK_MINE=1`):
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
Fail before / pass after (observed 2026-10-28):
```
$ CHECK_MINE=1 python -m unittest test_build_task      # unchanged fines_service.py
FAIL: test_half_cent_rounds_up_like_the_monolith
FAIL: test_parallel_run_allows_cutover
FAILED (failures=2)
$ python -m unittest test_build_task                   # solution
OK
```

## Try it (observed 2026-10-28)
```
$ python try_it.py
[1] new_feature.py imports the monolith -> {'gate': 'no-new-legacy-callers', 'ok': False, 'value': {'new': ['new_feature.py'], 'migrated': [], 'callers': 3}, 'budget': '<= 2 known callers, no new ones'}
[2] fixed service, 300 shadow requests -> {'ready': False, 'mismatch_rate': 0.0, 'reasons': ['only 300 comparisons (< 1000)']}
```

## Mac mini and Windows
Same commands inside the venv. The service binds 127.0.0.1 on a free port. Paths in the fitness report use `as_posix()`, so they read the same on both machines.

## Troubleshooting
| Symptom | Action |
|---|---|
| Mismatches on values that only differ in formatting ("2.0" vs "2.00") | Compare a cleaned value (both as `Decimal`), not raw strings, and log both. |
| Fitness gate fails after you migrated a caller | It reports `migrated`: remove that file from `legacy_callers.json` (the ratchet only shrinks). |
| `URLError` in `app.py` | Another process blocked the port: the service picks a free port each run; rerun. |
