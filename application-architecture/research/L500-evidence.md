# L500 research evidence – Application Architecture (lessons 23–27, "theory & rigour")

Method: SPEC.md, adapted to theory. Per lesson: 2–3 questions → web_search / web_fetch of primary papers, standards,
statutes and regulators → keep primary or official sources, use secondary pages only to cross-check a fact → score kept
sources 0–2 on implementable (I), current (C), authoritative (A), open (O), transferable (T), right depth (D); keep ≥ 8/12.
All fetches on 2026-10-30. "search-only" = text seen in a search result (with its URL) but the page itself not fetched.
Every number in the lessons, problem sets, exams and question bank comes from code that ran: `labs/L500/*/check_*.py`,
`research/l500_checks.py` and `research/qbank_checks.py`. Copyrighted texts are summarised, never reproduced.

## Lesson 23 – Foundations I: modularity theory
**Questions.** (1) What exactly is Parnas's criterion and what evidence does the paper give? (2) What are Martin's metric
definitions and ranges? (3) What does empirical work say about dependency structure and defects?

| Source | Decision | Score | Reason |
|---|---|---|---|
| Parnas 1972, CACM 15(12) 1053–1058, doi 10.1145/361598.361623 (cacm.acm.org page; ACM DL epdf text via search) | kept | 1/2/2/2/2/2 = 11 | Primary source; abstract and introduction read; KWIC example; "module = responsibility assignment" |
| Martin 1994, "OO Design Quality Metrics" (DePaul mirror of the objectmentor PDF, fetched in full) | kept | 2/1/1/2/2/2 = 10 | Defines Ca, Ce, I, A, D and the main sequence; author's own caveat; objectmentor.com fetch failed (network), DePaul copy used |
| Zimmermann & Nagappan 2008, ICSE (Microsoft Research page + author PDF via search) | kept | 1/1/2/2/2/2 = 10 | Network measures on dependency graphs; recall +10 points; 60 % of critical binaries |
| El Emam et al. 2001, IEEE TSE 27(7) (IEEE CSDL abstract) | kept | 1/1/2/1/2/2 = 9 | Size confounding of OO metrics; abstract only (paywalled) |
| Tarjan 1972 (SCC algorithm) | not cited | – | Not retrieved; the note only says "linear time", a textbook fact |

**Key facts.** Parnas: modularisation should allow drastic changes to one module without changing others and studying the
system one module at a time; "module" is a responsibility assignment rather than a subprogram; the unconventional
decomposition, implemented naively as subroutines, "will be less efficient in most cases" (abstract). Martin: I = Ce/(Ca+Ce),
A = abstract/total, "D … range [0, ~0.707]" while the formula is printed as ÷2 – lesson 23 notes the discrepancy and uses
Dn = |A + I − 1|; Martin: "a metric is not a god". Local run: the hexagonal lab has 10 import edges, is strictly layered
(ports 0 → app 3); counting `__main__` blocks adds the SCC {app, driving_cli}; domain Dn = 0.833.

## Lesson 24 – Foundations II: quality attributes and trade-offs
**Questions.** (1) What is the current edition of ISO/IEC 25010 and what changed? (2) How does ATAM define scenarios, utility
trees and its outputs? (3) What is the standard maths of availability and a citable proof of the steady-state result?

| Source | Decision | Score | Reason |
|---|---|---|---|
| ISO/IEC 25010:2023 – iso.org/standard/78176.html | kept | 1/2/2/1/2/1 = 9 | Edition 2, published 2023-11, nine characteristics, replaces 2011; paywalled |
| ISO OBP foreword of ISO/IEC 25010:2023 (iso.org/obp/ui, via search) | kept | 1/2/2/1/2/2 = 10 | List of changes from 2011 (safety, interaction capability, flexibility, inclusivity, faultlessness …) |
| Secondary summaries (sonarsource.com, utaa.org, pacificcert) | supporting only | – | Cross-checked the nine characteristic names; vendor/consultancy pages, not cited as sources |
| Kazman, Klein, Clements 2000, CMU/SEI-2000-TR-004 (SEI library page + full PDF via a university mirror) | kept | 2/1/2/2/2/2 = 11 | Nine steps, scenario types, utility tree with (importance, risk) on H/M/L, risk/non-risk/sensitivity/trade-off definitions |
| Treynor, Dahlin, Rau, Beyer 2017, "The Calculus of Service Availability" (CACM) | kept | 2/1/2/2/2/2 = 11 | MTTF/(MTTF+MTTR); rule of the extra 9; 3 × 20 min outages vs 99.99 % (≤ 53 min/year) |
| Gallager, MIT OCW 6.262 ch. 4 Renewal Processes | kept | 1/1/2/2/2/2 = 10 | Renewal-reward theorem (full proof cited for T24.3); CC BY-NC-SA course material |

**Key facts.** ISO/IEC 25010:2023 "is composed of nine characteristics"; usability → interaction capability; portability →
flexibility; safety added; accessibility split into inclusivity and user assistance (ISO foreword). ATAM is "a risk
identification method"; leaves prioritised on H/M/L because stakeholders "cannot reliably and repeatably make finer
distinctions" (SEI report §5.3). Local runs: Library Loans path 99.837569 % by formula = enumeration of 32 states; Monte Carlo
400,000 trials within 4σ; MTTF 720 h / MTTR 1 h simulated within 2·10⁻⁴ for exponential and uniform repair.

## Lesson 25 – Foundations III: formal reasoning and the evidence
**Questions.** (1) What exactly is behavioural subtyping? (2) What can and cannot be concluded from empirical studies of
modularity and defects? (3) Which studies are primary and accessible?

