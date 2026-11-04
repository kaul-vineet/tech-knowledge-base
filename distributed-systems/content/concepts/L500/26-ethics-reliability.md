## Why it matters
When a region's control plane fails, the people harmed include many who never chose the vendor. A patient cannot book an appointment. A caller to a contact centre gets silence. An engineer is paged to fix something they cannot see.

Reliability engineering is therefore not only a cost-benefit exercise. Professional codes treat avoiding harm, honest evaluation of risk and stewardship of infrastructure as obligations.

## Definitions and sources
**ACM Code of Ethics (2018).**
- 1.2 *Avoid harm*. It includes an obligation to report signs of system risk and, if leaders do not act, possibly to "blow the whistle" after careful assessment.
- 2.5 *Give comprehensive and thorough evaluations of computer systems and their impacts, including analysis of possible risks.*
- 3.7 *Recognize and take special care of systems that become integrated into the infrastructure of society.*
- 1.6 *Respect privacy.* 1.1 asks professionals to *promote environmental sustainability*.

**IEEE Code of Ethics.** Item 1: hold paramount the safety, health and welfare of the public, comply with sustainable development practices, protect privacy, and disclose promptly factors that might endanger the public or the environment. Item 5: acknowledge and correct errors.

**Blameless post-mortem** (Google SRE, chapter 15). A written record of an incident, its impact, its contributing causes and its follow-up actions. It identifies causes "without indicting any individual or team". Triggers include user-visible downtime, data loss of any kind, on-call intervention and monitoring failures.

**GDPR (Regulation (EU) 2016/679).**
- Article 32(1)(b)-(c) lists, among the appropriate security measures, "the ability to ensure the ongoing confidentiality, integrity, availability and resilience of processing systems and services" and "to restore the availability and access to personal data in a timely manner".
- Chapter V (Articles 44-49) governs transfers outside the EEA. A transfer needs an adequacy decision, or appropriate safeguards such as standard contractual clauses together with enforceable rights and effective remedies, or a derogation.
- In *Schrems II* (C-311/18, 2020) the CJEU invalidated the EU-US Privacy Shield adequacy decision and upheld the standard-clauses decision.

**Energy.**
- PUE = facility energy / IT energy.
- The IEA (2025) projects data-centre electricity use to reach about 945 TWh by 2030, just under 3% of global demand.
- The recast EU Energy Efficiency Directive (2023/1791, Art. 12) introduces energy-performance reporting for data centres above a power threshold.

## The case in brief
AWS's summary of 7 December 2021 describes a chain of events:
- An automated scaling activity triggered a surge of connections that overwhelmed devices between two internal networks.
- Retries deepened the congestion; a latent defect stopped clients from backing off.
- Monitoring went dark.
- The status dashboard could not fail over.
- Support-case creation broke from 7:33 AM to 2:25 PM PST.

The network devices recovered after 6 h 52 min: 412 minutes, 7.8 times a 99.99% yearly budget. The lesson's case adds a decision. An EU telehealth service is asked to add failover to a non-EEA region within a week.

## How to analyse
1. **Stakeholders and harms.** Direct and indirect, including people who cannot opt out. Note which harms *design* amplified, such as retry behaviour, or status tooling inside the failure domain.
2. **Obligations.** Map facts to specific principles: ACM 1.2, 2.5, 3.7 and 1.6, IEEE 1, GDPR Art. 32 and Chapter V. Keep law and ethics distinct. Law is a floor; the codes ask for more. This lesson is policy-level, not legal advice.
3. **Options with numbers.**
   - Availability budget: 99.95% of a month is 21.6 minutes.
   - RPO measured in lab 19: 16 acknowledged writes lost with asynchronous replication.
   - Energy: 40 kW at PUE 1.4 is 490.6 MWh a year, doubled by a hot standby.
   - Legal basis for any transfer.
4. **Recommendation.** It should be blameless, owned and testable. Use game days, bounded chaos experiments (lab 20) and quarterly failover tests.

## Common misconceptions
- **"Blameless means nobody is accountable."** Accountability moves to action items, review and publication. Blame drives incidents underground, so the organisation stops learning.
- **"More redundancy is always more ethical."** Untested failover causes outages. Hot standbys cost energy. Replicas abroad may be unlawful transfers. Proportionality is part of the duty.
- **"Availability is a business concern; privacy is the legal one."** GDPR Art. 32 makes availability and timely restoration part of *security*.
- **"Encryption makes any transfer fine."** It reduces risk, but the transfer rules still apply. Ask the DPO.
- **"The provider's outage is the provider's problem."** ACM 2.5 and 3.7 apply to your design choices: single region, no degraded mode, status page in the same failure domain.

## Further reading
ACM Code (2018); IEEE Code; AWS's December 2021 summary; Google SRE chapter 15; GDPR Art. 32 and CJEU press release 91/20; IEA, *Energy and AI* (2025).
