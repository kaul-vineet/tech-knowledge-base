"""Lesson 23 - how a language model works, in numpy: tokens, embeddings, softmax with temperature,
scaled dot-product attention, a bigram model, greedy/top-k/top-p sampling, cross-entropy and perplexity.

    python tiny_lm.py              demo: tokens -> embeddings -> causal attention -> bigram LM -> sampling
    python tiny_lm.py check T1     numerical check of theorem T1 (T1..T4); output is pasted into content/L500.json

Numbers are printed with 4 decimals so the output is identical on macOS, Windows and Linux.
"""
import sys

import numpy as np

CORPUS = ("the agent reads the ticket . the agent calls the tool . "
          "the tool returns the result . the agent writes the answer .")
HELD_OUT = "the agent reads the result . the tool calls the agent ."


def tokenize(text):
    return text.split()  # word-level tokens; real models use subword (BPE) tokens


def build_vocab(tokens):
    return {w: i for i, w in enumerate(sorted(set(tokens)))}


def softmax(z, T=1.0):
    z = np.asarray(z, dtype=float) / T
    z = z - z.max(axis=-1, keepdims=True)  # shift invariance (T1) keeps exp() from overflowing
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


def entropy(p):
    p = np.asarray(p, dtype=float)
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def attention(Q, K, V, causal=False, scale=True):
    """Scaled dot-product attention: softmax(Q K^T / sqrt(d)) V. Returns (output, weights)."""
    scores = Q @ K.T
    if scale:
        scores = scores / np.sqrt(Q.shape[-1])
    if causal:  # position i may only look at positions <= i
        n = scores.shape[0]
        scores = np.where(np.tril(np.ones((n, n), dtype=bool)), scores, -np.inf)
    W = softmax(scores)
    return W @ V, W


class Bigram:
    """P(w_i | w_{i-1}) from counts; k > 0 adds add-k smoothing. A row never seen is uniform."""

    def __init__(self, tokens, vocab, k=0.0):
        self.vocab, self.inv = vocab, {i: w for w, i in vocab.items()}
        n = len(vocab)
        self.counts = np.zeros((n, n))
        for a, b in zip(tokens, tokens[1:]):
            self.counts[vocab[a], vocab[b]] += 1
        smoothed = self.counts + k
        rows = smoothed.sum(axis=1, keepdims=True)
        self.P = np.where(rows > 0, smoothed / np.where(rows > 0, rows, 1), 1.0 / n)

    def cross_entropy(self, tokens, P=None):
        """Mean negative log-likelihood (nats/token) of tokens[1:] given the previous token."""
        P = self.P if P is None else P
        with np.errstate(divide="ignore"):
            nll = [-np.log(P[self.vocab[a], self.vocab[b]]) for a, b in zip(tokens, tokens[1:])]
        return float(np.mean(nll))

    def perplexity(self, tokens, P=None):
        return float(np.exp(self.cross_entropy(tokens, P)))


def truncate(probs, method="sample", k=None, p=None):
    """Return the renormalised distribution that greedy / top-k / top-p samples from."""
    probs = np.asarray(probs, dtype=float)
    order = np.argsort(-probs, kind="stable")  # ties: lower token id first
    keep = np.zeros_like(probs, dtype=bool)
    if method == "greedy":
        keep[order[0]] = True
    elif method == "top_k":
        keep[order[:k]] = True
    elif method == "top_p":
        cum = np.cumsum(probs[order])
        n_keep = int(np.searchsorted(cum, p - 1e-12) + 1)  # smallest prefix with mass >= p
        keep[order[:n_keep]] = True
    else:
        keep[:] = True
    q = np.where(keep, probs, 0.0)
    return q / q.sum()


def next_token_dist(model, prev, T=1.0, **kw):
    with np.errstate(divide="ignore"):
        logits = np.log(model.P[model.vocab[prev]])
    return truncate(softmax(logits, T), **kw)


def generate(model, start, n, rng, T=1.0, **kw):
    out = [start]
    for _ in range(n):
        q = next_token_dist(model, out[-1], T, **kw)
        out.append(model.inv[int(rng.choice(len(q), p=q))])
    return " ".join(out)


