# 03 on the Mac mini — real models behind the same gates, and simulations big enough to trust

In the sandbox the agent is a rule-following fake: it proposes `lam 0.97` because the brief says so and writes the
same naive summary every time. On the Mac mini the proposer becomes a real open-weight model (Ollama, Metal) and the
simulation gets all performance cores for a night. The pipeline, the contract, the budget and the claim checker are
unchanged — that is the point: **the model proposes, the code decides, whatever the model.**

Setup: `../../../../mac-mini/README.md` (profile, Ollama). `python3 ../../../../mac-mini/scripts/mac_profile.py`
tells you which 2–3 models fit (16/24 GB: `qwen2.5:3b, 7b, 14b`; 32/64 GB: `7b, 14b, 32b`).

| Script | `--here` (sandbox) | On the Mac |
|---|---|---|
| `compare_models.py` | fake model, one record | `--auto`: the profile's models; `--models a,b` |
| `overnight_sweep.py` | 48 runs + Sobol n ≤ 16, 2 workers | `coverage` 80,000 runs × 20,000 customers; `sobol --n 8192` |
| `export_rejections.py` | format check on the fake's 1 rejection | mlx-lm chat data from every model's rejections |
| `ci.sh` / `ci_ollama.sh` | — | medium sizes, run by `.github/workflows/mac-mini.yml` |

## Experiment 1 — three real models, one brief, the same gates
**Why.** The scorecard's M2 expects the agent to propose something the contract rejects; the fake always does. A real
model may refuse the out-of-envelope comparison itself, invent a field, loop until the call budget stops it, or
over-claim significance. Each of those must land on a gate, and the count per model is what you learn.
```zsh
cd integrated/labs/L600/03-agent-driven-simulation/mac_mini
ollama pull qwen2.5:3b && ollama pull qwen2.5:7b && ollama pull qwen2.5:14b   # or what mac_profile.py lists
export LOCAL_MODEL_URL=http://localhost:11434/v1
python3 compare_models.py --here          # the fake's row first: contract_rejected 1, budget_rejected 1, claims_dropped 1
python3 compare_models.py --auto          # one row per model -> ~/kb-runs/03-compare-models.jsonl
LOCAL_MODEL=qwen2.5:7b python3 ../run_project.py --real-model   # the full scorecard with one real model
```
**What you should see / how to read it.** One line per model with `contract_rejected`, `budget_rejected`,
`claims_dropped`, `budget_spent` of 300,000, `agent_calls` of 8, `stopped`. Read them as *where* each model's mistakes
were caught, not as a model ranking: `contract_rejected 0` with `claims_dropped 0` can mean a careful model **or** one
that skipped the risky comparison (check `proposals`). `published_traced` must equal `numbers_found` and
`budget_respected` must be `true` for every model — the script exits 1 otherwise, because that would be a gate failure,
not a model failure. `stopped: "agent budget: ..."` means the model never wrote a final answer within 8 calls.
`--real-model` may FAIL M2 (no contract rejection happened) — that is the known gap in `documentation/KNOWN-GAPS.md`,
now measured.
**Measure:** per model: contract_rejected, budget_rejected, claims_dropped / claims_total, budget_spent, agent_calls.
**Decides:** ADR-0001 (agent proposes, code decides) gets a "measured with real models" note. If any model needs all
8 calls, raise `MAX_CALLS` only with a reason; if every model avoids the out-of-envelope arm, M2 needs a second
seeded probe (a scripted bad proposal) instead of relying on the model to misbehave.

