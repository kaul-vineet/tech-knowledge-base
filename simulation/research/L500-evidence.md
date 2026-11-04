# L500 evidence - theory, ethics and readings (lessons 23-27)

All sources were retrieved on 2026-10-30 with web_fetch, or are marked "search only". Scores use the SPEC.md rubric: implementable, current, authoritative, open, transferable and right depth, each scored 0-2. Theory sources (classic papers and textbooks) are scored "current" = 2 when the result is still standard. Every number in content/L500.json comes from a script under labs/L500/ or from research/l500_checks.py; none comes from a source.

## Lesson 23 - probability and stochastic processes

**Research questions**
1. What is the cleanest rigorous route to the weak LLN for this audience?
2. How do we state the CLT and its rate honestly?
3. How do the Poisson axioms give exponential gaps?
4. How do we derive the M/M/1 law without generating functions?

**Kept**
- **Grinstead & Snell, *Introduction to Probability* (GNU FDL).** Chapters 8 (LLN), 9 (CLT) and 11 (Markov chains). The licence was confirmed on the PDF. Score 11.
- **MIT OCW 2.854 M/M/1 notes.** Already in VERIFIED-RESOURCES (L100). Score 10.
- **NIST/SEMATECH confidence limits page.** Already listed. Score 10.
- **Gallager, MIT 6.262 ch. 2 (Poisson processes).** Located by search; the PDF was not fetched. It is listed as further reading and no fact rests on it. Score 8 (search only).

**Dropped**
- Wikipedia (not a primary source).
- Measure-theoretic texts: wrong depth, and their licences are closed.

**Key facts and how they were checked**
- **Chebyshev → WLLN.** Proved in full in the lesson.
- **CLT.** A characteristic-function sketch, citing G&S ch. 9 for the full proof. Checked by KS distance (t2_clt.py).
- **Poisson P₀′ = −λP₀.** Derived in the lesson and checked by building the process from Bernoulli cells (t3_poisson.py).
- **Cut balance.** Derived in the lesson and checked three ways: the formula, a 200-state generator solve and a CTMC simulation (t4_birth_death.py).
- **P(S₁₀₀ > 130) = 0.00275 vs the CLT's 0.00135.** Computed in l500_checks.py. A first draft used t = 110, and the computation showed the CLT is almost exact there (0.1583 vs 0.1587), so the problem was changed to show tail behaviour honestly.

## Lesson 24 - numerical methods

**Research questions**
1. Euler's local and global error with a Lipschitz bound.
2. RK4's order conditions.
3. Stability regions and stiffness.
4. The IEEE 754 rounding model and the truncation/round-off trade-off.

**Kept**
- **Verschelde, UIC MCS 471 lecture on Runge-Kutta (2022).** Local vs global error, the order rule and RK4. The text fetched was partly garbled, and the facts used are standard. Score 9.
- **Princeton COS 323 (2011) lecture 19.** Explicit Euler region |1 + hλ| ≤ 1, implicit Euler unconditionally stable, stiffness definition. Score 9.
- **Berkeley Python Numerical Methods 22.4.** Already listed; it shows Euler instability but does not derive the region. Score 9.
- **Goldberg (1991), Oracle reprint (© ACM, reprinted by permission).** Ulps, machine epsilon, cancellation. Score 10.
- **Python tutorial on floating point (3.15.2 docs).** 0.1 + 0.2 and fsum. Score 11.

**Dropped**
- MIT 18.086 notes: the landing page fetched but the PDF was not read.
- Hairer, Nørsett & Wanner: not open.

**Facts and their checks**
- RK4's eight order conditions are checked in exact fractions (t2_rk4_order.py).
- RK4's real-axis limit −2.7853 comes from bisection.
- The stiff example's exact solution cos t was checked by substitution in the lesson text.
- Python 3.12+ `sum()` of floats uses compensated summation. A first draft printed `sum([0.1]*10)` = 1.0, so the check now uses an explicit `+=` loop (0.9999999999999999) and states this.
- The float32 Euler table shows a lucky partial cancellation at 10⁵ steps. It is reported as such, not hidden.

## Lesson 25 - random number generation and Monte Carlo theory

**Kept**
- **Hull & Dobell (1962)**, SIAM Review 4(3), UVic repository copy (reprinted with SIAM permission). Theorem 1 gives the full-period conditions. Score 10.
- **O'Neill (2014) PCG paper page.** Score 9.
- **Salmon et al. (2011) Random123, SC11 (© ACM, personal/classroom copying allowed).** Counter-based generators, Philox, BigCrush. Score 11.
- **NumPy PCG64 and Philox docs (v2.5).** PCG64: period 2¹²⁸, `advance()`/`jumped()`. Philox4x64: period 2²⁵⁶ − 1. Score 11.
- **NIST/SEMATECH e-Handbook 1.3.5.15 (chi-square) and 1.3.5.16 (KS).** Score 10.
- **Owen, *Monte Carlo theory, methods and examples*, ch. 8-9.** The author asks that the chapters not be redistributed, so they are linked, not copied. Score 9.

**Search only, not cited as primary**
- TestU01 page (iro.umontreal.ca/~simul/testu01/tu01.html), mentioned by name only.
- Park & Miller (1988): only the abstract was read; not used.