# ---------------------------------------------------------------- theorem checks
def check_T1():
    """Softmax with temperature = maximum-entropy (Gibbs) distribution; limits; dH/dT = Var(z)/T^3 >= 0."""
    rng = np.random.default_rng(0)
    z = np.array([2.0, 1.0, 0.5, -1.0, -3.0])
    lines = [f"shift invariance: max|softmax(z) - softmax(z+100)| < 1e-12: {bool(np.abs(softmax(z) - softmax(z + 100)).max() < 1e-12)}"]
    T = 0.7
    p = softmax(z, T)
    F = lambda q: float(q @ z + T * entropy(q))  # objective maximised by softmax(z/T)
    trials = rng.dirichlet(np.ones(len(z)), size=10000)
    best_other = max(F(q) for q in trials)
    lines.append(f"Gibbs objective E[z]+T*H at T=0.7: softmax {F(p):.4f}; best of 10000 random distributions {best_other:.4f}; "
                 f"T*log(sum exp(z/T)) = {T * np.log(np.exp(z / T).sum()):.4f}")
    lines.append(f"T=0.05: max prob {softmax(z, 0.05).max():.4f} at index {int(softmax(z, 0.05).argmax())} (argmax of z = {int(z.argmax())})")
    lines.append(f"T=100 : max |p - 1/5| = {np.abs(softmax(z, 100) - 0.2).max():.4f}")
    Ts = np.linspace(0.1, 10, 100)
    H = np.array([entropy(softmax(z, t)) for t in Ts])
    lines.append(f"entropy over T=0.1..10 strictly increasing: {bool(np.all(np.diff(H) > 0))} "
                 f"(H from {H[0]:.4f} to {H[-1]:.4f}; log 5 = {np.log(5):.4f})")
    t, h = 1.3, 1e-5
    fd = (entropy(softmax(z, t + h)) - entropy(softmax(z, t - h))) / (2 * h)
    q = softmax(z, t)
    var = float(q @ z**2 - (q @ z) ** 2)
    lines.append(f"dH/dT at T=1.3: finite difference {fd:.6f}; Var(z)/T^3 = {var / t**3:.6f}")
    return lines


def check_T2():
    """q.k has mean 0 and variance d when components are iid (0, 1); dividing by sqrt(d) keeps softmax out of saturation."""
    rng = np.random.default_rng(1)
    lines = []
    for d in (4, 64, 512):
        q = rng.standard_normal((20000, d))
        k = rng.standard_normal((20000, d))
        s = (q * k).sum(axis=1)
        lines.append(f"d={d:>3}: mean(q.k)/sqrt(d) = {s.mean() / np.sqrt(d):+.3f}  var(q.k)/d = {s.var() / d:.3f}  var(q.k/sqrt(d)) = {(s / np.sqrt(d)).var():.3f}")
    d, n_keys, trials = 512, 16, 2000
    stats = {}
    for scaled in (False, True):
        mx, ent, jac = [], [], []
        for _ in range(trials):
            q = rng.standard_normal(d)
            K = rng.standard_normal((n_keys, d))
            s = K @ q / (np.sqrt(d) if scaled else 1.0)
            w = softmax(s)
            mx.append(w.max())
            ent.append(entropy(w))
            jac.append(np.linalg.norm(np.diag(w) - np.outer(w, w)))  # softmax Jacobian: gradient signal
        stats[scaled] = (np.mean(mx), np.mean(ent), np.mean(jac))
    for scaled, name in ((False, "unscaled"), (True, "scaled  ")):
        m, e, j = stats[scaled]
        lines.append(f"d=512, 16 keys, {name}: mean max weight {m:.4f}  mean entropy {e:.4f} (log 16 = {np.log(16):.4f})  mean ||Jacobian|| {j:.4f}")
    return lines


