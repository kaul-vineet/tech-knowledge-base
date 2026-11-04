# L600 #06 evidence - verifiable, replicated science-data release pipeline

Checked 2026-10-30. Sources are primary only: RFCs, the TUF specification, NIST and ESA pages, the original papers
and official Python docs. Every URL below was retrieved during this build. Numbers in the lesson, concept note and
question bank are recomputed by `research/checks_06.py` (exit 0 = all match).

## Research questions
1. What exactly must a canonical JSON encoder do with doubles so two stacks hash the same bytes?
2. How do RFC 6962/9162 define the Merkle tree hash, inclusion and consistency proofs, and their verifiers?
3. What does TUF require of a client against rollback and freeze, and how does it rotate root keys?
4. How do anti-entropy protocols compare replicas cheaply?
5. What licence governs Gaia data, and when is inverting a parallax honest?

## Sources kept (score /12: implementable, current, authoritative, open, transferable, right depth)
| source | url | score | used for | verified how |
|---|---|---|---|---|
| RFC 8785 JCS | https://www.rfc-editor.org/rfc/rfc8785 | 12 | canonical.py, build task, ADR 0001 | Fetched the text. Number rule = ECMA-262 Number::toString (3.2.2.3). Keys sorted by UTF-16 code units (3.2.3). NaN/Infinity and lone surrogates are errors. tests/test_seam_canonical.py copies the 3.2.4 example **bytes** and the property-sorting vector; tests/test_build_task.py copies all 24 Appendix B samples. The solution passes all of them; the shipped `repr()` fails 3 of 5 tests. Appendix G lists a Python implementation, not installed here (no network installs). |
| RFC 9162 CT v2.0 (obsoletes 6962) | https://www.rfc-editor.org/rfc/rfc9162 | 12 | merkle.py, tlog.py | MTH with 0x00/0x01 prefixes and split k = largest power of two < n (2.1.1); PATH/PROOF generation (2.1.3.1, 2.1.4.1); iterative verifiers (2.1.3.2, 2.1.4.2) implemented step by step. test_m2_release.py reproduces the 2.1.5 example shapes (d0 -> [b, h, l]; PROOF(3) = [c, d, g, l]; PROOF(4) = [l]; PROOF(6) = [i, j, k]). All inclusion and consistency proofs for n <= 33 verify; forks and tampered leaves fail. Split views need gossip/witnesses (11.3). |
| RFC 6962 CT | https://www.rfc-editor.org/rfc/rfc6962 | 10 | lineage, "compare tree roots" | Same MTH definition and example; marked obsolete by 9162 on the RFC Editor page. Section 5 says clients should gossip STHs. |
| TUF specification 1.0.37 | https://theupdateframework.github.io/specification/latest/ | 12 | client.py order, trust.next_root, ADR 0002/0003 | Quotes used: rollback ("older than that which the client previously knew to be available"), indefinite freeze, "Clients MUST NOT replace a metadata file with a version number less than the one currently trusted", "Clients MUST NOT trust an expired file". Root N+1 must be signed by a threshold of root N and of root N+1, and its version must be exactly N+1 (section 5.3). Fixed update start time (5.1). The timestamp role is online and short-lived (2.1.4). Mirrors are untrusted (2.1.5, 2.2). Bogus clocks are an open question (7.1). |
| RFC 8032 EdDSA | https://www.rfc-editor.org/rfc/rfc8032 | 11 | M3 vector | Ed25519 signatures are 64 octets. TEST 1 (empty message) matches cryptography L200 #7's `RFC8032_T1`, which M3 re-verifies. |
| FIPS 204 ML-DSA | https://csrc.nist.gov/pubs/fips/204/final | 11 | dual signature | Final 2024-08-13. ML-DSA-65 signature size 3,309 B, observed from cryptography 50.0.2 (`len(sign())`) and matching cryptography L400 #17's qbank. |
| Dynamo (SOSP 2007) | https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf | 10 | mirrors.py bucket tree | Section 4.7: anti-entropy with Merkle trees; "each branch of the tree can be checked independently without requiring nodes to download the entire tree". |
| Demers et al. 1987, Epidemic algorithms | https://www.cis.upenn.edu/~bcpierce/courses/dd/papers/demers-epidemic.pdf | 10 | push-pull gossip | Anti-entropy: "every site regularly chooses another site at random and by exchanging database contents with it resolves any differences". The ACM DOI page returned no text to the fetcher, so this course copy is used (KNOWN GAP). |
| Gaia data licence | https://www.cosmos.esa.int/web/gaia-users/license | 11 | licence seam | "Gaia data are distributed under the CC BY-NC 3.0 IGO license." The credit text is reused verbatim from astronomy L400 #21's inputs.py, retrieved there on 2026-10-29. |
| Gaia DR3 contents | https://www.cosmos.esa.int/web/gaia/dr3 | 10 | scaling limit | DR3 released 2022-06-13; the data come from the Gaia Archive and partner data centres. ESA's EDR3 numbers page gives 1,811,709,771 sources with positions (> 1.8 billion). |
| Bailer-Jones 2015 | https://arxiv.org/abs/1507.02105 | 11 | science.py SNR >= 5 | Distance from parallax "is not trivial once the fractional parallax error is larger than about 20%". Our cut is parallax/error >= 5. |
| What's New in Python 3.1 | https://docs.python.org/3/whatsnew/3.1.html | 11 | the fault's realism | "repr(1.1) was computed as format(1.1, '.17g') which evaluated to '1.1000000000000001'". Python 3.1+ uses David Gay's shortest representation, which is why `repr` gives JCS's digits but not its layout. |

