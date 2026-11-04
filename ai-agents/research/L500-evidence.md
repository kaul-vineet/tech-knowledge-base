# L500 evidence – AI Agents, lessons 23–27 (Theory & Rigour)

Research done 2026-10-30 with web_search / web_fetch. Rubric as in SPEC.md (implementable, current, authoritative, open, transferable, right depth; 0–2 each; keep ≥ 8/12). For L500 "implementable" means "a result we can state precisely and check numerically or apply to a case". Every number in content/L500.json, the qbank and the exams comes from running `labs/L500/*` (verified by `research/l500_checks.py`, `research/qbank_checks.py`).

## Lesson 23 – Foundations I: how language models work
**Questions.** (1) What exactly does the Transformer paper say about the 1/√d_k scaling – proof or conjecture? (2) What are the standard definitions of perplexity and MLE n-gram estimation? (3) What is top-p sampling and why was it proposed?

| Source | Kept? | Score | Notes |
|---|---|---|---|
| Vaswani et al. 2017, arXiv:1706.03762v7 (abstract + HTML full text) | kept | 12 | Eq. 1, Sec. 3.2.1: "We suspect that for large values of d_k, the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients"; footnote gives the variance argument. h = 8, d_k = d_v = d_model/h = 64 (Sec. 3.2.2); masking with −∞ (Sec. 3.2.3); Table 1 complexities O(n²·d) vs O(n·d²); attention cheaper when n < d (Sec. 4). Licence: arXiv perpetual non-exclusive – summarised only. |
| Jurafsky & Martin, SLP3 ch. 3 (draft of 19 Aug 2026), web.stanford.edu | kept | 11 | MLE bigram = relative frequency (eq. 3.11); perplexity = inverse probability normalised by N (eq. 3.14–3.15); zero counts make perplexity uncomputable; perplexities comparable only with identical vocabularies; intrinsic vs extrinsic evaluation. |
| Holtzman et al. 2019, arXiv:1904.09751 (ICLR 2020) | kept | 10 | Likelihood-maximising decoding gives "bland and strangely repetitive" text; nucleus sampling truncates the unreliable tail. Abstract only used. |
| Generic blog explanations of attention | dropped | 5–6 | Secondary, not citable for the scaling claim; the paper itself is available. |

**Cross-checks.** The variance argument is derived in T2 and measured (Var(q·k)/d = 1.005, 0.992, 1.000 for d = 4, 64, 512). The saturation effect the authors "suspect" is measured, not assumed (mean max weight 0.9439 unscaled vs 0.2461 scaled at d = 512). Perplexity definitions agree between SLP3 and the derivation in T3 (uniform model → V = 11.0000).

## Lesson 24 – Foundations II: statistics for evaluating agents
**Questions.** (1) Which binomial interval should be recommended, by an authoritative source? (2) What is the original reference for the paired test? (3) What sample-size relation applies to a one-sided proportion test?

| Source | Kept? | Score | Notes |
|---|---|---|---|
| NIST/SEMATECH e-Handbook §7.2.4.1 | kept | 12 | Wilson method (Wilson 1927; recommended by Brown, Cai & DasGupta 2001 and Agresti & Coull 1998) obtained by inverting the score test; formula; lower limit cannot be negative; exact binomial interval procedure; terminology note on Agresti–Coull. |
| McNemar 1947, Psychometrika 12(2):153–157, doi:10.1007/BF02295996 (Cambridge Core landing page) | kept | 9 | Two formulas for correlated proportions; chi-square equivalent. Full text not retrieved (paywalled); the test statistic used is standard and is re-derived in T3. |
| Brown, Cai & DasGupta 2001 (Project Euclid) | not retrievable | – | Fetch returned no document; cited only via NIST. |
| Jurafsky & Martin ch. 3 §3.2 | kept (supporting) | 10 | "smallest test set that gives us enough statistical power". |

**Cross-checks.** Wilson formula = numerical bisection of the score equation (agree to 1e-9 for 20/20, 18/20, 180/200). Coverage computed exactly by summing binomial probabilities, no simulation (Wald 0.6389 vs Wilson 0.9245 at n = 20, p = 0.95). Sample size n = 253 for 0.90 → 0.85 checked with the exact binomial test (size 0.0473, power 0.7810 – reported honestly as slightly below 0.8).

## Lesson 25 – Foundations III: decision theory and planning
**Questions.** (1) Standard statement of MDPs, Bellman optimality and value iteration? (2) Original source for A* optimality? (3) Original source for Rice's theorem?

| Source | Kept? | Score | Notes |
|---|---|---|---|
| Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed. (book page, full PDF linked) | kept | 11 | MDPs, Bellman equations, value iteration (ch. 3–4). Only the book page was fetched; the contraction proof in T2 is self-contained. |
| Hart, Nilsson & Raphael 1968, IEEE Trans. SSC 4(2), IEEE Xplore 4082128 | kept | 9 | Found via search (abstract page); full text paywalled. Proof sketch in T3 is the standard argument; cited as the origin. |
| Rice 1953, Trans. AMS 74:358–366 (AMS page; PDF excerpt via search) | kept | 10 | "no nontrivial class is completely recursive". T4 uses the halting-problem reduction rather than Rice's notation. |
| Yao et al. 2023 (ReAct) | kept | 11 | Repetitive-loop failure mode; budget/back-off after 7 steps (HotpotQA). |

