"""L500 lesson 26 data: ethics, society and professional responsibility. Built into content/L500.json by build_l500_json.py."""

LESSON = {
    "id": "ethics-quantum-responsibility",
    "number": 26,
    "level": "L500",
    "title": "Ethics 26: honest claims, the duty to migrate, export controls and access",
    "phase": "Theory & Rigour",
    "category": "ethics",
    "description": "Responsible speed-up claims, harvest-now-decrypt-later and the professional duty to migrate to post-quantum "
                   "cryptography, export controls and dual use at policy level, and who gets access to quantum computing - "
                   "analysed with the ACM and IEEE codes, NIST, NCSC, US and EU primary sources.",
    "outcome": "You can audit a quantum claim against its evidence, justify a migration priority with Mosca's inequality and "
               "official timelines, explain at policy level what export controls cover and exclude (and when to ask a compliance "
               "officer), and evaluate access and equity trade-offs in a structured case analysis.",
    "estimatedTime": "4-5 hours (reading 2 h, case analysis 2-3 h)",
    "prerequisites": [
        "lesson 25 (what Shor and Grover can and cannot do; T25.1, T25.4)",
        "L400 #21 (crypto inventory, Mosca priorities, hybrid ML-KEM) and L400 #18 (fair benchmarking)",
        "no legal background needed; the lesson stays at policy level and is not legal advice",
    ],
    "learningObjectives": [
        "Critique a published quantum-advantage claim by separating the measured result, the classical baseline and later classical rebuttals, citing ACM 1.3/2.5 and IEEE 7.8 item 5.",
        "Analyze harvest-now-decrypt-later risk with Mosca's inequality (X + Y > Z) and justify migration priorities against NIST IR 8547 and NCSC timelines.",
        "Explain the policy logic and scope of quantum export controls (US EAR 900-series ECCNs, EU Regulation 2021/821 as amended) and the exclusions for public-domain information and basic research.",
        "Evaluate access and equity trade-offs (cost, cloud gatekeeping, talent and nationality rules) using ACM 1.4 and 3.7 and UN resolution A/RES/78/287.",
    ],
    "glossary": [
        {"term": "harvest now, decrypt later (HNDL)", "meaning": "Recording encrypted traffic today to decrypt it once a cryptographically relevant quantum computer exists."},
        {"term": "CRQC", "meaning": "Cryptographically relevant quantum computer: one able to run Shor's algorithm on deployed key sizes."},
        {"term": "Mosca's inequality", "meaning": "If X (how long data must stay secret) + Y (time to migrate) > Z (time until a CRQC), the data is already at risk."},
        {"term": "quantum advantage / supremacy claim", "meaning": "A claim that a quantum device did a task faster than any feasible classical method; always relative to a classical baseline."},
        {"term": "dual use", "meaning": "Technology with both civilian and military/security applications (EU Reg. 2021/821 definition)."},
        {"term": "ECCN", "meaning": "Export Control Classification Number on the US Commerce Control List (e.g. 4A906 for certain quantum computers)."},
        {"term": "deemed export", "meaning": "Releasing controlled technology to a foreign person inside the exporting country (US EAR concept)."},
        {"term": "public domain / basic scientific research", "meaning": "Information excluded from EU technology controls by the General Technology Note."},
    ],
    "caseStudy": {
        "case": "QuantaNova, a start-up, issues a press release: 'Our 120-qubit processor achieved quantum advantage on a sampling benchmark "
                "and will break RSA-2048 by 2029. Encryption as we know it is obsolete.' The release cites an unrefereed preprint; the "
                "benchmark compares against a single-CPU brute-force simulator. Three readers act on it. (1) The CISO of a regional hospital "
                "group, whose patient records must stay confidential for 25 years, is asked by the board whether to divert the 2027 IT budget "
                "to an emergency 'quantum-proofing' contract offered by a QuantaNova partner. (2) A university lab, which includes graduate "
                "students of several nationalities, plans to publish an open-source error-correction decoder and to tune it on a collaborator's "
                "cryogenic quantum processor abroad. (3) A national science agency is deciding whether to fund cloud access to quantum hardware "
                "for universities that cannot afford it. You are asked, as the computing professional advising all three, to write a structured analysis.",
        "stakeholders": [
            "QuantaNova staff and investors (reputation, funding, legal exposure for misleading statements)",
            "the hospital group's patients (long-lived confidentiality of health data) and its board and CISO",
            "the hospital's suppliers (TLS, VPN, PKI and medical-device vendors who must deliver PQC)",
            "the university lab, its international students and its overseas collaborator",
            "export-control authorities (US BIS, EU member-state authorities) and university compliance officers",
            "under-resourced universities and their students; the public who fund the agency",
            "the wider computing profession, whose credibility suffers from hype",
        ],
        "questions": [
            "Which statements in the press release are evidence, which are extrapolations, and which are unsupported? What would a fair benchmark have reported (L400 #18)?",
            "Using Mosca's inequality, NIST IR 8547 and the NCSC timeline, what should the CISO recommend, and why is 'emergency' the wrong framing even though the risk is real?",
            "What must the lab check before shipping code or tuning on foreign hardware, which exclusions might apply to publishing the decoder, and when must it involve the compliance office?",
            "How should the agency weigh broad access against concentration of resources, and how do nationality-based rules interact with ACM 1.4?",
            "Which ACM and IEEE principles apply to each actor, where do they conflict, and how do you resolve the conflict?",
        ],
        "frameworks": [
            "ACM Code of Ethics and Professional Conduct (2018): 1.2 Avoid harm; 1.3 Be honest and trustworthy; 1.4 Be fair and take action not to discriminate; 2.3 Know and respect existing rules; 2.5 Give comprehensive and thorough evaluations ... including analysis of possible risks; 2.7 Foster public awareness ...; 3.7 Recognize and take special care of systems that become integrated into the infrastructure of society",
            "IEEE Code of Ethics (IEEE Policies 7.8): item 2 (improve understanding of capabilities and societal implications of emerging technologies) and item 5 ('be honest and realistic in stating claims or estimates based on available data')",
            "NIST IR 8547 (final, October 2026): quantum-vulnerable public-key algorithms deprecated after 2030 and disallowed after 2035; HNDL; Mosca's X + Y > Z",
            "NIST FIPS 203 (ML-KEM, August 2024): the standardised replacement for key establishment",
            "UK NCSC, Timelines for migration to post-quantum cryptography (March 2025): discovery and plan by 2028, priority migration by 2031, complete by 2035",
            "US BIS interim final rule, 89 FR 72926 (6 September 2024): new 900-series ECCNs for quantum items (incl. 4A906, 4D906, 4E906, 3A901, 3A904), worldwide licence requirement, License Exception IEC, General License for quantum deemed exports with annual reporting",
            "EU Regulation (EU) 2021/821 (dual-use regime) and Commission Delegated Regulation (EU) 2025/2003 (new Annex I, in force from the day after publication on 14 November 2025); General Technology Note exclusions for 'in the public domain' and 'basic scientific research'",
            "UN General Assembly resolution A/RES/78/287 (7 June 2024): 2025 International Year of Quantum Science and Technology, with emphasis on developing countries",
            "Quantum (journal) Code of Conduct: misconduct includes 'misrepresentation and overstatement of results and the omission of crucial conditions and assumptions'",
        ],
        "modelAnswer": "1. Claims audit (ACM 1.3, 2.5, 2.7; IEEE item 5). Separate three layers. Measured: a sampling task ran on 120 qubits. Baseline: a "
                       "single-CPU brute-force simulator, which is not the best classical method; the 2019 Sycamore episode shows why this matters "
                       "(Google estimated 10,000 years classically; IBM's analysis argued days on a supercomputer with secondary storage; a 2022 "
                       "tensor-network computation sampled the circuits in about 15 hours on 512 GPUs). Extrapolation: 'break RSA-2048 by 2029' is "
                       "not supported by a sampling result; RSA needs Shor's algorithm with error correction, and published estimates for RSA-2048 "
                       "run to roughly a million noisy qubits (L400 #19). Verdict: the advantage claim is unproven until benchmarked against the best "
                       "classical method on equal budgets, and the RSA claim is hype that violates the honesty duties of both codes. A professional "
                       "response is to say so publicly and specifically (ACM 2.7), not to amplify it.\n"
                       "2. Hospital (ACM 1.2, 3.7; NIST IR 8547; NCSC). The risk is real for a reason unrelated to QuantaNova: with X = 25 years of "
                       "required confidentiality and Y of several years to migrate, X + Y exceeds any plausible Z, so HNDL already threatens records "
                       "sent today. The right response is a planned migration, not an emergency purchase: complete the cryptographic inventory and "
                       "plan (NCSC: by 2028), prioritise long-lived data flows for hybrid ML-KEM key establishment (FIPS 203) via mainstream vendors, "
                       "require PQC roadmaps in procurement, and meet the 2030/2035 NIST deprecation/disallowance dates. Buying from a vendor tied to "
                       "the hype raises a conflict of interest to disclose (ACM 1.3). The duty to migrate is a duty of care to patients who cannot "
                       "protect their own data.\n"
                       "3. University lab (ACM 2.3; BIS rule; EU 2021/821). Export controls target hardware and 'technology' for development or "
                       "production of controlled items (e.g. US ECCNs 4A906/4E906; EU entries added by Reg. 2025/2003), not teaching or published "
                       "science: the EU General Technology Note excludes information 'in the public domain' and 'basic scientific research'. "
                       "Publishing an open decoder is likely outside control, but the classification depends on facts (does the code embody "
                       "controlled production technology? is it published before sharing?). Tuning on foreign hardware and sharing unpublished "
                       "know-how with particular nationals can be an export or deemed export; the US rule created a General License for quantum "
                       "deemed exports with annual reporting, precisely because, in BIS's words, access to foreign expertise is particularly "
                       "necessary in quantum computing. Action: involve the compliance office before sharing; do not exclude students by "
                       "nationality pre-emptively (ACM 1.4), but do not ignore the law either (ACM 2.3: challenge rules through channels).\n"
                       "4. Agency (ACM 1.4, 3.7; A/RES/78/287). Shared cloud access lowers the cost barrier, but creates gatekeepers who set terms, "
                       "queue priority and data retention. Fund access with open-source toolchains and simulators (this course runs entirely on "
                       "them), training for under-resourced institutions, and transparent allocation; measure who uses it. The UN resolution "
                       "explicitly links quantum science to capacity-building in developing countries.\n"
                       "5. Conflicts and resolution. Honesty vs commercial pressure (resolve for honesty: 1.3 is not negotiable); openness vs export "
                       "law (comply, but use exclusions and challenge over-broad rules through channels, 2.3); urgency vs proportionality (plan to "
                       "the official timelines; spend where data lifetime is longest). The public good is the deciding consideration (ACM 3.1).",
    },
    "problemSet": [
        {"id": "qc-L500-26-P1", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "Mosca's inequality. Records must stay confidential for X = 10 years; migration will take Y = 6 years; assume a CRQC in Z = 12 years. Is the data at risk, and by how many years? What if migration is shortened to 2 years?",
         "solution": "X + Y = 16 > Z = 12, so data encrypted today is exposed for 16 - 12 = 4 years of its required secrecy period. With Y = 2: X + Y = 12, not greater than Z, so the margin is 0 years (borderline). The lesson: shortening Y (inventory, crypto agility) is the lever an organisation controls."},
        {"id": "qc-L500-26-P2", "type": "calculation", "difficulty": 2, "marks": 4,
         "problem": "A record captured in 2026 must stay secret for 25 years. If a CRQC appears in 2040, for how many years of its required secrecy period is the record exposed? Which NIST IR 8547 dates bracket the migration?",
         "solution": "Secrecy required until 2026 + 25 = 2051; exposure from 2040, i.e. 2051 - 2040 = 11 years. NIST IR 8547 deprecates quantum-vulnerable public-key algorithms after 2030 and disallows them after 2035; HNDL means the data at risk is what is sent before migration, whatever the CRQC date."},
        {"id": "qc-L500-26-P3", "type": "short-answer", "difficulty": 2, "marks": 5,
         "problem": "List three specific problems with the QuantaNova press release and rewrite its headline sentence so that it meets IEEE 7.8 item 5.",
         "solution": "Problems: (i) baseline is a weak classical method, not the best known; (ii) a sampling benchmark is extrapolated to factoring, a different task needing error correction; (iii) unrefereed evidence and no uncertainty stated; also 'encryption is obsolete' ignores symmetric crypto and standardised PQC (FIPS 203). Rewrite: 'On a random-circuit sampling benchmark, our 120-qubit processor ran faster than the classical simulator we tested; we have not yet compared against the best classical methods, and the result does not bear on breaking RSA.'"},
        {"id": "qc-L500-26-P4", "type": "essay", "difficulty": 3, "marks": 10,
         "problem": "Essay (600-800 words): 'Export controls on quantum computing protect security but slow science.' Evaluate using the BIS rule's own discussion of foreign talent, the EU General Technology Note exclusions and ACM 1.4 / 2.3.",
         "solution": "Model answer outline: the controls target items with clear security relevance (quantum computers above parameters, cryogenic systems, cryo-CMOS, related technology) and were coordinated with partners (BIS: multilateral controls are most effective). The costs are explicit in the primary source: BIS states that access to foreign expertise is particularly necessary in quantum computing, that more than half of QIST-related US degrees go to temporary residents, and it therefore created a General License for quantum deemed exports with reporting. Exclusions (public domain, basic scientific research in the EU GTN) protect open publication. Tensions: nationality-based rules vs ACM 1.4 non-discrimination; resolution via ACM 2.3 (comply, challenge through channels) and institutional compliance processes rather than individual exclusion. A good essay distinguishes hardware/production technology from teaching and published science, and avoids legal conclusions it cannot support."},
        {"id": "qc-L500-26-P5", "type": "short-answer", "difficulty": 2, "marks": 5,
         "problem": "Name two access barriers to quantum computing education or research and one policy that reduces each. Tie each to a principle (ACM 1.4 or 3.7) or to A/RES/78/287.",
         "solution": "(1) Cost of hardware access / cloud quotas -> funded shared access with transparent allocation (ACM 3.7: fair access to infrastructure). (2) Proprietary toolchains and accounts -> open-source simulators and SDKs as the default teaching stack, as this course does (ACM 1.4: inclusive and accessible technology). (3) Skills concentration in wealthy institutions -> capacity-building programmes, which A/RES/78/287 calls for, especially in developing countries."},
        {"id": "qc-L500-26-P6", "type": "calculation", "difficulty": 1, "marks": 3,
         "problem": "Google (2019) estimated 10,000 years of classical computation for a task its processor did in 200 s; Pan, Chen and Zhang (2022) sampled the same circuits in about 15 hours on 512 GPUs. By what factor did the classical estimate shrink, and how many times longer than the quantum run is 15 hours?",
         "solution": "10,000 years = 10,000 × 365.25 × 24 = 87,660,000 hours, and 87,660,000 / 15 = 5,844,000: the classical cost fell by a factor of about 5.8 million. 15 hours = 54,000 s, which is 270 times the 200 s quantum run, at a lower fidelity (F ≈ 0.0037 in their abstract). Advantage claims are relative to the best classical method known at the time, and that target moves."},
    ],
    "rubric": [
        {"criterion": "Use of primary sources", "excellent": "Cites the exact principle/section/date (ACM 1.3, IR 8547 2030/2035, 89 FR 72926) and quotes sparingly and accurately.", "adequate": "Cites sources correctly but generally.", "inadequate": "Relies on news or vendor summaries, or misstates a rule.", "weight": 25},
        {"criterion": "Stakeholder and harm analysis", "excellent": "Identifies all affected parties, including those without a voice (patients, excluded students), and weighs harms.", "adequate": "Main stakeholders covered.", "inadequate": "Only the decision-maker's interests considered.", "weight": 25},
        {"criterion": "Reasoned judgement", "excellent": "Names conflicts between principles and resolves them with an explicit argument; proportionate recommendations.", "adequate": "Recommendations follow from analysis but conflicts glossed.", "inadequate": "Assertion without argument, or legal conclusions beyond competence.", "weight": 30},
        {"criterion": "Technical accuracy", "excellent": "Quantum and crypto facts right (what Shor/Grover do, HNDL, PQC); numbers computed.", "adequate": "Minor imprecision.", "inadequate": "Hype or misconceptions repeated.", "weight": 20},
    ],
    "conceptNote": "content/concepts/L500/26-ethics-quantum-responsibility.md",
    "conceptSummary": "Four professional duties: report quantum results with their baseline and limits (the 2019 '10,000 years' became 15 GPU-hours by 2022); migrate long-lived secrets to post-quantum cryptography on a plan, because harvested data is exposed whenever a CRQC arrives (Mosca: X + Y > Z; NIST deprecate 2030, disallow 2035); know that export controls cover quantum hardware and production technology but exclude public-domain information and basic research, and ask compliance before sharing; and widen access fairly.",
    "sources": [
        {"title": "ACM Code of Ethics and Professional Conduct (adopted 22 June 2018)", "url": "https://www.acm.org/code-of-ethics"},
        {"title": "IEEE Code of Ethics (IEEE Policies 7.8)", "url": "https://www.ieee.org/about/corporate/governance/p7-8.html"},
        {"title": "NIST IR 8547 (final), Transition to Post-Quantum Cryptography Standards (October 2026)", "url": "https://csrc.nist.gov/pubs/ir/8547/final"},
        {"title": "NIST FIPS 203, Module-Lattice-Based Key-Encapsulation Mechanism Standard (August 2024)", "url": "https://csrc.nist.gov/pubs/fips/203/final"},
        {"title": "UK NCSC, Timelines for migration to post-quantum cryptography (20 March 2025)", "url": "https://www.ncsc.gov.uk/guidance/pqc-migration-timelines"},
        {"title": "US BIS interim final rule, Commerce Control List Additions and Revisions; Implementation of Controls on Advanced Technologies (89 FR 72926, 6 Sept 2024)", "url": "https://www.federalregister.gov/documents/2024/09/06/2024-19633/commerce-control-list-additions-and-revisions-implementation-of-controls-on-advanced-technologies"},
        {"title": "Commission Delegated Regulation (EU) 2025/2003 amending Regulation (EU) 2021/821 (list of dual-use items)", "url": "https://eur-lex.europa.eu/eli/reg_del/2025/2003/oj"},
        {"title": "UN General Assembly resolution A/RES/78/287, International Year of Quantum Science and Technology, 2025", "url": "https://digitallibrary.un.org/record/4052700"},
        {"title": "Google Research blog (2019), Quantum Supremacy Using a Programmable Superconducting Processor", "url": "https://research.google/blog/quantum-supremacy-using-a-programmable-superconducting-processor/"},
        {"title": "Pednault et al. (2019), Leveraging Secondary Storage to Simulate Deep 54-qubit Sycamore Circuits, arXiv:1910.09534", "url": "https://arxiv.org/abs/1910.09534"},
        {"title": "Pan, Chen, Zhang (2022), Solving the sampling problem of the Sycamore quantum circuits, arXiv:2111.03011 (PRL 129, 090502)", "url": "https://arxiv.org/abs/2111.03011"},
        {"title": "Quantum (journal), Terms and Conditions and Code of Conduct", "url": "https://quantum-journal.org/about/terms-and-conditions/"},
    ],
    "seeAlso": [
        "quantum-computing L400 #18 Benchmarking honestly against classical solvers: the method behind an honest advantage claim.",
        "quantum-computing L400 #19 Resource estimation: logical vs physical qubits and feasibility: why 'RSA by 2029' needs evidence of error-corrected scale.",
        "quantum-computing L400 #21 Quantum and post-quantum: crypto inventory and migration plan: the inventory and Mosca priorities that turn the duty to migrate into work.",
        "quantum-computing Capstone #22 Capstone: an end-to-end quantum optimisation service: code rejects 'quantum advantage' claims the report does not support.",
    ],
    "next": "L500 #27 Reading seminar: read Grover (1996) and Preskill (2018) in the original and respond critically.",
}