## Experiment 2 — does the 95 % CI really cover 95 % of the time? (overnight, all cores)
**Why.** M1 verifies the model with ONE 10-replication CI per utilisation. Whether a 95 % interval covers the M/M/1
formula 95 % of the time is a property of the procedure (warm-up, run length, replications), and only many independent
repetitions show it. At high utilisation the start-up transient biases each run's mean.
```zsh
python3 overnight_sweep.py --here                                   # 48 runs, 2 workers: format + determinism
caffeinate -i python3 overnight_sweep.py coverage --experiments 2000 --reps 10    # 4 x 2000 x 10 = 80,000 runs
python3 overnight_sweep.py coverage --experiments 300 --workers 1 --rhos 0.8      # same rows as with all cores
```
**What you should see / how to read it.** Per rho: `coverage`, `bias` (mean of means − formula) and `z_vs_95` = (coverage
− 0.95) / √(0.95·0.05/2000). |z| < 2 is consistent with 95 %. A coverage that falls as rho rises, with a positive
`bias`, is the initial transient: the runs start empty and short runs never forget it. `values_sha256_16` must be the
same for any `--workers` (seeds come from `(root, experiment, replication)`, not from the process).
**Measure:** coverage and bias at rho 0.5, 0.7, 0.8, 0.9.
**Decides:** `contract.RHO_MAX` (the verified envelope, now 0.9). If coverage at 0.9 is clearly below 0.95 (z < −3),
either lower RHO_MAX to the largest rho that passes or raise the warm-up/run length in M1 — record which in
ADR-0003, and re-run the scorecard.

## Experiment 3 — how big must a Sobol screening be before its ranking is real?
**Why.** The brief asks for `sobol 64`; the contract allows any size ≥ 2. With 1,000-customer runs the indices are
noisy and the ranking at small n can be an artefact. A large-n reference (8192 → 49,152 runs) settles it.
```zsh
caffeinate -i python3 overnight_sweep.py sobol --n 8192      # rows for n = 1024, 2048, 4096, 8192
```
**What you should see / how to read it.** One row per n with `ST` per input, `ranking` and `matches_reference`. The
first n from which every row says `true` is the smallest trustworthy size *for this model and these ranges*. In the
`--here` run (n = 2…16) the ranking flips between sizes — exactly the noise this experiment measures.
**Measure:** smallest n with a stable ranking; ST(lam) and ST(mu) at n = 8192.
**Decides:** the `run_screening` schema minimum for `sobol` (now 2) and the budget it implies (n × 6 × 1,000
customers must fit SIM_BUDGET = 300,000 → at most n = 50 today): either raise the minimum and the budget together,
or make the pipeline report "ranking not stable at this n" instead of a ranking.

## Optional — LoRA on the rejected proposals (MLX, MIT; documented experiment, not required)
`export_rejections.py` turns every proposal the **contract** refused into mlx-lm chat data (`train.jsonl`,
`valid.jsonl`): user = the proposal, assistant = `contract.validate`'s verdict recomputed now. Budget refusals are
skipped (they depend on what ran before, not on the proposal).
```zsh
python3 export_rejections.py --runs ~/kb-runs          # needs hundreds of examples: collect over many nights first
python3 -m pip install "mlx-lm[train]"                 # Apple silicon only
mlx_lm.lora --model Qwen/Qwen2.5-1.5B-Instruct --train --data ~/kb-runs/03-lora-data --iters 600
```
Read it as: does the adapted model *propose* fewer contract violations? Fuse the adapter (`mlx_lm.fuse --model ...`),
serve the result behind any OpenAI-compatible endpoint and re-run Experiment 1 with `--models`. It never removes a gate. With a few dozen examples the honest result is
"too little data" — the script says so.

## Overnight
`caffeinate -i python3 overnight_sweep.py both --experiments 2000 --n 8192` — 80,000 coverage runs of 20,000 customers
plus Sobol at four sizes, every performance core. It reveals the procedure's real coverage across the envelope and
the smallest trustworthy screening size; both feed the contract, not the agent. The `meta` row records workers,
seconds and the environment fingerprint; compare `values_sha256_16` with a second machine to test bit-for-bit
reproducibility across OSes (ADR-0002).

## Validation
Here (Linux, Python 3.12.15, numpy 2.5.3): `python -m unittest discover -s tests` (7 tests: fake-model comparison record,
unreachable server, model list from the profile, identical hashes for 1 vs 2 workers, coverage maths, export labels and
split). pendingMac: every real-model row, the 80,000-run coverage numbers, the n = 8192 Sobol reference, mlx-lm.
