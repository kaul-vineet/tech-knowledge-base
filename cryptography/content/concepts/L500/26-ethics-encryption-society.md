# Ethics: encryption, lawful access and responsible disclosure

## Why it matters
The code in this course protects health records, journalists' sources, payment data and abuse survivors. It also protects people under criminal investigation. Engineers who build cryptography make decisions that governments, courts and the public later fight over: whether a provider can read user data at all, whether a found vulnerability is fixed or kept, and whether a product may be shipped abroad. Professional codes do not give algorithmic answers. As the ACM Code says of itself, it is a basis for ethical decision-making, not an algorithm. They do require you to reason explicitly, honestly and with the public good as the primary consideration.

## The lawful-access debate
**The case for access.** Law enforcement argues that warrant-proof devices and end-to-end encryption put evidence beyond lawful process ("going dark"). A society governed by law should not have spaces that court orders cannot reach.

**The case against mandated access.** In *Keys Under Doormats* (2015), fifteen security researchers argued that exceptional-access mandates would be unworkable in practice. They would force developers to reverse forward-secrecy designs and would introduce hard-to-detect flaws. Who governs such access globally, and how it respects human rights, also remains unsolved. They recommended that proposers first publish concrete technical requirements for public analysis.

**The technical core** comes from lessons 23-25. An access mechanism is a key or a privileged code path. It must be protected for its whole lifetime, it is a single high-value target, and it changes the security game: the scheme is no longer IND-CCA secure against whoever holds or steals the access key.

## Case: Apple and the FBI (2016)
After the San Bernardino attack, a court ordered Apple to build iOS firmware that removed the auto-erase and retry delays on one seized iPhone and allowed electronic passcode entry. Apple's public letter called this a backdoor that could unlock any iPhone in someone's physical possession, and objected to the use of the All Writs Act of 1789. The FBI later gained access through an outside party and the government withdrew its filing.

The DOJ Inspector General's 2018 report found no evidence that the FBI had a capability at the time of its congressional testimony. It did find that internal coordination failures delayed finding the outside solution. Note the technical point: the request targeted the **guess-limiting layer**, because a 6-digit passcode has under 20 bits of entropy (lesson 24) while the AES key itself was never the weak point.

## Responsible (coordinated) disclosure
If you find a flaw, such as a library that reuses GCM nonces after a restart, the goal is to **reduce risk to users**. ISO/IEC 29147:2018, last confirmed in 2024 and now being revised, gives vendors requirements and recommendations for receiving reports and publishing remediation information. ISO/IEC 30111 covers the handling in between. The CERT Guide to Coordinated Vulnerability Disclosure (SEI, 2017; maintained as a web edition) describes the phases from the finder's side: discovery, reporting, validation and triage, remediation, public awareness and deployment. It also covers when to bring in a coordinator such as CERT/CC.

In practice:
- report privately through the vendor's published channel (SECURITY.md, a security contact or a private advisory);
- give a minimal reproduction and the impact;
- agree a timeline and escalate to a coordinator if the vendor does not respond;
- publish an advisory with the fix and credit;
- never test on systems you are not authorised to access (ACM 2.8).

The Apple-FBI outcome raises the opposite question. An exploit bought and kept secret protects one investigation and leaves every similar device exposed.

## Export rules at policy level
Encryption is a **dual-use** technology. The Wassenaar Arrangement's dual-use list places it in Category 5 Part 2, "Information Security", and countries implement that list in national law. In the US, the Export Administration Regulations apply. Most commercial encryption is exported under **License Exception ENC** (15 CFR 740.17) after self-classification or a BIS classification. Mass-market items typically end in ECCN 5A992/5D992, and reporting duties and restrictions apply for certain destinations (Country Groups E:1/E:2). The EU applies its dual-use regulation. For an engineer the duty is to **recognise** the question (shipping crypto, publishing crypto source, hiring abroad) and route it to trade-compliance specialists. This lesson is not legal advice.

## Frameworks to apply
- **ACM Code (2018):**
  - 1.2 Avoid harm (including the duty to report risks);
  - 1.6 Respect privacy;
  - 1.7 Honor confidentiality;
  - 2.3 Know and respect existing rules (and challenge unethical rules through existing channels first);
  - 2.5 Thorough evaluation of risks;
  - 2.9 Design robustly and usably secure systems;
  - 3.1 Public good as the central concern;
  - 3.7 Special care for systems that become societal infrastructure.
- **IEEE Code (Policies 7.8):** I.1 protect privacy and disclose dangers promptly; I.5 honest criticism and realistic claims.

## A structured case analysis
1. State the facts with sources, and label advocacy as advocacy.
2. List stakeholders, their interests and their risks.
3. Do the technical analysis: threat model, blast radius, entropy and keys.
4. Name the principles that conflict and say why one dominates here.
5. Take a position and answer the strongest counter-argument honestly, including who bears the cost of your choice.

## Common misconceptions
- **"A backdoor for one phone is a one-phone problem."** Once built and signed, a tool or technique is reusable and becomes a target.
- **"Ethics means always refusing law enforcement."** The codes require respecting lawful process and challenging it through legitimate channels. Refusal is a reasoned, accountable act, not a default.
- **"Full public disclosure on day one is most honest."** It can maximise harm before a fix exists. Coordinated disclosure balances user protection with transparency.
- **"Open-source crypto is never export-controlled."** Publicly available source is treated specially but not ignored; get advice.
