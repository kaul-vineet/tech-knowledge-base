# Known gaps (L600)

- **Not yet run on macOS or Windows.** All eight scorecards, failure labs, test suites and checks ran on Linux only; the
  `integrated` workflow runs them on all three operating systems.
- **No real local model.** Projects 03, 05 and 08 ran against the shared fake model. A real model may choose different
  steps; the deterministic checks still decide, but one scorecard line in 03 expects a specific rejection.
- **SDK cross-checks not run:** Qiskit (02, 07), astropy/astroplan (05), OPA for the policy file (08), and the
  MicroPython simulator for the micro:bit fleet (04, status `validated-stub`).
- **Teaching constructions, not deployable:** 01's key delivery is not HPKE/MLS; 02's handshake is a TLS-shaped model
  (RFC 10024 notes the hybrid security argument holds for real TLS 1.3 only).
- **Stated assumptions:** 02 uses z = 10 years and a 6,144-byte handshake budget; 05's weather model isn't fitted to
  site records and uses J2000 coordinates without precession (~0.36°); 04's radio stub has no airtime or collisions.
- **Known limits written into the lessons:** 03's claim checker matches numbers by value (a right number for the wrong
  quantity passes); 06 has no witness/monitor for split-view logs; 07 uses Wald error bars (Wilson is the follow-up).
- **Slow on network drives:** each project imports several earlier labs; on a local SSD a full run takes seconds.

## Mac mini track
- **Nothing has run on a Mac yet.** Every experiment ran here in its small "--here" mode. Real-model, Qiskit Aer, astropy,
  INDI/KStars, micro:bit simulator and overnight full-size results are marked "run on your Mac to confirm".
- **Real models can change scorecard lines:** a careful real model may fail lines that assume a gullible stand-in model
  (03 M2; 08 M3/M5). The safety lines must still pass. Each mac_mini README explains how to read the result.
- **Project 07's capacity claim is one seed deep.** The p95 queue-time fitness function passes on the shipped seed 7 but fails
  on seed 8 (170 s against the 30 s budget) with the same fleet. The Mac overnight run measures 40 seeds; until then, treat
  the 30 s figure as unproven.
- **Limits found by the new experiments:** 04's one-byte device ID caps a radio group at 255 boards, and the 16-bit sequence
  number wraps after 45.5 days. 01 must rotate keys by message count, not on a timer.
- **Steps not checked against current docs:** the INDI command-line tools, Ekos remote-server setup, and where Stellarium
  writes its output file on macOS.
