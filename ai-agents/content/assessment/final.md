# Final examination – AI Agents (week 14)

**Covers:** L100–L500 (lessons 1–27). **Time:** 3 hours. **Total:** 100 marks. Closed book; two A4 sheets of your own notes; a non-programmable calculator. Numerical answers to 4 decimals unless stated. Model-answer numbers were recomputed with the L500 lab modules (`research/l500_checks.py` verifies that they appear here).

---

### Q1 Derivation (14 marks)
(a) Derive the normal-approximation sample size for a one-sided test of H0: p = p0 against a drop to p1, at level α with power 1 − β. (b) Evaluate it for p0 = 0.92, p1 = 0.87, α = 0.05, power 0.8. (c) The exact binomial test at that n has which rejection rule, size and power? Comment.

**Model answer.** (a) Reject when p̂ ≤ c with c = p0 − z_{1−α}√(p0q0/n); power Φ((c − p1)/√(p1q1/n)) ≥ 1 − β ⇔ p0 − p1 ≥ z_{1−α}√(p0q0/n) + z_{1−β}√(p1q1/n) ⇔ n ≥ ((z_{1−α}√(p0q0) + z_{1−β}√(p1q1))/(p0 − p1))² (7). (b) n = 213 (3). (c) Reject if passes ≤ 188 of 213; size 0.0351, power 0.7373 – discreteness costs some power, so round n up and verify exactly if 0.8 is a hard requirement (4).

### Q2 Proof (12 marks)
Prove that the Bellman optimality operator of a finite MDP is a γ-contraction in the max-norm, and state the two consequences you use when you run value iteration.

**Model answer.** |max_a f − max_a g| ≤ max_a |f − g| (3). For each (s, a), rewards cancel and |Σ P(s′|s,a) γ(U(s′) − W(s′))| ≤ γ‖U − W‖ since ΣP = 1 (4). Max over a and s gives ‖TU − TW‖ ≤ γ‖U − W‖ (2). Consequences (Banach): unique fixed point V*; ‖V_t − V*‖ ≤ γ^t‖V_0 − V*‖, so value iteration converges geometrically and the greedy policy w.r.t. V* is optimal (3).

### Q3 Calculation (10 marks)
In the lab's ticket MDP (auto: resolved 0.80 − p_h with reward +9, tool error 0.20 with −1 and stay, wrong refund p_h with −51; γ = 0.95) the escalate action is re-priced at +5 because a new review tool halves staff time. (a) Find the break-even wrong-refund probability. (b) With p_h = 0.04, compute V(open) and the optimal first action.

**Model answer.** (a) V_auto = (7 − 60 p_h)/0.81; set equal to 5: p_h = (7 − 5·0.81)/60 = 0.0492 (5). (b) V_auto = (7 − 2.4)/0.81 = 5.6790 > 5, so auto (value iteration on `make_mdp(0.04)` agrees) (5). Note that cheaper review lowered the threshold from 0.0627 to 0.0492: better human tooling makes escalation the right call more often.

### Q4 Short explanation (10 marks)
Explain, as you would to a product manager, why "let another model check every generated script for dangerous behaviour" cannot replace a tool allow-list. Use the halting-problem reduction in your explanation, and say what the checker model can still be good for.

**Model answer.** Reduction: from any program M and input x build "run M on x, then call delete"; a perfect checker would decide whether M halts – impossible (Turing; Rice for any behavioural property) (4). So any checker is sometimes wrong or must say "unknown"; a model checker adds unmeasured error rates, drift with upgrades, and susceptibility to prompt injection (3). An allow-list answers a different, decidable question – which tools can this code name? – exactly and fail-safe (2). The checker can still explain risks to reviewers or add friction, but enforcement stays in code (1).

### Q5 Prediction (10 marks)
A bigram model with add-1 smoothing is trained on the lab corpus (V = 11). (a) Is its training perplexity higher or lower than the MLE model's 2.0612? Compute it. (b) Compute its held-out perplexity on the lab's held-out sentence and explain why it is finite. (c) A head uses d_k = 64 but an implementation scales by 1/√128. Give the wrong scale and its effect.

