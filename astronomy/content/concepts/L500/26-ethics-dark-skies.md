**Concept: sharing the sky, the land and the data**

## Why it matters
Astronomy looks outward, but its practice depends on others. The night sky is also the sky of satellite operators, their customers, cultural practitioners, amateur astronomers and wildlife. Observatories stand on land that has histories and owners. Open data creates value only when licences and credit are honoured. Software engineers in astronomy build the pipelines, brokers and releases where these questions become concrete decisions.

## Three areas, with primary sources

**1. Dark and quiet skies.** The IAU Centre for the Protection of the Dark and Quiet Sky from Satellite Constellation Interference (CPS) was launched on 1 April 2022 after the SATCON and Dark & Quiet Skies workshops. Its mission statement treats a dark and radio-quiet sky as essential to science, to the cultural heritage of humanity and to nocturnal wildlife. At the UN, COPUOS created a five-year agenda item for its Scientific and Technical Subcommittee starting in February 2025. The conference room paper A/AC.105/C.1/2026/CRP.22/Rev.1 (11 February 2026) describes:
- streaks in optical images, worst in twilight and at low elevation;
- false positives in time-domain surveys from glints;
- systematic errors from faint unmasked trails;
- radio interference, including unintended electromagnetic radiation.

It cites a visual-magnitude-7 brightness limit derived from the Vera C. Rubin Observatory's requirements. It notes that public two-line elements are accurate only to a few arcminutes. It recommends brightness prediction and validation, astronomy-grade ephemerides and data sharing. It also lists existing national law: the French Space Operations Act's magnitude-7 objective, the Italian Space Law of 2025, FCC licence conditions and the proposed EU Space Act. The paper also stresses that constellations bring real benefits, such as connectivity for remote and underserved areas. An honest analysis keeps both columns of the ledger.

**2. Observatory sites and Indigenous perspectives.** Maunakea in Hawai'i is the most documented case. The Hawai'i Supreme Court's amended opinion of 30 November 2018 (SCOT-17-0000777) records two positions:
- Native Hawaiian cultural practitioners regard the mountain as a sacred manifestation of their ancestry, to be honoured in its natural state.
- Appellees hold that telescope use is an allowed use, that mitigation reduces impact, and that the mountain can also be honoured through scientific knowledge.

The opinion records significant cumulative adverse impacts from earlier development. It holds that the summit's conservation lands are public resources held in trust, and it affirms the permit for the Thirty Meter Telescope; one justice dissented. In 2022 the legislature's Act 255 observed that Mauna Kea had come to symbolise "a rigid dichotomy between culture and science". It created a stewardship authority whose voting members include Native Hawaiian practitioners and lineal descendants. Read the documents themselves; secondary accounts often flatten them.

**3. Open data, equity and credit.** Gaia data are licensed CC BY-NC 3.0 IGO. Derived products must keep the non-commercial term and the attribution. The DR3 summary article is separately CC BY 4.0. Open access removes one barrier, but not the others: compute, training, bandwidth and publication costs. ACM Code 1.5 asks professionals to credit the creators of ideas and artefacts and to respect licences. That includes calibration and pipeline work, citizen scientists and early-career contributors.

## Tools for analysis
- **Stakeholder mapping.** Who is affected, who decides, and who has no seat at the table?
- **Separate law from recommendation from claim.** A UN conference room paper informs discussion. A statute binds. A court holding binds within its jurisdiction. A press release does neither.
- **Professional codes.** ACM 2018: 1.1 contribute to society, with all people as stakeholders; 1.2 avoid harm; 1.3 honesty; 1.4 fairness; 1.5 credit; 2.5 thorough evaluation of impacts and risks; 3.7 care for infrastructure-like systems. ABET student outcome 4 asks for ethical judgments in global, economic, environmental and societal contexts.
- **Quantify where you can.** A magnitude-5 satellite is 6.31 times brighter than the magnitude-7 recommendation. A satellite 550 km overhead stays sunlit until the Sun is 23.0° below the horizon, past astronomical twilight. At 350 km it is 18.6° (`sky_numbers.py`).

## Worked example
A colleague proposes silently dropping alerts near predicted satellite tracks. The numbers say the public ephemerides are too coarse for a 30″ mask. The code of ethics says silent changes misstate completeness (1.3) and can harm downstream users (1.2). The better design is engineering, not avoidance: flag, measure, publish, and let users choose.

## Common mistakes
- Treating one community spokesperson, or one public meeting, as consent.
- Quoting recommendations as if they were law, or law as if it were settled everywhere.
- Re-licensing derived data more permissively than its inputs allow.
- Presenting only the costs, or only the benefits, of a technology to make an argument easier.
