**Concept: open data and science software practice - standards, licences, credit and a release gate**

## Why it matters
Astronomy runs on shared data: Gaia, TESS, Kepler, ZTF and survey catalogues are reused in thousands of papers. Reuse works only if four things hold:
- tools can read the files, which is what Virtual Observatory standards are for;
- people can tell what they may do with them (licences);
- providers get credit (acknowledgements and citation);
- everyone can check they have the same bytes (checksums).

A release that drops a provider's licence condition or paraphrases its required acknowledgement is not a style problem. It is a problem you cannot fix after people have copied the data.

## Mental model
A release is a contract written as files. Code checks every clause before anything is published.

```
inputs (licence, credit) --> derived catalogue --> release/
                                                   |- catalogue.vot        VOTable 1.5: FIELD unit, ucd, datatype
                                                   |- CITATION.cff         cff-version, message, title, authors
                                                   |- LICENSE.txt          SPDX id, keeps NC/SA of the inputs
                                                   |- ACKNOWLEDGEMENTS.md  each provider's text, verbatim
                                                   |- MANIFEST.json        SHA-256 of every file
                             check(release) == []  --> publish ; else --> fix or human review
```

## Design space
- **Formats.** VOTable (IVOA; 1.5 is the current REC) carries units and UCDs with the data, which TOPCAT, Aladin and TAP services understand. CSV is easy and loses meaning; FITS tables keep units, but VO tooling prefers VOTable.
- **Licences.** Inputs come with terms: Gaia DR3 is CC BY-NC 3.0 IGO (ESA's licence page), most MAST data are public domain with a requested acknowledgement, and your own data are what you choose. A derived product must keep its inputs' conditions. NonCommercial and ShareAlike cannot both be kept (a BY-SA adaptation must stay BY-SA, which allows commercial use), so that case needs a person.
- **Citation.** CITATION.cff (CFF 1.2.0) makes software and data citable from the repository. The software citation principles ask for unique identification and the specific version; a DOI or an ASCL entry makes the citation persistent. FAIR R1.1 asks for "a clear and accessible data usage license".
- **Review mode.** Manual review only, an automated gate in CI, or the gate plus external validators (astropy.io.votable, cffconvert, STILTS votlint) and a DOI deposit.

## How to decide
Measure what each review mode catches on realistic defects instead of arguing. The criteria: no licence condition lost, verbatim credit, valid citation metadata, VOTables that tools read without guessing, and bytes that match the manifest.

**Worked example (lab run):** the shipped builder licensed the release CC-BY-4.0 by default. `check()` reports "licence: release CC-BY-4.0 drops the NC condition of input gaia_dr3_astrometry". The fixed builder chooses CC-BY-NC-4.0. Six defects were seeded into a good release, five of them with a freshly re-hashed manifest to imitate a careful-looking maintainer:
- the catalogue edited after the manifest;
- CITATION.cff without `message`;
- the licence relaxed to CC-BY-4.0;
- the Gaia credit paraphrased ("DPAC funding");
- a row missing a TD;
- a FIELD without a unit.

A "required files present" review caught 0/6; `check()` caught 6/6, each with a specific message. Adding a BY-SA input raises "NonCommercial and ShareAlike inputs conflict: needs human review"; without Gaia the release is CC-BY-4.0 and clean.

## Failure modes at scale
- **Licence drift through pipelines:** each derived product rebuilds metadata from defaults, and the strictest input's terms vanish three steps later. Carry input licences in metadata.json and propagate them mechanically.
- **Credit text rot:** providers update acknowledgement wording per data release (Gaia gives each release its own). Quote the text once, with its source and date, and re-check at each release.
- **Validator coverage:** our VOTable check covers structure, not the XML schema. Run astropy or votlint in CI, and treat disagreement between validators as a failure.
- **Over-trusting rules:** a rule table is not legal advice. New licence families (ODbL, custom archive policies) need a person before they get a row.

## Common mistakes
- Assuming "public data" means "no conditions". Gaia's terms are NonCommercial, and MAST asks for acknowledgements.
- Paraphrasing required acknowledgements to fit a page limit; copy them verbatim.
- Publishing a CSV without units, and a citation without a version.
