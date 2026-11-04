**Concept: reading primary sources - where Monte Carlo and V&V came from**

## Why it matters
Textbooks smooth history away. Reading the original papers shows what was hard at the time, what the authors admitted they did not know, and which of their words still frame the field. These two short papers are the roots of the two halves of this course: *how to compute with randomness* and *how to know whether to trust the result*.

## Reading 1: Metropolis & Ulam (1949), "The Monte Carlo Method"
- **Argument.** Many physical problems, such as neutron multiplication and diffusion, lead to integro-differential equations, or equivalently to products of probability matrices over many steps. Computing these exactly means multiple integrations that grow out of reach. Instead, *sample single chains of events*: follow one random history at a time with pseudo-random numbers and read off frequencies and averages. The authors present this as a statistical approach to such equations and stress that the new computing machines suit it well, including working on many machines in parallel.
- **What they left open.** They say a precise estimate of the error for a finite sample was still open. Lessons 23 and 25 answer this: the error is σ/√N (Theorem 25.3), and the interval comes from the CLT (Theorem 23.2), provided the variance is finite.
- **Companion check.** `labs/L500/27-readings/branching_process.py` follows 20,000 chains of a Poisson(1.2) branching process. It estimates the extinction probability as 0.6842 ± 0.0064, and that interval contains the analytic 0.6863 (the root of q = e^(1.2(q − 1))).
- **Access.** JSTOR (stable/2280232); the paper carries no open licence. Read it there. We summarise and never reproduce it.

## Reading 2: Sargent (2010), "Verification and validation of simulation models" (WSC)
- **Definitions.** *Verification* is ensuring that the computer program of the computerized model and its implementation are correct. *Validation* is substantiating that a model, within its domain of applicability, has a satisfactory range of accuracy consistent with its intended application.
- **Process model.** Problem entity → conceptual model → computerized model. Four checks attach to it: conceptual model validity, computerized model verification, operational validity and data validity.
- **Who decides.** Four approaches: the development team, user involvement, independent V&V and a scoring model. Sargent discourages scoring models.
- **Techniques.** Animation, comparison with other models, degenerate tests, event validity, extreme-condition tests, face validity, historical data validation, internal validity, sensitivity analysis, traces, Turing tests and others.
- **Procedure.** Specify the required accuracy *before* testing, test the assumptions, compare with system data, document, and review periodically.
- **The 2020 tutorial.** The same author's 2020 tutorial uses three decision approaches and adds parsimony and usability.
- **Access.** Free PDF from the WSC archive, © IEEE. Summarise; do not copy.

## How to read them
1. Read each paper once quickly for the argument.
2. Read it again with the five guiding questions for that paper in `readings`.
3. Write two sentences per section in your own words.
4. Connect each paper to one theorem (lessons 23-25) and one lab.
5. Draft the critical response: summary, evaluation, evidence (a seeded check), and limits.

## Common mistakes
- **Quoting instead of summarising.** It is weaker scholarship, and with copyrighted text it is a licence problem.
- **Treating 1949 as naive.** The authors flagged the error question themselves. Credit what they saw.
- **Treating Sargent's checklist as a guarantee.** Validity is a judgement against a purpose. The framework organises evidence; it does not replace judgement, especially for people-facing decisions (lesson 26).
