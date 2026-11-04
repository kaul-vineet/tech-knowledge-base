**Concept: ethics, society and professional responsibility for AI agents**

## Why it matters
An agent acts on someone's behalf: it answers customers, files tickets, issues refunds, reads private data. When it is wrong, a real person bears the cost, and someone – not the model – is answerable. The engineering in lessons 11–22 (guardrails, approval gates, audit logs, "code decides") is how responsibility becomes concrete. This lesson names the obligations those mechanisms serve and the law and standards that now require some of them.

## Accountability: the deployer answers for the agent
In *Moffatt v. Air Canada* (2024 BCCRT 149) an airline's website chatbot told a bereaved customer he could claim a bereavement fare retroactively within 90 days; the airline's own policy page said the opposite. The airline argued it could not be held liable for the chatbot. The tribunal called this "a remarkable submission", held that the chatbot "is still just a part of Air Canada's website", found negligent misrepresentation, and ordered the airline to pay the fare difference plus interest and fees. The engineering lesson: an agent's answer is your organisation's statement. The ACM Code says the same in professional terms: computing professionals "should not misrepresent an organization's policies or procedures" (1.3) and should give "comprehensive and thorough evaluations of computer systems and their impacts" (2.5). The NIST AI RMF 1.0 lists "accountable and transparent" among the characteristics of trustworthy AI and notes that "accountability presupposes transparency" (§3.4).

## Over-reliance and human factors
Putting a human "in the loop" does not by itself make a system safe. Parasuraman and Riley (1997) define *misuse* as over-reliance on automation, leading to monitoring failures and decision biases, and *abuse* as automating functions "without due regard for the consequences for human performance". The EU AI Act writes this into law for high-risk systems: people assigned to oversight must be able "to remain aware of the possible tendency of automatically relying or over-relying on the output … (automation bias)" and must be able to override or stop the system (Art. 14(4)(b), (d), (e)). NIST notes that people "may assume that AI systems work – and work well – in all settings". Design consequences: show the evidence, not just the answer; make "disagree" as easy as "approve"; measure reviewers' catch rate; rotate and limit review load.

## Bias and fairness
A support agent that misunderstands one dialect, or a triage rule tuned on one customer segment, can deliver systematically worse service to a group. ACM 1.4: "Be fair and take action not to discriminate", and "failure to design for inclusiveness and accessibility may constitute unfair discrimination". NIST's characteristic is "fair – with harmful bias managed", and it recommends disaggregating accuracy "for different data segments" – lesson 24's per-slice pass rates, with the multiple-comparison caution. The 2026 amendment to the AI Act (Regulation (EU) 2026/1744, "Digital Omnibus on AI") added Article 4a on processing special categories of personal data for bias detection and correction.

## Privacy and data protection
Agents accumulate context: transcripts, memories (lesson 9), retrieved documents (lesson 7), traces (lesson 13). ACM 1.6 asks that "only the minimum amount of personal information necessary should be collected" and that retention periods be "clearly defined, enforced, and communicated". The GDPR gives people the right "not to be subject to a decision based solely on automated processing … which produces legal effects concerning him or her or similarly significantly affects him or her" (Art. 22(1)), with safeguards including "the right to obtain human intervention" (Art. 22(3)). Lesson 21's retention job and redaction (lesson 11) are the practical side; a local model (Mac mini or Windows PC) reduces, but does not remove, data-protection duties.

## Transparency to the people affected
From 2 August 2026, providers must design AI systems that interact directly with people so that they are informed they are interacting with an AI system, unless that is obvious (AI Act Art. 50(1)). The omnibus regulation postponed most high-risk obligations (Annex III systems to 2 December 2027, Annex I systems to 2 August 2028) but left this transparency duty in place.

## When not to automate
Three primary sources converge. ACM 2.9: "In cases where misuse or harm are predictable or unavoidable, the best option may be to not implement the system." ACM 2.5: a system whose future risks "cannot be reliably predicted requires frequent reassessment … or it should not be deployed." NIST AI RMF: where risks are unacceptable, "development and deployment should cease in a safe manner". Lesson 25 gives the arithmetic (expected utility with an honest harm cost) and lesson 24 the uncertainty (a Wilson interval on the error rate). Do not automate when the harm of a wrong action is severe and irreversible, when you cannot measure the error rate with useful precision, when affected people cannot contest the outcome, or when the only "oversight" is a reviewer who will rubber-stamp.

## Common misconceptions
- **"The model vendor is responsible."** The deployer chose to put it in front of customers (Moffatt; NIST: "all parties and AI actors should manage risk in the AI systems they develop, deploy, or use").
- **"A disclaimer fixes it."** The tribunal asked why customers should have to double-check one part of a website against another.
- **"Human review = human oversight."** Only if the reviewer has the information, time, authority and incentive to disagree.
- **"Local means private."** Logs, memories and backups still hold personal data.

## Sources
ACM Code of Ethics and Professional Conduct (2018) · NIST AI 100-1, AI RMF 1.0 (2023) · Regulation (EU) 2024/1689 (AI Act), as amended by Regulation (EU) 2026/1744 · Regulation (EU) 2016/679 (GDPR) Art. 22 · Moffatt v. Air Canada, 2024 BCCRT 149 · Parasuraman & Riley (1997), Human Factors 39(2).
