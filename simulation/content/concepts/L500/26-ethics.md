**Concept: when the model's output is a decision about a person**

## Why it matters
Most models in this course feed a decision about *things*: how many desks to open, which inventory policy to use. The capstone was different, because it staffed people's shifts. In summer 2020 a statistical model in England helped decide every A level and GCSE grade. Its aggregate behaviour was defended with care, its individual consequences were not communicated, and it was withdrawn four days after results day. Once a model's output becomes a decision about a person, the professional duties change, and so does the evidence the model needs.

## Key ideas
- **Intended use first.** Sargent's definition of validity is relative to an intended application and a required range of accuracy, set *before* testing. A model can be valid for predicting a group (a school's grade distribution) and invalid for deciding an individual (one student's grade). Moving from one use to the other is a change of purpose, and it needs new evidence.
- **Aggregate validity is not individual validity.** The lesson's synthetic simulation (`labs/L500/26-ethics/aggregate_vs_individual.py`) ranks 100,000 students by a teacher judgement that correlates 0.80 with an exam score. It then assigns grades to reproduce the historical distribution exactly. The distribution error is 0.0000, yet only 40.0% of students get the grade the exam would have given (86.4% within one grade). Two equally good exam sittings agree only 39.7% of the time. Individual-level uncertainty is real in normal years too, which is a reason to communicate it, not to ignore it.
- **Small groups are noisy (Theorem 23.1).** A centre's top-grade share estimated from 3 years of 8 students has an SD of 0.090, a 34% relative error. At 200 students it is 7%. Ofqual's rule for groups under 15 (put more weight on teacher grades) follows from the statistics. But the teacher grades were optimistic, so the rule had a distributional effect that someone has to own.
- **Transparency and uncertainty communication.** The Office for Statistics Regulation (OSR) concluded that the models' "limitations … and uncertainty in the results … were not fully communicated". It also found that methodology was not published in advance and that there was "limited human review of outputs … at an individual level". Ofqual had explicitly ranked transparency below its other aims. Uncertainty statements must be written for each audience: a student, an admissions officer, a minister.
- **Validation duty.** Australia's Robodebt averaged annual income across fortnights. That assumption is false for people with irregular earnings, who are exactly the people moving on and off benefits. In a 2019 test case a court declared, with the government's consent, that a debt raised this way was not validly made, and a 2023 Royal Commission followed. Checking assumptions against the population a model is applied to is part of the job (conceptual model validity and data validity).
- **Reproducibility is verification, not validation.** CovidSim's code was released and independently re-run in 2020. That establishes that the published code gives the published numbers. It does not establish that the assumptions are adequate for a policy decision.
- **Misuse.** Misuse includes using a model outside its validated envelope, using an output as a decision without human review, and hiding behind the model ("the algorithm decided"). Safeguards include intended-use statements on the model card (L400 #21), pre-release review of predictable outliers, appeals designed before release, published methods, and a rule for when the model must *not* be used.

## The obligations, from primary sources
- **ACM Code (2018).** 1.2 avoid harm. 1.3 be honest and trustworthy. 2.5 "give comprehensive and thorough evaluations of computer systems and their impacts, including analysis of possible risks". 3.1 make the public good the central concern.
- **IEEE Code (Policies 7.8), I.5.** Be "honest and realistic in stating claims or estimates based on available data", seek honest criticism, and acknowledge errors.
- **AQuA Book (2025).** Four roles: commissioner, analyst, assurer and approver, with analyst and assurer kept separate. Quality assurance is proportionate to the risk of the intended use. Uncertainty is identified, managed and communicated.
- **NASA-STD-7009B (2024).** Credibility is assessed by factors such as input pedigree, verification, validation, uncertainty characterization and results robustness, and M&S results are reported to decision makers *together with* their credibility. It is a civilian engineering standard, used here by analogy.
- **OSR (2021).** Be open and trustworthy; be rigorous and ensure quality throughout; meet the need and provide public value. This includes testing acceptability with *all affected groups*.

## A method for case analysis
Work through the case in this order:
1. Facts.
2. Intended use, and any change of use.
3. Stakeholders and harms.
4. Obligations (codes, standards, statute).
5. Options.
6. A recommendation with named safeguards and owners.

The lesson's `caseStudy.modelAnswer` applies it to 2020. Hold the decision makers to professional standards while representing their constraints fairly: OSR found the teams "acted with honesty and integrity" under impossible timescales.

## Common misconceptions
- **"If the totals are right, the model is fair."** Fairness to individuals needs individual-level evidence and a route to challenge.
- **"Publishing the code makes the model trustworthy."** Publication enables verification; validity still has to be argued.
- **"Uncertainty will confuse people, so leave it out."** OSR identifies exactly that omission as a cause of lost confidence. Use natural frequencies ("about 1 in 10 students").
- **"Ethics is the policy team's job."** ACM 2.5 puts the evaluation of impacts and risks on the computing professional.

Sources: Ofqual interim report (2020) and statement of 17 August 2020; OSR (2021); ACM Code; IEEE 7.8; AQuA Book (2025); NASA-STD-7009B; Robodebt Royal Commission (2023); Nature (2020) on CovidSim. Next: the reading seminar.
