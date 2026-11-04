# 05 on the Mac mini — real models, independent astronomy, simulated hardware, 100,000 nights

The sandbox proves the scheduler's seams with a fake model, the lab's own two altitude routes and 1,000 Monte Carlo
nights. The Mac mini adds: real local models proposing plans (the validator still decides), two independent
astronomy cross-checks (astropy/astroplan numbers, Stellarium numbers and pictures), the INDI telescope and CCD
**simulators executing the plan**, and a 100,000-night weather run that sharpens every promise the scheduler makes.

| Script | `--here` (sandbox) | On the Mac |
|---|---|---|
| `agent_trials.py` | fake model: refused (1 zone, 3 airmass violations) | `--auto` / `--models`: one row per model |
| `astropy_check.py` | reference = the validator's LST route | astropy AltAz + astroplan (SKIP if not installed) |
| `stellarium_export.py` | prints the `.ssc` script | run it in Stellarium, then `--compare output.txt` |
| `indi_export.py` | prints the INDI command script (39 commands) | `--out night.sh` + `indiserver`, or `--execute` |
| `weather_overnight.py` | 2,000 nights, 2 workers | `--nights 100000`, all performance cores |

## Experiment 1 — a real model proposes tonight's plan
**Why.** The fake writes one deliberate mistake per class (a local time without a zone, windows ignored). A real model
makes its own: wrong target names, overlapping blocks, times off the 10-minute grid, numbers in the explanation that
are not facts. Every one must be refused by code; the plan is adopted only if it is valid **and** promises at least
the optimiser's expected value.
```zsh
cd integrated/labs/L600/05-observatory-scheduler/mac_mini
python3 agent_trials.py --here                         # fake: adopted optimiser, violation_kinds {zone 1, airmass 3}
LOCAL_MODEL_URL=http://localhost:11434/v1 python3 agent_trials.py --auto
LOCAL_MODEL=qwen2.5:7b python3 ../run_project.py --real   # the scorecard with a real model (M5 accepts either outcome)
```
**What you should see / how to read it.** Per model: `plan_lines`, `violations` and `violation_kinds`, `adopted`
(`optimiser` or `agent`), `explanation_published`, `invented_numbers`. Expect most real plans to be refused — read
*which* kind dominates: `zone` means the model ignores the ISO 8601 + zone rule (prompt wording), `airmass`/`darkness`
means it cannot do the sky maths (expected: that is the optimiser's job), `unknown` means invented targets. An
`adopted: agent` row is allowed only with `agent_ok: true` and `agent_value >= optimiser_value` (the script exits 1
otherwise). An unpublished explanation with `invented_numbers` is the number gate working.
**Measure:** per model: violations by kind, adopted, explanation published / invented numbers.
**Decides:** ADR-0004 (agent proposes, validator decides): if no model ever produces a valid plan, the agent's
role narrows to explaining (keep the proposal path only as a red-team input); if explanations keep failing the
number gate, keep the deterministic fallback text as the default.

## Experiment 2 — independent astronomy: astropy/astroplan numbers, Stellarium numbers and pictures
**Why.** Both lab routes (ephem.py's GMST and the validator's apparent sidereal time) use J2000 RA/Dec without
precession; KNOWN-GAPS puts that at up to ~0.36°. Vega's block reaches airmass 1.93 against the 2.0 limit, so a
few tenths of a degree can matter. astropy (BSD-3-Clause) and Stellarium (GPL-2.0) are independent implementations.
```zsh
python3 -m pip install astropy astroplan                 # astroplan 0.10.1 is pure Python (sdist)
python3 astropy_check.py                                 # astropy AltAz (pressure 0) and astroplan Observer.altaz
brew install --cask stellarium                           # or the installer from https://stellarium.org
python3 stellarium_export.py --out ~/kb-runs/05-plan.ssc
#   Stellarium: F12 (script console) -> load 05-plan.ssc -> run; it ends with "done" in output.txt
python3 stellarium_export.py --compare "$HOME/Library/Application Support/Stellarium/output.txt"
```
**What you should see / how to read it.** `astropy_check.py`: one line per reference with `max_dalt_deg`,
`max_dairmass` and `ff1_violations_by_reference`, then one line per block. With `--here` (LST route) the difference is
0.0019°; against astropy expect **tenths of a degree** — mostly precession of the J2000 coordinates to 2026, which our
routes skip — and the airmass difference largest for the lowest block (Vega). Stellarium's
`stellarium_geometric` is comparable to ours (no refraction); `max_refraction_deg` shows how much refraction would
lift the targets (it makes airmass *smaller*, so ignoring it is the safe side). Visually: each target is centred and
above the horizon at every sample; nothing sets mid-block. The output.txt path is Stellarium's user-data folder on
macOS — if it is elsewhere, the F12 console shows the script's output too.
**Measure:** max |Δaltitude| and max |Δairmass| vs astropy and vs Stellarium; any block whose reference airmass > 2.0.
**Decides:** FF1's margin and ADR-0001: if `ff1_violations_by_reference` is ever non-empty, either precess the
coordinates in sky.py (the exporter already does it for INDI) or tighten the scheduling limit to 2.0 minus the
measured Δairmass; if all differences stay well below the margin, record the measured bound in KNOWN-GAPS
instead of the estimate.

## Experiment 3 — the INDI simulators execute the night (INDI LGPL-2.1, KStars/Ekos GPL)
**Why.** A plan is only useful if a telescope can execute it. INDI's `indi_simulator_telescope` and
`indi_simulator_ccd` behave like a mount and a camera on the INDI protocol; the exporter drives them with INDI's own
command-line tools, so every step is a standard property you can watch. The new seam: the plan is J2000 but
`EQUATORIAL_EOD_COORD` is **epoch of date**, so the exporter precesses (IAU 1976, Meeus ch. 21; tested against
Meeus example 21.b). Sending J2000 as JNow points 0.09–0.37° off for these targets (`--no-precess` shows it).
```zsh
python3 indi_export.py --here | head -30                 # the commands (dry run, works anywhere)
python3 indi_export.py --out ~/kb-runs/05-night-indi.sh   # compressed: one 10 s exposure per block
# INDI on the Mac: build indi-core from source (official README; on macOS install to /usr/local), or use KStars
# (https://kstars.kde.org/download/, Ekos is its INDI client). Container route with Colima (see ../../../../mac-mini/COLIMA.md):
#   docker run --rm -it -v ~/kb-runs:/runs debian:trixie bash -c \
#     "apt-get update && apt-get install -y indi-bin python3 && (indiserver -v indi_simulator_telescope indi_simulator_ccd &) \
#      && sleep 5 && bash /runs/05-night-indi.sh"
indiserver -v indi_simulator_telescope indi_simulator_ccd &     # native route: port 7624
bash ~/kb-runs/05-night-indi.sh                          # or: python3 indi_export.py --execute
indi_getprop "Telescope Simulator.EQUATORIAL_EOD_COORD.*"      # where the mount points now
```
**What you should see / how to read it.** For each block: `ON_COORD_SET.TRACK=On`, a goto with RA in **hours** and
Dec in degrees (sent together: INDI needs RA and DEC atomically), a wait until the slew's state is Ok, one exposure
and a wait until the CCD's state is Ok; at the end `TELESCOPE_PARK.PARK=On` and "plan executed". In KStars connected
to the same server (Ekos → profile → remote host localhost:7624) the telescope cross-hair jumps target to target.
An `indi_eval` timeout means a step never reached Ok (Alert = 3): the script stops there (`set -e`), which is what a
robotic observatory must do. `--realtime` waits for each block's UTC start and fills the block with exposures — only
meaningful on the night itself; the compressed mode runs any day in minutes.
**Measure:** blocks executed / planned; slew time per block (timestamps from `indi_getprop -1 ..._TS` or the log);
pointing error = separation between the commanded JNow position and `EQUATORIAL_EOD_COORD` after the slew.
**Decides:** ADR-0001 (typed UTC at every seam) gains a coordinate-epoch rule: J2000 inside the scheduler, epoch
of date only at the INDI boundary, with the precession test as its seam test; slew times measured here replace
the scheduler's implicit zero-slew assumption (add a transition time per block if they exceed one 10-minute slot).

## Overnight — 100,000 nights of weather
```zsh
caffeinate -i python3 weather_overnight.py --nights 100000          # P_CLEAR_TO_CLOUD 0.02 / 0.04 / 0.08
```
For both plans: mean value ± 95 % CI, P(value = 0), quantiles, P(optimised < greedy), and every block's observed
completion against its promise p_complete with a z score — at 100,000 nights a |z| above ~3 would expose a real
mismatch between the Markov model and the promise formula (the scorecard's 1,000 nights cannot). The cloudier and
clearer rows show whether FF2 (optimised ≥ 1.15 × greedy) survives a site whose weather differs from the assumed
chain. In the `--here` run (2,000 nights) the ratio was 1.25 / 1.26 / 1.31 for P = 0.02 / 0.04 / 0.08 — read the
Mac's 100,000-night numbers the same way, with CIs ~7× narrower. **Decides:** ADR-0003 (Markov weather): if FF2
fails at a plausible cloudiness, the optimiser must plan with the site's fitted parameters, not the defaults.

## Validation
Here (Linux, Python 3.12.15, numpy 2.5.3): `python -m unittest discover -s tests` (16 tests: precession vs Meeus 21.b,
INDI command set and atomic RA;DEC, J2000-as-JNow seam, realtime filling, `bash -n` of the script, execute-without-INDI
skip, LST reference route, a forced FF1 violation, astropy-missing skip, Stellarium script + compare on synthetic
output, Monte Carlo chunks = one matrix, 1 vs 2 workers identical, fake-model trial). pendingMac: real models, astropy
and astroplan numbers, Stellarium output, INDI execution, 100,000 nights.
