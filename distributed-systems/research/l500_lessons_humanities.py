"""Lesson text for L500 #26 (ethics) and #27 (reading seminar). Assembled by research/build_l500.py."""

PLATFORMS = {"mac": "expected", "windows": "expected"}

ACM = {"title": "ACM Code of Ethics and Professional Conduct (adopted 22 June 2018)", "url": "https://www.acm.org/code-of-ethics"}
IEEE = {"title": "IEEE Code of Ethics (IEEE Policies 7.8, revisions through June 2020)", "url": "https://www.ieee.org/about/corporate/governance/p7-8.html"}
AWS = {"title": "AWS, Summary of the AWS Service Event in the Northern Virginia (US-EAST-1) Region, 10 December 2021", "url": "https://aws.amazon.com/message/12721/"}
SRE = {"title": "Google SRE book, chapter 15: Postmortem Culture: Learning from Failure", "url": "https://sre.google/sre-book/postmortem-culture/"}
GDPR = {"title": "Regulation (EU) 2016/679 (GDPR), EUR-Lex; Article 32 text as published by legislation.gov.uk", "url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng"}
GDPR32 = {"title": "GDPR Article 32 (security of processing), text of the adopted EU regulation (legislation.gov.uk)", "url": "https://www.legislation.gov.uk/eur/2016/679/article/32/adopted"}
SCHREMS = {"title": "CJEU press release 91/20, Case C-311/18 (Schrems II), 16 July 2020", "url": "https://curia.europa.eu/jcms/upload/docs/application/pdf/2020-07/cp200091en.pdf"}
IEA = {"title": "IEA (2025), Energy and AI - Energy demand from AI (CC BY 4.0)", "url": "https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai"}
EED = {"title": "Directive (EU) 2023/1791 on energy efficiency (recast), EUR-Lex - Article 12, data centres", "url": "https://eur-lex.europa.eu/eli/dir/2023/1791/oj/eng"}
LAMPORT_1978 = {"title": "Lamport (1978), Time, Clocks, and the Ordering of Events in a Distributed System, CACM 21(7) (author's PDF)",
                "url": "https://lamport.azurewebsites.net/pubs/time-clocks.pdf"}
RAFT_USENIX = {"title": "Ongaro & Ousterhout (2014), In Search of an Understandable Consensus Algorithm, USENIX ATC 14, pp. 305-319 (open access)",
               "url": "https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro"}
RAFT_EXT = {"title": "Ongaro & Ousterhout (2014), extended version (tech report, 20 May 2014)", "url": "https://raft.github.io/raft.pdf"}

ESSAY_RUBRIC = [
    {"criterion": "Stakeholders and harms", "excellent": "Identifies direct and indirect stakeholders (incl. end users of customers and people who cannot opt out) and concrete harms with evidence from the source",
     "adequate": "Main stakeholders named; harms generic", "inadequate": "Only the company and its customers; no evidence", "weight": "25%"},
    {"criterion": "Use of codes, law and standards", "excellent": "Cites specific principles/articles (e.g. ACM 1.2, 2.5, 3.7; GDPR Art. 32(1)(b)-(c)) and applies them to facts; distinguishes law from ethics",
     "adequate": "Cites correctly but applies loosely", "inadequate": "No citations, or misquotes a source", "weight": "25%"},
    {"criterion": "Trade-off analysis", "excellent": "Weighs at least two options with costs (availability, privacy, energy, money) quantified where possible; acknowledges uncertainty",
     "adequate": "Options listed; one-sided weighing", "inadequate": "No alternatives considered", "weight": "30%"},
    {"criterion": "Recommendation and professional tone", "excellent": "Clear, actionable, blameless; names owners and follow-up checks", "adequate": "Recommendation present but vague",
     "inadequate": "Blames individuals or gives no recommendation", "weight": "20%"},
]