Dropped: blog posts on canonical JSON, and the OLPC "canonical JSON" (TUF's examples use it, but it forbids
floats, so it cannot carry a catalogue). Cassandra/Riak repair docs and Sigstore Rekor were not fetched, so they are
not cited.

## What ran here (Linux, Python 3.12, numpy, cryptography 50.0.2)
- `run_project.py`: PASS 12/12, exit 0. Each `--inject` gives FAIL with exit 1: float-format 9/12, drop-old-key
  11/12, no-freshness 10/12, licence-drop 11/12. Outputs are pasted in the lab README.
- `python -m unittest discover -s tests -t tests`: 44 tests OK, run 3 times (125 s, 113 s, 156 s wall). Tests use a
  fake clock only.
- `BUILD_TARGET=mine python -m unittest tests.test_build_task`: FAILED (failures=3); against the solution: OK.
- tryIt 1 and 2 print the lesson's expected lines; checks_06.py re-runs them as subprocesses and compares.
- pytest is not installed in the sandbox, so unittest is the runner. The spec's `python -m pytest ... -q` is pending CI.

## Derived or chosen numbers (not from a source)
- TTL 3,600 s, gossip period 60 s, 16 buckets and a release every 1,200 s are lab parameters. The rule
  "TTL > re-sign interval + worst lag + skew" follows from the TUF expiry check plus the measured lag. It is shown
  by tryIt 2, not by a source.
- F2's bound of 4 rounds is the measured worst case over 100 seeds (3), plus one round of margin. Push-pull rounds
  are synchronous: each mirror learns what its peer knew at the start of the round.
- Demo keys come from SHA-256 of fixed seed strings so output is reproducible. ML-DSA signing is randomized, so the
  release.json hash differs per run; the lesson quotes no number that depends on it.

## Known gaps / pending CI
- macOS and Windows runs; a cross-language JCS check (for example npm `canonicalize` from RFC 8785 Appendix G);
  the minisign and CyberChef exercises (manual).
- No witness or monitor: split-view detection is discussed, not built.
- Equivocation by a retired key (a second, different "v2") is caught only by clients that pinned v2 or by
  log monitors. It is documented in ADR 0003, not tested.
- TUF sub-step numbers inside section 5.3 were not cited, because their numbering could not be confirmed from the
  fetched text.
