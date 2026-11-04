**Concept: Reading seminar – Parnas (1972) and the SEI ATAM report (2000)**

## Why read primary sources
Every boundary rule and every quality scenario in this course descends from a small number of original texts. Reading
them yourself shows what the authors actually claimed, what evidence they offered, and which of today's "best practices"
are later reinterpretations. Both texts are free to read: the ACM Digital Library has been fully open access since
1 January 2026, and the SEI publishes the ATAM report as a free download. Free to read is not free to copy – summarise in
your own words, quote sparingly with page or section references, and cite.

## Reading 1 – Parnas, "On the criteria to be used in decomposing systems into modules" (CACM, 1972)
**What it argues.** Modularisation is expected to bring three benefits: shorter development (separate groups work with
little communication), product flexibility (drastic changes to one module without changing others) and comprehensibility
(study the system one module at a time). Whether these benefits appear depends on the *criterion* used to split the
system. Parnas treats a module as a responsibility assignment, not a subprogram.

**How it argues.** With a deliberately small example, a KWIC index generator, he describes a conventional decomposition by
processing steps and an unconventional one in which each module hides a design decision. He then walks through likely
changes and shows which modules each change touches. The evidence is a reasoned comparison on one example, not an
experiment – keep that in mind when you generalise.

**What to watch for.** His conclusion recommends starting from a list of difficult or likely-to-change design decisions; it
also discusses efficiency, noting that the unconventional decomposition implemented naively as subroutine calls may be
slower, and sketching another way to implement it. Ask what this means for module boundaries that are network calls.

**Link to the course.** Lesson 23's `KWIC_*` model is our reading of his argument; the guiding questions ask you to check
it against the paper. Lessons 3, 7 and 17 are Parnas modules with checked interfaces.

## Reading 2 – Kazman, Klein and Clements, "ATAM: Method for Architecture Evaluation" (CMU/SEI-2000-TR-004)
**What it argues.** Architectures embody trade-offs among quality attributes; without a structured analysis an
organisation cannot know whether its decisions mitigate risks. The report presents the Architecture Tradeoff Analysis
Method, developed and refined in practice by its authors.

**How it works.** Nine steps grouped as presentation (method, business drivers, architecture), investigation (architectural
approaches, a quality-attribute utility tree, analysis), testing (stakeholder scenario brainstorming and prioritisation,
re-analysis) and reporting, run in two phases with different stakeholder groups. Scenarios come in three types – use case,
growth and exploratory – and leaf scenarios are prioritised by importance and difficulty on a High/Medium/Low scale.

**What it produces.** Not a score: risks, non-risks, sensitivity points and trade-off points, plus a shared, concrete
statement of quality requirements. The authors stress that the method identifies risk and trends early rather than
predicting quality attributes precisely.

**What to watch for.** The report assumes an evaluation *event* with an architecture presentation. Ask how that maps to a
team shipping weekly: utility trees kept in the repository, scenarios as tests, ADRs for decisions, fitness functions and
the lesson 22 scorecard for continuous re-evaluation.

## How to write the critical response
State a thesis in one sentence. Support it with two or three specific points from the reading, paraphrased and cited.
Present the strongest counter-argument fairly (for Parnas: Conway's law and team-aligned boundaries; for ATAM: cost and
cadence). Apply it to one concrete Library Loans decision, with evidence from a lab. Finish with what would change your
mind. The rubric rewards argument and application over summary.
