## Why it matters
A reviewer approved "votedFor need not be persisted; the term is enough". Three unit tests passed. The bug - a restarted node votes twice in one term, so two leaders share a term - needs a specific seven-step interleaving that no hand-written test happened to contain. Distributed protocols fail in interleavings, and humans are bad at enumerating them. Two tools do it automatically: **model checking** explores every reachable state of a protocol model, and **linearizability checking** decides whether a history recorded from a real system could have come from one correct copy.

## Mental model
```
model checking:   init --a1--> s1 --a2--> s2 ...   breadth-first over ALL reachable states
                  each state: check invariants;    violation -> shortest trace from init
history checking: client ops [start, end] -> search an order that respects real time
                  and the sequential spec (Wing & Gong), memoising (linearized set, state)
```
The model checker checks the **design** on a small instance; the history checker checks the **implementation** on real runs.

## Design space
- **Example-based tests**: precise, cheap, and blind to interleavings nobody wrote down.
- **Random simulation / property tests** (lessons 18 and 20): many runs, finds common bugs, no guarantee.
- **Explicit-state model checking**: exhaustive within bounds (here 3 nodes, terms up to 2); returns the shortest counterexample. TLA+ with the TLC model checker is the established tool (MIT licence; v1.7.4 is the latest stable release, v1.8.0 a pre-release). `Election.tla` is this lab's model in TLA+.
- **Linearizability checking of histories**: Porcupine implements a memoised Wing & Gong search with P-compositionality; etcd and MIT 6.5840 use it. Checking a history is NP-complete in general; registers are tractable, and memoisation (Lowe 2017) avoids exploring a configuration twice.

Forces: model checking needs a faithful model and small bounds (state explosion); history checking needs a run that actually exhibits the bug.

## How to decide
1. State the invariants first: ElectionSafety (one leader per term) and, closer to the cause, VoteOnce (nobody votes twice in a term), written over a **ghost log** of every vote that a restart cannot erase.
2. Model-check protocol changes in CI; raise the bounds in nightly runs.
3. Record histories from seeded runs of the implementation and check them; keep the shortest failing window as a regression test.

Worked example (lab output). BFS over the lesson protocol explores 4,519 distinct states and returns a 7-step trace: n0 times out; n1 votes for n0; n0 becomes leader of term 1; n2 times out; **n1 restarts and forgets its vote**; n1 votes for n2; n2 becomes leader of term 1. The three example tests pass on this protocol. Random simulation hits the bug in 16 of 1,000 walks (shortest 8 steps). With the vote persisted, BFS explores all 1,853 reachable states and finds no violation; with VoteOnce added and the bug re-introduced, the trace shrinks to 4 steps, at the cause. The history checker agrees with Porcupine's README examples and with the exhaustive L300 checker on 300 short histories (both reject the same 89), then rejects lab 17's 2,273-operation R = 2 W = 2 history in 48,590 steps, naming r6's read of 28 at 1738.9 ms - the first new-then-old inversion. The exhaustive checker needed 265.6 ms at 41 operations, the memoised one 0.29 ms (one run; times vary).

## Failure modes at scale
- **State explosion**: one more term multiplies the space by 16 (1,853 -> 29,221 states). Use symmetry, smaller models and bounded runs; accept that bugs needing larger instances can hide.
- **Model drift**: the Python model, `Election.tla` and the real code diverge. History checks of the implementation cover part of the gap.
- **Unexplored histories**: a linearizability checker only judges runs that happened; pair it with fault injection (lesson 20) so the bad interleavings occur.
- **Indeterminate operations**: timed-out operations may or may not have taken effect; real checkers must consider both cases (the lab's histories have no timeouts).

## Common mistakes
- Checking only the consequence (two leaders) and not the cause (a second vote), which makes traces longer and harder to read.
- Believing a green model check covers sizes it never explored.
- Writing invariants over state that a crash erases, so the model "forgets" the evidence.
