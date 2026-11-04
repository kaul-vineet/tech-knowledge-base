**Concept: Ethics and professional responsibility – accessibility, privacy by design and honest technical debt**

## Why it matters
Library Loans is a public service. Whether a blind member can sign in, whether the city keeps a permanent record of what
everyone reads, and whether the council is told the truth about both are decisions architects make or enable. They are
not afterthoughts for a UI designer or a lawyer: they are quality attributes that are costly to retrofit, and they carry
professional duties. This note is not legal advice; it shows how to reason and whom to ask.

## Accessibility is an architectural requirement
WCAG 2.2 became a W3C Recommendation on 5 October 2023 (updated 12 December 2024) and was approved as ISO/IEC 40500:2025
in October 2025. It adds nine success criteria to WCAG 2.1 and removes 4.1.1 Parsing; six of the nine are at level A or AA,
the level most policies reference. Several of them are decided by architecture, not styling:
- **3.3.8 Accessible Authentication (Minimum), AA** – sign-in must not rely on a cognitive function test such as a puzzle
  unless an alternative or assistance exists. Whether you can meet it depends on the identity provider you chose (lesson 10).
- **2.5.7 Dragging Movements, AA** – anything done by dragging needs a single-pointer alternative; a component-library choice.
- **2.5.8 Target Size (Minimum), AA** – targets at least 24 by 24 CSS pixels, or enough spacing, with listed exceptions.

Precedent shows the stakes. In *Robles v. Domino's Pizza* (9th Cir., 2019) the court held that Title III of the
Americans with Disabilities Act applied to the chain's website and app, which connect customers to the goods and services
of its physical restaurants. In the EU, the European Accessibility Act (Directive 2019/882) covers services such as e-commerce and e-books;
whether it covers a given public library service is a question for counsel – national public-sector rules may apply
instead. ISO/IEC 25010:2023 now names *inclusivity* as a subcharacteristic of interaction capability, so it belongs in the
utility tree (lesson 24) as an (H, M) scenario with a measurable response, and in release gates.

## Privacy by design and by default
GDPR Article 25(1) requires the controller, both when deciding the means of processing and during processing, to implement
appropriate technical and organisational measures, *such as pseudonymisation*, designed to implement data-protection
principles *such as data minimisation*. Article 25(2) requires that by default only personal data necessary for each
specific purpose are processed – covering the amount collected, the extent of processing, the storage period and
accessibility. This is enforced on its own terms: in November 2022 the Irish Data Protection Commission found infringements
of Articles 25(1) and 25(2) in Facebook and Instagram contact-importer and search features and imposed fines totalling
€265 million on Meta Platforms Ireland. Libraries have a stronger tradition still: the ALA's privacy interpretation treats
circulation records as confidential and asks libraries to retain the minimum and anonymise where possible.

For Library Loans this translates into architecture: keep active loans; delete or anonymise returned loans after a fixed
period by a scheduled job checked by a fitness function; make history for recommendations opt-in and revocable; give
analytics pseudonymised events with the key held by the loans service; enforce "analytics never reads member identifiers"
as a tested policy (lesson 19).

## Technical debt and honesty
Ward Cunningham introduced the debt metaphor in 1992: shipping not-quite-right code is like borrowing; a little debt speeds
development if it is repaid promptly, and every minute spent on not-quite-right code is interest. The metaphor contains an
ethical test: debt is acceptable when the people who pay the interest know about it and agreed to it. An inaccessible
sign-in logged as "minor tech debt" fails that test – the interest is paid by disabled members who were not asked.

The ACM Code (2018) is direct about the duties involved. 1.3 asks computing professionals to be honest and to provide full
disclosure of system capabilities, limitations and potential problems, and calls deliberately false or misleading claims a
violation. 1.4 notes that failure to design for inclusiveness and accessibility may constitute unfair discrimination. 1.6
asks that only the minimum personal information be collected, with retention periods defined, enforced and communicated.
2.5 asks for thorough evaluations including risks. 1.2 adds a duty to report signs of system risks that might result in
harm. The ACM/IEEE-CS Software Engineering Code adds PUBLIC, PRODUCT and JUDGMENT principles in the same spirit.

## Common misconceptions
- **"We pass an automated checker, so we conform."** Automated tools cover only part of WCAG; keyboard and screen-reader
  testing by people is still required.
- **"Privacy is the DPO's job."** Article 25 obligations bind the controller at design time – that includes the architecture.
- **"Saying 'compliant' is just marketing."** A conformance claim is a factual statement; if it is false, it is a
  misrepresentation, not a trade-off.
- **"Tech debt is a private engineering matter."** When the interest falls on users, it is their matter too.
