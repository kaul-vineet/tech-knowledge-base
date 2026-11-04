"""Build content/qbank/L500.json (45 questions, lessons 23-27) and content/assessment/concept-inventory.json (15 items).

Each question is written with the correct option first; the builder moves it to a balanced target position.
Calculation options come from research/qbank_checks.py (CALCS via ID_MAP); code-reading answers are the snippet's
real stdout. Re-run, then: python research/check_l500_qbank.py && python research/qbank_checks.py
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qbank_checks as QC  # noqa: E402

TOPIC = Path(__file__).resolve().parent.parent


def run(code):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(code, "<snippet>", "exec"), {"__name__": "__snippet__"})
    return out.getvalue().strip()


def Q(lesson, qtype, diff, question, options, explanation, source, code=None):
    return {"lesson": lesson, "type": qtype, "difficulty": diff, "question": question, "code": code,
            "options": options, "explanation": explanation, "source": source}


S23, S24, S25 = "Lesson 23", "Lesson 24", "Lesson 25"
S26, S27 = "Lesson 26", "Lesson 27"

QUESTIONS = [
    # ------------------------------------------------------------ lesson 23
    Q(23, "concept", 2, "You lower the sampling temperature from 1.0 to 0.5 for the same logits. What happens to the next-token distribution?",
      ["It gets sharper: the most likely token gains probability, entropy falls, the argmax is unchanged",
       "The argmax can change, because dividing every logit by 0.5 reorders tokens whose logits are close together",
       "It gets flatter: probabilities move towards uniform and entropy rises",
       "Nothing changes in the distribution; temperature only affects decoding speed"],
      "Dividing all logits by T < 1 stretches their differences, so softmax concentrates mass on the largest logit; T1 shows dH/dT >= 0. Order is preserved because division by a positive number keeps the ranking.",
      f"{S23} T1"),
    Q(23, "calculation", 2, "Logits z = (2, 1, 0), temperature 1. What probability does softmax give the first token (4 decimals)?",
      ["calc"], "exp(2)/(exp(2) + exp(1) + 1) = 7.389/11.107 = 0.6652. 0.6667 is the tempting linear normalisation 2/(2+1+0), which ignores the exponential; 0.8668 is the T = 0.5 value.",
      f"{S23} problem 2"),
    Q(23, "concept", 3, "Why does scaled dot-product attention divide QK^T by sqrt(d_k)?",
      ["To keep score variance at 1: q.k has variance d_k, and a saturated softmax has near-zero gradients",
       "It normalises every query and key vector to length 1, turning the dot product into a cosine similarity",
       "It is needed so that each row of attention weights sums to 1 after the softmax",
       "It halves the memory needed for the attention matrix when d_k is large"],
      "Var(q.k) = d_k under the independence assumption (T2); unscaled scores have standard deviation sqrt(d_k), softmax becomes nearly one-hot and its Jacobian vanishes. Rows sum to 1 because of softmax itself, with or without scaling.",
      f"{S23} T2; Vaswani et al. 2017 Sec. 3.2.1"),
    Q(23, "code-reading", 2, "What does this print?",
      None,
      "Subtracting the max (or adding 100 to every logit) cancels in the ratio, so both lists are equal: softmax is shift-invariant (T1). Equal logits give a uniform distribution, not zeros.",
      f"{S23} T1 (shift invariance)",
      code="import math\n\ndef softmax(z):\n    m = max(z)\n    e = [math.exp(x - m) for x in z]\n    s = sum(e)\n    return [round(x / s, 3) for x in e]\n\nprint(softmax([1, 2, 3]) == softmax([101, 102, 103]), softmax([0, 0]))"),
    Q(23, "code-reading", 2, "A model assigns these probabilities to the correct next tokens of a 4-token text. What does this print?",
      None,
      "Perplexity is exp of the mean negative log probability, i.e. the inverse geometric mean of the probabilities: (0.5 * 0.25 * 0.5 * 0.0625)^(-1/4) = 256^(1/4) = 4.0. Averaging the probabilities (0.328) and inverting gives about 3.05, a common slip; 1.39 is the cross-entropy ln 4, before exponentiating.",
      f"{S23} T3; Jurafsky & Martin eq. 3.15",
      code="import math\n\nprobs = [0.5, 0.25, 0.5, 0.0625]\nce = -sum(math.log(p) for p in probs) / len(probs)\nprint(round(math.exp(ce), 2))"),
    Q(23, "code-reading", 2, "This is the top-p rule from the lab, applied to the bigram row for 'the'. What does it print?",
      None,
      "Sorted by probability: agent (0.375) then tool (0.625 total) reaches 0.6, so the loop stops after two tokens with mass 0.625. The kept mass is what was accumulated, not the threshold p.",
      f"{S23} T4; lab tiny_lm.truncate",
      code="probs = {'agent': 0.375, 'tool': 0.25, 'answer': 0.125, 'result': 0.125, 'ticket': 0.125}\nkept, mass = [], 0.0\nfor tok, p in sorted(probs.items(), key=lambda kv: -kv[1]):\n    kept.append(tok)\n    mass += p\n    if mass >= 0.6:\n        break\nprint(kept, mass)"),
    Q(23, "scenario", 3, "A small local model, decoded greedily, keeps repeating 'Thought: I should check the order. Action: get_order' in an agent loop. Which change addresses the cause rather than the symptom?",
      ["Cap the loop and detect repeated actions in code; sample with top-p so the trajectory can leave the cycle",
       "Lower the temperature further so the model becomes more certain about which next step is the right one to take",
       "Raise max_tokens so the model has room to finish its reasoning before acting",
       "Switch to top-k with k = 1 because it removes unlikely tokens from the distribution"],
      "Greedy decoding is a deterministic map; when its argmax path revisits a state it cycles (T4, the lab's 'the agent calls the agent ...'). Lower temperature and top-k with k = 1 are both still greedy; a budget and repeat detection bound the damage, and sampling can break the cycle.",
      f"{S23} T4; Lesson 6 step budget; Yao et al. 2023 Sec. 3.3"),
    Q(23, "concept", 2, "A held-out sentence contains a bigram that never occurred in the training corpus. What is the unsmoothed (MLE) bigram model's perplexity on it?",
      ["Infinite, because that bigram gets probability 0 and log 0 is minus infinity",
       "Exactly V, because unseen bigrams fall back to the uniform distribution",
       "The same as on the training set, because perplexity is normalised per token",
       "Slightly higher than on training, because one unseen token barely moves the average"],
      "MLE assigns count/total = 0 to unseen bigrams, so one term of the average negative log-likelihood is infinite (T3 d). Smoothing (add-k) or a softmax model, which never outputs exactly 0, keeps it finite: the lab shows 4.4475 with add-0.1.",
      f"{S23} T3; lab check T3"),
    Q(23, "debugging", 3, "A team trains a tiny decoder on next-token prediction. Training loss drops to almost zero within minutes, but generated text is gibberish. Their attention code builds scores = Q @ K.T / sqrt(d) and applies softmax. What is the most likely bug?",
      ["The causal mask is missing, so each position can attend to the very token it is supposed to predict",
       "The 1/sqrt(d) scaling makes the attention softmax far too flat for the model to learn which positions matter",
       "Softmax should be applied over the query axis instead of the key axis",
       "The value matrix V must be normalised to unit length before mixing"],
      "Without the mask, position i sees token i+1 during training and copies it, so loss collapses; at generation time the future is not available and the shortcut fails (problem 9). Scaling affects sharpness, not leakage.",
      f"{S23} problem 9; Vaswani et al. Sec. 3.2.3"),
    # ------------------------------------------------------------ lesson 24
    Q(24, "calculation", 2, "An agent passes all 20 golden cases. What is the lower end of the 95 % Wilson interval for its true pass rate (4 decimals)?",
      ["calc"], "Wilson at 20/20 gives [0.8389, 1]: a perfect score on 20 cases is compatible with a true rate near 84 %. The Wald interval collapses to [1, 1]; 0.8316 is the exact Clopper-Pearson lower bound, a different method.",
      f"{S24} T1; NIST e-Handbook 7.2.4.1"),
    Q(24, "concept", 2, "Which statement about a 95 % confidence interval for a pass rate is correct?",
      ["If the procedure were repeated on many independent samples, about 95 % of the intervals would contain the true rate",
       "There is a 95 % probability that the true rate lies somewhere inside this particular interval we computed from the data",
       "95 % of the individual golden cases have pass probabilities inside the interval",
       "Repeating the same 20 cases many times makes the interval contain the rate 95 % of the time"],
      "Coverage is a property of the interval-building procedure over repeated samples. A computed interval either contains the fixed true rate or not; per-case probabilities and re-running the same cases are different questions.",
      f"{S24} Definitions; misconceptions"),
    Q(24, "calculation", 2, "An evaluation report runs an independent test at alpha = 0.05 on each of 10 ticket categories. If nothing changed, what is the probability of at least one false alarm (4 decimals)?",
      ["calc"], "FWER = 1 - 0.95^10 = 0.4013. 0.5000 is the union bound 10 x 0.05; with Bonferroni (0.005 each) the FWER would be 0.0489.",
      f"{S24} T4"),
    Q(24, "code-reading", 3, "What does this exact McNemar test print?",
      None,
      "With b = 2, c = 0 there are 2 discordant cases: 2 * (1/4) = 0.5. With b = 6, c = 0: 2 * (1/64) = 0.03125, rounded 0.0312. Forgetting the factor 2 (one-sided) gives 0.25 and 0.0156.",
      f"{S24} T3; lab eval_stats.mcnemar_exact",
      code="from math import comb\n\ndef mcnemar(b, c):\n    n = b + c\n    tail = sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n\n    return round(min(1.0, 2 * tail), 4)\n\nprint(mcnemar(2, 0), mcnemar(6, 0))"),
    Q(24, "scenario", 3, "Prompt A and prompt B were both run on the same 300 golden cases. Which analysis answers 'is B's pass rate different from A's'?",
      ["McNemar's test on the cases where exactly one prompt passed, plus reading those discordant cases",
       "A two-proportion z-test that treats the 300 runs of A and the 300 runs of B as two independent samples",
       "Comparing whether the two 95 % Wilson intervals overlap",
       "A chi-square test on the 2x2 table of total passes and fails for A and B"],
      "The design is paired, so only discordant cases inform the difference (T3); the unpaired tests ignore the shared difficulty of cases and lose power (lab: p 0.0414 paired vs 0.1882 unpaired on the same counts). Overlap of intervals is not a test.",
      f"{S24} T3; problem 4"),
    Q(24, "calculation", 3, "How many independent golden cases does the normal-approximation formula require to detect a drop from 90 % to 80 % with a one-sided test at alpha = 0.05 and power 0.8?",
      ["calc"], "n = ((1.6449 * 0.3 + 0.8416 * 0.4)/0.1)^2 = 68.6 -> 69. Using the two-sided z = 1.96 gives 86; 100 is the naive 1/delta^2; 25 ignores the power term.",
      f"{S24} T2"),
    Q(24, "concept", 2, "Why is the Wald interval p_hat +/- z sqrt(p_hat(1 - p_hat)/n) a poor choice for agent pass rates?",
      ["Near 0 or 1 it collapses or leaves [0, 1]; its real coverage can be far below 95 %",
       "It is always wider than the Wilson interval, so a gate that uses it hides real regressions",
       "It needs the exact binomial distribution, which is too slow to compute for large n",
       "It only works for paired comparisons, not for a single pass rate"],
      "At 20/20 the Wald interval is [1, 1] and at 18/20 its upper end is 1.03. The exact coverage sums in check T1 show 0.6389 for Wald versus 0.9245 for Wilson at n = 20, p = 0.95.",
      f"{S24} T1"),
    Q(24, "debugging", 3, "A weekly report says: 'New prompt significantly worse for category refunds-de (p = 0.03).' You learn 18 categories were tested at 0.05 and only this one was flagged. What is the right reading?",
      ["About one false alarm is expected among 18 tests at 0.05; confirm on fresh cases or a corrected threshold",
       "p = 0.03 means there is a 97 % chance that the regression is real, so the prompt must be rolled back immediately",
       "The other 17 categories passing proves the prompt is better overall",
       "The result is invalid because p-values cannot be computed per category"],
      "FWER for 18 independent tests is 1 - 0.95^18 = 0.60; Bonferroni would require p <= 0.0028. A p-value is not the probability that the effect is real.",
      f"{S24} T4; misconceptions"),
    Q(24, "design", 3, "Your gate must catch a 2-point drop from 95 % to 93 % in a refund agent, and you can afford about 200 labelled cases. What is the most defensible design?",
      ["Keep a per-case gate, admit 200 cases cannot see a 2-point drop, and monitor that rate in production",
       "Use the 200 cases with a 95 % pass bar; a 2-point drop will show up as about 4 failed cases",
       "Run each of the 200 cases 10 times so the suite has 2,000 cases and enough power",
       "Lower alpha to 0.01 so that any detected drop is certainly real"],
      "T2 gives roughly a thousand independent cases for a 2-point drop at this level, so 200 cannot see it reliably; rerunning the same cases does not add independent cases, and a lower alpha reduces power further. Be explicit about what the gate cannot see.",
      f"{S24} T2; worked example"),
    # ------------------------------------------------------------ lesson 25
    Q(25, "calculation", 1, "A tool call succeeds independently with probability 0.5. With a budget of 3 attempts, what is the expected number of calls (2 decimals)?",
      ["calc"], "E[min(N, 3)] = 1 + 0.5 + 0.25 = 1.75. 2.00 is E[N] = 1/p without a budget; 3.00 is the worst case, not the mean.",
      f"{S25} T1"),
    Q(25, "concept", 3, "Under T1's model, when does allowing one more attempt lower the expected cost of a call that costs c, with C_fail the cost of giving up?",
      ["When the conditional success probability of that attempt satisfies p_i * C_fail >= c",
       "Whenever the success probability of the first attempt is above 0.5",
       "Whenever the remaining budget is below the expected number of attempts 1/p",
       "Never, because each extra attempt adds its call cost to the total"],
      "cost(k+1) - cost(k) = -P(reach) (p_k C_fail - c): the sign depends only on p_k C_fail - c. With correlated failures p_k shrinks, so the optimal budget is finite.",
      f"{S25} T1"),
    Q(25, "code-reading", 3, "Value iteration for one state: act (0.8 chance of +5, else -1 and stay, gamma 0.9) or escalate (+3). What does it print?",
      None,
      "The fixed point of V = 0.8*5 + 0.2*(-1 + 0.9 V) is V = 3.8/0.82 = 4.634 > 3, so acting wins and V rounds to 4.63. 3.8 is the one-step value without the future term.",
      f"{S25} T2",
      code="V = 0.0\nfor _ in range(200):\n    V = max(0.8 * 5 + 0.2 * (-1 + 0.9 * V), 3.0)\nprint(round(V, 2))"),
    Q(25, "concept", 2, "Which property guarantees that value iteration converges to a unique optimal value function in a finite MDP?",
      ["The Bellman operator is a gamma-contraction in the max-norm when the discount gamma is below 1",
       "Every policy eventually reaches a terminal state with probability 1, so the values stop changing",
       "The rewards are bounded between 0 and 1",
       "The transition probabilities are deterministic"],
      "||TU - TW|| <= gamma ||U - W|| and Banach's fixed-point theorem give existence, uniqueness and geometric convergence (T2). Termination or bounded rewards alone do not give the contraction.",
      f"{S25} T2"),
    Q(25, "scenario", 3, "An A* planner over tool steps uses a heuristic that sometimes overestimates the remaining cost. In testing it returns a plan costing 8 where a 4-cost plan exists. What explains this?",
      ["Overestimation can give an optimal-path node a larger f than a worse goal, so optimality is lost",
       "A* is only guaranteed to be optimal on unit-cost graphs, so weighted tool steps break the guarantee",
       "The planner must have a bug, because A* always returns the cheapest path",
       "Overestimation only affects speed, so the 8-cost plan must also be optimal"],
      "Optimality needs h <= h* (T3). In the lab's plan graph h(search_kb) = 9 > h* = 2 makes A* return cost 8 instead of 4. BFS needs unit costs; A* does not.",
      f"{S25} T3; lab check T3"),
    Q(25, "concept", 3, "Why can no analyser, however sophisticated, decide for every agent-generated script whether it will ever call delete?",
      ["A perfect decider would solve the halting problem, via the script 'run M on x, then call delete'",
       "Scripts generated by language models are random, so their behaviour cannot be predicted",
       "Static analysis tools do not yet support the newest Python syntax",
       "The decision would take exponential time, which is too slow in practice"],
      "The reduction is exact: the wrapped script deletes iff M halts on x (T4, Rice's theorem). It is impossibility, not slowness or randomness; restricted languages or syntactic allow-lists remain decidable.",
      f"{S25} T4"),
    Q(25, "design", 3, "Given T4, how should an agent that writes and runs small scripts be prevented from destroying data?",
      ["Expose only allow-listed tools and require approval for side effects, checked before execution",
       "Ask a second model to read every generated script and approve it only if it judges the script harmless",
       "Run each script under a larger step budget until the analyser is certain",
       "Scan the script's printed output for the word 'delete' after it runs"],
      "Capability restriction decides a syntactic question exactly and fails safe (T4); a judge model is itself unverified and injectable, a bigger budget still ends in 'unknown', and post-hoc scanning is too late.",
      f"{S25} T4; problem 8; Lesson 20"),
    Q(25, "calculation", 2, "Auto-approval yields +2 when right and -40 when wrong; human review always yields +0.5. Above what error rate should the agent stop auto-approving (4 decimals)?",
      ["calc"], "2(1 - e) - 40e = 0.5 gives e = 1.5/42 = 0.0357. 0.0375 forgets that a wrong approval also loses the +2; 0.0500 ignores the review option entirely.",
      f"{S25} expected utility; problem 3"),
    Q(25, "debugging", 2, "An agent's retry loop keeps resending a request that fails with HTTP 400 until the conversation times out. In T1's terms, what is wrong?",
      ["For a 4xx p_i is about 0, so p_i * C_fail < c: no retry pays, and the loop has no budget",
       "The success probability is low but still positive, so the loop only needs exponential backoff with jitter",
       "Retries are fine; the timeout is too short for the loop to finish",
       "The loop should retry with a higher temperature to get a different request"],
      "A malformed request fails again (p_i near 0), so every retry is pure cost and only a budget stops it; lesson 14 raises 4xx immediately. Backoff spaces out retries but does not change p.",
      f"{S25} T1; Lesson 14"),
    # ------------------------------------------------------------ lesson 26
    Q(26, "concept", 2, "In Moffatt v. Air Canada (2024 BCCRT 149), why did the airline's defence about its chatbot fail?",
      ["It held the chatbot was part of the airline's website, and the airline answers for all information on it",
       "The tribunal found the chatbot was a separate legal entity, but held the airline liable because it had insured the bot",
       "The customer proved the chatbot was trained on the wrong policy document",
       "Canadian law makes software vendors, not deployers, liable for chatbot errors"],
      "The tribunal called the separate-entity argument 'remarkable' and found negligent misrepresentation by the airline. Nothing in the decision shifts liability to a vendor.",
      f"{S26} case study"),
    Q(26, "concept", 2, "EU AI Act Art. 14(4)(b) requires that people overseeing a high-risk system remain aware of which tendency?",
      ["Automatically relying or over-relying on the system's output (automation bias)",
       "Distrusting the system after a single false alarm (disuse)",
       "Changing the system's configuration without documentation",
       "Sharing the system's output with unauthorised third parties"],
      "Art. 14(4)(b) names automation bias explicitly; Parasuraman and Riley call it misuse. Disuse is a real effect but not what this paragraph addresses.",
      f"{S26} over-reliance; AI Act Art. 14"),
    Q(26, "scenario", 2, "Your customer-facing support agent launches in the EU in November 2026. Under AI Act Art. 50(1) and (5), what must users be told, and when?",
      ["That they are interacting with an AI system - clearly, at the latest at first interaction, unless obvious",
       "Nothing until December 2027, because the omnibus regulation postponed every AI Act obligation including Art. 50",
       "The model's name and parameter count, in the privacy policy",
       "That answers are not legally binding, in a disclaimer after each answer"],
      "Art. 50 applies from 2 August 2026 and the omnibus left that date in place; it postponed the high-risk (Annex III) obligations to 2 December 2027. Disclaimers did not save the airline in Moffatt.",
      f"{S26} transparency; AI Act Art. 50"),
    Q(26, "concept", 3, "When does GDPR Art. 22 give a person rights over an agent's decision?",
      ["When the decision is based solely on automated processing and produces legal or similarly significant effects on them",
       "Whenever any personal data, such as a customer's name or order number, is included in a prompt sent to a language model",
       "Only when the decision is made by a high-risk system under the AI Act",
       "Only when the person has explicitly consented to the use of AI"],
      "Art. 22(1) covers solely automated decisions with legal or similarly significant effects; where allowed (contract, law, consent), Art. 22(3) requires safeguards such as human intervention and the right to contest. Consent is one exception, not the trigger.",
      f"{S26} privacy; GDPR Art. 22"),
    Q(26, "calculation", 2, "An agent answers 5,000 questions a month with a 4 % error rate; each error costs 100. Reviewing every answer costs 1 per answer and catches 80 % of errors. What is the monthly cost with full review?",
      ["calc"], "Review 5,000 x 1 = 5,000 plus residual errors 200 x 0.2 = 40 x 100 = 4,000: total 9,000, versus 20,000 without review. 16,000 is the harm avoided, not a cost.",
      f"{S26} problem 3"),
    Q(26, "concept", 2, "Which ACM Code principle states that 'the best option may be to not implement the system'?",
      ["2.9, when misuse or harm are predictable or unavoidable",
       "1.6, when personal data cannot be minimised",
       "3.1, when the public good is not the central concern",
       "2.6, when the team lacks competence in the area"],
      "Principle 2.9 (robustly and usably secure systems) ends with that sentence; 2.5 adds that systems with unpredictable risks need frequent reassessment or should not be deployed.",
      f"{S26} when not to automate; ACM Code 2.9"),
    Q(26, "code-reading", 2, "A fairness check flags languages whose pass rate is below 90 %. What does it print?",
      None,
      "es is 0.80 and flagged; pt is exactly 0.90, so '< 0.9' does not flag it - although 9/10 has a Wilson interval of roughly [0.60, 0.98] (lesson 24). en at 0.95 passes.",
      f"{S26} bias and fairness; Lesson 24",
      code="results = {'en': (95, 100), 'es': (40, 50), 'pt': (9, 10)}\nflagged = [lang for lang, (passed, n) in results.items() if passed / n < 0.9]\nprint(flagged)"),
    Q(26, "concept", 1, "What are the four functions of the NIST AI RMF 1.0 Core?",
      ["GOVERN, MAP, MEASURE, MANAGE",
       "IDENTIFY, PROTECT, DETECT, RESPOND",
       "PLAN, BUILD, VERIFY, DEPLOY",
       "ASSESS, MITIGATE, MONITOR, REPORT"],
      "NIST AI 100-1 Part 2 defines GOVERN (cross-cutting), MAP, MEASURE and MANAGE. IDENTIFY/PROTECT/DETECT/RESPOND belong to the NIST Cybersecurity Framework.",
      f"{S26} frameworks; NIST AI 100-1 Sec. 5"),
    Q(26, "concept", 3, "Regulation (EU) 2026/1744 (Digital Omnibus on AI) changed the AI Act timetable. Which statement is correct?",
      ["Obligations for Annex III high-risk systems now apply from 2 December 2027 instead of 2 August 2026",
       "All AI Act obligations, including the Art. 50 transparency duty for chatbots, were postponed to August 2028",
       "The AI Act was repealed and replaced by voluntary codes of practice",
       "Only general-purpose AI model obligations were postponed; high-risk dates are unchanged"],
      "The omnibus, published 24 July 2026, moved Annex III high-risk obligations to 2 December 2027 and Annex I systems to 2 August 2028, while the 2 August 2026 transparency date remained.",
      f"{S26} transparency; EP Legislative Train"),
    # ------------------------------------------------------------ lesson 27
    Q(27, "concept", 1, "What is the central architectural claim of 'Attention Is All You Need'?",
      ["A sequence-transduction model can dispense with recurrence and convolution and rely on attention alone",
       "Recurrent networks become competitive once an attention layer is added between encoder and decoder",
       "Convolutional networks with dilated kernels outperform attention for translation",
       "Attention weights can explain a translation model's decisions to end users"],
      "The abstract proposes the Transformer, 'based solely on attention mechanisms'; attention combined with RNNs already existed (Sec. 1-2). Interpretability is mentioned only as a possible side benefit.",
      f"{S27} reading 1; Vaswani et al. abstract"),
    Q(27, "calculation", 1, "In the base Transformer d_model = 512 with h = 8 heads and d_k = d_model/h. What scale factor multiplies QK^T (4 decimals)?",
      ["calc"], "d_k = 64 and 1/sqrt(64) = 0.1250. 0.0442 uses the full d_model; 0.0156 divides by d_k instead of its square root.",
      f"{S27} problem 1; Vaswani et al. Sec. 3.2.2"),
    Q(27, "concept", 3, "What exactly do Vaswani et al. say about why unscaled dot-product attention underperforms for large d_k?",
      ["They suspect large dot products push softmax into regions with tiny gradients, motivated by a variance argument",
       "They prove that unscaled dot-product attention cannot converge during training for any key dimension d_k above 64",
       "They show experimentally that the scale factor has no effect at the base model size",
       "They attribute it to numerical overflow in half-precision arithmetic"],
      "Sec. 3.2.1 says 'we suspect' and gives the variance footnote; lesson 23's T2 proves the variance and measures the saturation. Distinguishing measured from conjectured is the point of the seminar.",
      f"{S27} guiding question 2; Lesson 23 T2"),
    Q(27, "concept", 2, "According to the paper's Table 1 and Sec. 4, when is a self-attention layer computationally cheaper than a recurrent layer?",
      ["When the sequence length n is smaller than the representation dimension d",
       "When the sequence length n is larger than the representation dimension d",
       "Always, because self-attention needs O(1) sequential operations",
       "Only when attention is restricted to a neighbourhood of size r"],
      "Per-layer cost is O(n^2 d) versus O(n d^2), so attention is cheaper when n < d. O(1) sequential operations is about parallelism, not total compute; long agent contexts have n far above d.",
      f"{S27} problem 1; Vaswani et al. Table 1"),
    Q(27, "concept", 2, "How does ReAct change the agent's action space?",
      ["It adds language 'thoughts' that update the context but produce no observation from the environment",
       "It replaces tool actions with chain-of-thought text, so the agent no longer needs any environment calls",
       "It lets the model edit the environment's observations before reading them",
       "It adds a second model that chooses actions while the first writes reasoning"],
      "Sec. 2 augments A with the language space L; a thought does not affect the environment and yields no observation, but it conditions later actions. One frozen model produces both.",
      f"{S27} reading 2; Yao et al. Sec. 2"),
    Q(27, "concept", 2, "Which actions did ReAct's Wikipedia API offer for HotpotQA and FEVER?",
      ["search[entity], lookup[string] and finish[answer]",
       "search[query], click[link] and buy[item]",
       "retrieve[k], rerank[passages] and answer[text]",
       "open[url], scroll[n] and cite[source]"],
      "Sec. 3.1 describes a deliberately simple API with search, lookup and finish, weaker than modern retrievers; click/buy-style actions belong to WebShop.",
      f"{S27} guiding question 2; Yao et al. Sec. 3.1"),
    Q(27, "scenario", 3, "A blog post claims 'ReAct cuts hallucinated successes from 14 % to 6 %'. The numbers come from 50 labelled correct trajectories per method. What is the best critical response?",
      ["Plausible direction, but 3/50 vs 7/50 gives wide Wilson intervals and p near 0.18: the size is not established",
       "The claim is proven beyond doubt, because the paper passed peer review at ICLR and the authors labelled the data",
       "The claim is wrong, because ReAct scored lower than chain-of-thought on HotpotQA",
       "The comparison is invalid, because hallucination cannot be measured by humans"],
      "Lesson 24's tools: Wilson intervals [0.0206, 0.1622] and [0.0695, 0.2619] overlap heavily and the two-proportion p is 0.1824 (problem 3). Peer review does not shrink sampling error; a lower EM score is a different metric.",
      f"{S27} problem 3; Yao et al. Table 2"),
    Q(27, "concept", 3, "On HotpotQA with PaLM-540B prompting, what did ReAct's Table 1 show?",
      ["ReAct alone scored slightly below CoT, and the best result came from combining ReAct with CoT-SC",
       "ReAct alone scored far above every prompting baseline, including chain-of-thought with self-consistency",
       "Act-only scored highest because reasoning traces distracted the model",
       "All prompting methods matched the supervised state of the art"],
      "EM: ReAct 27.4, CoT 29.4, CoT-SC 33.4, ReAct -> CoT-SC 35.1, supervised SoTA 67.5. The paper's argument is about grounding and combination, not a single headline win.",
      f"{S27} reading 2; Yao et al. Table 1"),
    Q(27, "calculation", 2, "For a 2,048-token context and d = 512, how many times more per-layer operations does self-attention (n^2 d) need than a recurrent layer (n d^2)?",
      ["calc"], "n^2 d / (n d^2) = n/d = 2048/512 = 4.00. 0.25 inverts the ratio; 16.00 squares it. Long contexts are where attention's quadratic cost dominates.",
      f"{S27} problem 1; Vaswani et al. Table 1"),
]

DISTRACTORS = {  # code-reading wrong options (the correct one is the real stdout)
    4: ["False [0.5, 0.5]", "True [0.0, 0.0]", "False [1.0, 0.0]"],
    5: ["3.05", "0.33", "1.39"],
    6: ["['agent'] 0.375", "['agent', 'tool', 'answer'] 0.75", "['agent', 'tool'] 0.6"],
    13: ["0.25 0.0156", "0.5 0.0156", "1.0 0.0312"],
    21: ["3.0", "3.8", "4.0"],
    34: ["['es', 'pt']", "['pt']", "[]"],
}


# Concept inventory: 15 misconception-targeted items, taken pre (week 1) and post (week 14); not graded.
# Same schema as qbank items, level L500, lesson 23 (administered with the first L500 lesson); "targets" names the
# misconception and the lesson that addresses it.
INVENTORY = [
    ("Temperature 0 makes a model correct", "23",
     "A team sets temperature 0 'so the agent stops making mistakes'. What does temperature 0 actually guarantee?",
     ["Same input, same most-likely output every time - right or wrong",
      "The model only outputs answers it has seen verbatim in its training data",
      "The model refuses to answer whenever its confidence is below a safe threshold",
      "Factual errors are removed because random sampling is the cause of hallucinations"],
     "Temperature 0 is argmax decoding: deterministic, not correct. If the most likely continuation is wrong, it is wrong every time."),
    ("High probability means true", "23",
     "A model assigns 0.97 probability to its answer token. What does that number tell you on its own?",
     ["Its likelihood under the model, which is not the same as being correct",
      "That the answer is correct about 97 times out of 100 for questions like this one",
      "That 97 % of the training documents contained this exact answer",
      "That the answer passed the model's internal fact-checking stage"],
     "Token probabilities describe text continuation; calibration against correctness has to be measured on labelled cases (lesson 24)."),
    ("Truncated sampling removes wrong tokens", "23",
     "Which tokens can top-p (nucleus) sampling never remove from the candidate set?",
     ["The most probable ones, even when the most probable token is wrong",
      "Tokens that are factually incorrect for the specific question the user asked",
      "Tokens that would make the output invalid JSON",
      "Tokens that repeat something already generated"],
     "Top-p keeps the smallest high-probability prefix; it filters by probability, not by correctness, validity or repetition."),
    ("Attention weights explain decisions", "23",
     "An attention head puts most weight on the word 'refund' when the agent chooses the refund tool. What can you conclude?",
     ["Only where that head read from - not why the model chose the tool",
      "The model chose the tool because of the word 'refund', so removing it will change the choice",
      "All other heads and layers ignored the rest of the input",
      "The tool choice was decided in this layer and later layers only copied it"],
     "Many heads and layers combine; attention weights show where information was read, not a causal explanation."),
    ("Lower perplexity means a better agent", "23",
     "Model B has lower perplexity than model A on a held-out text. What follows for your ticket-triage agent?",
     ["B predicts that text better; triage quality must still be measured on the task",
      "B will triage more tickets correctly, because perplexity measures overall model quality",
      "B is safer, because lower perplexity means fewer hallucinated facts",
      "B needs less context, because perplexity is measured per token"],
     "Perplexity is intrinsic and comparable only with the same tokenizer and test set; task success needs an extrinsic evaluation."),
    ("A confidence interval is a probability about one interval", "24",
     "An eval report says: pass rate 88 %, 95 % CI [80 %, 94 %]. Which statement is justified?",
     ["Intervals built this way contain the true rate in about 95 % of repeated evaluations",
      "There is a 95 % probability that the agent's true pass rate lies somewhere between 80 % and 94 %",
      "95 % of future evaluations will report a pass rate between 80 % and 94 %",
      "The agent passes between 80 % and 94 % of cases 95 % of the time"],
     "Coverage is a property of the procedure; any single computed interval either contains the true rate or does not."),
    ("Re-running the same cases adds cases", "24",
     "You run each of 20 golden cases 10 times (temperature 0.7) and get 200 results. What do you have?",
     ["Repeated measurements of 20 cases, not 200 independent cases",
      "A 200-case evaluation with ten times the statistical power of the original",
      "A 200-case evaluation, but only if the seed differs on every run",
      "A suite that now covers ten times more of the task's input space"],
     "Independence across task inputs is what makes n; repeats measure model randomness on the same inputs."),
    ("Overlapping intervals mean no difference", "24",
     "Version A's 95 % interval overlaps version B's. Both ran on the same cases. What should you do next?",
     ["Test the paired difference using the cases where exactly one version passed",
      "Conclude there is no difference, because the intervals overlap",
      "Conclude B is worse if its point estimate is lower",
      "Run a significance test that treats the two versions' results as independent samples"],
     "Overlap is not a test; paired data call for a paired test (McNemar) on the discordant cases."),
    ("A p-value is the probability the effect is real", "24",
     "A regression test reports p = 0.01. Which reading is correct?",
     ["With no regression, results this extreme would occur about 1 % of the time",
      "There is a 99 % probability that the regression is real",
      "There is a 1 % probability that the new version is better",
      "The regression reduces the pass rate by about 1 percentage point compared with the baseline"],
     "A p-value is computed assuming no effect; it is not the probability that the effect exists, nor its size."),
    ("More retries always help", "25",
     "An API call fails. When is retrying the same request a bad idea, even though retries are cheap?",
     ["When the failure will repeat (a 4xx, the same bad input), so another try cannot succeed",
      "Never; with enough retries every request eventually succeeds",
      "Only when the API charges per call, because otherwise a failed retry costs nothing at all",
      "Only when the user is waiting for the answer"],
     "Retry pays only while p_i * C_fail >= c; correlated failures make p_i near 0, and a stuck loop needs a budget."),
    ("An LLM plan is an optimal plan", "25",
     "A model writes a 6-step plan for a task. What do you know about it without further checks?",
     ["It is one proposal; neither its cost nor its validity is guaranteed until checked or searched",
      "It is the cheapest plan the model could find, because models search before answering",
      "It is valid, because the model only proposes steps that exist as tools",
      "It is complete, because planning prompts force the model to list every step"],
     "Search with an admissible heuristic has optimality guarantees; a sampled plan has none and must be verified in code."),
    ("A good analyser can predict any script's behaviour", "25",
     "Can a sufficiently advanced analyser decide, for every script an agent writes, whether it will ever delete data?",
     ["No; that would solve the halting problem, so restrict what scripts can call instead",
      "Yes, given enough compute time and a large enough model",
      "Yes, if the scripts are written in a typed language",
      "Only for scripts shorter than a few hundred lines"],
     "Rice's theorem: non-trivial behavioural properties are undecidable; allow-lists decide a syntactic property exactly."),
    ("A human in the loop makes it safe", "26",
     "A company adds a reviewer who approves every agent refund before payment. What is the main remaining risk?",
     ["The reviewer may come to approve by default because the agent is usually right (automation bias)",
      "None; human review removes the agent's errors by definition",
      "The reviewer will reject too many correct refunds because people distrust AI",
      "Legal liability moves from the company to the reviewer"],
     "Oversight works only if reviewers can and do disagree; measure catch rates (AI Act Art. 14(4)(b); Parasuraman & Riley)."),
    ("A disclaimer shifts responsibility", "26",
     "A chatbot answer ends with 'Check our policy page for details'. The answer misstates the policy and a customer relies on it. Who is likely responsible?",
     ["The company deploying the chatbot, as for any other statement on its website",
      "The customer, because the disclaimer told them to check the policy page",
      "The model vendor, because the model generated the wrong statement",
      "Nobody, because chatbot output is not a statement by the company"],
     "Moffatt v. Air Canada: the chatbot is part of the company's website and the company is responsible for its information."),
    ("Local means no data-protection duties", "26",
     "An agent runs on a local model on the office Mac mini. Which statement about personal data is correct?",
     ["Data protection still applies to prompts, memories, logs and backups that contain personal data",
      "Data protection does not apply because no data leaves the building",
      "Only the model weights need protection, because they encode the training data",
      "Personal data may be kept indefinitely because local storage is cheap"],
     "Local hosting reduces transfer risk but not duties such as minimisation, retention and rights over automated decisions."),
]


def build_inventory():
    out = []
    for i, (target, lesson, question, opts, expl) in enumerate(INVENTORY, start=1):
        pos = [0, 1, 2, 3][(i * 3 + i // 4) % 4]
        options = opts[1:pos + 1] + [opts[0]] + opts[pos + 1:]
        out.append({"id": f"ag-CI-{i:03d}", "level": "L500", "lesson": 23, "type": "concept", "difficulty": 2,
                    "question": question, "options": options, "answer": pos, "explanation": expl,
                    "source": f"Concept inventory (pre/post); misconception addressed in Lesson {lesson}",
                    "targets": {"misconception": target, "lesson": int(lesson)}})
    path = TOPIC / "content" / "assessment" / "concept-inventory.json"
    if path.exists():
        os.remove(path)
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(out)} concept-inventory items to {path.relative_to(TOPIC)}")


def main():
    calc_ids = {k: v for k, v in QC.ID_MAP.items() if k.startswith("ag-L500-")}
    out, positions = [], [0, 1, 2, 3]
    for i, q in enumerate(QUESTIONS, start=1):
        qid = f"ag-L500-{i:03d}"
        if q["type"] == "calculation":
            res = QC.CALCS[calc_ids[qid]]()
            opts = [res["correct"], *res["wrong"]]
        elif q["type"] == "code-reading":
            opts = [run(q["code"]), *DISTRACTORS[i]]
        else:
            opts = q["options"]
        target = positions[(i * 3 + i // 4) % 4]
        correct, wrong = opts[0], opts[1:]
        options = wrong[:target] + [correct] + wrong[target:]
        item = {"id": qid, "level": "L500", "lesson": q["lesson"], "type": q["type"], "difficulty": q["difficulty"],
                "question": q["question"]}
        if q["code"]:
            item["code"] = q["code"]
        item.update({"options": options, "answer": target, "explanation": q["explanation"], "source": q["source"]})
        out.append(item)
    path = TOPIC / "content" / "qbank" / "L500.json"
    if path.exists():
        os.remove(path)
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(out)} questions to {path.relative_to(TOPIC)}")
    build_inventory()


if __name__ == "__main__":
    main()
