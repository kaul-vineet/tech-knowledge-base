# Pedagogy review — undergraduate perspective (2026-10-29)

**Verdict:** excellent practice-led lab courses; to count as undergraduate courses each needed a theory companion, varied
assessment, ethics and primary literature. L500 ("Theory & rigour", lessons 23–27 per topic) and the assessment pack in
`<topic>/content/assessment/` implement the recommendations below.

## Strengths
- Clear progression: run → build → harden → design → capstone (apply → analyse → evaluate → create).
- Active learning: predict-then-reveal "Try it", deliberate failure labs, build tasks graded by tests.
- Professional judgement taught explicitly: ADRs, fitness functions, measured option comparison.
- Honesty modelled: every lesson states what ran and what is pending.
- Rigorous AI rule ("the model explains; code decides") enforced in code and tested against attacks.

## Gaps found (measured across 176 lessons)
1. No mathematical foundations: no lesson listed a maths/physics prerequisite; 2–8 concept notes per course had any derivation or proof.
2. One assessment type: all 176 checkpoints were code tests; no written work, exams, oral defence or peer review.
3. Few "understand/explain" outcomes; concept text 13–22% of each course.
4. Ethics and society content in 0–2 lessons per course (most "ethics" mentions were software licences).
5. No primary-literature reading assignments.
6. Only individual work; communication never assessed.
7. No pre/post measure of learning.

## Recommendations (implemented in L500 unless noted)
1. Foundations module per course (3 lessons) with proofs, derivations and problem sets.
2. Assessment mix: code labs 35% · problem sets 25% · two exams 20% · capstone + oral defence + peer-reviewed ADRs 20%.
3. One ethics/society lesson per course with a structured case study.
4. Reading seminar: two foundational papers per course with critical response.
5. Teams and communication: pair programming at L200, team capstone roles, ADR design reviews, presentation.
6. Evidence of learning: 15-item pre/post concept inventory per course; spaced retrieval via the practice question bank.
7. Outcomes mapped to ACM/IEEE CS2023 and ABET student outcomes (syllabus.md).
8. Interdisciplinary capstone options (e.g. Simulation + Astronomy + AI Agents; Cryptography + Distributed Systems + App Architecture) — proposed, not yet built.

## Suggested 14-week semester
Week 1 setup + pre-test · 2–4 L100 + reading 1 · 5–6 Foundations + problem sets · 7–8 L200 (pairs) + midterm ·
9–10 L300 + ethics + reading 2 · 11–12 L400 + design reviews · 13–14 team capstone, oral defence, final, post-test.
Recommended order across courses: Simulation before Astronomy; Cryptography before Quantum L400; App Architecture before Distributed Systems L400.
