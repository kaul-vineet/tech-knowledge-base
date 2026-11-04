"""Lesson 26 illustration (SYNTHETIC data, not Ofqual's model): a model can reproduce the grade DISTRIBUTION exactly
and still give many INDIVIDUALS a grade different from the one an exam would have given; and small groups make any
centre-level prediction noisy. Numbers here support the case discussion; they are not claims about 2020."""
import math

import numpy as np

rng = np.random.default_rng(2601)
GRADES = ["A*", "A", "B", "C", "D", "E", "U"]
SHARE = np.array([0.08, 0.18, 0.25, 0.22, 0.15, 0.08, 0.04])  # synthetic historical distribution
N = 100_000


def grade_by_rank(score):
    """Give the top 8% an A*, the next 18% an A, ...: the output distribution equals SHARE exactly."""
    order = np.argsort(-score)
    g = np.empty(score.size, dtype=int)
    g[order] = np.repeat(np.arange(7), np.round(SHARE * score.size).astype(int))[: score.size]
    return g


ability = rng.standard_normal(N)
exam_score = ability + 0.5 * rng.standard_normal(N)  # what the exam would have measured (itself noisy)
exam = grade_by_rank(exam_score)
z = (exam_score - exam_score.mean()) / exam_score.std()
retest = grade_by_rank(ability + 0.5 * rng.standard_normal(N))  # a second, equally good exam sitting
for r in (0.80, 0.90):
    teacher_score = r * z + math.sqrt(1 - r * r) * rng.standard_normal(N)  # teacher judgement, correlation r with exam
    model = grade_by_rank(teacher_score)  # rank-based standardisation to the historical distribution
    dist_err = np.abs(np.bincount(model, minlength=7) / N - SHARE).max()
    print(f"teacher-exam correlation {np.corrcoef(teacher_score, exam_score)[0, 1]:.2f}: distribution error {dist_err:.4f}; same grade as exam {np.mean(model == exam):.1%}; "
          f"within one grade {np.mean(np.abs(model - exam) <= 1):.1%}")
print(f"exam vs an equally good re-sit: same grade {np.mean(retest == exam):.1%}; within one {np.mean(np.abs(retest - exam) <= 1):.1%}")

print("small centres: a centre's top-two-grade share (true p = 0.26) estimated from 3 past years of n students each:")
for n in (5, 8, 15, 50, 200):
    hist = rng.binomial(3 * n, 0.26, 20_000) / (3 * n)
    print(f"  n = {n:>3}: SD {hist.std():.3f} (theory sqrt(p(1-p)/3n) = {math.sqrt(0.26 * 0.74 / (3 * n)):.3f}), relative error {hist.std() / 0.26:.0%}")
