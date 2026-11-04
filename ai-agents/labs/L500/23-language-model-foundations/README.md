# 23 – Foundations I: how language models work

Tokens, embeddings, softmax with temperature, scaled dot-product attention with a causal mask, a bigram language model, greedy/top-k/top-p sampling, cross-entropy and perplexity - in about 200 lines of numpy. `check T1..T4` prints the numerical check of each theorem in lesson 23.

Concept note: `../../../content/concepts/L500/23-language-model-foundations.md` · lesson object: `content/L500.json` #23 (theorems, proofs, problem set)
Dependencies: Python 3.12, numpy (2.x; validated with 2.5.3). No model server is needed: L500 labs check mathematics, not model output.

## Run
macOS / Linux (zsh, bash):
```bash
python3 tiny_lm.py            # demo
python3 tiny_lm.py check T1   # numerical check of theorem T1 (T1, T2, T3, T4)
python3 -m unittest -v
```
Windows (PowerShell):
```powershell
py -3.12 tiny_lm.py
py -3.12 tiny_lm.py check T1
py -3.12 -m unittest -v
```

### Expected output – demo (observed 2026-10-30, Python 3.12.15, Linux sandbox)
```
tokens: 24  vocabulary: 11  first ids: [7, 1, 4, 7, 8, 0]
causal attention weights for 'the agent reads the ticket' (row = query position):
      the 1.000 0.000 0.000 0.000 0.000
    agent 0.698 0.302 0.000 0.000 0.000
    reads 0.347 0.278 0.375 0.000 0.000
      the 0.282 0.089 0.346 0.282 0.000
   ticket 0.089 0.200 0.173 0.089 0.449
rows sum to 1: True; future weights all 0: True; output shape (5, 8)
greedy: the agent calls the agent calls the agent calls
 top_k: the tool returns the agent calls the agent reads
 top_p: the ticket the tool . the tool . the
T=1.5 sample: the the tool returns calls reads tool . the
perplexity train 2.8251  held-out 4.4475  uniform 11
```

### Expected output – `check T1` (observed 2026-10-30)
```
shift invariance: max|softmax(z) - softmax(z+100)| < 1e-12: True
Gibbs objective E[z]+T*H at T=0.7: softmax 2.2211; best of 10000 random distributions 2.2168; T*log(sum exp(z/T)) = 2.2211
T=0.05: max prob 1.0000 at index 0 (argmax of z = 0)
T=100 : max |p - 1/5| = 0.0057
entropy over T=0.1..10 strictly increasing: True (H from 0.0005 to 1.5953; log 5 = 1.6094)
dH/dT at T=1.3: finite difference 0.396496; Var(z)/T^3 = 0.396496
```
All four checks' outputs are recorded in `content/L500.json` (`theorems[].checkOutput`); `python research/l500_checks.py` re-runs them and fails on any difference. Numbers are printed to 4 decimals with seeded generators so macOS and Windows should print the same text (status `expected` until the CI matrix runs).

### Tests
`python -m unittest` -> `Ran 7 tests ... OK`.

## How to use this lab with the lesson
1. Read the theorem statement in the lesson and try the proof yourself.
2. Predict the check's output before running it (which way should each number move?).
3. Run the check; change one parameter in the `check_T*` function (seed, dimension, probability) and explain the new output.
4. Use the module's functions to verify your numerical answers in the problem set.
