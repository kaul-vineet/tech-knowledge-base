**Concept: evaluating agents with a golden set – a regression gate for prompts**

## Why it matters
A prompt is code that nobody compiles. Someone "tidies" the instructions, three hand-picked examples still look fine, the change merges – and two categories of real tickets quietly go to the wrong queue. Unit tests miss it: the code did not change, the model's behaviour did. A golden set turns "it looks fine" into a number, and a gate turns the number into a blocked merge.

## Mental model
A golden set is a frozen exam: fixed questions, fixed marking scheme, the same marker every time. A change may only ship if it scores at least as well as the version it replaces – overall and on every question it used to get right.

```
prompt v2 ─► run 20 golden cases ─► checks per case ─► report (pass rate, per-case results)
                                     structural · exact · rubric        │
baseline.json (last good run) ──────────────────────────────────► gate: rate ≥ bar AND no regressions ─► exit 0 / 1
```

## How it works
1. **Cases are data.** `golden.jsonl` holds 20 tickets, each with labelled `expect` fields and a rubric hint. Coverage of every category beats volume. → see lab step 2
2. **Three kinds of check.** *Structural*: valid JSON, exactly the agreed keys, values from the allowed set. *Exact*: category and priority equal the label. *Rubric*: a scored checklist (summary ≤ 12 words, mentions the key term, no apology) that passes at 2 of 3 points – partial credit without a judge model. → see lab step 4
3. **Baseline, then compare.** `--write-baseline` stores the last accepted run. The gate blocks if the pass rate falls below 95 % *or* any case that passed before now fails. → see lab step 2
4. **Worked example.** v1 scores 20/20. The "cleanup" v2 drops `account` from the category list: a three-case spot check still scores 3/3, but the full set gives 18/20 (90 %) and the gate prints `regressions vs baseline: ['t07', 't15']`, exit code 1. → see lab step 3
5. **Run it in CI.** The gate is an ordinary script with an exit code, so a workflow step fails the build. promptfoo expresses the same cases as YAML/JSONL assertions and exits 100 when a test fails. → see lab step 6
6. **Slice the score.** An overall rate hides small categories; the build task adds a per-category bar (`account: 0/2 passed`). → see lab step 5

## Failure modes
- **Silent drift:** a model or server upgrade changes outputs while the prompt stays the same. You notice only if the gate runs on every model change, not just prompt edits.
- **Stale golden set:** new ticket types never enter the set, so the score stays 100 % while users complain. Watch for production failures that have no matching case.
- **Flaky judge:** a model-graded rubric gives different scores on identical outputs. You see the pass rate move with no code change; pin the judge, use temperature 0, or keep rubrics deterministic as here.
- **Gaming the set:** deleting failing cases makes the gate green (Try it 2).

## Common mistakes
- Gating only on the average, so a regression in a small category passes.
- Re-writing the baseline after every red run instead of fixing the prompt.
- Using a judge model as the only check when an exact or structural check would do.
