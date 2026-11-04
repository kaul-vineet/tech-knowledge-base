**Concept: decision theory and planning – expected utility, budgets, search, and what no checker can decide**

## Why it matters
An agent loop is a sequence of decisions under uncertainty: call the tool again or give up, act or escalate, follow this plan or that one, allow this generated program or not. Lessons 6, 14, 15, 18 and 20 gave rules for each – step budgets, retry limits, approval gates, allow-lists, "code decides". This lesson derives those rules from four results, so you can defend the numbers in a design review and recognise when a rule no longer applies.

## Definitions
- **Expected utility (EU).** For an action a with outcomes o of probability P(o | a) and utility U(o): EU(a) = Σ_o P(o | a) U(o). The rational choice under the stated probabilities and utilities is argmax_a EU(a). Utilities include costs: a person's time, a wrong refund, a customer kept waiting.
- **Markov decision process (MDP).** States S, actions A, transition probabilities P(s′ | s, a), rewards r, discount γ ∈ [0, 1). A policy π maps states to actions; its value V^π(s) is the expected discounted sum of rewards (Sutton & Barto, ch. 3).
- **Bellman optimality operator.** (TV)(s) = max_a Σ_{s′} P(s′ | s, a)[r + γV(s′)]. Value iteration repeats V ← TV.
- **Search.** Breadth-first search (BFS) explores states in order of depth; A* orders the frontier by f(n) = g(n) + h(n), cost so far plus a heuristic estimate of the cost to go. A heuristic is *admissible* if it never overestimates, *consistent* if h(n) ≤ c(n, m) + h(m) for every edge.
- **Decidable property.** One for which some algorithm always halts with the correct yes/no answer for every input program.

## Key results (proved in the lesson, checked in `decision_planning.py`)
1. **Retries (T1).** If each attempt succeeds independently with probability p, the expected number of attempts with budget k is (1 − (1 − p)^k)/p and the chance of giving up is (1 − p)^k. Allowing attempt i+1 changes expected cost by −P(reach it)·(p_i·C_fail − c), where c is the cost of a call and C_fail the cost of giving up. So: *retry while p_i·C_fail ≥ c*. With independent failures that is "always" or "never"; with correlated failures (the same bad input fails again, p_i shrinking) the best budget is finite; with a stuck loop (p = 0) an unbudgeted loop has unbounded cost. A budget is a bound on the worst case, not a tuning knob for the average.
2. **Bellman and value iteration (T2).** T is a γ-contraction in the max-norm: ‖TU − TW‖ ≤ γ‖U − W‖. By Banach's fixed-point theorem there is exactly one optimal value function V*, value iteration converges to it geometrically, and acting greedily with respect to V* is optimal. One-step expected-utility choice is the special case with no future.
3. **Search optimality (T3).** BFS finds shortest paths when every step costs 1. A* with an admissible (graph search: consistent) heuristic returns an optimal path (Hart, Nilsson & Raphael 1968); an overestimating heuristic can return a worse one. The proof is one inequality: any node on an optimal path has f ≤ C*, so it is expanded before a goal with cost > C*.
4. **Undecidability (T4).** No algorithm can decide, for every program in a general-purpose language, whether it will ever call `delete`. If one could, it would decide the halting problem: wrap any program M as "run M; then call delete". This is an instance of Rice's theorem (1953): every non-trivial property of what programs *do* is undecidable. Practical checkers are therefore either incomplete (run with a step budget, may answer "unknown") or conservative (allow-lists over what a program *can name*, which may reject safe programs).

## Intuition
Utility makes trade-offs explicit: "escalate" is not a failure, it is an action with a known cost. Budgets exist because your estimate of p is the thing most likely to be wrong in production; a budget makes the damage of that error bounded. Search gives guarantees because it explores alternatives under a known cost model; an LLM "plan" is one sample from a distribution with no optimality or completeness guarantee – useful as a proposal or a heuristic, but checked by code. Undecidability is why the boundary in lesson 20 is a *capability* boundary: you cannot predict what arbitrary generated code will do, but you can decide in linear time which tools it is able to call.

## Worked example (the ticket MDP from the lab)
State "open"; actions: auto (call the refund tool, cost 1: resolved +10 with probability 0.75, tool error stays open 0.20, wrong refund −50 with 0.05), escalate (+4, a person handles it), close (−5). With γ = 0.95, "always auto" is worth (0.75·9 − 0.20·1 − 0.05·51)/(1 − 0.95·0.20) = 4.9383 > 4, so the agent should act. Value iteration reaches the same 4.9383 after 16 iterations. Raise the wrong-refund probability to 0.07 and the policy flips to escalate; the break-even is 0.0627. A one-percentage-point change in an error rate you estimated from 50 cases (lesson 24: the Wilson interval is wide) changes the right design. That is why lesson 20 keeps refunds above a threshold in code and lesson 21 monitors the error rate after release.

## How this connects to the course
- Lesson 6's step budget and lesson 14's retry budget are T1's worst-case bound; lesson 14's "retry only 5xx" is T1's p_i: a 4xx will fail again, so p_i ≈ 0.
- Lesson 15's approval gate and lesson 20's "code decides" are T2's escalate action with an explicit utility.
- Lesson 17's planner and the capstone's runbook steps are plans; T3 says to verify a proposed plan's cost and preconditions in code.
- Lessons 11 and 16 use allow-lists; T4 is why a smarter "intent analyser" cannot replace them.

## Common misconceptions
- **"More retries always help."** Only while p_i·C_fail ≥ c, and only if the attempts are independent. Correlated failures make extra attempts waste.
- **"Expected utility means ignoring rare disasters."** Put the disaster's real cost in U; if it is unacceptable at any probability, it is a constraint (forbid the action), not a term in a sum.
- **"Discounting is about money."** γ < 1 also guarantees convergence and expresses that a resolution now is worth more than one later.
- **"A* is always optimal."** Only with an admissible heuristic (consistent for graph search).
- **"An LLM planner is a search algorithm."** It samples a plan; it does not enumerate alternatives or prove anything about cost.
- **"A good enough static analyser can tell us what any agent-written script will do."** Not for all programs – that is a theorem, not an engineering gap. Restrict the language or the capabilities instead.

## Sources
Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed. (2018), ch. 3–4 · Hart, Nilsson & Raphael (1968), IEEE Trans. SSC 4(2) · Rice (1953), Trans. AMS 74:358–366 · Yao et al. 2023 (ReAct) for LLM planning loops.
