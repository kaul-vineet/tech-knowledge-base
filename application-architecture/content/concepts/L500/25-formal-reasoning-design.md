**Concept: Formal reasoning about design – contracts, invariants, Liskov substitution, model checking and the empirical evidence**

## Why it matters
Tests show that a few runs work; reasoning shows that all runs work – within stated assumptions. Lesson 8 gave Library
Loans an aggregate with invariants; lesson 9 and lesson 12 had concurrent consumers; lesson 19 had policies that must
hold for every input. This lesson supplies the reasoning tools behind them – contracts, invariant induction, behavioural
subtyping, explicit-state model checking – and an honest look at what empirical research says about modular design.

## Definitions
- **Contract (Hoare logic; Meyer's design by contract).** For an operation: a precondition the caller must establish, a
  postcondition the operation guarantees, and a frame ("nothing else changes").
- **Invariant.** A predicate on an object's state that holds after construction and after every public operation. For
  the `Member` aggregate: at most `max_loans` active loans and no book twice among them.
- **Failure atomicity.** A rejected operation leaves the state unchanged.
- **Behavioural subtype (Liskov and Wing, 1994).** S is a subtype of T when properties provable about T objects also hold
  for S objects – so code written against T's specification still works with an S.
- **Transition system, safety property, model checking.** A model is a set of states with labelled transitions. A safety
  property says something bad never happens. A model checker explores every reachable state and either proves the
  property for the model or returns a counterexample trace.

## Key results (proofs in `content/L500.json`, checks in `labs/L500/25-formal-reasoning`)
1. **T25.1 Invariant induction.** If the invariant holds after construction, every public operation preserves it when
   started inside its precondition, and rejected calls change nothing, then the invariant holds in every state reachable
   through the public API. Encapsulation is the hidden premise: if outside code can append to the internal list, the
   proof covers nothing. That is why `Member.loans` returns a tuple.
2. **T25.2 The substitution rule.** If pre_T ⇒ pre_S (a subtype may accept *more*) and pre_T ∧ post_S ⇒ post_T (a subtype
   may promise *more*), every client proved correct against T stays correct with S. Liskov and Wing's full definition also
   preserves invariants and constrains history.
3. **T25.3 BFS model checking.** On a finite model, breadth-first search visits exactly the reachable states and stops; the
   first unsafe state it dequeues is at minimal distance, so the parent chain is a shortest counterexample.

## Intuition
A precondition is a *division of labour*: the caller checks, the operation trusts. Weakening it in a subtype is safe
because old callers already satisfy the stronger condition; strengthening it is not, because old callers never checked the
new condition. Postconditions run the other way. The lab shows both failures with concrete classes: `GenerousLimit` lets a
client written for "never more than three loans" take five; `NoOverdueAccepted` throws on 33 of the 44 inputs the
supertype accepts. Neither breaks a type checker – Python would accept all three – which is exactly Liskov and Wing's point:
signatures are not behaviour.

Model checking turns a concurrency argument into a search. The buggy borrow flow reads "book free" and later inserts a
loan; two members interleave and both hold the book. BFS finds the four-step trace (A reads, B reads, A borrows, B borrows)
after exploring nine states. The fix – one atomic conditional insert, as a unique constraint or a compare-and-set version
check (lesson 8) – leaves eight reachable states, none unsafe, no deadlock, and the book can always become free again.
The price of exhaustiveness is state explosion: with n members the buggy model has 3ⁿ states and the fixed one
(n + 2)·2ⁿ⁻¹ (problem P25-6). Production model checkers fight this with techniques such as symmetry and partial-order
reduction; distributed-systems L400 #21 applies model checking to larger protocols.

## Worked example
`check_formal.py` drives the unchanged L200 #8 `Member` class with 310,352 random `borrow`/`give_back` calls (178,288 of
them rejected by the rules). After every call it checks the invariant; after every successful borrow, the postcondition;
after every rejected call, that the state is unchanged. All three counts are zero. That is evidence, not proof – the proof
is T25.1 – but it would catch a regression such as checking the limit after appending.

## What the empirical evidence says – and does not say
Architects often claim that modular design reduces defects. Three studies show how carefully that claim must be made.
- **Zimmermann and Nagappan (2008)** built dependency graphs for Windows Server 2003 and used network measures to predict
  defect-prone binaries. Recall was about 10 percentage points higher than with complexity metrics, and the measures
  identified 60 % of the binaries developers considered critical, twice as many as complexity metrics. Strong evidence that
  dependency structure *predicts* where defects are; it is observational, from one system, and does not show that changing
  the structure would remove defects.
- **El Emam, Benlarbi, Goel and Rai (2001)** re-examined object-oriented metric "validations" on a large C++
  telecommunications framework. Before controlling for class size the metrics looked predictive; after controlling for size,
  none of the metrics they studied remained associated with fault-proneness. Size is a confounder: big classes have more
  coupling *and* more faults.
- **MacCormack, Rusnak and Baldwin (2006)** used design structure matrices to compare Linux with the first release of
  Mozilla, finding Linux more modular, and found that a deliberate Mozilla redesign produced a markedly more modular
  architecture. It measures structure and its link to organisation, not defects, and the authors call the results
  exploratory.

The honest claim is therefore modest: dependency structure is associated with where defects and change costs concentrate;
we use it to focus review, testing and refactoring, and we measure outcomes (defect rates, lead time) instead of promising
them. Lesson 26 explains why that modesty is an ethical duty, not just good science.

## Common misconceptions
- **"Contracts are just assertions."** Assertions *check* contracts at run time; the contract is the specification that
  divides responsibility and supports proof.
- **"If it type-checks, it substitutes."** Types capture signatures, not behaviour (stack vs queue in Liskov and Wing).
- **"A passing model check proves the code correct."** It proves the model; keep model and code linked by replaying the
  counterexample schedule against the real repository.
- **"Random testing found nothing, so the invariant holds."** Random traces sample; induction proves.
- **"Metric X is validated."** Ask: controlled for size? one system or many? prediction or intervention?

## Check yourself
1. Which premise of T25.1 would a public `loans` list break? 2. Give a subtype that weakens a precondition safely.
3. Why is BFS, not depth-first search, the right choice when you want the shortest counterexample?
