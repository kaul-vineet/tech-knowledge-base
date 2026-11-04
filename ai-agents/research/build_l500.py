"""Build content/L500.json (lessons 23-27). Theorem checkOutput is captured by running the check now;
calculation solutions embed numbers recomputed by research/l500_checks.py. Re-run after editing:

    python research/build_l500.py && python research/l500_checks.py
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import l500_checks as C  # noqa: E402

TOPIC = Path(__file__).resolve().parent.parent
LAB23 = "labs/L500/23-language-model-foundations/tiny_lm.py"
LAB24 = "labs/L500/24-evaluation-statistics/eval_stats.py"
LAB25 = "labs/L500/25-decision-planning/decision_planning.py"
PLATFORMS = {"mac": "expected", "windows": "expected"}


def thm(name, statement, proof, check):
    return {"name": name, "statement": statement, "proof": proof, "check": check, "checkOutput": C.run_check(check)}


def prob(pid, problem, ptype, difficulty, solution, marks):
    return {"id": pid, "problem": problem, "type": ptype, "difficulty": difficulty, "solution": solution, "marks": marks}


def v(pid):
    return C.PROBLEM_CHECKS[pid]()


WRITTEN_RUBRIC = [
    {"criterion": "Correctness of derivations and calculations", "excellent": "Every step valid and justified; numbers match a code check to 4 decimals.",
     "adequate": "Method right with a slip that does not change the conclusion.", "inadequate": "Wrong method or unjustified steps.", "weight": 40},
    {"criterion": "Stating assumptions", "excellent": "Names each assumption (independence, unit variance, admissibility, discount < 1) and where it fails for real agents.",
     "adequate": "Assumptions stated but not challenged.", "inadequate": "Assumptions missing.", "weight": 20},
    {"criterion": "Numerical verification", "excellent": "Own code reproduces the result and probes an edge case.",
     "adequate": "Runs the lab check and reports its output.", "inadequate": "No check, or output not matched to the claim.", "weight": 20},
    {"criterion": "Connection to agent engineering", "excellent": "Explains which design rule from L100-L400 the result justifies or limits.",
     "adequate": "Mentions a related lesson.", "inadequate": "No connection.", "weight": 20},
]

# ============================================================== lesson 23
p2, p4, p5, p7, p8 = v("l23-p2"), v("l23-p4"), v("l23-p5"), v("l23-p7"), v("l23-p8")
L23 = {
    "id": "language-model-foundations", "number": 23, "level": "L500",
    "title": "Foundations I: how language models work",
    "category": "theory: probability and linear algebra of LLMs",
    "description": "Tokens, embeddings, softmax and temperature, scaled dot-product attention and why 1/sqrt(d), next-token sampling (greedy/top-k/top-p), cross-entropy and perplexity - derived, then checked with a tiny numpy model.",
    "outcome": "You can derive softmax-with-temperature, explain the 1/sqrt(d) in attention from a variance argument, prove that counting minimises cross-entropy, and predict what greedy, top-k and top-p decoding will do to a given distribution.",
    "estimatedTime": "4-5 hours (lecture 90 min, lab 60 min, problem set 2 h)",
    "prerequisites": [
        "Linear algebra: vectors, dot products, matrix multiplication, transpose",
        "Probability: discrete distributions, expectation, variance of sums of independent variables",
        "Calculus: partial derivatives, Lagrange multipliers, logarithms and exponentials",
        "Lesson 2: Call a model over HTTP (temperature and top_p fields)",
        "Lesson 4: Structured output (why temperature 0 for JSON)",
    ],
    "learningObjectives": [
        "Derive softmax with temperature as the maximum-entropy distribution for given logits and prove that entropy increases with temperature.",
        "Explain, using the variance of a sum of independent products, why attention scores are divided by sqrt(d) and what goes wrong without it.",
        "Prove with Gibbs' inequality that relative-frequency (MLE) estimates minimise training cross-entropy, and relate cross-entropy to perplexity.",
        "Analyze the distribution that greedy, top-k and top-p decoding actually sample from, and evaluate when each degenerates.",
    ],
    "glossary": [
        {"term": "token", "meaning": "Unit of text in the model's fixed vocabulary of V entries; text becomes a list of integer ids."},
        {"term": "embedding", "meaning": "Learned vector (row of a V x d table) looked up for each token id."},
        {"term": "logit", "meaning": "Unnormalised score z_i for vocabulary entry i; softmax turns logits into probabilities."},
        {"term": "temperature T", "meaning": "Divisor of the logits before softmax: T < 1 sharpens, T > 1 flattens, T -> 0 is argmax."},
        {"term": "scaled dot-product attention", "meaning": "softmax(QK^T / sqrt(d_k)) V: each position averages the values of the positions it may see, weighted by query-key similarity."},
        {"term": "causal mask", "meaning": "Sets scores for later positions to -infinity so position i only uses positions <= i."},
        {"term": "cross-entropy", "meaning": "Average negative log-probability the model gives the tokens that actually occur (nats or bits per token)."},
        {"term": "perplexity", "meaning": "exp(cross-entropy): the effective number of equally likely choices per token; uniform model = V."},
        {"term": "top-p (nucleus) sampling", "meaning": "Sample from the smallest set of most likely tokens whose total probability is at least p, renormalised."},
    ],
    "theorems": [
        thm("T1 Softmax with temperature is the maximum-entropy (Gibbs) distribution",
            "For logits z in R^V and T > 0, p_i = exp(z_i/T) / sum_j exp(z_j/T) is the unique maximiser over the probability simplex of F(p) = sum_i p_i z_i + T H(p), where H(p) = -sum_i p_i log p_i; the maximum is T log sum_j exp(z_j/T). Moreover softmax is invariant to adding a constant to all logits, tends to the uniform distribution on argmax z as T -> 0+, to the uniform distribution on all V tokens as T -> infinity, and dH/dT = Var_p(z) / T^3 >= 0.",
            "**Maximiser.** Maximise F subject to sum_i p_i = 1 with the Lagrangian L = sum p_i z_i - T sum p_i log p_i + lambda (sum p_i - 1). Setting dL/dp_i = z_i - T(log p_i + 1) + lambda = 0 gives log p_i = z_i/T + (lambda - T)/T, i.e. p_i = c exp(z_i/T); normalisation fixes c = 1 / sum_j exp(z_j/T). F is strictly concave (H is strictly concave, the first term is linear) and dF/dp_i -> +infinity as p_i -> 0, so the stationary point is interior and is the unique maximum. Substituting log p_i = z_i/T - log Z gives F = sum p_i z_i - sum p_i z_i + T log Z = T log Z.\n\n**Shift.** exp((z_i + c)/T) = e^{c/T} exp(z_i/T); the factor cancels between numerator and denominator.\n\n**Limits.** Divide numerator and denominator by exp(z_max/T). Each term exp((z_i - z_max)/T) -> 0 for z_i < z_max as T -> 0+, and = 1 for maximisers, giving the uniform distribution on argmax z (greedy when the argmax is unique). As T -> infinity every exponent -> 0, every term -> 1, giving 1/V.\n\n**Monotone entropy.** Write beta = 1/T and Z(beta) = sum exp(beta z_i). Then H = log Z - beta E_p[z]. Since d log Z / d beta = E_p[z] and d E_p[z] / d beta = Var_p(z), dH/dbeta = E_p[z] - E_p[z] - beta Var_p(z) = -beta Var_p(z). By the chain rule dH/dT = dH/dbeta * (-1/T^2) = Var_p(z)/T^3 >= 0, with equality only if all logits are equal. QED.\n\n**Reading.** Temperature is the exchange rate between expected score and entropy: the sampling knob you set in lesson 2 picks a point on this trade-off.",
            f"{LAB23} check T1"),
        thm("T2 Why attention divides by sqrt(d)",
            "Let q, k in R^d have independent components with mean 0 and variance 1 (q independent of k). Then E[q.k] = 0 and Var(q.k) = d, so q.k / sqrt(d) has variance 1 for every d. Without the scaling, scores have standard deviation sqrt(d); softmax over such scores approaches one-hot and its Jacobian diag(p) - p p^T approaches 0, so gradients through the attention weights vanish.",
            "q.k = sum_{i=1}^d q_i k_i. Each term has mean E[q_i]E[k_i] = 0 and variance E[q_i^2 k_i^2] - 0 = E[q_i^2] E[k_i^2] = 1 (independence). The d terms are independent, so their variances add: Var(q.k) = d, and Var(q.k / sqrt(d)) = d/d = 1.\n\n**Saturation.** If the largest score exceeds all others by at least Delta, then p_max >= 1 / (1 + (n - 1) e^{-Delta}). With scores of standard deviation sqrt(d) the typical gap grows like sqrt(d), so p_max -> 1. The softmax Jacobian has entries p_i(delta_ij - p_j); for a one-hot p every entry is 0, so dL/dscores = J^T dL/dp -> 0 and the query/key projections stop learning.\n\n**Scope.** The assumptions hold at initialisation with unit-variance weights; in a trained model they are approximate. Vaswani et al. (2017, Sec. 3.2.1 and footnote) state the variance argument and say they *suspect* the small-gradient effect; the numerical check below measures it. If components had variance sigma^2 the same proof gives Var(q.k) = sigma^4 d and the right scale would be sigma^2 sqrt(d) (problem 3). QED.",
            f"{LAB23} check T2"),
        thm("T3 Gibbs' inequality: counting minimises cross-entropy; perplexity = exp(cross-entropy)",
            "For distributions p, q on a finite set, H(p, q) = -sum_x p(x) log q(x) >= H(p) = H(p, p), with equality iff q = p on the support of p. Consequently (a) on a training corpus the bigram table P(b|a) = count(ab)/count(a) (MLE) has the lowest training cross-entropy of all bigram tables; (b) perplexity PP = exp(H) = (prod_t q(w_t | w_{t-1}))^{-1/N}, so minimising cross-entropy and minimising perplexity are the same; (c) the uniform model has PP = V; (d) if any test bigram has q = 0, PP is infinite.",
            "KL(p||q) = H(p, q) - H(p) = -sum_{p(x)>0} p(x) log(q(x)/p(x)). Because log is strictly concave, Jensen gives -sum p log(q/p) >= -log sum_{p>0} p (q/p) = -log sum_{p>0} q(x) >= -log 1 = 0. Equality needs q/p constant on the support (strict concavity) and all of q's mass on that support, i.e. q = p.\n\n(a) Let n_ab be the bigram counts and N = sum n_ab. The training cross-entropy of a table q is -(1/N) sum_{a,b} n_ab log q(b|a) = sum_a (n_a/N) H(phat(.|a), q(.|a)) with phat(b|a) = n_ab/n_a. Each row's term is minimised separately, and by Gibbs at q(.|a) = phat(.|a).\n\n(b) exp(-(1/N) sum_t log q_t) = (prod_t q_t)^{-1/N} (Jurafsky & Martin eq. 3.15).\n\n(c) q = 1/V for every token gives H = log V and PP = V.\n\n(d) log 0 = -infinity, so one zero-probability event makes H and PP infinite; smoothing (add-k) or softmax outputs (always > 0) avoid it. QED.",
            f"{LAB23} check T3"),
        thm("T4 Truncated sampling is sampling conditioned on the kept set",
            "Let p be a next-token distribution and S a set of kept tokens: S = {argmax} (greedy), the k most probable tokens (top-k), or the smallest prefix of tokens sorted by probability whose mass is at least p_top (top-p). Sampling from q(w) = p(w) 1[w in S] / p(S) is sampling from p conditioned on W in S. Greedy equals top-k with k = 1 and is the T -> 0 limit of temperature sampling when the argmax is unique; |S| for top-p is 1 when the largest probability is at least p_top and grows as the distribution flattens.",
            "P(W = w | W in S) = P(W = w, W in S) / P(W in S) = p(w) 1[w in S] / p(S) = q(w). Top-k with k = 1 keeps exactly the argmax, so its q is the indicator of the argmax, as is greedy; T1 gives the temperature limit. For top-p the kept size is min{m : sum_{i<=m} p_(i) >= p_top} where p_(1) >= p_(2) >= ...; it equals 1 iff p_(1) >= p_top, and for the uniform distribution it equals ceil(p_top V). Ties are broken by token id in the lab, which is why the kept set is well defined. QED.\n\n**Consequence.** Truncation removes unlikely tokens, never likely-but-wrong ones; and greedy decoding repeats whenever the most likely continuation leads back to an earlier state (the lab's 'the agent calls the agent calls ...', the degeneration studied by Holtzman et al. 2019).",
            f"{LAB23} check T4"),
    ],
    "problemSet": [
        prob("l23-p1", "Derive softmax with temperature from first principles: maximise sum_i p_i z_i + T H(p) over the probability simplex with a Lagrange multiplier. State why the stationary point is the global maximum.", "derivation", 2,
             "Lagrangian L = sum p_i z_i - T sum p_i log p_i + lambda(sum p_i - 1). dL/dp_i = z_i - T log p_i - T + lambda = 0 => p_i = exp(z_i/T) exp((lambda - T)/T). Summing to 1: exp((lambda - T)/T) = 1/sum_j exp(z_j/T), so p_i = exp(z_i/T)/sum_j exp(z_j/T). Global: the objective is strictly concave (Hessian of -T sum p log p is diag(-T/p_i), negative definite), the constraint set is convex, and the gradient of the entropy term blows up at the boundary so the optimum is interior; a stationary point of a strictly concave function on a convex set is its unique maximiser.", 8),
        prob("l23-p2", "For logits z = (2, 1, 0) compute the softmax probabilities at T = 1 and at T = 0.5 (4 decimals) and the entropy of each in nats. Which is sharper and by how much did the entropy change?", "calculation", 1,
             f"T = 1: exp(2), exp(1), exp(0) = 7.389, 2.718, 1; sum 11.107; p = ({p2[0]}, {p2[1]}, {p2[2]}). T = 0.5: logits become (4, 2, 0); p = ({p2[3]}, {p2[4]}, {p2[5]}). Entropy -sum p ln p: T = 1 gives {p2[6]} nats, T = 0.5 gives {p2[7]} nats. T = 0.5 is sharper; entropy fell, as T1 predicts (dH/dT >= 0). Check: python -c \"import tiny_lm as t; print(t.softmax([2,1,0],0.5))\".", 6),
        prob("l23-p3", "Generalise T2: if the components of q and k are independent with mean 0 and variance sigma^2, what is Var(q.k), and what scaling keeps attention scores at unit variance? What happens to the argument if q and k are correlated (e.g. a token attending to itself with W_Q = W_K)?", "proof", 2,
             "Each term q_i k_i has mean 0 and variance E[q_i^2]E[k_i^2] = sigma^4; d independent terms give Var(q.k) = d sigma^4, so divide by sigma^2 sqrt(d). If q = k (self-similarity with shared projections) then q.k = |q|^2 has mean d sigma^2, not 0: the self-score is systematically large and the token attends mostly to itself unless the projections differ. Independence of q and k is therefore an assumption about the learned projections, not a fact; the 1/sqrt(d) rule controls only the spread due to dimension.", 8),
        prob("l23-p4", "Using the lab's MLE bigram model (corpus in tiny_lm.CORPUS), compute the probability of the continuation 'the agent calls the tool .' given that it starts with 'the' (product of 5 bigram probabilities) and its perplexity over those 5 predicted tokens.", "calculation", 2,
             f"P(agent|the) = 3/8, P(calls|agent) = 1/3, P(the|calls) = 1, P(tool|the) = 2/8, P(.|tool) = 1/2 (tool is followed once by '.' and once by 'returns'). Product = 3/8 * 1/3 * 1 * 1/4 * 1/2 = {p4[0]}. Perplexity = {p4[0]}^(-1/5) = {p4[1]}: on average about 2.3 equally likely choices per token, below the uniform model's 11.", 6),
        prob("l23-p5", "Row 'the' of the bigram model is agent 0.375, tool 0.25, answer/result/ticket 0.125 each (ties broken by token id: answer < result < ticket). Which tokens does top-p with p = 0.7 keep, what is their total mass, and what are the renormalised sampling probabilities?", "calculation", 1,
             f"Sorted: agent 0.375 (cum 0.375), tool 0.25 (0.625 < 0.7), answer 0.125 (0.75 >= 0.7) -> stop. Kept {{agent, tool, answer}}, mass {p5[0]}. Renormalised: agent {p5[1]}, tool {p5[2]}, answer {p5[3]}. result and ticket can never be sampled even though they are exactly as likely as answer - a consequence of the tie-break, worth knowing when you debug 'why is this token never produced'.", 5),
        prob("l23-p6", "Greedy decoding of the lab model from 'the' produces 'the agent calls the agent calls ...'. Explain with T4 why this happens, why top-p sampling escapes it, and why lesson 4 nevertheless uses temperature 0 for JSON output.", "short-answer", 2,
             "Greedy picks argmax at each step: after 'the' the argmax is 'agent' (0.375); after 'agent' the three continuations tie at 1/3 and the tie-break picks 'calls'; after 'calls' the only continuation is 'the'. The state 'the' recurs, so the deterministic map cycles. Top-p keeps several tokens and samples, so the trajectory can leave the cycle (the lab's top-p sample visits ticket and tool). For JSON the goal is the single most likely well-formed output and reproducibility, not diversity; repetition loops are prevented by schema validation, max_tokens and the step budget, and correctness is still checked in code (lesson 4).", 6),
        prob("l23-p7", "(a) A model gives probability 0.25 to every correct token of a 100-token text. Compute its cross-entropy (nats/token) and perplexity. (b) Another gives 0.9 to 99 tokens and 1e-6 to one token. Compute both again and compare with a model that gives 0.9 to all 100 tokens. What does this say about perplexity as a metric?", "calculation", 2,
             f"(a) H = -ln 0.25 = {p7[0]} nats, PP = e^H = {p7[1]}. (b) H = (99 * -ln 0.9 + -ln 1e-6)/100 = (99 * 0.10536 + 13.8155)/100 = {p7[2]} nats, PP = {p7[3]}; with 0.9 everywhere PP would be {p7[4]}. One confidently wrong token raises perplexity by about 15 %: perplexity punishes overconfidence on rare events heavily because log probabilities are unbounded below. It measures calibrated prediction of every token, not task success.", 6),
        prob("l23-p8", "In the base Transformer d_k = 64. What are sqrt(d_k) and the scale 1/sqrt(d_k)? If an implementation mistakenly used the concatenated dimension 2 d_k = 128 for the scaling of a 64-dimensional head, by what factor would the score standard deviation be too small, and what would that do to attention?", "calculation", 1,
             f"sqrt(64) = {p8[0]}, scale = {p8[1]}. Using sqrt(128) = {p8[2]} divides by an extra factor sqrt(2) = 1.414, so the scores' standard deviation is 1/sqrt(2) = 0.707 of the intended 1: softmax becomes flatter (higher entropy, by T1 an effective temperature of 1.414), attention averages more positions and is less selective. Not fatal, but a silent quality loss - a good reason to test attention code against the formula (lab test_tiny_lm.py).", 5),
        prob("l23-p9", "Prove that with a causal mask the attention output at position i does not depend on tokens at positions j > i (in one layer), and explain why this is what makes next-token training on a whole sequence in parallel legitimate.", "proof", 2,
             "Masked scores s_ij = -infinity for j > i, so softmax weights w_ij = exp(s_ij)/sum_l exp(s_il) = 0 for j > i (exp(-inf) = 0) and the output o_i = sum_j w_ij v_j = sum_{j<=i} w_ij v_j involves only v_1..v_i, which are functions of x_1..x_i. By induction over layers (each layer's position-i output depends only on positions <= i of its input) the final representation at i depends only on x_1..x_i. Hence the prediction for token i+1 never sees token i+1, and all n next-token losses of a sequence can be computed in one forward pass without leaking the answer (Vaswani et al. Sec. 3.2.3).", 6),
    ],
    "rubric": WRITTEN_RUBRIC,
    "projectFiles": [
        {"path": LAB23, "purpose": "Tokens, embeddings, softmax, causal attention, bigram LM, sampling, perplexity; `check T1..T4` prints each theorem's numerical check."},
        {"path": "labs/L500/23-language-model-foundations/test_tiny_lm.py", "purpose": "7 unit tests (python -m unittest)."},
    ],
    "runCommands": {"mac": "cd labs/L500/23-language-model-foundations && python3 tiny_lm.py && python3 tiny_lm.py check T2",
                    "windows": "cd labs\\L500\\23-language-model-foundations; py -3.12 tiny_lm.py; py -3.12 tiny_lm.py check T2"},
    "conceptNote": "content/concepts/L500/23-language-model-foundations.md",
    "conceptSummary": "An LLM scores every vocabulary entry; softmax-with-temperature (the maximum-entropy distribution for those scores) turns scores into probabilities; attention is a softmax lookup whose 1/sqrt(d) keeps scores at unit variance; counting minimises cross-entropy and perplexity = exp(cross-entropy); greedy/top-k/top-p sample from p conditioned on a kept set.",
    "sources": [
        {"title": "Vaswani et al. 2017 - Attention Is All You Need (arXiv:1706.03762v7), Sec. 3.2 and Table 1", "url": "https://arxiv.org/abs/1706.03762"},
        {"title": "Jurafsky & Martin - Speech and Language Processing, ch. 3 N-gram Language Models (perplexity, MLE)", "url": "https://web.stanford.edu/~jurafsky/slp3/3.pdf"},
        {"title": "Holtzman et al. 2019 - The Curious Case of Neural Text Degeneration (nucleus sampling, arXiv:1904.09751)", "url": "https://arxiv.org/abs/1904.09751"},
    ],
    "seeAlso": [
        "ai-agents L100 #2 Call a model over HTTP: temperature and top_p are the T1/T4 knobs in the request body.",
        "ai-agents L100 #4 Structured output: temperature 0 = argmax decoding (T1 limit, T4).",
        "ai-agents L200 #9 State and memory: token budgets exist because attention cost grows with context length.",
        "ai-agents L400 #19 Cost, latency and model choice: the KV cache stores the keys and values of T2's attention for every earlier token.",
    ],
    "next": "L500 #24 Foundations II: statistics for evaluating agents - the model is probabilistic, so its evaluation must be too",
    "platforms": PLATFORMS,
    "validation": {"status": "validated-local",
                   "how": "python tiny_lm.py (demo) and tiny_lm.py check T1..T4 run on Python 3.12.15 + numpy 2.5.3 in the Linux sandbox; outputs pasted into checkOutput; python -m unittest -> 7 tests OK; research/l500_checks.py re-runs every check and compares.",
                   "pendingCi": ["macOS and Windows runs in the CI matrix (output printed to 4 decimals so it should match exactly)"]},
}

# ============================================================== lesson 24
q1, q3, q4, q6, q8 = v("l24-p1"), v("l24-p3"), v("l24-p4"), v("l24-p6"), v("l24-p8")
L24 = {
    "id": "evaluation-statistics", "number": 24, "level": "L500",
    "title": "Foundations II: statistics for evaluating agents",
    "category": "theory: inference for pass rates",
    "description": "Pass rates as binomial proportions, Wilson confidence intervals, sample size to detect a regression, paired comparisons with McNemar's test, and multiple-comparison control - derived, then computed with standard-library Python.",
    "outcome": "You can put an honest interval on any pass rate, say how many golden cases a gate needs to see a given regression, compare two agent versions on the same cases correctly, and avoid false alarms from slicing.",
    "estimatedTime": "4-5 hours (lecture 90 min, lab 60 min, problem set 2 h)",
    "prerequisites": [
        "Probability: Bernoulli and binomial distributions, independence, expectation and variance",
        "Statistics: normal approximation, z-scores, hypothesis tests and p-values (introductory level)",
        "Algebra: solving a quadratic inequality",
        "Lesson 12: Evaluating agents with a golden set (the 20-case gate)",
        "Lesson 21: Governance and evaluation in production (drift test, model upgrade gate)",
    ],
    "learningObjectives": [
        "Derive the Wilson score interval by inverting the score test and explain why the Wald interval fails near 0 and 1.",
        "Derive the sample size needed to detect a given regression with stated level and power, and evaluate what an existing golden set can and cannot detect.",
        "Prove that McNemar's test statistic depends only on discordant pairs and explain why pairing increases power.",
        "Evaluate a multi-slice evaluation report for multiple-comparison errors using Boole's inequality and Bonferroni correction.",
    ],
    "glossary": [
        {"term": "binomial proportion", "meaning": "p_hat = X/n where X ~ Binomial(n, p) counts passes among n independent cases."},
        {"term": "coverage", "meaning": "Probability, over repeated samples, that an interval procedure contains the true p."},
        {"term": "Wilson score interval", "meaning": "All p not rejected by the score test |p_hat - p| <= z sqrt(p(1-p)/n); stays inside [0, 1]."},
        {"term": "power", "meaning": "Probability that a test detects a real effect of a stated size (1 - beta)."},
        {"term": "discordant pair", "meaning": "A case passed by exactly one of the two versions being compared."},
        {"term": "McNemar's test", "meaning": "Paired test of equal pass rates using only discordant pairs: b ~ Binomial(b + c, 1/2) under H0."},
        {"term": "family-wise error rate (FWER)", "meaning": "Probability of at least one false positive among m tests."},
        {"term": "Bonferroni correction", "meaning": "Test each of m hypotheses at alpha/m so the FWER is at most alpha."},
    ],
    "theorems": [
        thm("T1 Binomial pass rate and the Wilson score interval",
            "If n cases pass independently with probability p, p_hat = X/n is unbiased with Var(p_hat) = p(1-p)/n. The set {p : |p_hat - p| <= z sqrt(p(1-p)/n)} is the interval centre +/- half with centre = (p_hat + z^2/(2n)) / (1 + z^2/n) and half = z/(1 + z^2/n) * sqrt(p_hat(1-p_hat)/n + z^2/(4n^2)) (Wilson 1927). It lies in [0, 1] and has positive width even when p_hat = 0 or 1.",
            "X = sum of n independent Bernoulli(p) variables, so E[X] = np and Var(X) = np(1-p); dividing by n gives E[p_hat] = p, Var(p_hat) = p(1-p)/n.\n\n**Inversion.** Squaring the score inequality: (p_hat - p)^2 <= z^2 p(1-p)/n. Expanding, f(p) = (1 + z^2/n) p^2 - (2 p_hat + z^2/n) p + p_hat^2 <= 0. f is a quadratic with positive leading coefficient, so the solution set is the closed interval between its roots, and the quadratic formula gives p = [(2 p_hat + z^2/n) +/- sqrt((2 p_hat + z^2/n)^2 - 4(1 + z^2/n) p_hat^2)] / (2(1 + z^2/n)). Simplifying the discriminant: (2 p_hat + z^2/n)^2 - 4(1 + z^2/n)p_hat^2 = 4 z^2/n (p_hat(1 - p_hat) + z^2/(4n)), which yields centre and half above.\n\n**Inside [0, 1].** f(0) = p_hat^2 >= 0 and f(1) = (1 - p_hat)^2 >= 0, and the vertex (the centre) lies in [0, 1] because it is a weighted average of p_hat and 1/2; a convex quadratic that is non-negative at 0 and 1 with its minimum inside has both roots in [0, 1]. At p_hat = 1 the half-width is z sqrt(z^2/(4n^2))/(1 + z^2/n) > 0.\n\n**Wald.** Replacing p(1-p) by p_hat(1-p_hat) under the root gives p_hat +/- z sqrt(p_hat(1-p_hat)/n), which has zero width at p_hat in {0, 1} and can leave [0, 1]; its coverage near the boundary is poor, as the exact coverage sums below show (NIST e-Handbook 7.2.4.1; Brown, Cai and DasGupta 2001). QED.",
            f"{LAB24} check T1"),
        thm("T2 Sample size to detect a regression",
            "For a one-sided test of H0: p = p0 against H1: p = p1 < p0 at level alpha with power 1 - beta, the normal approximation requires n >= ((z_{1-alpha} sqrt(p0 q0) + z_{1-beta} sqrt(p1 q1)) / (p0 - p1))^2, q = 1 - p. n grows as 1/(p0 - p1)^2. Because X is discrete, the exact binomial test at that n has size <= alpha and power close to (sometimes slightly below) 1 - beta.",
            "Reject 'no regression' when p_hat <= c. Under H0, p_hat is approximately N(p0, p0 q0/n), so level alpha requires c = p0 - z_{1-alpha} sqrt(p0 q0/n). Under H1, p_hat is approximately N(p1, p1 q1/n) and the power is Phi((c - p1)/sqrt(p1 q1/n)). Power >= 1 - beta iff (c - p1)/sqrt(p1 q1/n) >= z_{1-beta} iff p0 - p1 >= z_{1-alpha} sqrt(p0 q0/n) + z_{1-beta} sqrt(p1 q1/n). Multiplying by sqrt(n)/(p0 - p1) and squaring gives the bound. Halving delta = p0 - p1 multiplies n by 4 (up to the slow change in the sqrt terms).\n\n**Exact check.** The exact test rejects when X <= c* with c* the largest count such that P(X <= c* | p0) <= alpha; its size is that tail and its power is P(X <= c* | p1). Discreteness makes both slightly smaller than the approximation suggests, so compute them and round n up if needed. QED.",
            f"{LAB24} check T2"),
        thm("T3 McNemar's exact test for paired pass/fail results",
            "Run versions A and B on the same n independent cases. Let b = #(A passes, B fails) and c = #(A fails, B passes). The difference in pass rates is (b - c)/n. Under H0: P(A pass, B fail) = P(A fail, B pass), conditional on m = b + c, b ~ Binomial(m, 1/2), so the exact two-sided p-value is min(1, 2 sum_{i <= min(b, c)} C(m, i) / 2^m). The concordant pairs do not enter. For large m, (|b - c| - 1)^2/(b + c) is approximately chi-square with 1 degree of freedom (McNemar 1947).",
            "Each case falls into one of four cells with probabilities pi_11 (both pass), pi_10, pi_01, pi_00, independently across cases. P(A pass) - P(B pass) = (pi_11 + pi_10) - (pi_11 + pi_01) = pi_10 - pi_01: the concordant cell cancels, so H0 of equal pass rates is pi_10 = pi_01. Given that a case is discordant, it is of type 10 with probability pi_10/(pi_10 + pi_01) = 1/2 under H0, independently of the other cases. Hence, conditional on m discordant cases, b ~ Binomial(m, 1/2), and the exact p-value is the probability under that distribution of a split at least as uneven as observed. Because the p-value is computed from the exact null distribution, P(p <= alpha | H0) <= alpha. The chi-square form is the normal approximation to that binomial, (b - m/2)^2/(m/4) = (b - c)^2/m, with continuity correction.\n\n**Why pairing helps.** Var(p_hat_A - p_hat_B) = [Var(A) + Var(B) - 2 Cov(A, B)]/n per case; when both versions find the same cases hard, Cov > 0 and the paired variance is smaller than the unpaired sum the two-sample test assumes. QED.",
            f"{LAB24} check T3"),
        thm("T4 Multiple comparisons: Boole's inequality and Bonferroni",
            "For events A_1..A_m (false alarm in test i), P(union A_i) <= sum P(A_i). Hence testing each of m hypotheses at level alpha/m keeps the family-wise error rate <= alpha under any dependence. If the tests are independent with levels alpha_i, FWER = 1 - prod(1 - alpha_i); with all alpha_i = alpha this is 1 - (1 - alpha)^m.",
            "For two events, P(A or B) = P(A) + P(B) - P(A and B) <= P(A) + P(B); induction on m gives Boole's inequality. With alpha_i = alpha/m, the sum is alpha. Under independence, P(no false alarm) = prod P(not A_i) = prod (1 - alpha_i), and FWER is its complement. For alpha = 0.05 and m = 20 that is 1 - 0.95^20 = 0.6415: in an unchanged system, about two of twenty slice gates are expected to fail. Bonferroni is conservative when tests are positively dependent; exact discrete tests have attained sizes below their nominal alpha, which makes it more conservative still (see check). QED.",
            f"{LAB24} check T4"),
    ],
    "problemSet": [
        prob("l24-p1", "An agent passes 47 of 50 golden cases. Compute the 95 % Wilson interval and the 95 % Wald interval (4 decimals). Which one would you report, and why?", "calculation", 1,
             f"p_hat = 0.94, z = 1.96. Wilson: [{q1[0]}, {q1[1]}]. Wald: 0.94 +/- 1.96 sqrt(0.94 * 0.06/50) = [{q1[2]}, {q1[3]}] - the upper end exceeds 1, an impossible value. Report Wilson: it is the inversion of the score test, stays in [0, 1], and has near-nominal coverage close to the boundary where agent pass rates live (T1 check: Wald 0.64 coverage at n = 20, p = 0.95).", 6),
        prob("l24-p2", "Starting from the score inequality |p_hat - p| <= z sqrt(p(1-p)/n), derive the Wilson interval's centre and half-width. Show that its centre is a weighted average of p_hat and 1/2 and give the weights.", "derivation", 2,
             "Square and collect: (1 + z^2/n) p^2 - (2 p_hat + z^2/n) p + p_hat^2 <= 0. Roots: [(2 p_hat + z^2/n) +/- (2z/sqrt(n)) sqrt(p_hat(1 - p_hat) + z^2/(4n))] / (2(1 + z^2/n)). Centre = (p_hat + z^2/(2n))/(1 + z^2/n) = w p_hat + (1 - w)(1/2) with w = n/(n + z^2) and 1 - w = z^2/(n + z^2) (because z^2/(2n) / (1 + z^2/n) = (z^2/(n+z^2)) * 1/2). Half-width = z/(1 + z^2/n) sqrt(p_hat(1 - p_hat)/n + z^2/(4n^2)). The shrinkage towards 1/2 is what keeps the interval away from the boundary for small n.", 8),
        prob("l24-p3", "Your gate must detect a drop from 95 % to 90 % with a one-sided test at alpha = 0.05 and power 0.8. (a) How many independent cases does the normal-approximation formula require? (b) For that n, what rejection rule does the exact binomial test use and what are its exact size and power? (c) How many cases at alpha = 0.01?", "calculation", 2,
             f"(a) z_0.95 = 1.6449, z_0.8 = 0.8416: n = ((1.6449 sqrt(0.95 * 0.05) + 0.8416 sqrt(0.90 * 0.10))/0.05)^2 -> {q3[0]}. (b) Reject if passes <= {q3[1]} of {q3[0]}: exact size {q3[2]} (<= 0.05), exact power {q3[3]} (a little under 0.8 because X is discrete - round n up if 0.8 is a hard requirement). (c) z_0.99 = 2.3263 gives n = {q3[4]}. Lesson 12's 20 cases are an order of magnitude short; they catch big breaks and named regressions, not 5-point drifts.", 8),
        prob("l24-p4", "Old and new prompts run on the same 300 cases: 238 pass both, 12 pass only with the old prompt, 4 only with the new one, 46 fail both. Compute the exact McNemar p-value, the continuity-corrected chi-square statistic and its p-value, and the p-value an (incorrect) unpaired two-proportion z-test would give for 250 vs 242 passes.", "calculation", 2,
             f"b = 12, c = 4, m = 16. Exact: 2 * P(Bin(16, 0.5) <= 4) = {q4[0]}. Chi-square with correction: (|12 - 4| - 1)^2/16 = 49/16 = {q4[1]}, p = {q4[2]}. Unpaired: p = {q4[3]}. Neither paired test reaches 0.05, but the paired analysis is far more sensitive than the unpaired one, which wastes the 284 concordant cases' information about shared difficulty. Practical reading: read the 12 regressions; if they share a cause, fix it rather than wait for significance.", 8),
        prob("l24-p5", "A colleague says: 'Version B's 95 % interval [0.86, 0.94] overlaps version A's [0.88, 0.95], so there is no difference.' Give two reasons why this inference is unsound for agent evaluation.", "short-answer", 2,
             "1) Overlap of two marginal intervals is not a test of the difference: intervals can overlap while the difference is significant, because the standard error of a difference is smaller than the sum of the two half-widths (it adds in quadrature). 2) If both versions ran on the same cases the data are paired; the correct test (McNemar) uses only discordant cases and can be much more powerful than any comparison of marginal intervals. Also, 'not significant' is not 'no difference' - report the interval for the difference and the power.", 6),
        prob("l24-p6", "An evaluation report checks 12 ticket categories, each with its own test at alpha = 0.05. Assuming independence and no real change, what is the probability of at least one false alarm? What per-test level does Bonferroni prescribe, and what FWER results under independence?", "calculation", 1,
             f"FWER = 1 - 0.95^12 = {q6[0]}: almost a coin flip. Bonferroni: alpha/12 = {q6[1]} per category; FWER = 1 - (1 - {q6[1]})^12 = {q6[2]} <= 0.05. The price is lower power per category; pre-register the categories you gate on and treat the rest as exploratory.", 5),
        prob("l24-p7", "Prove Boole's inequality for m events and deduce that Bonferroni controls the FWER without any independence assumption.", "proof", 1,
             "m = 1 trivial. Assume P(A_1 or ... or A_{m-1}) <= sum_{i<m} P(A_i). With B = union of the first m - 1 events, P(B or A_m) = P(B) + P(A_m) - P(B and A_m) <= P(B) + P(A_m) <= sum_{i<=m} P(A_i). Each test at level alpha/m has P(A_i) <= alpha/m under its null, so P(any false alarm) <= m * alpha/m = alpha. No independence was used - only additivity of probability and non-negativity of P(B and A_m).", 5),
        prob("l24-p8", "Lesson 12's gate requires a 95 % pass rate on 20 cases. (a) A run scores 19/20: give the 95 % Wilson interval. Is a true rate below 95 % consistent with it? (b) With the exact one-sided test at alpha = 0.05 and n = 20, what rejection rule, size and power do you get against a drop from 95 % to 85 %? (c) What do you recommend?", "calculation", 3,
             f"(a) [{q8[0]}, {q8[1]}]: true rates from about 76 % to 99 % are consistent; 19/20 says little about whether the bar is met. (b) Reject 'p = 0.95' if passes <= {q8[2]}; size {q8[3]}; power {q8[4]} against 85 % - two out of three ten-point drops go undetected. (c) Keep the per-case 'no previously passing case may fail' rule (it catches known regressions deterministically), add cases where failures are costly, report intervals, and use T2 to size a separate, larger regression suite for drift - e.g. 150 cases for a 95 % -> 90 % drop.", 8),
    ],
    "rubric": WRITTEN_RUBRIC,
    "projectFiles": [
        {"path": LAB24, "purpose": "Wilson/Wald intervals, exact coverage, sample size and exact power, McNemar, FWER; `check T1..T4`."},
        {"path": "labs/L500/24-evaluation-statistics/test_eval_stats.py", "purpose": "6 unit tests (python -m unittest)."},
    ],
    "runCommands": {"mac": "cd labs/L500/24-evaluation-statistics && python3 eval_stats.py && python3 eval_stats.py check T3",
                    "windows": "cd labs\\L500\\24-evaluation-statistics; py -3.12 eval_stats.py; py -3.12 eval_stats.py check T3"},
    "conceptNote": "content/concepts/L500/24-evaluation-statistics.md",
    "conceptSummary": "A pass rate is a binomial proportion: report Wilson intervals, size the golden set from the regression you must detect (n ~ 1/delta^2), compare versions on the same cases with McNemar (only discordant cases count), and correct for the number of slices you test.",
    "sources": [
        {"title": "NIST/SEMATECH e-Handbook of Statistical Methods 7.2.4.1 - Confidence intervals for proportions (Wilson method, exact binomial)", "url": "https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm"},
        {"title": "McNemar (1947) - Note on the sampling error of the difference between correlated proportions or percentages, Psychometrika 12(2):153-157", "url": "https://doi.org/10.1007/BF02295996"},
        {"title": "Jurafsky & Martin - ch. 3, training/dev/test sets and statistical power", "url": "https://web.stanford.edu/~jurafsky/slp3/3.pdf"},
    ],
    "seeAlso": [
        "ai-agents L300 #12 Evaluating agents with a golden set: the 20-case gate whose power T2 computes.",
        "ai-agents L300 #16 Red-teaming prompt injection: a block rate on 8 attacks is a proportion with a wide interval.",
        "ai-agents L400 #21 Governance and evaluation in production: the model-upgrade comparison is a paired design (T3); the drift alarm is a multiple-testing problem over time (T4).",
        "ai-agents L400 #22 An incident-triage agent: the capstone scorecard's per-milestone rates.",
    ],
    "next": "L500 #25 Foundations III: decision theory and planning - turning measured rates into decisions",
    "platforms": PLATFORMS,
    "validation": {"status": "validated-local",
                   "how": "python eval_stats.py (demo) and eval_stats.py check T1..T4 run on Python 3.12.15 (standard library only) in the Linux sandbox; outputs pasted into checkOutput; python -m unittest -> 6 tests OK; research/l500_checks.py re-runs every check.",
                   "pendingCi": ["macOS and Windows runs in the CI matrix (random.Random with fixed seeds and math.comb are platform-independent)"]},
}

# ============================================================== lesson 25
r1, r3, r4, r6, r7 = v("l25-p1"), v("l25-p3"), v("l25-p4"), v("l25-p6"), v("l25-p7")
L25 = {
    "id": "decision-planning", "number": 25, "level": "L500",
    "title": "Foundations III: decision theory and planning",
    "category": "theory: decisions, MDPs, search, computability",
    "description": "Expected utility, the expected cost of retries and why loops need budgets, MDPs and value iteration, BFS/A* versus LLM planning, and why no checker can decide what an arbitrary tool program will do - so agents use allow-lists.",
    "outcome": "You can justify a retry budget, an escalate-or-act threshold and an allow-list from first principles, verify a plan with search, and explain to a reviewer why 'just analyse the generated code' cannot replace capability restrictions.",
    "estimatedTime": "4-5 hours (lecture 90 min, lab 60 min, problem set 2 h)",
    "prerequisites": [
        "Probability: geometric distribution, expectation, conditional probability",
        "Discrete mathematics: graphs, induction, proof by contradiction",
        "Analysis: geometric series, max-norm, contraction mappings (Banach fixed-point theorem, statement only)",
        "Theory of computation: the halting problem (statement)",
        "Lesson 6: A minimal agent loop; Lesson 14: Reliability: timeouts, retries, budgets and fallbacks",
    ],
    "learningObjectives": [
        "Derive the expected number of attempts under a retry budget and the condition under which one more attempt lowers expected cost.",
        "Prove that the Bellman optimality operator is a gamma-contraction and use value iteration to evaluate an act-versus-escalate policy.",
        "Prove the optimality of A* with an admissible heuristic and critique LLM-generated plans against search guarantees.",
        "Explain, by reduction from the halting problem, why deciding whether an arbitrary tool program calls a dangerous tool is impossible, and evaluate allow-lists as the sound alternative.",
    ],
    "glossary": [
        {"term": "expected utility", "meaning": "EU(a) = sum_o P(o|a) U(o); choose the action with the highest EU under stated probabilities and utilities."},
        {"term": "retry budget", "meaning": "Maximum number of attempts k; bounds worst-case cost at k calls."},
        {"term": "MDP", "meaning": "States, actions, transition probabilities, rewards and discount gamma; a policy maps states to actions."},
        {"term": "Bellman optimality operator", "meaning": "(TV)(s) = max_a sum_s' P(s'|s,a)[r + gamma V(s')]."},
        {"term": "value iteration", "meaning": "Repeat V <- TV until the change is below a tolerance."},
        {"term": "admissible heuristic", "meaning": "h(n) never exceeds the true cost from n to the goal."},
        {"term": "consistent heuristic", "meaning": "h(n) <= c(n, m) + h(m) for every edge n -> m (implies admissible)."},
        {"term": "Rice's theorem", "meaning": "Every non-trivial property of the function a program computes is undecidable."},
        {"term": "allow-list", "meaning": "Explicit set of permitted tools/capabilities checked syntactically before execution."},
    ],
    "theorems": [
        thm("T1 Expected cost of retries and when another attempt pays",
            "If attempts succeed independently with probability p, the number of attempts until success N ~ Geometric(p) has E[N] = 1/p; with a budget of k attempts E[min(N, k)] = (1 - (1-p)^k)/p and P(give up) = (1-p)^k. More generally, if attempt i+1 succeeds with conditional probability p_i given i failures, a call costs c and giving up costs C_fail, then allowing attempt i+1 changes the expected cost by -P(reach attempt i+1) (p_i C_fail - c). Hence retry while p_i C_fail >= c: with constant p the optimal budget is 0 or unbounded; with decreasing p_i (correlated failures) it is finite; with p = 0 (a stuck loop) the cost without a budget is unbounded and a budget k bounds it by k c.",
            "**Tail sum.** For a non-negative integer variable Y, E[Y] = sum_{i>=0} P(Y > i). With Y = min(N, k): P(Y > i) = P(N > i) = (1 - p)^i for i < k and 0 for i >= k. So E[min(N, k)] = sum_{i=0}^{k-1} (1-p)^i = (1 - (1-p)^k)/p (geometric series); k -> infinity gives 1/p. Giving up means all k attempts fail: (1-p)^k.\n\n**Marginal attempt.** Let r_i = prod_{j<i} (1 - p_j) be the probability of reaching attempt i+1 (r_0 = 1). With budget k the expected cost is cost(k) = c sum_{i<k} r_i + C_fail r_k. Then cost(k+1) - cost(k) = c r_k + C_fail (r_{k+1} - r_k) = c r_k - C_fail r_k p_k = -r_k (p_k C_fail - c). The sign depends only on p_k C_fail - c. If p_k is constant the sign never changes; if p_k decreases (each failure is evidence the input is bad, the 4xx case of lesson 14) the sign turns negative at the first k with p_k C_fail < c, which is the optimal budget. If p = 0, cost(k) = c k -> infinity.\n\n**Engineering reading.** The budget is not chosen from the mean - with p = 0.7 the mean is 1.43 attempts - but to bound the case where your estimate of p is wrong. QED.",
            f"{LAB25} check T1"),
        thm("T2 Bellman optimality: value iteration converges to the unique optimal value",
            "For a finite MDP with discount gamma in [0, 1), the operator (TV)(s) = max_a sum_s' P(s'|s, a)[r(s, a, s') + gamma V(s')] satisfies ||TU - TW||_inf <= gamma ||U - W||_inf. Hence T has a unique fixed point V*, value iteration V_{t+1} = T V_t converges with ||V_t - V*|| <= gamma^t ||V_0 - V*||, and the policy that is greedy with respect to V* maximises expected discounted utility. A one-step decision (no future) reduces to choosing argmax_a EU(a).",
            "For any functions f, g of a: |max_a f(a) - max_a g(a)| <= max_a |f(a) - g(a)| (if the left max is attained at a*, max f - max g <= f(a*) - g(a*); symmetric for the other sign). Apply it with f(a) = sum P(s'|s,a)[r + gamma U(s')] and g the same with W: the rewards cancel and |sum_s' P(s'|s,a) gamma (U(s') - W(s'))| <= gamma max_s' |U(s') - W(s')| because the P(.|s,a) sum to 1. Taking the max over s gives the contraction. The Banach fixed-point theorem (complete metric space, contraction) gives existence, uniqueness and the geometric rate. Greedy optimality: the greedy policy's value satisfies V^pi = T^pi V^pi with T^pi V* = T V* = V*, so V^pi = V* (Sutton & Barto, ch. 3-4). QED.\n\n**Agent reading.** 'Escalate' is an action with a utility, not a failure; whether to act or escalate is decided by numbers you can audit, and it flips when an error rate crosses a computable threshold (check: 0.0627).",
            f"{LAB25} check T2"),
        thm("T3 BFS and A* optimality; overestimating heuristics break it",
            "In a graph with unit edge costs, BFS returns a shortest path. In a graph with non-negative edge costs, A* (expand the frontier node with the smallest f = g + h) returns an optimal path when h is admissible (tree search) or consistent (graph search with a closed set) (Hart, Nilsson & Raphael 1968). An overestimating heuristic can make A* return a suboptimal path.",
            "**BFS.** By induction on d, BFS dequeues every node at depth d before any node at depth d + 1, and the first time a node is discovered it is via a shortest path; so the goal is reached with its shortest distance.\n\n**A* (admissible).** Let C* be the optimal cost and suppose A* selects the goal G with g(G) > C*. Along an optimal path there is always a frontier node n whose g(n) equals its optimal cost g*(n) (the deepest expanded node of that path has a successor on the frontier). Then f(n) = g*(n) + h(n) <= g*(n) + h*(n) = C* < g(G) = f(G) (h(G) = 0), so n has a smaller f and would be expanded before G - a contradiction. With a closed set, consistency guarantees that f is non-decreasing along any path, so a node is first expanded with its optimal g. \n\n**Overestimate.** If h(n) > h*(n) on an optimal path, f(n) may exceed f of a worse goal path; the check's plan graph shows A* returning cost 8 instead of 4 when h(search_kb) = 9 > h* = 2.\n\n**LLM planning.** An LLM proposes one plan sampled from a distribution; it neither enumerates alternatives nor guarantees cost or validity. Treat it as a heuristic or a candidate: verify preconditions and cost in code, or search over its proposals. QED.",
            f"{LAB25} check T3"),
        thm("T4 Deciding whether an arbitrary tool program calls delete is impossible (Rice) - hence allow-lists",
            "Let programs be written in a Turing-complete language with access to a tool delete. There is no algorithm D that, for every program P, halts and correctly answers whether P can ever call delete. More generally (Rice 1953), every non-trivial property of a program's behaviour is undecidable. Consequently a checker for agent-generated programs must be incomplete (bounded execution, may answer 'unknown') or conservative (decide a syntactic property such as 'names only allow-listed tools', which may reject safe programs).",
            "Suppose D exists. Given any program M and input x, construct P_{M,x}: 'simulate M on x, using no tools; when the simulation halts, call delete'. The construction is mechanical. P_{M,x} calls delete iff M halts on x. Then H(M, x) = D(P_{M,x}) would decide the halting problem, which Turing proved undecidable. Contradiction, so no D exists. The same reduction works for any behavioural property that some program has and some program lacks (Rice).\n\n**What remains decidable.** (1) Bounded execution: run P for B steps - correct 'calls delete' answers when it happens early, 'unknown' otherwise (check: collatz_then_delete(27) needs 111 steps; budgets 10 and 100 say unknown). Nobody has proved that the Collatz loop halts for every n, so no one can certify collatz_then_delete for all inputs today. (2) Syntactic restriction: whether the program text names a tool outside an allow-list is decidable in linear time and sound (anything accepted cannot call a forbidden tool if tool access goes through names), but conservative: never_deletes is rejected although its delete branch is unreachable.\n\n**Agent reading.** This is why lessons 11, 15, 16 and 20 restrict capabilities at the boundary (allow-lists, approval for side effects) instead of trusting a model - or a smarter analyser - to predict what generated code will do. QED.",
            f"{LAB25} check T4"),
    ],
    "problemSet": [
        prob("l25-p1", "A flaky tool succeeds independently with probability 0.6 per call. With a budget of 4 attempts, compute the expected number of calls and the probability of giving up. What is the expected number of calls without a budget?", "calculation", 1,
             f"E[min(N, 4)] = (1 - 0.4^4)/0.6 = 1 + 0.4 + 0.16 + 0.064 = {r1[0]}. P(give up) = 0.4^4 = {r1[1]}. Without a budget E[N] = 1/0.6 = {r1[2]} - finite, but only because p > 0; the budget protects against p being 0 in production.", 5),
        prob("l25-p2", "Prove E[min(N, k)] = sum_{i=0}^{k-1} (1-p)^i for N ~ Geometric(p) using the tail-sum formula, and prove the tail-sum formula for non-negative integer random variables.", "proof", 2,
             "Tail sum: Y = sum_{i>=0} 1[Y > i] for a non-negative integer Y (there are exactly Y indices i in {0, ..., Y-1}); take expectations and swap sum and expectation (non-negative terms, Tonelli) to get E[Y] = sum_i P(Y > i). For Y = min(N, k): Y > i iff N > i and i < k. P(N > i) = P(first i attempts fail) = (1-p)^i. So E[Y] = sum_{i=0}^{k-1} (1-p)^i = (1 - (1-p)^k)/p.", 6),
        prob("l25-p3", "A refund agent can auto-approve small refunds. Auto-approval yields utility +3 (customer served, no staff time) when correct and -60 when wrong (money lost, complaint); it is wrong 4 % of the time. Human review always gets it right but costs 2 units of staff time (utility 3 - 2). Compute both expected utilities. Above what error rate should the agent stop auto-approving?", "calculation", 2,
             f"EU(auto) = 0.96 * 3 + 0.04 * (-60) = {r3[0]}. EU(review) = 3 - 2 = {r3[1]}. Review wins. Break-even: 3(1 - e) - 60e = 1 => 3 - 63e = 1 => e = 2/63 = {r3[2]} (about 3.2 %). Because the error rate itself is estimated (lesson 24), compare the upper end of its Wilson interval with the threshold before enabling auto-approval.", 6),
        prob("l25-p4", "In the lab's ticket MDP set the wrong-refund probability to 0.03 (resolved 0.77, tool error 0.20, rewards +9 / -1 / -51 including the step cost, gamma = 0.95). Compute the value of 'always auto' in closed form and decide between auto and escalate (+4).", "calculation", 2,
             f"V = 0.77 * 9 + 0.20 * (-1 + 0.95 V) + 0.03 * (-51) => V (1 - 0.19) = 6.93 - 0.20 - 1.53 = 5.20 => V = 5.20/0.81 = {r4[0]} > 4, so auto. Value iteration in decision_planning.py (make_mdp(0.03)) gives the same number.", 6),
        prob("l25-p5", "Prove that the Bellman optimality operator is a gamma-contraction in the max-norm. Where exactly does the proof use gamma < 1 and that the transition probabilities sum to 1?", "proof", 3,
             "Use |max_a f - max_a g| <= max_a |f - g|. For fixed s, a the reward terms cancel and |sum_s' P(s'|s,a) gamma (U(s') - W(s'))| <= gamma sum_s' P(s'|s,a) |U(s') - W(s')| <= gamma ||U - W|| sum_s' P(s'|s,a) = gamma ||U - W||: the last step uses sum_s' P = 1 (for terminal states with no successors the term is 0 <= gamma ||U - W||). Max over a then over s: ||TU - TW|| <= gamma ||U - W||. gamma < 1 is what makes this a contraction (factor strictly below 1); with gamma = 1 the operator is only non-expansive, and convergence needs extra conditions (e.g. guaranteed termination).", 8),
        prob("l25-p6", "For the lab's plan graph (start -> lookup_order 1, start -> search_kb 2, lookup_order -> check_policy 6, search_kb -> check_policy 1, check_policy -> draft_reply 1) decide whether h = {start: 4, lookup_order: 6, search_kb: 2, check_policy: 1, draft_reply: 0} is admissible and consistent, and give the cost A* returns.", "calculation", 2,
             f"True costs-to-go h*: start 4, lookup_order 7, search_kb 2, check_policy 1, draft_reply 0; h <= h* everywhere, so admissible: True. Consistency, edge by edge: 4 <= 1 + 6, 4 <= 2 + 2, 6 <= 6 + 1, 2 <= 1 + 1, 1 <= 1 + 0 - consistent: True. A* returns cost 4 via start -> search_kb -> check_policy -> draft_reply.", 5),
        prob("l25-p7", "A model call fails in a correlated way: attempt i+1 succeeds with probability p_i = 0.8 * 0.4^i given i failures. A call costs 2, giving up costs 30. Find the cost-minimising budget k* and compare the expected cost with k = 1 and k = 20.", "calculation", 2,
             f"Retry while p_i * 30 >= 2, i.e. p_i >= 0.0667: p_0 = 0.8, p_1 = 0.32, p_2 = 0.128, p_3 = 0.0512 < 0.0667 -> k* = 3 attempts. Expected cost: k* = 3 -> {r7[1]}; k = 1 -> {r7[2]} (2 + 0.2 * 30); k = 20 -> {r7[3]}. Under correlated failures extra attempts waste money; the optimal budget is small.", 6),
        prob("l25-p8", "A teammate proposes replacing the tool allow-list with an LLM-based 'intent analyser' that reads each generated script and approves it if it will not delete data. Using T4, write a short argument (150-250 words) for the design review.", "essay", 2,
             "Model answer: Deciding whether an arbitrary script will ever call delete is undecidable: a perfect analyser would solve the halting problem via the construction 'run M on x, then delete'. So any analyser - LLM or static - must sometimes be wrong or say unknown. An LLM analyser adds two further problems: its errors are not bounded or characterised (lesson 24: we would need a large labelled set to estimate them, and the rate would drift with model upgrades), and it reads attacker-controlled text, so prompt injection (lesson 16) can steer its verdict. An allow-list decides a different, syntactic question - which tools can the script name? - exactly and in linear time; it is sound (if tool access goes through named, mediated calls) and fails safe by rejecting. The analyser can still be useful as an explainer or a pre-filter that adds friction, but the enforcement point must be the allow-list plus approval for side effects (lessons 11, 15, 20).", 8),
    ],
    "rubric": WRITTEN_RUBRIC,
    "projectFiles": [
        {"path": LAB25, "purpose": "Expected utility, retry costs, ticket MDP + value iteration, BFS/A*, budgeted checker vs allow-list; `check T1..T4`."},
        {"path": "labs/L500/25-decision-planning/test_decision_planning.py", "purpose": "5 unit tests (python -m unittest)."},
    ],
    "runCommands": {"mac": "cd labs/L500/25-decision-planning && python3 decision_planning.py && python3 decision_planning.py check T4",
                    "windows": "cd labs\\L500\\25-decision-planning; py -3.12 decision_planning.py; py -3.12 decision_planning.py check T4"},
    "conceptNote": "content/concepts/L500/25-decision-planning.md",
    "conceptSummary": "Retry while p_i C_fail >= c, and always cap loops because p can be 0; act-or-escalate is an expected-utility (MDP) decision that flips at a computable error rate; search with admissible heuristics is optimal, LLM plans are unverified proposals; what arbitrary code will do is undecidable, so enforce capabilities with allow-lists.",
    "sources": [
        {"title": "Sutton & Barto - Reinforcement Learning: An Introduction, 2nd ed. (MDPs, Bellman equations, value iteration)", "url": "http://incompleteideas.net/book/the-book-2nd.html"},
        {"title": "Hart, Nilsson & Raphael (1968) - A Formal Basis for the Heuristic Determination of Minimum Cost Paths, IEEE Trans. SSC 4(2)", "url": "https://ieeexplore.ieee.org/document/4082128"},
        {"title": "Rice (1953) - Classes of recursively enumerable sets and their decision problems, Trans. AMS 74:358-366", "url": "https://www.ams.org/journals/tran/1953-074-02/S0002-9947-1953-0053041-6/home.html"},
        {"title": "Yao et al. 2023 - ReAct (LLM agents interleaving reasoning and acting; repetitive-loop failure mode)", "url": "https://arxiv.org/abs/2210.03629"},
    ],
    "seeAlso": [
        "ai-agents L100 #6 A minimal agent loop: the step budget is T1's worst-case bound.",
        "ai-agents L300 #14 Reliability: timeouts, retries, budgets and fallbacks: retry only what can succeed later (p_i > 0).",
        "ai-agents L300 #15 Safe tool execution: approval for side effects is the escalate action of T2.",
        "ai-agents L400 #20 Deterministic core, LLM at the edge: capability boundaries because behaviour is undecidable (T4).",
        "ai-agents L400 #17 Multi-agent patterns: when one agent with tools is enough: planner outputs are proposals to verify (T3).",
    ],
    "next": "L500 #26 Ethics, society and professional responsibility - who answers when the agent's decision is wrong",
    "platforms": PLATFORMS,
    "validation": {"status": "validated-local",
                   "how": "python decision_planning.py (demo) and check T1..T4 run on Python 3.12.15 (standard library only) in the Linux sandbox; outputs pasted into checkOutput; python -m unittest -> 5 tests OK; research/l500_checks.py re-runs every check.",
                   "pendingCi": ["macOS and Windows runs in the CI matrix"]},
}

# ============================================================== lesson 26
e3, e4 = v("l26-p3"), v("l26-p4")
L26 = {
    "id": "ethics-responsibility", "number": 26, "level": "L500",
    "title": "Ethics, society and professional responsibility for AI agents",
    "category": "ethics, law and standards",
    "description": "Accountability for what an agent says and does, over-reliance and human factors, bias and fairness, privacy and data protection, transparency, and when not to automate - grounded in the ACM Code, NIST AI RMF 1.0, the EU AI Act and GDPR, and analysed through a real tribunal decision.",
    "outcome": "You can analyse an agent deployment for accountability, oversight, fairness, privacy and transparency obligations, cite the primary source for each, quantify the effect of human factors on harm, and argue when a task should not be automated.",
    "estimatedTime": "3-4 hours (seminar 90 min, case analysis 2 h)",
    "prerequisites": [
        "Lesson 11: Guardrails basics; Lesson 15: Safe tool execution; Lesson 21: Governance and evaluation in production",
        "Lesson 24 (Wilson intervals) and Lesson 25 (expected utility) for the quantitative questions",
        "No legal background assumed; reading statutes and decisions is practised in the lesson",
    ],
    "learningObjectives": [
        "Explain who is accountable for an agent's statements and actions, using a tribunal decision and the ACM Code.",
        "Analyze how automation bias undermines human oversight and evaluate oversight designs against EU AI Act Art. 14(4).",
        "Evaluate an agent's handling of personal data against ACM 1.6 and GDPR Art. 22, and its disclosure duties against AI Act Art. 50(1).",
        "Critique a proposed automation using expected-harm arithmetic and the 'do not deploy' criteria in ACM 2.5/2.9 and the NIST AI RMF.",
    ],
    "glossary": [
        {"term": "deployer", "meaning": "Person or organisation using an AI system under its authority (AI Act Art. 3(4)); answerable for its use."},
        {"term": "negligent misrepresentation", "meaning": "Tort: an inaccurate statement made without reasonable care, reasonably relied on, causing loss (applied in Moffatt v. Air Canada)."},
        {"term": "automation bias", "meaning": "Tendency to rely or over-rely on automated output (AI Act Art. 14(4)(b)); 'misuse' in Parasuraman & Riley."},
        {"term": "human oversight", "meaning": "Ability of assigned people to understand, monitor, override and stop a system (AI Act Art. 14)."},
        {"term": "data minimisation", "meaning": "Collect only the personal data necessary for the purpose (ACM 1.6)."},
        {"term": "solely automated decision", "meaning": "Decision with legal or similarly significant effect and no meaningful human involvement (GDPR Art. 22)."},
        {"term": "residual risk", "meaning": "Risk remaining after risk treatment (NIST AI RMF 1.2.3, citing ISO Guide 73)."},
    ],
    "caseStudy": {
        "case": "Moffatt v. Air Canada, 2024 BCCRT 149 (British Columbia Civil Resolution Tribunal, 14 February 2024). After a grandparent's death, a customer asked the airline website's support chatbot about bereavement fares. The chatbot said he could buy now and apply for the reduced fare within 90 days of ticketing; a hyperlinked policy page said bereavement requests after travel were not accepted. He bought two full-price tickets relying on the chatbot, applied within 90 days, and was refused. An airline representative later admitted the chatbot had used 'misleading words'. Before the tribunal the airline argued it could not be held liable for information provided by one of its agents, servants or representatives, including a chatbot. The tribunal found the airline owed a duty of care, that the chatbot is 'still just a part of Air Canada's website', that the airline 'is responsible for all the information on its website', that it did not take reasonable care to ensure the chatbot was accurate, and that the customer's reliance was reasonable; it awarded the fare difference (650.88 CAD) plus interest and fees (812.02 CAD in total). Your company is about to launch a refund-and-policy agent built with the patterns of lessons 7-22. Use the case to review it.",
        "stakeholders": [
            "Customers relying on answers, including people in distress or with limited time (vulnerable users)",
            "The deploying company (legal liability, reputation, cost of errors)",
            "Support staff who review agent output or handle escalations (workload, automation bias, deskilling)",
            "Engineers and product owners who design, evaluate and operate the agent (professional duties under the ACM Code)",
            "Model and tool providers (upstream risk, documentation of limitations)",
            "Regulators and tribunals (consumer protection, data protection, AI Act authorities)",
            "Customers whose personal data is processed in prompts, memories and traces",
        ],
        "questions": [
            "Who was accountable for the chatbot's statement, and why did the 'separate entity' argument fail? Which ACM principles (cite numbers) would have required the company to act differently before launch?",
            "The correct policy was one click away. Why was that not a defence? What does this imply for disclaimers and 'see policy page' links in agent answers?",
            "Which engineering controls from lessons 7-22 would most plausibly have prevented the wrong answer (name the lesson and mechanism)? Which would only have detected it after the fact?",
            "If the company adds human review of policy answers, how could automation bias defeat it? Propose two measures and relate them to AI Act Art. 14(4)(b) and (d).",
            "What personal data does a refund agent process, how long should transcripts and memories be kept, and when does GDPR Art. 22 apply to a refund decision?",
            "What must the agent disclose to users from 2 August 2026 under AI Act Art. 50(1)?",
            "Is there a class of questions this agent should not answer at all? Argue using ACM 2.5/2.9 and the NIST AI RMF 'cease deployment' criterion, and quantify with expected harm.",
        ],
        "frameworks": [
            "ACM Code of Ethics and Professional Conduct (2018): 1.2 Avoid harm; 1.3 Be honest and trustworthy (do not misrepresent an organisation's policies); 1.4 Be fair; 1.6 Respect privacy; 2.5 Comprehensive evaluations; 2.9 Robustly and usably secure (and 'not to implement' when harm is predictable); 3.7 Systems integrated into society.",
            "NIST AI 100-1, AI RMF 1.0 (2023): trustworthiness characteristics (valid and reliable; safe; secure and resilient; accountable and transparent; explainable and interpretable; privacy-enhanced; fair - with harmful bias managed); functions GOVERN, MAP, MEASURE, MANAGE; risk tolerance and 'cease in a safe manner'.",
            "Regulation (EU) 2024/1689 (AI Act), as amended by Regulation (EU) 2026/1744: Art. 14 human oversight (automation bias, override, stop); Art. 50(1) disclosure of interaction with an AI system (applies from 2 August 2026); Art. 4 AI literacy.",
            "Regulation (EU) 2016/679 (GDPR): Art. 22 solely automated decisions with legal or similarly significant effects; right to human intervention and to contest.",
            "Human factors: Parasuraman & Riley (1997) - use, misuse (over-reliance), disuse, abuse of automation.",
            "Moffatt v. Air Canada, 2024 BCCRT 149 - negligent misrepresentation by a chatbot; deployer liability.",
        ],
        "modelAnswer": "1) Accountability: the airline. The tribunal treated the chatbot as part of the website; a company is responsible for all information on its website, whether static or generated, so delegating to software does not delegate responsibility. Before launch, ACM 1.3 (do not misrepresent an organisation's policies; be transparent about limitations), 2.5 (thorough evaluation, extraordinary care for ML risks) and 1.2 (avoid harm) required evaluating the chatbot against the actual policy. 2) The link was no defence because the customer had no reason to know which part of the site was reliable, and the company did not explain why a customer should double-check one part against another; disclaimers do not cure a wrong affirmative statement. Design implication: answers about entitlements must be generated from, and checked against, the authoritative policy, not merely link to it. 3) Prevention: lesson 7 RAG with citation checks against the policy source and a minimum-score refusal; lesson 20 'code decides' - eligibility rules (bereavement, retroactivity) computed by code from policy data, the model only explains; lesson 12 golden set including policy edge cases (retroactive claims) with a regression gate; lesson 21 pinning and re-evaluation on model or policy change. Detection only: lesson 13 traces, lesson 21 drift monitoring, complaint review. 4) Automation bias: reviewers who see a fluent answer and a high approval rate start approving by default (Parasuraman & Riley's misuse). Measures: show the policy clause next to the draft and require the reviewer to tick which clause applies (Art. 14(4)(a), (c): understand and interpret); seed known-wrong drafts and measure catch rate; make reject/override one click and protected from performance metrics (Art. 14(4)(d)); keep a stop switch (Art. 14(4)(e)). Problem 3's arithmetic shows that catch rate falling from 90 % to 50 % nearly doubles monthly harm cost. 5) Data: name, booking, possibly health or death information (sensitive context), payment data; minimise what enters prompts, redact (lesson 11), set and enforce retention for transcripts and memories (lesson 21), keep traces free of personal data where possible. A refund refusal decided solely by the agent can be a decision with similarly significant effect: provide human intervention and a way to contest (GDPR Art. 22(3)) - in practice, route refusals to a person. 6) Art. 50(1): users must be informed they are interacting with an AI system unless obvious, clearly and at the latest at first interaction (Art. 50(5)). 7) Do not let the agent make binding statements about entitlements, legal rights or refunds outside code-checked rules; route bereavement and other distress cases to a person. Justification: harm is foreseeable (ACM 2.9), the error rate on rare policy edge cases cannot be estimated precisely from small samples (lesson 24), and expected-harm arithmetic (lesson 25) favours review when the error cost is high relative to review cost.",
    },
    "problemSet": [
        prob("l26-p1", "Map each of the following agent features to the ACM Code principle(s) it serves and to one NIST AI RMF trustworthiness characteristic: (a) answers cite the policy paragraph used; (b) per-language pass rates in the eval report; (c) a 30-day retention job for transcripts; (d) refunds above a threshold need approval.", "short-answer", 1,
             "(a) ACM 1.3 honesty/transparency, 2.5 evaluation; NIST accountable and transparent / explainable. (b) ACM 1.4 fairness; NIST fair - with harmful bias managed, and valid and reliable (disaggregated accuracy). (c) ACM 1.6 (retention periods defined and enforced, minimum data); NIST privacy-enhanced. (d) ACM 1.2 avoid harm, 2.9 secure; NIST safe, and accountable (a named person decides). Credit any defensible mapping with a reason.", 6),
        prob("l26-p2", "Explain automation bias using Parasuraman & Riley's categories (use, misuse, disuse, abuse). Give one agent-specific example of each and the design measure that counters it.", "short-answer", 2,
             "Use: choosing to engage the agent - counter with clear capability statements. Misuse (over-reliance): reviewers approve drafts without reading - counter with evidence display, seeded errors, catch-rate metrics, limited review load. Disuse (under-use, often after false alarms): staff ignore a guardrail that flags too often - counter by tuning thresholds on base rates and measuring false-alarm rate. Abuse (automating without regard to human performance): management removes the human step because the agent 'is right 98 % of the time' and leaves staff only the hardest cases without context - counter with human-factors review of role design, staged rollout and monitoring.", 6),
        prob("l26-p3", "A policy-answering agent handles 10,000 questions a month with a 2 % error rate; each wrong answer costs 200 on average (refunds, complaints, rework). Option A: no review. Option B: review every answer at 1.50 each; reviewers catch 90 % of errors. Option C: review only refund/policy answers - 30 % of traffic that contains 80 % of the errors - with the same 90 % catch rate. Option C': as C, but automation bias lowers the catch rate to 50 %. Compute the monthly cost of each option.", "calculation", 2,
             f"Errors per month: 10,000 * 0.02 = 200. A: 200 * 200 = {e3[0]}. B: review 10,000 * 1.50 = 15,000 + residual errors 200 * 0.1 = 20 -> 4,000; total {e3[1]}. C: review 3,000 * 1.50 = 4,500; caught 0.9 * 0.8 * 200 = 144; residual 56 * 200 = 11,200; total {e3[2]}. C': caught 0.5 * 160 = 80, residual 120 * 200 = 24,000; total {e3[3]}. Targeted review is cheapest only while reviewers stay vigilant: the human-factors assumption is worth 12,800 a month and must be measured (seeded errors), not assumed.", 6),
        prob("l26-p4", "From the tribunal's figures: the customer paid 1,630.36 CAD for two flights; the tribunal found the bereavement fares, including fixed charges and taxes, would have cost 979.48 CAD. Compute the damages and the total award with 36.14 CAD pre-judgment interest and 125 CAD fees. Then explain in one sentence why the tribunal's adverse inference about the fare value matters for engineers keeping evidence.", "calculation", 1,
             "Damages = 1,630.36 - 979.48 = 650.88 CAD; total = 650.88 + 36.14 + 125.00 = 812.02 CAD (matches the order). The tribunal drew an adverse inference because the airline, best placed to prove the real fare, provided no evidence - an organisation that cannot produce its agent's logs, configuration and policy versions will struggle to defend what its agent said, so the audit trail of lessons 13, 15 and 21 is also legal evidence.", 5),
        prob("l26-p5", "From 2 August 2026, what does AI Act Art. 50(1) require of a customer-facing agent, when must the information be given (Art. 50(5)), and how did Regulation (EU) 2026/1744 change the timetable for high-risk obligations?", "short-answer", 1,
             "Art. 50(1): providers must design systems that interact directly with people so that those people are informed they are interacting with an AI system, unless obvious to a reasonably well-informed, observant and circumspect person in context. Art. 50(5): in a clear and distinguishable manner at the latest at the time of first interaction, meeting accessibility requirements. The Digital Omnibus on AI (Regulation (EU) 2026/1744, in force 27 July 2026) postponed high-risk obligations: Annex III systems from 2 August 2026 to 2 December 2027, Annex I (product legislation) systems to 2 August 2028; the Art. 50 transparency date of 2 August 2026 stayed.", 5),
        prob("l26-p6", "Essay (600-800 words): 'Our agent is 98 % accurate on the golden set, so it is safe to let it decide refunds without review.' Evaluate this claim using at least three primary sources from this lesson, lesson 24's statistics and lesson 25's expected-utility reasoning. Conclude with a deployment recommendation.", "essay", 3,
             "A strong answer: (1) questions the number - on what n, with what Wilson interval (98 % of 50 cases is compatible with roughly 89-100 %), on which slices (fairness, ACM 1.4; NIST disaggregation), and whether the golden set contains the rare, costly cases (Moffatt's retroactive claim); (2) computes expected harm per decision with the upper end of the error interval and a realistic error cost, versus review cost (lesson 25 break-even); (3) identifies whose harm it is and whether they can contest (GDPR Art. 22; ACM 1.2), and the deployer's accountability (Moffatt; NIST accountable and transparent); (4) considers human factors - if review is added, automation bias (AI Act Art. 14(4)(b); Parasuraman & Riley); (5) applies the 'do not deploy' criteria (ACM 2.5/2.9; NIST cease if unacceptable) to the high-cost slice; (6) recommends a split: code-decided auto-approval below a threshold for well-measured cases, human decision for refusals and sensitive cases, disclosure under Art. 50(1), monitoring and a stop switch. Graded with the rubric.", 20),
    ],
    "rubric": [
        {"criterion": "Use of primary sources", "excellent": "Quotes or precisely paraphrases the relevant article/principle/paragraph with its number, and applies it to the facts.",
         "adequate": "Names the right sources but applies them loosely.", "inadequate": "No sources, secondary summaries only, or misstated law.", "weight": 25},
        {"criterion": "Stakeholder and harm analysis", "excellent": "Identifies all affected parties including indirect ones, and who bears which harm; considers vulnerable users.",
         "adequate": "Main stakeholders and harms identified.", "inadequate": "Only the company's perspective.", "weight": 20},
        {"criterion": "Quantitative reasoning", "excellent": "Uses intervals and expected-harm arithmetic correctly, with stated assumptions and sensitivity (e.g. catch rate).",
         "adequate": "Some numbers, assumptions implicit.", "inadequate": "No quantification or wrong arithmetic.", "weight": 20},
        {"criterion": "Engineering controls", "excellent": "Maps each risk to a concrete mechanism from L100-L400 and says whether it prevents or only detects.",
         "adequate": "Lists relevant controls.", "inadequate": "Generic 'add guardrails'.", "weight": 20},
        {"criterion": "Judgement and recommendation", "excellent": "Clear, proportionate recommendation including what not to automate, with residual risk stated.",
         "adequate": "Recommendation present but weakly justified.", "inadequate": "No recommendation or one that ignores the analysis.", "weight": 15},
    ],
    "conceptNote": "content/concepts/L500/26-ethics-responsibility.md",
    "conceptSummary": "The deployer answers for its agent (Moffatt v. Air Canada); human oversight fails under automation bias unless designed and measured (AI Act Art. 14(4)); fairness needs disaggregated evaluation; privacy needs minimisation and retention; people must be told they are talking to an AI (Art. 50(1), from 2 Aug 2026); and when harm is predictable and unmeasurable, do not automate (ACM 2.5/2.9, NIST).",
    "sources": [
        {"title": "ACM Code of Ethics and Professional Conduct (2018)", "url": "https://www.acm.org/code-of-ethics"},
        {"title": "NIST AI 100-1 - Artificial Intelligence Risk Management Framework (AI RMF 1.0), January 2023", "url": "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf"},
        {"title": "NIST AI RMF page (revision status; Generative AI Profile NIST-AI-600-1)", "url": "https://www.nist.gov/itl/ai-risk-management-framework"},
        {"title": "Regulation (EU) 2024/1689 (Artificial Intelligence Act), EUR-Lex (consolidated version 27/07/2026)", "url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng"},
        {"title": "Regulation (EU) 2026/1744 (Digital Omnibus on AI), Official Journal", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202601744"},
        {"title": "European Parliament Legislative Train - Digital Omnibus on AI (adoption and publication dates)", "url": "https://www.europarl.europa.eu/legislative-train/spotlight-JD26/file-digital-omnibus-on-ai"},
        {"title": "Regulation (EU) 2016/679 (GDPR), Art. 22 - text as adopted (legislation.gov.uk mirror of the OJ version)", "url": "https://www.legislation.gov.uk/eur/2016/679/article/22/adopted"},
        {"title": "Moffatt v. Air Canada, 2024 BCCRT 149 - reasons for decision (copy hosted by The Sedona Conference)", "url": "https://www.thesedonaconference.org/sites/default/files/meeting_paper/Moffet%20v%20AirCanada.pdf"},
        {"title": "Parasuraman & Riley (1997) - Humans and Automation: Use, Misuse, Disuse, Abuse, Human Factors 39(2):230-253", "url": "https://web.mit.edu/16.459/www/parasuraman.pdf"},
    ],
    "seeAlso": [
        "ai-agents L200 #11 Guardrails basics: redaction and approval are the privacy and oversight mechanisms.",
        "ai-agents L300 #15 Safe tool execution: approval queue and audit log - evidence of who decided.",
        "ai-agents L400 #20 Deterministic core, LLM at the edge: entitlements decided by code from policy data.",
        "ai-agents L400 #21 Governance and evaluation in production: retention, pinning, monitoring.",
    ],
    "next": "L500 #27 Reading seminar: the Transformer and ReAct papers",
    "platforms": PLATFORMS,
    "validation": {"status": "validated-local",
                   "how": "No lab code; the two calculation problems (26-p3, 26-p4) are recomputed by research/l500_checks.py. Statute and decision text checked against the retrieved primary sources on 2026-10-30 (see research/L500-evidence.md).",
                   "pendingCi": []},
}

# ============================================================== lesson 27
s1, s3 = v("l27-p1"), v("l27-p3")
L27 = {
    "id": "reading-seminar", "number": 27, "level": "L500",
    "title": "Reading seminar: Attention Is All You Need and ReAct",
    "category": "primary literature",
    "description": "Read, summarise and critique the two papers this course rests on: Vaswani et al. 2017 (the Transformer) and Yao et al. 2023 (ReAct). Guided questions, a critical response, and calculations that connect each paper to lessons 23-25.",
    "outcome": "You can explain each paper's claim, mechanism and evidence in your own words, check a key equation or number yourself, and write a critical response that separates what was measured from what was conjectured.",
    "estimatedTime": "5-6 hours (reading 3 h, seminar 90 min, response 1.5 h)",
    "prerequisites": [
        "Lesson 23 (attention, softmax, 1/sqrt(d)) and Lesson 24 (Wilson intervals) for the calculations",
        "Lesson 6: A minimal agent loop (the loop ReAct prompts)",
        "Reading academic English; no prior paper-reading experience assumed",
    ],
    "learningObjectives": [
        "Summarise each paper's research question, mechanism and evidence accurately and in your own words.",
        "Analyze one central equation or table of each paper by recomputing it.",
        "Evaluate the strength of each paper's evidence (baselines, sample sizes, variance, ablations) using lesson 24's tools.",
        "Critique the gap between each paper's setting and production agents, including safety limitations the authors state.",
    ],
    "glossary": [
        {"term": "ablation", "meaning": "Experiment that removes or varies one component to measure its contribution (Transformer Table 3; ReAct's Act-only and CoT baselines)."},
        {"term": "BLEU", "meaning": "Machine-translation metric based on n-gram overlap with reference translations."},
        {"term": "few-shot prompting", "meaning": "Conditioning a frozen model on a handful of worked examples in the prompt instead of training it."},
        {"term": "chain-of-thought (CoT)", "meaning": "Prompting a model to write intermediate reasoning before the answer."},
        {"term": "self-consistency (CoT-SC)", "meaning": "Sample several CoT answers and take the majority."},
        {"term": "exact match (EM)", "meaning": "Share of answers identical to the reference after normalisation (HotpotQA metric)."},
    ],
    "readings": [
        {"citation": "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention Is All You Need. Advances in Neural Information Processing Systems 30. arXiv:1706.03762 (v7, 2 Aug 2023).",
         "url": "https://arxiv.org/abs/1706.03762",
         "why": "Every model behind the course's chat-completions endpoint is a Transformer. The paper defines scaled dot-product and multi-head attention (lesson 23's T2 is its footnoted variance argument), motivates attention by per-layer cost, parallelism and path length, and is the reason context length drives cost (lessons 9 and 19). Licence: arXiv perpetual non-exclusive licence - read it there; this course summarises and does not reproduce it.",
         "guidingQuestions": [
             "State the problem the paper addresses and the one architectural change it proposes. What did recurrence cost that attention avoids (Sec. 1, 4)?",
             "Re-derive equation (1) and the reason for dividing by sqrt(d_k) given in Sec. 3.2.1. What exactly do the authors claim, and what do they only 'suspect'?",
             "Why does the model need positional encodings, and what evidence do the authors give for sinusoidal versus learned encodings (Sec. 3.5, Table 3 row E)?",
             "Table 1 compares layer types by complexity, sequential operations and maximum path length. Under what condition on n and d is self-attention cheaper than recurrence, and does that condition hold for today's long-context agents?",
             "Which results are single training runs without variance estimates, and which conclusions in Sec. 6.2 would you want to see replicated with several seeds before relying on them?",
         ],
         "responsePrompt": "In 800-1,000 words: summarise the paper's contribution in your own words (no copied sentences); evaluate the evidence for one claim of your choice (baseline fairness, number of runs, metric validity); and explain one consequence of the architecture for building agents today (context cost, KV cache, causal masking, or decoding). Recompute one number from the paper and show your working."},
        {"citation": "Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. International Conference on Learning Representations (ICLR 2023). arXiv:2210.03629 (v3, 10 Mar 2023).",
         "url": "https://arxiv.org/abs/2210.03629",
         "why": "ReAct is the thought-action-observation loop that lesson 6's agent and most agent frameworks implement. It shows when acting helps reasoning (grounding, fewer hallucinations) and when it hurts (rigid loops, uninformative search), and its error analysis and ethics statement anticipate this course's budgets, evaluation and allow-lists. Licence: read on arXiv; summarised, not reproduced.",
         "guidingQuestions": [
             "How does ReAct formally change the agent's action space (Sec. 2), and why does a 'thought' produce no observation?",
             "On HotpotQA and FEVER the action space is deliberately weak (search, lookup, finish). Why did the authors choose this, and how should it affect how you read the comparison with chain-of-thought?",
             "Table 2's success/failure modes come from 50 labelled trajectories per group. Compute Wilson intervals for one pair of percentages (problem 3) and say which differences you would trust.",
             "The paper reports a frequent failure where the model repeats earlier thoughts and actions. Relate this to lesson 25's retry analysis and to how a step budget and loop detection would change outcomes.",
             "The ethics statement limits experiments to environments without dangerous actions. Which design choices in lessons 11, 15 and 20 operationalise that limitation for a production agent, and which risks remain?",
         ],
         "responsePrompt": "In 800-1,000 words: summarise ReAct's method and main findings in your own words; critically evaluate one comparison (prompted baselines, number of examples, model availability and reproducibility, metric); and propose how you would evaluate a ReAct-style agent for your own use case with the tools of lessons 12, 24 and 25 (golden set size, paired comparison, budgets). Cite section or table numbers for every claim about the paper."},
    ],
    "problemSet": [
        prob("l27-p1", "In the base Transformer d_model = 512 and h = 8 heads with d_k = d_model/h. Compute d_k and the attention scale. For a sequence of n = 100 tokens compute the per-layer operation counts n^2 d (self-attention) and n d^2 (recurrent) with d = 512, their ratio, and the sequence length at which they are equal.", "calculation", 1,
             f"d_k = 512/8 = {s1[0]}; scale 1/sqrt(64) = {s1[1]}. n^2 d = 100^2 * 512 = {s1[2]}; n d^2 = 100 * 512^2 = {s1[3]}; recurrent/self-attention = d/n = {s1[4]}. Equal when n = d = 512. Agents with 32k-token contexts are far past the crossover, which is why attention cost and KV-cache memory (lesson 19) dominate long-context serving.", 5),
        prob("l27-p2", "Summarise the Transformer paper in exactly three sentences of your own (problem, mechanism, evidence). Then list two claims that are measured and one that is a conjecture, citing sections.", "short-answer", 1,
             "Example: Recurrent sequence models compute step by step, which limits parallel training and makes distant dependencies hard to learn. The Transformer replaces recurrence with stacked multi-head scaled dot-product self-attention, position-wise feed-forward layers and positional encodings. On WMT 2014 translation it reached higher BLEU than prior models at lower training cost and transferred to constituency parsing. Measured: BLEU and training cost (Table 2); effect of heads and key size (Table 3 A, B). Conjecture: that unscaled dot products hurt because of small softmax gradients - the authors 'suspect' it (Sec. 3.2.1); also that sinusoids 'may' extrapolate to longer sequences (Sec. 3.5).", 5),
        prob("l27-p3", "ReAct's Table 2 reports false-positive rates (correct answer with hallucinated reasoning or facts) of 6 % for ReAct and 14 % for CoT among successful trajectories, from 50 labelled examples each. Treating these as 3/50 and 7/50, compute 95 % Wilson intervals and an unpaired two-proportion p-value. What can and cannot be concluded?", "calculation", 2,
             f"ReAct 3/50: [{s3[0]}, {s3[1]}]; CoT 7/50: [{s3[2]}, {s3[3]}]; two-proportion p = {s3[4]}. The direction favours ReAct but 50 examples per group cannot establish the difference at conventional levels; the larger contrast in failure modes (hallucination 0 % vs 56 % of failures) is more convincing. The authors present the table as a qualitative analysis of sampled trajectories; reading it as a precise rate would overstate it.", 6),
        prob("l27-p4", "Rewrite one ReAct HotpotQA trajectory pattern (Thought -> search[...] -> Observation -> Thought -> lookup[...] -> ... -> finish[...]) as the message sequence of lesson 6's agent loop. Where do the step budget, tool allow-list and stop condition appear, and which ReAct failure does each address?", "short-answer", 2,
             "System prompt with tool specs for search, lookup, finish (allow-list: only these three, all read-only - matching the paper's safe action space). Each assistant turn = a Thought plus one tool call; each tool result = an Observation message. finish[...] is the stop condition. The step budget (the paper backs off to CoT-SC after 7 HotpotQA steps) bounds the repetitive-loop failure; loop detection (same action twice) can stop earlier; the allow-list prevents actions with side effects (ethics statement). Uninformative search is not fixed by any of these - it needs better retrieval (lesson 7).", 6),
        prob("l27-p5", "Both papers report results from single model families and, for ReAct, a model (PaLM-540B) that was not openly accessible. Discuss in 150-250 words what this means for reproducibility and for transferring the findings to the small local models used in this course.", "short-answer", 2,
             "Points: the authors acknowledge PaLM was not openly available and provided prompts and GPT-3 experiments to help reproducibility; results may depend on model scale - the paper itself shows prompted ReAct performing worst among four methods at 8B/62B and best only after fine-tuning; local 1.5B-7B models may follow the format less reliably, so the format must be validated in code (lesson 4) and the gains re-measured on your own golden set with paired tests (lessons 12, 24). For the Transformer, the architecture is widely replicated, but specific numbers (BLEU, cost) are tied to 2017 hardware and data. Transfer the mechanism, re-measure the effect.", 6),
        prob("l27-p6", "Critical response (800-1,000 words) for one of the two readings, following its responsePrompt.", "essay", 3,
             "Graded with the lesson rubric: accurate own-words summary; a recomputed number with working; evaluation of evidence with explicit attention to sample size, baselines and variance; a concrete, testable consequence for agent engineering; correct citation of sections/tables; no reproduced text beyond short quoted phrases.", 20),
    ],
    "rubric": [
        {"criterion": "Accurate summary in own words", "excellent": "Problem, mechanism, evidence and limitations stated correctly; no copied sentences.",
         "adequate": "Mostly accurate; some paraphrase too close to the source.", "inadequate": "Inaccurate or copied.", "weight": 25},
        {"criterion": "Technical engagement", "excellent": "Recomputes an equation or number correctly and explains its role.",
         "adequate": "Explains a mechanism without recomputation.", "inadequate": "Only restates the abstract.", "weight": 20},
        {"criterion": "Evaluation of evidence", "excellent": "Assesses baselines, sample sizes, variance and ablations; separates measured from conjectured.",
         "adequate": "Identifies one weakness.", "inadequate": "Accepts all claims uncritically.", "weight": 25},
        {"criterion": "Relevance to agent engineering", "excellent": "Draws a concrete, testable consequence for the course's agents.",
         "adequate": "General relevance stated.", "inadequate": "No connection.", "weight": 15},
        {"criterion": "Citation and integrity", "excellent": "Precise section/table citations; quotations marked and minimal.",
         "adequate": "Citations present but imprecise.", "inadequate": "Missing citations or unmarked copying.", "weight": 15},
    ],
    "conceptNote": "content/concepts/L500/27-reading-seminar.md",
    "conceptSummary": "Read in three passes (map, mechanism, critique); the Transformer gives the attention mechanism and its costs, ReAct gives the thought-action-observation loop and its failure modes; recompute a number, size the evidence with lesson 24, and summarise in your own words.",
    "sources": [
        {"title": "Vaswani et al. 2017 - Attention Is All You Need (arXiv:1706.03762v7)", "url": "https://arxiv.org/abs/1706.03762"},
        {"title": "Vaswani et al. 2017 - HTML full text (arXiv)", "url": "https://arxiv.org/html/1706.03762v7"},
        {"title": "Yao et al. 2023 - ReAct: Synergizing Reasoning and Acting in Language Models (arXiv:2210.03629v3)", "url": "https://arxiv.org/abs/2210.03629"},
        {"title": "Yao et al. 2023 - ReAct PDF (v3, ICLR 2023 camera-ready)", "url": "https://arxiv.org/pdf/2210.03629v3"},
    ],
    "seeAlso": [
        "ai-agents L100 #6 A minimal agent loop: the ReAct loop with a budget.",
        "ai-agents L200 #7 Retrieval-augmented answers: better retrieval addresses ReAct's uninformative-search failures.",
        "ai-agents L400 #19 Cost, latency and model choice: attention cost and the KV cache in practice.",
    ],
    "next": "Course assessment: content/assessment/ (final exam, capstone oral defence)",
    "platforms": PLATFORMS,
    "validation": {"status": "validated-local",
                   "how": "Readings retrieved from arXiv on 2026-10-30 (abstract pages, HTML/PDF full text); all paper facts in this lesson checked against them. Calculation problems 27-p1 and 27-p3 recomputed by research/l500_checks.py.",
                   "pendingCi": []},
}


def main():
    out = TOPIC / "content" / "L500.json"
    text = json.dumps([L23, L24, L25, L26, L27], indent=1, ensure_ascii=False) + "\n"
    if out.exists():
        os.remove(out)  # the mount breaks in-place rewrites: delete, then write
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out.relative_to(TOPIC)}: 5 lessons, "
          f"{sum(len(l.get('theorems', [])) for l in (L23, L24, L25))} theorems, "
          f"{sum(len(l['problemSet']) for l in (L23, L24, L25, L26, L27))} problems")


if __name__ == "__main__":
    main()