| Source | Decision | Score | Reason |
|---|---|---|---|
| Liskov & Wing 1994, TOPLAS 16(6), doi 10.1145/197320.197383 (author PDF at columbia.edu, via search) | kept | 1/1/2/2/2/2 = 10 | Subtype requirement; stack vs queue; full treatment cited for T25.2 |
| Zimmermann & Nagappan 2008 | kept (again) | 10 | see lesson 23 |
| El Emam et al. 2001 | kept (again) | 9 | see lesson 23 |
| MacCormack, Rusnak, Baldwin 2006, Management Science 52(7) (HBS working-paper PDF, via search) | kept | 1/1/2/2/2/2 = 10 | DSM metrics; Linux vs first Mozilla; redesign more modular; "exploratory" |
| Meyer, design by contract (book) | not cited | – | Not retrieved; named only as the origin of the term |

**Honesty notes.** The concept note reports what each study measured and found, and labels them observational /
exploratory; no causal claim is made. The 60 % and "+10 points recall" figures are from the Zimmermann & Nagappan abstract.

## Lesson 26 – Ethics: accessibility, privacy by design, technical debt
**Questions.** (1) What is the current WCAG version and status (2.2? ISO?) and which new AA criteria are architectural?
(2) What does GDPR Art. 25 say, and is it enforced on its own? (3) Which professional codes apply?

| Source | Decision | Score | Reason |
|---|---|---|---|
| W3C WCAG 2.2 Recommendation (w3.org/TR/WCAG22, 12 Dec 2024 version) | kept | 2/2/2/2/2/2 = 12 | Normative text; W3C document licence |
| W3C WAI "What's New in WCAG 2.2" | kept | 2/2/2/2/2/2 = 12 | 9 new SC, levels; 4.1.1 removed; published 5 Oct 2023 |
| W3C Understanding SC 2.5.8 | supporting | – | 24 × 24 CSS px and the five exceptions (fetched) |
| W3C press release 21 Oct 2025 (ISO/IEC 40500:2025) | kept | 1/2/2/2/2/1 = 10 | WCAG 2.2 approved as ISO/IEC 40500:2025, free from ISO |
| GDPR Art. 25 (EUR-Lex ELI page; article text cross-checked on legislation.gov.uk, EU "as adopted" version) | kept | 2/2/2/2/2/2 = 12 | Text of 25(1)–(3); UK version has 2026 amendments (1A, 1B) – EU text used |
| Irish DPC decision, Meta Dataset, 25 Nov 2022 | kept | 1/2/2/2/2/2 = 11 | Art. 25(1) and 25(2) infringements, €265 m |
| Robles v. Domino's, 9th Cir. No. 17-55504 (opinion PDF, uscourts.gov) | kept | 1/1/2/2/1/2 = 9 | ADA Title III applied to website/app (US law; transferable as precedent of risk, not EU law) |
| Directive (EU) 2019/882 (EUR-Lex summary) | kept | 1/2/2/2/1/1 = 9 | Scope (e-commerce, e-books …) – the case states public-library coverage is for counsel |
| ACM Code of Ethics 2018 (acm.org, fetched in full) | kept | 2/2/2/2/2/2 = 12 | Principles 1.2, 1.3, 1.4, 1.6, 2.4, 2.5, 3.1, 3.7 |
| SE Code of Ethics 5.2 (computer.org) | kept | 1/1/2/2/2/1 = 9 | Eight principles (PUBLIC, PRODUCT, JUDGMENT …) |
| ALA Privacy interpretation of the Library Bill of Rights | kept | 1/2/2/2/1/2 = 10 | Circulation records confidential; minimum retention; anonymise |
| Cunningham 1992 OOPSLA experience report (c2.com) | kept | 1/1/2/2/2/2 = 10 | Origin of the debt metaphor and "interest" |
| wcag22aa.org, equalweb.com, thedpo.eu | dropped | – | Secondary/commercial; used only to cross-check dates already on W3C/DPC pages |

## Lesson 27 – Reading seminar
| Source | Decision | Score | Reason |
|---|---|---|---|
| Parnas 1972 | kept | 11 | Access verified: ACM DL fully open access since 1 Jan 2026 (acm.org bulletin, fetched via search); dl.acm.org DOI page fetch returned no text, so the CACM article page is linked |
| SEI ATAM report 2000 | kept | 11 | SEI library page fetched (free "Download PDF"); report front matter: "Unlimited distribution subject to the copyright", © 2000 Carnegie Mellon University |
| ACM open-access bulletin (1 Jan 2026) | supporting | – | Access statement for reading 1 |

## Assessment pack (syllabus)
| Source | Decision | Reason |
|---|---|---|
| CS2023 knowledge areas (csed.acm.org/knowledge-areas) | kept | Names and abbreviations of the 17 KAs (SE, SEP, SDF, MSF, PDC, SEC, HCI, FPL, SF …) |
| ABET CAC criteria 2026–2027 (PDF, fetched) | kept | General outcomes (1)–(5) + CS outcome (6); ABET forbids reproduction – syllabus paraphrases |
| ABET EAC criteria 2026–2027 (page, fetched) | kept | Outcomes (1)–(7) for engineering programmes; paraphrased |

**Finding on the spec.** L500-SPEC asks for "ABET student outcomes 1–7". Verified: 1–7 is the *engineering* (EAC) list; the
*computing* (CAC) general criteria have 1–5, plus programme-criteria outcome 6 for computer science. The syllabus maps to both.