def check_T3():
    """Gibbs' inequality: the relative-frequency (MLE) bigram minimises training cross-entropy; PP = exp(H); uniform PP = V."""
    rng = np.random.default_rng(2)
    toks = tokenize(CORPUS)
    vocab = build_vocab(toks)
    mle = Bigram(toks, vocab, k=0.0)
    h_mle = mle.cross_entropy(toks)
    worse = 0
    best_other = np.inf
    for _ in range(1000):
        noise = rng.dirichlet(np.ones(len(vocab)), size=len(vocab))
        lam = rng.uniform(0.01, 0.5)
        P = (1 - lam) * mle.P + lam * noise
        h = mle.cross_entropy(toks, P)
        best_other = min(best_other, h)
        worse += h > h_mle
    lines = [f"V = {len(vocab)} tokens, {len(toks) - 1} training bigrams",
             f"MLE training cross-entropy {h_mle:.4f} nats/token, perplexity {np.exp(h_mle):.4f}",
             f"1000 perturbed models: {worse} have higher cross-entropy; lowest {best_other:.4f}"]
    U = np.full((len(vocab), len(vocab)), 1 / len(vocab))
    lines.append(f"uniform model perplexity {mle.perplexity(toks, U):.4f} (= V)")
    held = tokenize(HELD_OUT)
    lines.append(f"held-out perplexity: MLE (k=0) {mle.perplexity(held)}; add-0.1 {Bigram(toks, vocab, k=0.1).perplexity(held):.4f}; "
                 f"add-1 {Bigram(toks, vocab, k=1.0).perplexity(held):.4f}")
    return lines


def check_T4():
    """Truncated sampling draws from the conditional distribution on the kept set; greedy = top-k(1) = T->0."""
    rng = np.random.default_rng(3)
    toks = tokenize(CORPUS)
    model = Bigram(toks, build_vocab(toks), k=0.0)
    row = model.P[model.vocab["the"]]
    lines = ["P(. | the): " + "  ".join(f"{model.inv[i]}={row[i]:.3f}" for i in np.argsort(-row, kind="stable") if row[i] > 0)]
    for kw in ({"method": "top_k", "k": 3}, {"method": "top_p", "p": 0.6}, {"method": "top_p", "p": 0.9}):
        q = truncate(row, **kw)
        draws = rng.choice(len(q), size=20000, p=q)
        emp = np.bincount(draws, minlength=len(q)) / 20000
        kept = [model.inv[i] for i in np.flatnonzero(q)]
        lines.append(f"{kw}: keeps {kept} (mass {row[q > 0].sum():.3f}); max |empirical - p/mass| = {np.abs(emp - q).max():.4f}")
    g = truncate(row, "greedy")
    lines.append(f"greedy == top_k(1): {bool(np.array_equal(g, truncate(row, 'top_k', k=1)))}; "
                 f"softmax(log p / 0.01) max |diff| to greedy = {np.abs(softmax(np.log(np.where(row > 0, row, 1e-300)), 0.01) - g).max():.4f}")
    return lines


CHECKS = {"T1": check_T1, "T2": check_T2, "T3": check_T3, "T4": check_T4}


def demo():
    toks = tokenize(CORPUS)
    vocab = build_vocab(toks)
    ids = [vocab[t] for t in toks]
    print(f"tokens: {len(toks)}  vocabulary: {len(vocab)}  first ids: {ids[:6]}")
    rng = np.random.default_rng(42)
    d = 8
    E = rng.standard_normal((len(vocab), d))  # embedding table: one learned row per token id
    X = E[ids[:5]]  # "the agent reads the ticket"
    Wq, Wk, Wv = (rng.standard_normal((d, d)) / np.sqrt(d) for _ in range(3))
    out, W = attention(X @ Wq, X @ Wk, X @ Wv, causal=True)
    print("causal attention weights for 'the agent reads the ticket' (row = query position):")
    for i, r in enumerate(W):
        print(f"  {toks[i]:>7} " + " ".join(f"{x:.3f}" for x in r))
    print(f"rows sum to 1: {bool(np.allclose(W.sum(axis=1), 1))}; future weights all 0: {bool(np.all(np.triu(W, 1) == 0))}; output shape {out.shape}")
    model = Bigram(toks, vocab, k=0.1)
    for kw in ({"method": "greedy"}, {"method": "top_k", "k": 2}, {"method": "top_p", "p": 0.9}):
        print(f"{kw['method']:>6}: {generate(model, 'the', 8, np.random.default_rng(7), **kw)}")
    print(f"T=1.5 sample: {generate(model, 'the', 8, np.random.default_rng(7), T=1.5)}")
    print(f"perplexity train {model.perplexity(toks):.4f}  held-out {model.perplexity(tokenize(HELD_OUT)):.4f}  uniform {len(vocab)}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "check":
        print("\n".join(CHECKS[sys.argv[2]]()))
    else:
        demo()