LESSON_26 = {
    "id": "ethics-reliability-duty",
    "number": 26,
    "level": "L500",
    "title": "Ethics: reliability as a professional duty - outages, blameless post-mortems, data residency and energy",
    "category": "ethics",
    "description": "Read a real cloud outage summary as an ethical document: who was harmed, what professional codes and law require of the engineers, how a blameless post-mortem assigns learning rather than blame, how data-protection law constrains where replicas and failover may go, and what redundancy costs in energy.",
    "outcome": "You can analyse an outage or design decision with stakeholders, harms, codes (ACM 2018, IEEE), law at policy level (GDPR, data transfers, EU energy reporting) and quantified trade-offs, and write a blameless, actionable recommendation.",
    "estimatedTime": "3 hours (reading primary sources, case analysis, written answer)",
    "prerequisites": [
        "Arithmetic with percentages and rates (availability budgets, energy = power x time)",
        "Lessons 4 (retries), 19 (multi-region RTO/RPO) and 20 (chaos engineering, blast radius) for the technical facts the case relies on",
    ],
    "learningObjectives": [
        "Analyze a published outage summary to identify stakeholders, direct and indirect harms, and the technical decisions that amplified them.",
        "Evaluate a post-mortem against the blameless-postmortem criteria and explain why blame suppresses the information reliability depends on.",
        "Explain at policy level how GDPR Article 32 and the Chapter V transfer rules (as read in Schrems II) constrain replication and cross-border failover.",
        "Evaluate the energy cost of redundancy with PUE arithmetic and place it in the context of IEA projections.",
        "Critique a reliability decision using specific ACM Code and IEEE Code principles and recommend a course of action.",
    ],
    "glossary": [
        {"term": "blameless post-mortem", "meaning": "A written incident record that identifies contributing causes without indicting individuals, assuming people acted in good faith on the information they had (Google SRE ch. 15)."},
        {"term": "error budget", "meaning": "The downtime an availability target allows, e.g. 99.95% of 30 days = 21.6 minutes."},
        {"term": "data residency", "meaning": "Where personal data is stored and processed; for EU personal data, transfers outside the EEA need an adequacy decision, appropriate safeguards (e.g. standard contractual clauses) or a derogation (GDPR Chapter V)."},
        {"term": "Article 32 GDPR", "meaning": "Security of processing: appropriate measures including 'the ability to ensure the ongoing confidentiality, integrity, availability and resilience of processing systems' and to restore availability 'in a timely manner'."},
        {"term": "PUE", "meaning": "Power Usage Effectiveness: total facility energy / IT equipment energy (1.0 is the ideal)."},
        {"term": "infrastructure system", "meaning": "ACM Code 3.7: a system integrated into society's infrastructure, whose leaders have an added responsibility to be good stewards."},
    ],
    "caseStudy": {
        "case": "On 7 December 2021 an automated activity to scale one AWS service in us-east-1 triggered unexpected behaviour from many clients on AWS's internal network; the surge of connections overwhelmed the devices linking the internal and main networks, and the resulting delays caused 'even more connection attempts and retries'. Monitoring was impaired, so operators worked from logs; internal DNS was moved off the congested paths by 9:28 AM PST and the network devices fully recovered by 2:22 PM PST. AWS reports that its clients' well-tested back-off behaviour failed because of a latent issue, that the Service Health Dashboard could not fail over to its standby region (updates resumed at 8:22 AM, via a global banner some customers found hard to read), that support-case creation was impaired from 7:33 AM to 2:25 PM, and that Amazon Connect had elevated failures for phone calls and chats. Extension for analysis: you lead platform engineering for an EU telehealth booking service hosted only in that region. After the event the board asks you to add automatic failover to a second region within a week, and the cheapest region with capacity is outside the EEA.",
        "stakeholders": [
            "Patients booking or attending appointments (cannot choose the hosting region; some cannot wait)",
            "Clinics and call-centre staff whose phone and chat tools (e.g. contact-centre services) failed",
            "Your on-call engineers and the provider's operators (working with impaired monitoring)",
            "Customer engineering teams trying to understand impact without dashboards",
            "Data subjects whose health data would be replicated abroad; the supervisory authority",
            "The cloud provider and its other tenants (shared fate of one region's control plane)",
            "People affected by the energy use of a permanently running standby region",
        ],
        "frameworks": [
            "ACM Code 1.2 Avoid harm - including the obligation to report signs of system risk; 2.5 comprehensive evaluation including analysis of possible risks; 3.7 special care for systems integrated into society's infrastructure; 1.6 Respect privacy; 1.1 promote environmental sustainability; 1.3 transparency about limitations and potential problems",
            "IEEE Code of Ethics item 1 (safety, health and welfare of the public; sustainable development; privacy; disclose factors that might endanger the public or the environment) and item 5 (acknowledge and correct errors)",
            "Google SRE ch. 15: post-mortem triggers and blameless culture ('You can't fix people, but you can fix systems and processes')",
            "GDPR Art. 32(1)(b)-(c): availability, resilience and timely restoration are security obligations; Chapter V transfers as summarised by the CJEU in C-311/18 (adequacy decision, or appropriate safeguards such as standard data protection clauses plus enforceable rights and effective legal remedies)",
            "Energy: IEA (2025) projects data-centre electricity use to about 945 TWh by 2030 (just under 3% of global demand); Directive (EU) 2023/1791 Art. 12 requires EU data centres above a power threshold to report energy performance",
        ],
        "questions": [
            "Who was harmed by the 2021 event, directly and indirectly, and which harms were amplified by design decisions (retries without effective back-off, status tooling in the affected region, support tooling on the internal network)?",
            "Rewrite one finger-pointing sentence about the event into a blameless one, and list three action items with owners.",
            "Your board wants cross-region failover in a week. Which ACM principles apply, and what would 'comprehensive evaluation of risks' require before you ship it?",
            "At policy level, what must be true before EU health data is replicated to a non-EEA region? What design alternatives avoid the transfer?",
            "Estimate the energy cost of a hot standby versus a warm standby, and argue whether the extra availability is proportionate for a booking service.",
            "When, under ACM 1.2 and IEEE 1, would an engineer be obliged to escalate a known reliability risk beyond their manager?",
        ],
        "modelAnswer": (
            "**Harms and stakeholders.** Direct: customers who could not launch instances, change DNS records, log in to the console, or receive events, and their end users; contact-centre calls and chats failed, which for a clinic means patients who cannot book or reschedule. Indirect: engineers on both sides worked blind (CloudWatch delays, impaired monitoring), so recovery was slower and customers could not assess their own impact. Three amplifiers are design decisions, not individual mistakes: clients whose back-off had a latent defect (the retry storm mechanism of L100 #4 and L300 #16), a status page whose failover depended on the failing region, and support tooling on the internal network. ACM 3.7 applies with force: a region's control plane is infrastructure for thousands of organisations.\n\n"
            "**Blameless rewrite.** Not 'the scaling team broke the network' but 'an automated scaling activity triggered a client behaviour that had not been observed in production; the clients' back-off did not engage because of a latent issue'. Actions: disable the trigger until fixed (owner: scaling service); add a back-off conformance test to the client library and a chaos experiment with a bounded blast radius (owner: networking clients, L400 #20 method); move status and support tooling to an independent region and test failover quarterly (owner: support engineering). Google SRE's triggers (user-visible downtime, monitoring failure) both apply, so a post-mortem is mandatory, and it must be reviewed and shared.\n\n"
            "**One-week failover.** ACM 2.5 asks for a comprehensive risk evaluation; 1.3 asks for honesty about limitations. A failover built in a week is itself a risk: untested failover is a classic cause of outages, and asynchronous replication loses acknowledged writes (lab 19 measured 16 lost writes with async, 0 with majority-sync). An ethical answer is a staged plan: measure RTO/RPO in a game day first, communicate what is and is not protected, and treat the deadline as negotiable when public harm is at stake (ACM 2.1: professionals 'should resist inducements to neglect' their responsibility for quality; ACM 2.3: rules that cause recognizable harm should be challenged).\n\n"
            "**Data residency (policy level, not legal advice).** Health data is personal data, and GDPR Art. 32(1)(b)-(c) makes availability and timely restoration part of security, so failover is not optional ethics - it is a legal expectation, proportionate to risk. But copying it outside the EEA is a transfer under Chapter V: it needs an adequacy decision for that country, or appropriate safeguards such as standard contractual clauses together with enforceable rights and effective legal remedies for data subjects (CJEU press release 91/20). In Schrems II the Court invalidated the EU-US Privacy Shield adequacy decision while holding the standard-contractual-clauses decision valid - so the legal basis for a transfer can disappear, and a DR plan that depends on one is a business-continuity risk in itself. Alternatives: a second EEA region, encryption with keys held in the EU (reduces but does not remove the question), or failing over only non-personal functions (a static 'call this number' page).\n\n"
            "**Energy.** At 40 kW of IT load and PUE 1.4 the primary uses about 490.6 MWh a year; a hot standby roughly doubles that, a warm standby (replicas only, compute scaled down) costs a fraction. IEA projects data-centre demand near 945 TWh by 2030; each design adds a little, and ACM 1.1 asks professionals to promote environmental sustainability. Proportionality: a booking service with a phone fallback may justify warm standby in a second EEA region, not a permanently hot global one.\n\n"
            "**Escalation.** If a known risk could cause significant, unjust harm (patients missing care) and leaders do not act, ACM 1.2 says it 'may be necessary to blow the whistle', after carefully assessing the situation; IEEE 1 requires prompt disclosure of factors that might endanger the public. Escalate first through internal channels with evidence (the measured RPO, the transfer analysis)."
        ),
    },
    "problemSet": [
        {"id": "26-P1", "type": "calculation", "difficulty": 1, "marks": 3,
         "problem": "A booking service promises 99.95% availability per 30-day month. How much downtime does that allow?",
         "answer": "21.6 minutes",
         "solution": "(1 - 0.9995) x 30 x 24 x 60 = 0.0005 x 43,200 = 21.6 minutes. One unplanned failover that takes half an hour breaks the promise."},
        {"id": "26-P2", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "In AWS's 2021 summary, the event began at 7:30 AM PST and the network devices fully recovered at 2:22 PM PST. How long is that, and how does it compare with the yearly downtime budget of a 99.99% (365-day) target?",
         "answer": "412 minutes, 7.8 times the 52.6-minute annual budget",
         "solution": "14:22 - 07:30 = 6 h 52 min = 412 minutes. Budget: (1 - 0.9999) x 365 x 24 x 60 = 52.56 minutes. Answer: 412 minutes, 7.8 times the 52.6-minute annual budget. Several services recovered later (STS at 4:28 PM, EventBridge backlog until 6:40 PM), so the user-visible impact for some customers was longer."},
        {"id": "26-P3", "type": "short-answer", "difficulty": 2, "marks": 6,
         "problem": "Give two reasons from the Google SRE chapter why post-mortems must be blameless, and one way blamelessness is compatible with accountability.",
         "solution": "(1) If people are punished, they stop bringing issues to light, so incidents and risks are 'swept under the rug' and the organisation loses the information it needs. (2) Blame fixes nothing: 'You can't fix people, but you can fix systems and processes'; investigating why someone had incomplete or incorrect information leads to effective prevention. Accountability survives as ownership of action items, mandatory review ('no postmortem left unreviewed'), and sharing results widely - accountability for learning, not for having been on call."},
        {"id": "26-P4", "type": "essay", "difficulty": 3, "marks": 15,
         "problem": "Write a 500-700 word recommendation to your CTO on whether to replicate EU customers' personal data to a non-EEA region for disaster recovery. Cite at least two ACM Code principles and GDPR Articles 32 and 44-46 at policy level; quantify at least one trade-off.",
         "solution": "Model outline: (1) Goal and facts: RTO/RPO targets, data categories (health data is special-category), current single-region risk. (2) Duty to be available: GDPR Art. 32(1)(b)-(c) - availability, resilience and timely restoration are security measures; ACM 2.9 and 3.7. (3) Duty of care for data: Chapter V - transfer only with an adequacy decision, appropriate safeguards (SCCs) that provide effective protection (Schrems II), or a derogation; ACM 1.6 (minimum data, protection from unauthorised access). (4) Options with numbers: second EEA region (higher cost, no transfer); non-EEA warm standby with EU-held keys (cheaper, transfer analysis + legal review needed); degrade gracefully (static contact page, no personal data). Quantify: a 99.95% target allows 21.6 min/month - which option meets it in a regional outage, and what each costs in money and MWh. (5) Recommendation, owners, and review date; note this is not legal advice and requires the DPO. Graded with the lesson rubric."},
        {"id": "26-P5", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "A service draws 40 kW of IT power around the clock in a facility with PUE 1.4. Estimate annual facility energy, and the total if a fully active standby of the same size runs in a second facility with the same PUE.",
         "answer": "490.6 MWh per year; 981.1 MWh with a fully active standby",
         "solution": "40 kW x 1.4 x 8,760 h = 490,560 kWh = 490.6 MWh. A same-size hot standby doubles it. Answer: 490.6 MWh per year; 981.1 MWh with a fully active standby. A warm standby that only runs replicas might add a fraction of that - measure it rather than assume."},
        {"id": "26-P6", "type": "short-answer", "difficulty": 2, "marks": 6,
         "problem": "AWS's summary says its clients' back-off 'designed to allow our systems to recover' did not work because of a latent issue. Explain, using lessons 4 and 16, why retry behaviour is an ethical as well as a technical concern, and propose a test that would have exposed the issue.",
         "solution": "Retries without effective back-off multiply load exactly when a dependency is weakest (lab 4: retries at every layer multiply; lab 16: unbounded queues turn overload into long outages), so one component's latent defect becomes a shared-fate outage for thousands of organisations - ACM 1.2 (avoid harm, consider emergent properties of systems) and 3.7 (infrastructure stewardship). A test: a fault-injection experiment in a staging cell that makes the network device drop or delay a growing fraction of connections and asserts that aggregate client connection rate falls (back-off engages) within N seconds; run it as a release gate and a periodic bounded chaos experiment (L400 #20)."},
    ],
    "rubric": ESSAY_RUBRIC,
    "conceptNote": "content/concepts/L500/26-ethics-reliability.md",
    "conceptSummary": "Reliability is an ethical duty because infrastructure failures harm people who never chose the vendor: ACM 1.2, 2.5 and 3.7 and IEEE 1 make risk evaluation, disclosure and stewardship obligations. Blameless post-mortems turn incidents into system fixes. GDPR makes availability part of security (Art. 32) but limits where replicas may go (Chapter V, Schrems II). Redundancy costs energy (PUE arithmetic; IEA projects ~945 TWh for data centres by 2030), so proportionality is part of the judgement.",
    "sources": [ACM, IEEE, AWS, SRE, GDPR32, SCHREMS, IEA],
    "seeAlso": [
        "distributed-systems L100 #4 Retries with exponential backoff, jitter and a retry budget: the mechanism whose failure amplified the 2021 event",
        "distributed-systems L400 #19 Multi-region design: latency budget, leader placement, follower reads, failover RTO/RPO: the RPO you promise determines who loses data in a failover",
        "distributed-systems L400 #20 Chaos engineering: hypotheses, steady state, blast radius and seeded fault campaigns: bounded experiments as an ethical practice (blast radius = who you are allowed to hurt)",
        "distributed-systems L300 #16 Backpressure and load shedding: bounded queues, 503 + Retry-After, AIMD concurrency limits: graceful degradation instead of collapse",
    ],
    "next": "L500 #27 Reading seminar: Lamport (1978) and Ongaro & Ousterhout (2014) - read the primary sources behind lessons 6, 12, 23 and 24",
    "platforms": PLATFORMS,
    "validation": {
        "status": "validated-local",
        "how": "No lab code. Every quoted fact was checked against the fetched primary source (AWS summary, ACM Code, IEEE Code, Google SRE ch. 15, GDPR Art. 32 text, CJEU press release 91/20, IEA Energy and AI); calculation answers recomputed by research/l500_checks.py.",
        "pendingCi": ["Directive (EU) 2023/1791 Art. 12 wording was not displayed in the fetched EUR-Lex excerpt (see KNOWN-GAPS)"],
    },
}