**Model answer.** (a) Higher: smoothing moves mass away from observed bigrams, and MLE minimises training cross-entropy (Gibbs); 5.9458 (4). (b) 6.7417; every bigram has probability ≥ 1/(count + V) > 0, so no log 0 term (3). (c) 1/√128 = 0.0884 instead of 0.1250 (√128 = 11.3137): scores have standard deviation 0.707 instead of 1, an effective temperature of √2 – flatter, less selective attention (3).

### Q6 Design critique (14 marks)
An L400-style incident-triage agent reports per-service accuracy for 8 services every week and pages the owning team when a service's accuracy is "significantly below 90 % (p < 0.05)". (a) In a week where nothing changed, how likely is at least one false page? (b) Propose a corrected rule. (c) Name two engineering controls from L300/L400 that must stay in place regardless of these statistics, and why.

**Model answer.** (a) 1 − 0.95⁸ = 0.3366, assuming independence (4). (b) Bonferroni: page only if p < 0.05/8 = 0.00625, or pre-register the services that gate and treat the rest as exploratory; report Wilson intervals and require confirmation on the following week's fresh cases (5). (c) Deterministic per-case regression gate on the golden incidents (known failures caught with certainty, lesson 12/22) and code-decided severity and actions with approval for side effects (lesson 20, capstone ADR-001) – statistical monitoring detects drift but does not prevent a wrong action (5).

### Q7 Ethics (16 marks)
A retailer deploys a refund agent in the EU in November 2026. It answers policy questions and auto-approves refunds under 50 EUR; refusals are sent automatically. Using primary sources, identify (a) the deployer's accountability if the agent misstates policy, (b) the disclosure duty, (c) the data-protection issue with automatic refusals, (d) the oversight risk if staff review refusals in bulk, and (e) one class of request the agent should not decide. Cite article/principle numbers.

**Model answer.** (a) Deployer liable for its agent's statements – Moffatt v. Air Canada (chatbot "part of" the website; negligent misrepresentation); ACM 1.3 (do not misrepresent an organisation's policies), 2.5 (thorough evaluation) (4). (b) AI Act Art. 50(1): inform users they are interacting with an AI system, clearly and at the latest at first interaction (Art. 50(5)); applies from 2 August 2026 (3). (c) GDPR Art. 22: a solely automated refusal with significant effect requires a lawful basis and safeguards – human intervention, the right to express a view and contest (Art. 22(3)) – so route refusals to a person (3). (d) Automation bias – AI Act Art. 14(4)(b) (named for high-risk systems; a good practice standard here), Parasuraman & Riley's misuse: show evidence, measure catch rate with seeded errors, make override easy (3). (e) Bereavement, health or vulnerability-related requests, or anything outside code-checked rules – harm is foreseeable and error rates on rare cases cannot be measured precisely (ACM 2.9 "may be to not implement"; NIST AI RMF "cease" when risk is unacceptable) (3).

### Q8 Reading (14 marks)
(a) In "Attention Is All You Need", what is d_k for the base model, and under what condition is self-attention cheaper per layer than recurrence? (b) In ReAct, what does a "thought" change and what does it not? (c) ReAct's error analysis used 50 trajectories per group. Give one consequence for how you read its percentages, with a number from lesson 24's methods.

**Model answer.** (a) d_k = d_model/h = 512/8 = 64; cheaper when n < d (O(n²d) vs O(n d²)) (4). (b) A thought updates the context (plans, extracted facts, exception handling) but does not act on the environment and produces no observation (4). (c) Percentages from 50 items carry wide intervals: 3/50 has a Wilson interval of [0.0206, 0.1622]; differences such as 6 % vs 14 % (p ≈ 0.18 unpaired) are directional evidence, not precise rates (6).
