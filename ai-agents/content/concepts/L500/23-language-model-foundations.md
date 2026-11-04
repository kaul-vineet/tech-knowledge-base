**Concept: how a language model works – tokens, embeddings, softmax, attention, sampling, perplexity**

## Why it matters
Every agent in this course sits on top of one operation: given the tokens so far, produce a probability distribution over the next token, then pick one. Temperature, top-p, "the model is confident", context limits, and the advice to use temperature 0 for JSON all follow from a few short derivations. Knowing them lets you predict behaviour instead of collecting folklore.

## Definitions
- **Token.** The unit the model reads and writes: a sub-word piece from a fixed vocabulary of V entries (BPE and similar). A sentence becomes a list of integer ids. The lab uses whole words (V = 11) so you can read every number.
- **Embedding.** A learned table E with one row of d numbers per token id. Looking up the ids of a sentence gives a matrix X (n × d). Nothing in the row "means" anything by itself; meaning is whatever makes the next-token loss small.
- **Logits and softmax.** The model's last layer outputs one score z_i per vocabulary entry. Softmax turns scores into probabilities: p_i = exp(z_i / T) / Σ_j exp(z_j / T). T is the temperature.
- **Scaled dot-product attention.** Each position gets a query q, a key k and a value v (linear maps of X). Position i mixes the values with weights softmax(q_i · k_j / √d) over the positions j it may see; a causal mask hides j > i (Vaswani et al. 2017, eq. 1).
- **Language model.** Any rule P(w_t | w_<t). A bigram model keeps only the previous token: P(w_t | w_{t−1}) = count(w_{t−1} w_t) / count(w_{t−1}) – the maximum-likelihood estimate (Jurafsky & Martin, ch. 3).
- **Cross-entropy and perplexity.** On a text of N predicted tokens, H = −(1/N) Σ log q(w_t | context) nats per token, and PP = exp(H). Perplexity is the "effective number of choices" per token.

## Key results (proved in the lesson, checked in `tiny_lm.py`)
1. **Softmax is the maximum-entropy choice (T1).** Among all distributions p, softmax(z/T) maximises E_p[z] + T·H(p). Temperature is the exchange rate between "pick high scores" and "stay uncertain". Consequences you can check numerically: adding a constant to every logit changes nothing; T → 0 gives the argmax (greedy); T → ∞ gives the uniform distribution; and dH/dT = Var_p(z)/T³ ≥ 0, so raising the temperature can only raise entropy.
2. **Why 1/√d (T2).** If query and key components are independent with mean 0 and variance 1, then q · k has mean 0 and variance d. With d = 512 the raw scores have a standard deviation of about 22.6; softmax of numbers that far apart is nearly one-hot, and its Jacobian diag(p) − ppᵀ is nearly zero, so learning stalls. Dividing by √d makes the variance 1 for every d. In the check, unscaled attention over 16 keys puts 0.94 of its weight on one key on average; scaled, 0.25.
3. **Cross-entropy is minimised by the true distribution (T3, Gibbs' inequality).** H(p, q) ≥ H(p) with equality only when q = p. So counting and normalising (MLE) gives the bigram table with the lowest training cross-entropy; a uniform model has perplexity exactly V; and a single unseen bigram (q = 0) makes perplexity infinite, which is why real models never assign exactly zero (smoothing, or softmax which is always positive).
4. **Truncated sampling is conditioning (T4).** Greedy, top-k and top-p all keep a set S of tokens and sample from p restricted to S, renormalised: p(w)/p(S). Greedy is top-k with k = 1 and the T → 0 limit. Top-p adapts the set size to the shape of the distribution (Holtzman et al. 2019).

## Intuition
Think of the model as a scorer followed by a dial. The scorer (embeddings + attention + feed-forward layers) produces logits; it is the expensive, learned part. The dial (temperature, top-k, top-p) is cheap and entirely yours: it reshapes the same scores into a sharper or flatter distribution and decides how much of the tail you are willing to sample. Attention is a learned, content-based lookup: a soft "find the earlier tokens that matter for this one and average their values". The √d is just unit bookkeeping so the lookup does not degenerate into a hard, untrainable one.

## Worked example (from the lab)
Corpus: "the agent reads the ticket . the agent calls the tool . the tool returns the result . the agent writes the answer ." – 24 tokens, V = 11.
- P(agent | the) = 3/8 = 0.375, P(tool | the) = 2/8, and 0.125 each for ticket, result, answer.
- Greedy decoding from "the" gives "the agent calls the agent calls the agent calls": the most likely continuation of each step is a loop. This is the degeneration Holtzman et al. describe, in miniature.
- Top-p with p = 0.6 keeps {agent, tool} (mass 0.625) and samples them as 0.6 and 0.4.
- Training perplexity of the MLE model is 2.0612; the uniform model scores 11.0000 = V. On the held-out sentence the MLE model scores infinity because "tool calls" never occurred; add-0.1 smoothing gives 4.4475.
- The causal attention matrix for "the agent reads the ticket" is lower-triangular and every row sums to 1: position 1 can only look at itself (weight 1.000).

## How this connects to the course
Lesson 4 (structured output) and lesson 19 (cost and model choice) use temperature 0 or low top-p because they want the mode, not variety. Lesson 9's token budgets and lesson 19's KV cache exist because attention compares every position with every earlier one: cost grows with n² per layer (Vaswani et al., Table 1). Lesson 12's golden set measures task success, not perplexity; T3 explains why the two can disagree: perplexity rewards calibrated probabilities for every token, a task checks one decision.

## Common misconceptions
- **"Temperature 0 makes the model correct."** It makes it deterministic (argmax). If the argmax is wrong, it is wrong every time.
- **"High probability means true."** Probability is about text continuation under the training distribution. A fluent wrong answer can have high probability; calibration has to be measured (lesson 24).
- **"Top-k and top-p remove bad tokens."** They remove *unlikely* tokens. The likely-but-wrong token survives every truncation.
- **"Attention weights are explanations."** They show where a head looked, not why the output was produced; many heads and layers combine.
- **"Lower perplexity always means a better agent."** Perplexities are only comparable with the same tokenizer and test set, and an intrinsic improvement does not guarantee a better task score (Jurafsky & Martin, §3.3).
- **"The 1/√d is a tuned hyper-parameter."** It is derived from a variance argument; it holds exactly only under the independence and unit-variance assumptions, which is why the paper says it *suspects* the gradient effect rather than claiming a law.

## Sources
Vaswani et al. 2017, arXiv:1706.03762 (§3.2.1, Table 1) · Jurafsky & Martin, *Speech and Language Processing*, ch. 3 (n-grams, perplexity) · Holtzman et al. 2019, arXiv:1904.09751 (nucleus sampling).