**Facts and their checks**
- Hull-Dobell is checked exhaustively for m = 64, 60 and 81.
- The RANDU identity is proved and checked over 99,998 triples, which use exactly 15 planes.
- RANDU's period 2²⁹ is computed as the multiplicative order in l500_checks.py.
- The chi-square tail function is anchored to tabulated 5% points (124.342 at 100 df, 3.841 at 1 df, 16.919 at 9 df) and the Kolmogorov 5% point to 1.358.
- The importance-sampling closed form e¹⁶·P(Z > 8) is derived in the lesson and compared with the sample relative SE (0.0212 vs 0.0212).
- **RANDU 3-D test design.** A first design (10³ cells, 30,000 triples) gave p = 0.00099 for RANDU, which is not decisive, so the test was strengthened to 20³ cells and 200,000 triples. Both runs are recorded here for honesty.

## Lesson 26 - ethics

**Research questions**
1. A real, civilian case where a model decided things about people, with primary documents.
2. The professional codes' exact clauses.
3. Government standards on analytical quality assurance and uncertainty.
4. Contrasting cases on validation duty and transparency.

**Kept**

| Source | Facts used | Score |
|---|---|---|
| Ofqual interim report (13 Aug 2020), executive summary fetched | DCP model; A* 7.7% → 13.9% under CAGs; groups < 15 weighted towards CAGs; "no statistical model can reliably predict grades for particularly small groups"; 96.4% within one grade of CAG; 51 of 55 A levels > 90% within ±1 in back-tests; transparency a lower priority after consultation; Table 2.1 entries (A level 718,276; GCSE 4,771,415); statutory direction under s.129(6) ASCL Act 2009 | 11 |
| Ofqual statement from Roger Taylor (17 Aug 2020) | Reversal to CAG or calculated grade, whichever higher; apology | 10 |
| OSR, *Ensuring statistical models command public confidence* (2 Mar 2021) | Three principles; limitations and uncertainty "not fully communicated"; method not published in advance; limited professional statistical consensus; "limited human review of outputs … at an individual level"; acceptability testing focused on process; teams acted with honesty and integrity; Recommendation 4 cites the Aqua Book | 12 |
| ACM Code of Ethics (2018) | 1.1, 1.2, 1.3, 2.4, 2.5, 3.1 (may be republished unchanged with the notice; we paraphrase) | 12 |
| IEEE Policies 7.8 | Item I.5 | 11 |
| AQuA Book (gov.uk, 30 Jul 2025) | Four roles (commissioner, analyst, assurer, approver); analyst and assurer separate; proportionality; uncertainty identified, managed and communicated; replaces the 2015 edition | 11 |
| Aqua Book 2015 PDF (HM Treasury, OGL v3) | Had three roles; cited for history | 10 |
| NASA-STD-7009B (2024) public PDF, front matter and table of contents | Credibility factors (capability and results assessment); §4.3.8 reporting to decision makers (heading only; text not reached) | 9 |
| Robodebt Royal Commission report page (2023) | Income averaging; 2019 Federal Court consent declaration ("not validly made"); 57 recommendations. Facts read from the CC BY copy because the official PDF links did not load | 9 |
| CovidSim repo (GPL-3.0) | Deterministic given threads and seed; report9 folder | 10 |
| Nature news (18 Jun 2020) | Code released end of April 2020; CODECHECK re-run 1 June | 9 |

**Dropped**
- News coverage of the 2020 grading case (secondary).
- Claims about which school types benefited from the small-cohort rule: not verified in a primary source, so the lesson does not make them.
- UK GDPR Article 22 (automated decisions): relevant but not retrieved, so not cited. Listed in KNOWN-GAPS.

**Corrections from research.** The initial brief listed eight NASA credibility factors. Those are the 2008 baseline; the lesson uses 7009B's factors. It assumed Sargent 2020 was co-authored; it is sole-authored. It assumed the Aqua Book had four roles; only the 2025 edition does.

## Lesson 27 - readings

| Source | Retrieved | Licence | Use | Score |
|---|---|---|---|---|
| Metropolis & Ulam (1949), JASA 44(247):335-341, JSTOR stable/2280232 | Full text fetched | No open licence shown; JSTOR terms | Summary only. Facts: statistical approach to integro-differential equations; neutron multiplication as chains of events; sampling single chains instead of multiple integrations or matrix products; computing machines and parallel work; finite-sample error estimate still open. The DOI landing page and the publisher site returned no text; open copies seen in search results are JSTOR printouts and are not linked | 10 |
| Sargent (2010), WSC, informs-sim.org/wsc10papers/016.pdf | Fetched | © 2010 IEEE | Summary only. Definitions; four decision approaches (scoring model discouraged); process model with four checks; technique list; procedure with the accuracy requirement set early | 12 |
| Sargent (2020), WSC advanced tutorial, informs-sim.org/wsc20papers/002.pdf | Fetched | © 2020 IEEE | Sole author; three decision approaches; adds parsimony and usability | 10 |

## Assessment pack

- **CS2023 knowledge areas.** Names verified at csed.acm.org/knowledge-areas.
- **ABET.** EAC 2025-26 outcomes 1-7 and CAC 2026-27 outcomes 1-5 (plus CS outcome 6) verified on abet.org and paraphrased only (all rights reserved). The EAC 2026-27 page was search only.
- **14-week plan.** L500-SPEC says the plan comes "from the review", but neither REVIEW-L100-L200.md nor REVIEW-L300.md contains a 14-week plan. The syllabus was designed here so that each theory lesson lands next to the lab that uses it (KNOWN-GAPS).