**Cross-checks.** Retry formula vs 20,000-run simulations (e.g. p = 0.3, k = 8: 3.1412 vs 3.1198); value iteration vs closed form (4.9383); contraction ratio measured ≤ 0.95; A* with admissible heuristic = BFS optimum (15) and fewer expansions (26 vs 58); overestimating heuristic returns cost 8 vs 4.

## Lesson 26 – Ethics, society and professional responsibility
**Questions.** (1) What do primary law and professional codes require for chatbots/agents (disclosure, oversight, automated decisions)? (2) Current status of the EU AI Act timetable in October 2026? (3) A real case on accountability for an AI agent's statements.

| Source | Kept? | Score | Notes |
|---|---|---|---|
| ACM Code of Ethics and Professional Conduct (2018), acm.org | kept | 12 | Quoted: 1.3 (not misrepresent policies), 1.4, 1.6 (minimum data, retention), 2.4, 2.5 ("should not be deployed"), 2.9 ("best option may be to not implement"). Publishable unchanged with copyright notice. |
| NIST AI 100-1 (AI RMF 1.0) PDF + NIST AI RMF page | kept | 12 | Trustworthiness characteristics; GOVERN/MAP/MEASURE/MANAGE; "humans may assume that AI systems work"; "cease in a safe manner"; disaggregation. Page notes AI RMF 1.0 is being revised (White House AI Action Plan) – recorded in KNOWN-GAPS. |
| Regulation (EU) 2024/1689, EUR-Lex (consolidated version 27/07/2026 listed) | kept | 11 | Recitals fetched from EUR-Lex; article text for Art. 14 and 50 read on artificialintelligenceact.eu (mirror with dates per Art. 113 as amended) and cross-checked with the EP Legislative Train and two law-firm summaries for the omnibus dates. |
| Regulation (EU) 2026/1744 (Digital Omnibus on AI), OJ PDF (search result) + EP Legislative Train + Council press release 29 Jun 2026 | kept | 10 | Signed 8 Jul 2026, published 24 Jul 2026, in force 27 Jul 2026; Annex III high-risk to 2 Dec 2027, Annex I to 2 Aug 2028; Art. 50 date 2 Aug 2026 unchanged; AI-literacy duty softened; Art. 4a bias-detection processing. |
| GDPR Art. 22 (legislation.gov.uk "as adopted" EU text) | kept | 10 | Exact wording of Art. 22(1), (3). EUR-Lex HTML of the GDPR fetched (consolidated 2016 text) but the article view used the legislation.gov.uk mirror of the OJ version. |
| Moffatt v. Air Canada, 2024 BCCRT 149 (full reasons; Sedona Conference copy; CanLII URL returned no document) | kept | 10 | Paragraphs 24–44 used: duty of care, "remarkable submission", "still just a part of Air Canada's website", damages 650.88, total 812.02. |
| Parasuraman & Riley 1997, Human Factors 39(2) (MIT-hosted PDF, search excerpt) | kept | 9 | Definitions of use, misuse (over-reliance), disuse, abuse. |
| Law-firm summaries (Orrick, Akin) of the omnibus | background only | 6 | Used only to cross-check dates; not cited in lessons. |
| artificialintelligenceact.eu | background/mirror | 7 | Non-official mirror; used to read article text and amended application dates; official sources cited instead. |

## Lesson 27 – Reading seminar
| Source | Kept? | Score | Notes |
|---|---|---|---|
| Vaswani et al. 2017 (abstract, HTML v7) | kept | 12 | As above. |
| Yao et al. 2023, arXiv:2210.03629v3 (abstract + PDF) | kept | 12 | Action space Â = A ∪ L; HotpotQA/FEVER API search/lookup/finish; Table 1 (EM: Standard 28.7, CoT 29.4, CoT-SC 33.4, Act 25.7, ReAct 27.4, ReAct→CoT-SC 35.1; supervised 67.5); Table 2 from 50 trajectories per group (false positives 6 % vs 14 %; hallucination 0 % vs 56 % of failures; repetitive-loop reasoning errors); ALFWorld +34 %, WebShop +10 % absolute; back-off after 7/5 steps; prompted ReAct worst at 8B/62B, best after fine-tuning; ethics statement on action spaces; PaLM not openly accessible. |

## Assessment pack
| Source | Kept? | Notes |
|---|---|---|
| ABET Criteria for Accrediting Computing Programs 2025–2026 | kept | CAC outcomes 1–5 + CS outcome 6 (wording checked). |
| ABET Criteria for Accrediting Engineering Programs 2025–2026 | kept | EAC outcomes 1–7 (wording checked). The spec's "ABET 1–7" applies to EAC; both mappings are given. |
| CS2023 knowledge areas (csed.acm.org/knowledge-areas) | kept | 17 KAs; abbreviations used in the syllabus mapping. |

Sources kept for L500: 21 unique documents (rows above, excluding dropped/background rows and the Council press release, which was seen only as a search result). New rows added to `documentation/VERIFIED-RESOURCES.md`.
