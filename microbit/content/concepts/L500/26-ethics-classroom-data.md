# Concept: Ethics — classroom data, children's privacy, e-waste and accessibility

## Why it matters
The capstone (lesson 22) puts sensor boards in a classroom and sends readings to a dashboard. A temperature reading looks harmless, but a per-desk noise level, a motion count or a timestamped button press is data about identifiable children once it can be linked to a seat, a timetable or a name. Physical computing also creates batteries and boards that become waste, and it can exclude pupils who cannot see the LEDs or press the buttons. These are design inputs, not afterthoughts.

## The professional baseline
- **ACM Code of Ethics (2018).** Principle 1.2 *Avoid harm* asks you to analyse "the consequences of data aggregation and emergent properties of systems"; 1.6 *Respect privacy*; 1.1 notes that well-being "requires a safe natural environment" and asks for environmental sustainability; 3.7 covers systems that become part of society's infrastructure.
- **IEEE Code of Ethics (Policies 7.8).** Item 1: hold paramount the safety, health and welfare of the public, "strive to comply with ethical design and sustainable development practices", and "protect the privacy of others".
- **UN CRC General comment No. 25 (2021)** explains how children's rights apply in the digital environment, including non-discrimination in access.

## Law and regulators at policy level (not legal advice)
- **UK — ICO Age appropriate design code ("Children's code").** A statutory code under section 123 of the Data Protection Act 2018 with 15 standards for online services likely to be accessed by children, among them *best interests of the child*, *data protection impact assessments*, *default settings*, ***data minimisation***, *profiling* and ***connected toys and devices***. It was issued on 12 August 2020, and services were expected to conform by 2 September 2021. The ICO notes the guidance is under review after the Data (Use and Access) Act 2025. Whether a school's own sensor network is in scope is a legal question; its standards are still a good design checklist.
- **India — Digital Personal Data Protection Act 2023, section 9.** A child is anyone under 18. A data fiduciary must obtain *verifiable consent of the parent* before processing a child's personal data, must not process in a way likely to harm a child's well-being, and must not undertake *tracking or behavioural monitoring* of children or targeted advertising at them. The DPDP Rules 2025 were notified on 13 November 2025 with an 18-month phased timeline and limited exemptions (the government's summary names healthcare, education and real-time safety). Check the commencement status on the date you deploy.

## Minimisation as engineering
Data minimisation is a design property you can test: decide what leaves the board. A room-level mean temperature every 10 minutes answers "is the room too warm?"; a per-desk microphone level every second can reveal who talks. Aggregate on the gateway, drop identifiers, keep the shortest retention that answers the question, and write the purpose down before collecting. The lesson 21 rule applies to people too: code decides what is collected; nothing collects "just in case".

## E-waste and batteries
The Global E-waste Monitor 2024 (ITU/UNITAR) reports 62 million tonnes of e-waste in 2022, of which 22.3 % was documented as formally collected and recycled, and projects 82 million tonnes by 2030. In the EU the WEEE Directive 2012/19/EU puts collection and treatment duties on producers. A classroom's share is small, but design choices multiply: lesson 14's always-on logger would need about 158 battery sets per board per 39-week school year, the adaptive one 4 (problem 26.4). Reuse boards across cohorts, prefer rechargeable or USB power where safe, and plan collection of dead cells.

## Accessibility of physical computing
The Micro:bit Educational Foundation's hardware accessibility statement groups barriers into sensory outputs (LEDs, speaker), physical inputs (small buttons, gestures) and setup tasks; its teacher guides note, for example, that Bluetooth pairing and compass calibration need sight (USB transfer avoids the first) and that the Python Editor supports keyboard and screen-reader use. Dashboards built in lessons 17–22 are web content: WCAG 2.2 (a W3C Recommendation since 5 October 2023) is the reference. Offer redundant outputs (sound and LEDs; serial text a screen reader can read) and external switches on the edge connector.

## A structured case analysis
1. Facts and the decision to make. 2. Stakeholders and what each stands to gain or lose. 3. Data inventory: field, identifiability, purpose, retention. 4. Obligations (codes, law, school policy). 5. Options, including "do not collect". 6. Choice, with the residual risk named. 7. What you will measure to know it worked.

## Common misconceptions
- *"It's only sensor data."* Linkable to a seat and a timetable, it is personal data about a child.
- *"Consent fixes everything."* Under DPDP s.9(3) some processing of children's data is barred regardless; under the Children's code the best-interests standard still applies.
- *"Accessibility is a software problem."* The board itself has sensory and motor barriers.
- *"Sustainability is someone else's job."* The ACM and IEEE codes make it yours.
