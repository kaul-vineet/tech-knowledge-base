"""L500 lesson 27 data: reading seminar (Grover 1996, Preskill 2018). Built into content/L500.json by build_l500_json.py.

Licence note: Grover's arXiv preprint is distributed under arXiv's licence (no open content licence), Preskill's paper is
CC BY 4.0 (Quantum). Both are summarised here in our own words; nothing is reproduced.
"""

LESSON = {
    "id": "reading-seminar-grover-preskill",
    "number": 27,
    "level": "L500",
    "title": "Reading seminar 27: Grover (1996) and Preskill (2018)",
    "phase": "Theory & Rigour",
    "category": "reading seminar",
    "description": "Read two foundational primary sources - the paper that introduced quantum search and the paper that named the "
                   "NISQ era - with guided questions, then write a critical response that connects them to lessons 23-26.",
    "outcome": "You can read a primary quantum-computing paper for its claims, assumptions and evidence, relate its arguments to "
               "the theorems you proved (T25.1) and the practice you built (L300-L400), and write a critical response that "
               "evaluates what has held up and what has changed.",
    "estimatedTime": "5-6 hours (reading 3 h, seminar 1 h, response 1-2 h)",
    "prerequisites": [
        "lessons 23-26, especially T25.1 (Grover) and lesson 26 (claims and baselines)",
        "reading a technical paper: abstract, claims, assumptions, evidence, limitations",
    ],
    "learningObjectives": [
        "Explain the central claim and the 'inversion about average' argument of Grover (1996) and relate it to the reflection proof of T25.1.",
        "Analyze Preskill's (2018) definition of NISQ, his reasons for caution, and the applications he considers plausible.",
        "Evaluate which claims in each paper have been confirmed, sharpened or overtaken by later work (BBBV/Boyer et al.; 2019-2022 supremacy and rebuttals).",
        "Critique, in a structured written response, how the two papers frame expectations for practitioners, using evidence from the course labs.",
    ],
    "glossary": [
        {"term": "inversion about average", "meaning": "Grover's name for the diffusion step: each amplitude a_i -> 2·mean - a_i (= 2|s><s| - I)."},
        {"term": "NISQ", "meaning": "Noisy Intermediate-Scale Quantum: devices of 50 to a few hundred qubits without error correction, whose gate noise limits circuit size (Preskill 2018, section 4.1)."},
        {"term": "quantum supremacy", "meaning": "A demonstrated task beyond feasible classical computation, whether or not useful (term used by Preskill)."},
        {"term": "critical response", "meaning": "A short essay that summarises a source fairly, then evaluates its claims against evidence."},
    ],
    "readings": [
        {
            "citation": "L. K. Grover, 'A fast quantum mechanical algorithm for database search', Proceedings of the 28th Annual ACM Symposium on the Theory of Computing (STOC), May 1996, pp. 212-219; updated preprint arXiv:quant-ph/9605043v3 (19 Nov 1996).",
            "url": "https://arxiv.org/abs/quant-ph/9605043",
            "why": "The origin of the algorithm you ran in L200 #8 and derived in T25.1. The abstract frames search as finding a phone number in an unsorted directory: classically about N/2 look-ups for a 50% chance, quantumly O(√N) steps, and claims near-optimality. The v3 proof uses an 'inversion about average' interpretation. Licence: distributed by arXiv (no open content licence found on the abstract page), so read it there and quote only short attributed phrases.",
            "guidingQuestions": [
                "State the problem Grover solves precisely. What is the 'database' in the abstract really, and what does an oracle query correspond to in your L200 #8 lab?",
                "Explain 'inversion about average' as a matrix. Show that it equals 2|s><s| - I and connect it to the reflection argument in T25.1.",
                "Grover claims the algorithm is within a small constant factor of the fastest possible quantum algorithm. Which later papers prove matching lower bounds, and what do they show (BBBV 1997; Boyer et al. 1998)?",
                "Which assumptions are needed for the speed-up to be practical (oracle cost, error rates, clock speeds, number of marked items)? Use T25.1 and the IBM course's caution about quadratic advantages.",
                "The abstract contrasts quantum with any classical algorithm, 'deterministic or probabilistic'. Is the comparison fair as stated? What would a fair benchmark (L400 #18) require?",
            ],
            "responsePrompt": "In 500-700 words, explain Grover's central argument in your own notation, verify one numerical claim with labs/L500/25-algorithms-and-complexity/theorems.py (e.g. the iteration count for N = 1024), and evaluate whether 'database search' is a good description of what the algorithm accelerates in practice.",
        },
        {
            "citation": "J. Preskill, 'Quantum Computing in the NISQ era and beyond', Quantum 2, 79 (2018), doi:10.22331/q-2018-08-06-79; arXiv:1801.00862.",
            "url": "https://quantum-journal.org/papers/q-2018-08-06-79/",
            "why": "The paper that named the era your L300 labs simulate. Its abstract argues that 50-100-qubit devices may surpass classical computers on some tasks but that gate noise limits reliable circuit size, that such devices will not change the world right away, and that the goal must remain more accurate gates and eventually fault tolerance. Licence: Quantum publishes under CC BY 4.0; we still summarise rather than reproduce.",
            "guidingQuestions": [
                "How does Preskill define NISQ, and which two limits (size and noise) does each word refer to? Map them to your L300 #12 noise-model results.",
                "Which applications does Preskill treat as promising for NISQ devices (e.g. simulation of quantum many-body physics, variational and optimisation methods, quantum machine learning), and what caveats does he attach to each?",
                "Preskill defines a quantum speed-up against the best classical hardware and algorithm, and adds a note that Tang's quantum-inspired classical algorithm removed the exponential speed-up of quantum recommendation systems. What does this teach about speed-up claims (lesson 25, P9)?",
                "What has happened since 2018 to the 'quantum supremacy' expectation he discusses? Use the Sycamore claim and its classical rebuttals (lesson 26).",
                "Why does he argue that fault tolerance remains the long-term goal? Connect to the resource estimates in L400 #19.",
            ],
            "responsePrompt": "In 500-700 words, summarise Preskill's argument fairly, then evaluate one of his predictions against evidence available today (cite at least one primary source from lesson 26 or the course labs). Close with what a software engineer should take from the paper when asked to 'add quantum' to a product.",
        },
    ],
    "problemSet": [
        {"id": "qc-L500-27-P1", "type": "calculation", "difficulty": 1, "marks": 3,
         "problem": "Grover's abstract contrasts about N/2 classical look-ups (for a 50% chance) with O(√N) quantum steps. For N = 10^6, compute the classical figure and the optimal Grover iteration count from T25.1, with its success probability.",
         "solution": "Classical: N/2 = 500,000 look-ups for a 50% chance. Grover: θ = asin(10^-3), k = floor(π/(4θ)) = 785 iterations with P ≈ 1.0000 (0.99999996). The ratio is about 637, but each quantum step includes an oracle call and a diffusion circuit on error-corrected hardware, so wall-clock comparisons need the overheads of L400 #19."},
        {"id": "qc-L500-27-P2", "type": "short-answer", "difficulty": 1, "marks": 3,
         "problem": "Show that Grover's 'inversion about average' a_i -> 2·mean(a) - a_i is the matrix 2|s><s| - I.",
         "solution": "With |s> = (1/√N)Σ|i>, (|s><s| a)_i = (1/N)Σ_j a_j = mean(a). So ((2|s><s| - I)a)_i = 2·mean(a) - a_i. The lab code in T25.1 implements exactly 'psi = 2 * psi.mean() - psi'."},
        {"id": "qc-L500-27-P3", "type": "calculation", "difficulty": 2, "marks": 4,
         "problem": "A simple model of NISQ noise: a circuit of G gates, each failing independently with probability ε, succeeds with probability (1 - ε)^G. Compute this for ε = 10^-3 with G = 1000 and G = 100, and for ε = 10^-4 with G = 1000. What circuit size keeps success near 1/e?",
         "solution": "(1 - 0.001)^1000 = 0.3677; (1 - 0.001)^100 = 0.9048; (1 - 0.0001)^1000 = 0.9048. Success stays near 1/e ≈ 0.37 when G ≈ 1/ε: reliable circuit size scales inversely with the error rate, which is the quantitative core of 'noise limits the size of circuits that can be executed reliably'. Preskill makes the same naive estimate (section 4.2: with two-qubit error rates above 0.1%, circuits of much more than about 1000 gates are out of reach) and notes in section 6.4 that some noise-resilient circuits may do better; correlated errors can do worse."},
        {"id": "qc-L500-27-P4", "type": "short-answer", "difficulty": 2, "marks": 5,
         "problem": "For each paper, give one claim that later work confirmed or sharpened and one that later work qualified.",
         "solution": "Grover: confirmed/sharpened - near-optimality (BBBV 1997 lower bound; Boyer et al. 1998 exact formula and quantum counting); qualified - practical value: a quadratic speed-up is easily erased by hardware overheads (IBM course caution; L400 #19). Preskill: confirmed - 'will not change the world right away' and noise as the binding constraint; sharpened/qualified - supremacy experiments arrived (2019) but classical methods narrowed the gap (2019 days-scale estimate, 2022 15 GPU-hours), showing advantage claims are moving targets."},
        {"id": "qc-L500-27-P5", "type": "essay", "difficulty": 3, "marks": 10,
         "problem": "Critical response (choose one reading's responsePrompt). 500-700 words, at least two citations, one number verified by code.",
         "solution": "Graded with this lesson's rubric. A strong response summarises fairly (no strawman), identifies the paper's assumptions, tests one claim with code from labs/L500, brings in at least one later source, and ends with a reasoned judgement rather than a verdict of 'good/bad'."},
        {"id": "qc-L500-27-P6", "type": "short-answer", "difficulty": 2, "marks": 4,
         "problem": "Both papers are freely readable but under different licences. What may you do with each in your own course notes, and what does the ACM Code (1.5) ask of you?",
         "solution": "Preskill (Quantum) is CC BY 4.0: you may share and adapt with attribution. Grover's arXiv preprint carries arXiv's distribution licence, which grants arXiv (not you) the right to distribute: link to it and quote briefly with attribution, but do not copy it. ACM 1.5 asks you to credit creators and respect copyrights and licence agreements; summarising in your own words with citations satisfies both."},
    ],
    "rubric": [
        {"criterion": "Fair summary", "excellent": "States the paper's claims, assumptions and evidence accurately in own words; no quotation beyond short attributed phrases.", "adequate": "Accurate but misses an assumption.", "inadequate": "Misrepresents or copies the source.", "weight": 25},
        {"criterion": "Critical evaluation", "excellent": "Tests at least one claim against later evidence and the course's own results; distinguishes what held up from what changed.", "adequate": "Some evaluation, mostly descriptive.", "inadequate": "Purely descriptive or purely opinion.", "weight": 35},
        {"criterion": "Evidence and verification", "excellent": "One number verified with labs/L500 code (output quoted); at least two primary citations.", "adequate": "Citations present, no code check.", "inadequate": "No citations.", "weight": 25},
        {"criterion": "Writing", "excellent": "Clear structure, within length, precise terminology.", "adequate": "Readable, minor issues.", "inadequate": "Disorganised or far outside length.", "weight": 15},
    ],
    "conceptNote": "content/concepts/L500/27-reading-seminar.md",
    "conceptSummary": "Two primary sources, read critically. Grover (1996) introduced O(√N) search with 'inversion about average' and claimed near-optimality, later proved. Preskill (2018) named the NISQ era: noisy 50-100+ qubit devices may beat classical computers on some tasks but will not change the world right away, so fault tolerance stays the goal. The seminar asks what each claimed, what held up, and what changed.",
    "sources": [
        {"title": "Grover (1996), A fast quantum mechanical algorithm for database search, arXiv:quant-ph/9605043", "url": "https://arxiv.org/abs/quant-ph/9605043"},
        {"title": "Preskill (2018), Quantum Computing in the NISQ era and beyond, Quantum 2, 79", "url": "https://quantum-journal.org/papers/q-2018-08-06-79/"},
        {"title": "Quantum journal: Terms and Conditions announcement (CC BY 4.0 licence for published works)", "url": "https://quantum-journal.org/terms-and-conditions-announcement/"},
        {"title": "arXiv.org non-exclusive license to distribute", "url": "https://arxiv.org/licenses/nonexclusive-distrib/1.0/license.html"},
        {"title": "Bennett, Bernstein, Brassard, Vazirani (1997), Strengths and weaknesses of quantum computing, arXiv:quant-ph/9701001", "url": "https://arxiv.org/abs/quant-ph/9701001"},
        {"title": "Boyer, Brassard, Høyer, Tapp (1998), Tight bounds on quantum searching, arXiv:quant-ph/9605034", "url": "https://arxiv.org/abs/quant-ph/9605034"},
        {"title": "ACM Code of Ethics and Professional Conduct (2018), principle 1.5", "url": "https://www.acm.org/code-of-ethics"},
    ],
    "seeAlso": [
        "quantum-computing L200 #8 Small Grover search: the algorithm of reading 1, run and plotted.",
        "quantum-computing L300 #12 Noise models: how Bell and GHZ results degrade: the 'noisy' in NISQ, measured.",
        "quantum-computing L300 #14 QAOA on MaxCut vs the classical optimum: a NISQ application Preskill discusses, tested against the classical optimum.",
        "quantum-computing L400 #19 Resource estimation: logical vs physical qubits and feasibility: the 'beyond' in Preskill's title.",
    ],
    "next": "Course assessment pack: content/assessment/ (syllabus, midterm, final, concept inventory, capstone oral defence, ADR peer review).",
}
