import unittest

import numpy as np

import tiny_lm as t


class TinyLMTest(unittest.TestCase):
    def setUp(self):
        self.toks = t.tokenize(t.CORPUS)
        self.vocab = t.build_vocab(self.toks)

    def test_softmax_shift_and_temperature_limits(self):
        z = np.array([2.0, 1.0, -1.0])
        self.assertTrue(np.allclose(t.softmax(z), t.softmax(z + 50)))
        self.assertAlmostEqual(t.softmax(z, 0.01).max(), 1.0, places=6)
        self.assertTrue(np.allclose(t.softmax(z, 1e6), 1 / 3, atol=1e-5))

    def test_causal_attention_rows_and_mask(self):
        rng = np.random.default_rng(0)
        X = rng.standard_normal((4, 8))
        out, W = t.attention(X, X, X, causal=True)
        self.assertTrue(np.allclose(W.sum(axis=1), 1))
        self.assertTrue(np.all(np.triu(W, 1) == 0))
        self.assertEqual(out.shape, (4, 8))

    def test_bigram_mle_is_relative_frequency(self):
        m = t.Bigram(self.toks, self.vocab)
        self.assertAlmostEqual(m.P[self.vocab["the"], self.vocab["agent"]], 3 / 8)
        self.assertTrue(np.allclose(m.P.sum(axis=1), 1))

    def test_perplexity_uniform_is_vocab_size(self):
        m = t.Bigram(self.toks, self.vocab)
        U = np.full((len(self.vocab),) * 2, 1 / len(self.vocab))
        self.assertAlmostEqual(m.perplexity(self.toks, U), len(self.vocab))

    def test_unseen_bigram_needs_smoothing(self):
        held = t.tokenize(t.HELD_OUT)
        self.assertEqual(t.Bigram(self.toks, self.vocab).perplexity(held), float("inf"))
        self.assertLess(t.Bigram(self.toks, self.vocab, k=0.1).perplexity(held), 11)

    def test_top_p_keeps_smallest_prefix(self):
        q = t.truncate([0.5, 0.3, 0.15, 0.05], "top_p", p=0.8)
        self.assertTrue(np.allclose(q, [0.625, 0.375, 0, 0]))
        self.assertTrue(np.array_equal(t.truncate([0.2, 0.5, 0.3], "greedy"), [0, 1, 0]))

    def test_theorem_checks_hold(self):
        self.assertIn("strictly increasing: True", "\n".join(t.check_T1()))
        self.assertIn("1000 have higher cross-entropy", "\n".join(t.check_T3()))
        self.assertIn("greedy == top_k(1): True", "\n".join(t.check_T4()))


if __name__ == "__main__":
    unittest.main()
