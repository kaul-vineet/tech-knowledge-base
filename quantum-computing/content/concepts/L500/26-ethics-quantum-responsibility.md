# Ethics 26: honest claims, the duty to migrate, export controls and access

Quantum computing raises four professional questions for a software engineer: how to talk about results honestly, what to do now about cryptography, what the law says about sharing quantum technology, and who gets access. This note frames each one with primary sources. It is a policy-level overview, not legal advice.

## 1. Responsible claims

The ACM Code (2018) asks professionals to be "honest and trustworthy" (1.3) and to provide full disclosure of capabilities and limitations. It also asks for "comprehensive and thorough evaluations" including risks (2.5) and for professionals to address misleading information (2.7). IEEE's Code (Policies 7.8, item 5) is blunter: be "honest and realistic in stating claims or estimates based on available data". The journal *Quantum* lists "overstatement of results and the omission of crucial conditions and assumptions" as misconduct.

A worked case shows why baselines matter. In 2019, Google reported that its Sycamore processor did a sampling task in 200 seconds that would take a top supercomputer 10,000 years. Days later, IBM researchers argued that the same circuits could be simulated "in a matter of days" using secondary storage. In 2022, Pan, Chen and Zhang sampled them in about 15 hours on 512 GPUs, at lower fidelity. The quantum experiment was real and important. The *comparison* moved by a factor of about 5.8 million (problem P6) because the classical baseline improved. Preskill (2018) defines speed-up against the best classical hardware and algorithm and warns that this is a moving target.

**Practice:** state the task, the baseline, the budget and the uncertainty. Never extrapolate a sampling result to factoring or to "useful applications". Correct hype politely and specifically.

## 2. Harvest now, decrypt later, and the duty to migrate

Shor's algorithm (T25.4) breaks RSA, elliptic-curve and Diffie-Hellman key exchange on a large enough fault-tolerant machine. An adversary does not need that machine today: traffic recorded now can be decrypted later. That is harvest now, decrypt later (HNDL). Mosca's inequality turns this into a test. If X (how long data must stay secret) plus Y (how long migration takes) exceeds Z (time until a cryptographically relevant quantum computer), the data is already at risk.

The official timelines are concrete:
- NIST IR 8547 (final, October 2026) deprecates quantum-vulnerable public-key algorithms after 2030 and disallows them after 2035.
- FIPS 203 (2024) standardises ML-KEM for key establishment.
- The UK NCSC asks organisations to finish discovery and a migration plan by 2028, complete priority migrations by 2031, and complete migration by 2035.

The ethical duty follows from ACM 1.2 (avoid harm) and 3.7 (special care for systems that society depends on). Data subjects such as patients cannot protect their own long-lived records. The professional response is a planned, inventory-driven migration (L400 #21), not panic buying.

## 3. Export controls and dual use

Quantum computers, cryogenic systems and related technology are now controlled as dual-use items.
- The US Bureau of Industry and Security's interim final rule of 6 September 2024 (89 FR 72926) added 900-series ECCNs, including 4A906 (quantum computers), 3A904 (cryogenic cooling) and 3A901 (cryo-CMOS and parametric amplifiers), with worldwide licence requirements and a licence exception for countries with equivalent controls.
- The same rule created a General License for "deemed exports" of quantum technology to some foreign nationals, with annual reporting. BIS explains why: access to foreign expertise is "particularly necessary in quantum computing", and more than half of US quantum-related degrees go to temporary residents.
- In the EU, Regulation 2021/821 governs dual-use items. Delegated Regulation 2025/2003 replaced its Annex I from November 2025. Its General Technology Note excludes information "in the public domain" and "basic scientific research".

**Practice:** published teaching material and open research are generally outside control. Hardware, unpublished production know-how and hands-on transfers may not be. Ask your compliance office *before* sharing. Do not exclude colleagues by nationality pre-emptively (ACM 1.4). Comply with the law, and challenge rules you think wrong through proper channels (ACM 2.3).

## 4. Access and equity

Hardware is scarce and expensive, so access runs through a few cloud providers and well-funded labs. That concentrates who learns, who publishes and who sets defaults. ACM 1.4 asks for inclusive, accessible technology. ACM 3.7 asks the stewards of infrastructure to set fair access policies. UN resolution A/RES/78/287, which proclaimed 2025 the International Year of Quantum Science and Technology, stresses cooperation and capacity-building in developing countries. Open-source simulators, the stack this whole course uses, are a practical equaliser: every lab here runs on a laptop.

## Using the case study

The lesson's case combines all four issues: a start-up press release, a hospital's migration budget, a university lab's open-source decoder, and a funding agency. Work through it in this order: facts, stakeholders, applicable principles and rules, conflicts, recommendation. Show where principles pull against each other, such as openness versus compliance, or urgency versus proportionality. Explain how you resolved each conflict. The public good is the tiebreaker (ACM 3.1).

## Common misconceptions

- **"Quantum computers already break RSA."** No published demonstration factors keys anywhere near deployed sizes. The risk is future decryption of data recorded today.
- **"Post-quantum means quantum key distribution."** PQC is classical software (for example ML-KEM). QKD needs quantum hardware.
- **"Export controls forbid teaching quantum computing to international students."** Public-domain information and basic research are excluded. Specific technology transfers may need a licence.
- **"An advantage claim is a fact about the device."** It is a fact about the device *and* the best classical method known at the time.