READING_RUBRIC = [
    {"criterion": "Accurate summary", "excellent": "States the paper's problem, model, main result and argument in own words; no factual errors; page/section references",
     "adequate": "Main result right; argument summarised loosely", "inadequate": "Misstates the result or copies text", "weight": "30%"},
    {"criterion": "Critical engagement", "excellent": "Identifies an assumption and tests it against a lab result or later work; distinguishes what the paper proves from what it claims",
     "adequate": "Some critique, not tied to evidence", "inadequate": "Summary only", "weight": "35%"},
    {"criterion": "Connection to the course", "excellent": "Links precisely to lessons (e.g. 6, 12, 23, 24) and explains what the paper explains about a measured behaviour",
     "adequate": "Generic link", "inadequate": "No link", "weight": "20%"},
    {"criterion": "Writing and citation", "excellent": "Clear structure, 800-1,000 words, quotations short and attributed (licence respected)", "adequate": "Minor issues",
     "inadequate": "Over length, unattributed quotes or long verbatim passages", "weight": "15%"},
]

LESSON_27 = {
    "id": "reading-seminar-lamport-raft",
    "number": 27,
    "level": "L500",
    "title": "Reading seminar: Lamport (1978) and Ongaro & Ousterhout (2014)",
    "category": "reading seminar",
    "description": "Read two foundational primary papers - Lamport's happened-before and logical clocks, and the Raft paper - with guiding questions, connect each claim to a lab you ran, and write a critical response.",
    "outcome": "You can read a systems paper for its model, claims and proof structure, explain both papers' main arguments in your own words, and critique them with evidence from your own measurements.",
    "estimatedTime": "4-5 hours (two papers, seminar discussion, written response)",
    "prerequisites": [
        "Lessons 23 and 24 (the theory both papers rely on)",
        "Lessons 6 (Lamport clocks) and 12 (Raft) - the labs that implement the papers",
    ],
    "learningObjectives": [
        "Explain Lamport's definition of happened-before, the clock condition, and the 'anomalous behaviour' that motivates physical clocks.",
        "Explain Raft's decomposition (election, replication, safety) and reconstruct the Leader Completeness argument.",
        "Analyze each paper's system model and identify which assumption a lab violated when it failed.",
        "Critique a paper's claims (e.g. 'understandable') against the evidence the paper offers.",
    ],
    "glossary": [
        {"term": "strong clock condition", "meaning": "Lamport: ordering must also respect causality through channels outside the system (e.g. a phone call); logical clocks alone cannot guarantee it."},
        {"term": "state machine approach", "meaning": "Lamport 1978: every process executes the same commands in the same (timestamp) order; the basis of replicated state machines."},
        {"term": "Leader Completeness", "meaning": "Raft: an entry committed in a term is present in the logs of all leaders of higher terms."},
        {"term": "election restriction", "meaning": "Raft §5.4.1: a voter denies its vote to a candidate whose log is less up-to-date (last term, then length)."},
        {"term": "joint consensus", "meaning": "Raft's membership change: majorities of the old and new configurations must overlap during the transition."},
    ],
    "readings": [
        {
            "citation": "Leslie Lamport. Time, Clocks, and the Ordering of Events in a Distributed System. Communications of the ACM 21(7):558-565, July 1978.",
            "url": "https://lamport.azurewebsites.net/pubs/time-clocks.pdf",
            "why": "Defines happened-before as a partial order built only from events observable in the system, proves that simple counter rules (IR1, IR2) satisfy the clock condition, shows how a total order solves mutual exclusion without a central scheduler - the seed of the state machine approach - and explains why logical order can still disagree with what users perceive. Lab 6 implements its rules; T23.1 is its proof. Licence: (c) 1978 ACM; the paper grants fair use in teaching and research with the copyright notice - read it at the URL; this course summarises, it does not reproduce it.",
            "guidingQuestions": [
                "Why does Lamport define 'happened before' without physical clocks, and why must specifications be stated in terms of events observable within the system?",
                "State the Clock Condition and the two conditions C1 and C2 that imply it. Which implementation rule secures each?",
                "In the mutual exclusion algorithm, why is a central scheduler that grants requests in arrival order wrong? Reconstruct the three-process counterexample.",
                "What is 'anomalous behaviour' and why can no algorithm that only uses events inside the system prevent it? How does the Strong Clock Condition fix it?",
                "Lamport notes that the state machine approach halts if a single process fails, and that failure is only meaningful with physical time. Connect this to FLP (T24.2) and to lab 12.",
            ],
            "responsePrompt": "In 800-1,000 words, explain how Lamport's total order turns a distributed synchronisation problem into a state machine replicated on every process, then critique the approach's failure model using one measurement from lab 6 or lab 12 and one later result (FLP or Raft).",
        },
        {
            "citation": "Diego Ongaro and John Ousterhout. In Search of an Understandable Consensus Algorithm. 2014 USENIX Annual Technical Conference (USENIX ATC 14), pp. 305-319, Philadelphia, June 2014 (Best Paper). Extended version: raft.github.io/raft.pdf, 20 May 2014.",
            "url": "https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro",
            "why": "Presents Raft, designed for understandability by decomposition (leader election, log replication, safety) and state-space reduction, with a safety argument for Leader Completeness, a timing requirement for availability, and a user study (43 students; 33 answered Raft questions better than Paxos questions). Lab 12 implements a simplified Raft and shows what the election restriction protects; T24.4 compares it with Paxos. Licence: USENIX open access - read the paper at the URL or the extended version at raft.github.io; this course summarises only.",
            "guidingQuestions": [
                "What two reasons do the authors give for replacing Paxos, and which of them is an empirical claim? What evidence do they give?",
                "List the five properties in Figure 3 and say which mechanism maintains each one.",
                "Reconstruct the Leader Completeness proof by contradiction (§5.4.3): where does it use majority intersection, and where does it use the election restriction?",
                "Explain Figure 8: why may a leader not commit an entry from an earlier term by counting replicas, and how does committing a current-term entry fix it?",
                "State the timing requirement broadcastTime << electionTimeout << MTBF. Why does safety not depend on it, and what fails when it is violated?",
            ],
            "responsePrompt": "In 800-1,000 words, evaluate the claim that Raft is 'more understandable than Paxos'. Summarise the evidence the paper offers, compare Raft's election restriction with Paxos's phase-1 value adoption (T24.4), and use lab 12's failure (stale follower elected, committed entries lost) to argue what a reader must understand to implement Raft safely.",
        },
    ],
    "problemSet": [
        {"id": "27-P1", "type": "calculation", "difficulty": 1, "marks": 3,
         "problem": "In Lamport's mutual exclusion algorithm with N processes, how many messages does one request-use-release cycle send at most (request to every other process, acknowledgements, release to every other process)? Compute for N = 5.",
         "answer": "12 messages",
         "solution": "Rule 1 sends N - 1 requests, rule 2 returns up to N - 1 acknowledgements (footnote: an acknowledgement is unnecessary if a later-stamped message was already sent), rule 3 sends N - 1 releases: at most 3(N - 1). For N = 5: 12 messages."},
        {"id": "27-P2", "type": "short-answer", "difficulty": 2, "marks": 5,
         "problem": "Explain Lamport's 'anomalous behaviour' example (a request, then a phone call, then a second request) and the two remedies the paper proposes.",
         "solution": "A person issues request A on computer A, telephones a friend who then issues request B on computer B; B may get a lower timestamp than A because the phone call is outside the system, so the system cannot know A preceded B. Remedies: (1) put the ordering information into the system - the friend asks for a timestamp later than A's; (2) use physical clocks synchronised tightly enough to satisfy the Strong Clock Condition (Lamport derives epsilon/(1 - kappa) <= mu)."},
        {"id": "27-P3", "type": "short-answer", "difficulty": 2, "marks": 6,
         "problem": "Using Raft's Figure 8, explain why an entry stored on a majority can still be overwritten, and what rule prevents it.",
         "solution": "S1 (term 2) replicates entry 2 to S2 and crashes; S5 wins term 3 with votes from S3, S4 and itself and writes a different entry at index 2; S1 returns in term 4 and replicates its term-2 entry to a majority - but it is not committed: if S1 crashes, S5 can win again (its last term 3 is more up-to-date than S2/S3's last term 2) and overwrite it. Rule (§5.4.2): a leader only commits entries from its current term by counting replicas; earlier entries become committed indirectly via Log Matching once a current-term entry commits."},
        {"id": "27-P4", "type": "calculation", "difficulty": 2, "marks": 4,
         "problem": "Lamport's theorem bounds clock skew by approximately epsilon = d(2 kappa tau + xi). Evaluate it for a network of diameter d = 3, drift kappa = 1e-6, a message on every link every tau = 1 s, and unpredictable delay xi = 1 ms.",
         "answer": "3.006 ms",
         "solution": "epsilon = 3 x (2 x 1e-6 x 1 s + 0.001 s) = 3 x 0.001002 s = 0.003006 s = 3.006 ms. The unpredictable delay dominates; the drift term is 0.006 ms."},
        {"id": "27-P5", "type": "calculation", "difficulty": 1, "marks": 3,
         "problem": "The Raft paper says a typical cluster has five servers. What majority does it need and how many failures does it tolerate?",
         "answer": "majority 3, tolerates 2 failed servers",
         "solution": "Majority = floor(5/2) + 1 = 3; 5 - 3 = 2 servers may fail. Answer: majority 3, tolerates 2 failed servers (the paper: 'a typical cluster of five servers can tolerate the failure of any two servers')."},
        {"id": "27-P6", "type": "essay", "difficulty": 3, "marks": 15,
         "problem": "Critical response (choose one reading's responsePrompt). 800-1,000 words.",
         "solution": "Graded with the lesson rubric. A strong response: summarises the model and main result accurately with section references; picks one assumption (e.g. Lamport's reliable FIFO channels, or Raft's crash-recovery with stable storage) and shows with a lab measurement what breaks without it (lab 12: 'safety violations: 3' when the election restriction is removed); distinguishes proven properties (Raft's safety, formally specified and proven per the paper) from empirical claims (understandability, from a 43-student study); quotes at most a sentence or two, attributed."},
    ],
    "rubric": READING_RUBRIC,
    "conceptNote": "content/concepts/L500/27-reading-seminar.md",
    "conceptSummary": "Lamport (1978) defines causality from observable events, proves that two counter rules give a consistent total order, and uses it to replicate a state machine - while warning that logical order can disagree with what users see and that failures need physical time. Ongaro & Ousterhout (2014) design Raft for understandability, prove Leader Completeness from majority overlap plus the election restriction, and separate safety from timing. Read for model, claim, argument and evidence; then test each against a lab.",
    "sources": [LAMPORT_1978, RAFT_USENIX, RAFT_EXT],
    "seeAlso": [
        "distributed-systems L100 #6 Ordering events with Lamport clocks: Lamport's IR1/IR2 in running code",
        "distributed-systems L300 #12 Replicated log with Raft (simplified): terms, commit index, re-election, election restriction: the Raft mechanisms the paper argues are needed, and what breaks without one",
        "distributed-systems L400 #21 Verifying correctness: model checking and linearizability checking: the kind of formal check the Raft authors cite for their safety proof",
    ],
    "next": "Done: the course assessment pack (content/assessment/) - syllabus, midterm, final, concept inventory, capstone oral defence and ADR peer review",
    "platforms": PLATFORMS,
    "validation": {
        "status": "validated-local",
        "how": "Both papers fetched and read on 2026-10-30 (author PDF; USENIX page and extended tech report); every claim in the questions and solutions was checked against the fetched text; calculation answers recomputed by research/l500_checks.py.",
        "pendingCi": [],
    },
}
