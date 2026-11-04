# Reading seminar 27: Grover (1996) and Preskill (2018)

Textbooks and lab guides compress decades of argument into a few formulas. Primary papers show the original claim, the assumptions behind it, and the author's own caveats. This seminar pairs a founding algorithm paper with an agenda-setting perspective paper, each followed by later evidence.

## How to read a paper in this course

1. **Abstract and conclusion first.** Write the main claim in one sentence.
2. **Find the assumptions.** What must hold for the claim to be true? Think oracle model, noise level, input format, classical baseline.
3. **Find the evidence.** Is it a proof, a numerical example, an experiment, or an argument from authority?
4. **Check one thing yourself.** Use a theorem from lessons 23-25 or a script in `labs/L500`.
5. **Ask what changed.** Which later work confirmed, sharpened or overturned the claim?

## Reading 1: Grover (1996)

*A fast quantum mechanical algorithm for database search* (STOC 1996; arXiv:quant-ph/9605043v3).

**What it claims.** Grover frames the problem as a phone directory of N names in random order. Classically you must look at about N/2 names for a 50% chance of finding a given one. The quantum algorithm needs only O(√N) steps. The abstract also says the algorithm is within a small constant factor of the best possible quantum algorithm. The revised version simplifies the proof with an "inversion about average" interpretation.

**Connect it.** "Inversion about average" is the map a_i -> 2·mean - a_i, which is the matrix 2|s><s| - I (problem P2). It is one of the two reflections in T25.1, and the lab code implements it as `2 * psi.mean() - psi`. The optimality claim was later proved: Bennett, Bernstein, Brassard and Vazirani (1997) gave the lower bound, and Boyer, Brassard, Høyer and Tapp (1998) gave the exact success formula and handled unknown numbers of solutions.

**Read critically.** "Database" suggests stored data, but the speed-up applies to queries of a function that can be computed on a superposition. A real database first has to be loaded, which costs about N steps. For N = 10^6, about 785 Grover iterations replace 500,000 classical look-ups. Each iteration, though, is a deep circuit on error-corrected hardware (L400 #19).

**Licence.** The paper is distributed by arXiv under arXiv's own licence, not an open content licence. Read it there and quote only short, attributed phrases.

## Reading 2: Preskill (2018)

*Quantum Computing in the NISQ era and beyond*, Quantum 2, 79 (CC BY 4.0).

**What it claims.** Preskill coins "NISQ": noisy devices of 50 to a few hundred qubits without error correction. He argues they may beat classical computers on some tasks, but gate noise limits reliable circuit size. Naively, with two-qubit error rates above 0.1%, circuits of much more than about 1000 gates are out of reach. He sees NISQ machines as tools for exploring many-body physics that will not "change the world right away". The long-term goal remains accurate gates and full fault tolerance.

**Connect it.** The noise argument is our problem P3: (1 - ε)^G ≈ 0.3677 for ε = 10^-3 and G = 1000. Preskill defines a quantum speed-up against the best classical hardware *and* algorithm, and calls the classical side a moving target. He discusses QAOA and VQE (L300 #14-#15), quantum annealing, quantum machine learning and its input/output bottlenecks, and HHL. He also adds a note that Tang's quantum-inspired classical algorithm removed the exponential speed-up claimed for quantum recommendation systems.

**Read critically.** Which predictions held up? The 2019 supremacy experiment arrived, and classical simulations then narrowed the gap (lesson 26). The NISQ applications he lists remain unproven at useful scale. Error correction is advancing, as he said it must.

## The response assignment

Choose one reading's response prompt (500-700 words). A strong response does five things:
- summarises fairly in your own words;
- names the paper's assumptions;
- verifies one number with code;
- brings in at least one later source;
- ends with a reasoned judgement for a practitioner.

The rubric weights fair summary 25%, critical evaluation 35%, evidence 25% and writing 15%.

## Seminar format (60 minutes)

10 minutes on each paper's claim in one sentence; 20 minutes on guiding questions in pairs; 20 minutes of whole-group debate on the motion "Grover's algorithm will matter in practice before NISQ devices do"; 10 minutes on what each of you will verify in code for the response.
