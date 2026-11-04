# L600 Mac mini track — evidence log

Every tool fact used by the Mac mini track (integrated/mac-mini/ and each project's `mac_mini/` folder) is recorded here
with its primary source (official docs or the project's own repository) and its licence. Sections are append-only:
the shared section is written by the track owner, then one section per project (`## NN — slug`).
Rules: open source only; facts not verified against a primary source are marked "unverified"; nothing here is a Mac
measurement — results that need the Mac are listed as pendingMac in each project's `content/parts/NN.json`.

## Shared — integrated/mac-mini/ and .github/workflows/mac-mini.yml (agent A, retrieved 2026-11-02)

| Fact used | Source (primary) | Licence / version | Used in |
|---|---|---|---|
| Ollama binds 127.0.0.1:11434 by default; change the bind address with `OLLAMA_HOST`; macOS app: `launchctl setenv OLLAMA_HOST ...` then restart; default context 4096 (`OLLAMA_CONTEXT_LENGTH`); RAM scales with `OLLAMA_NUM_PARALLEL` × context; f16 KV cache by default; `ollama ps` PROCESSOR column (100% GPU / CPU / split); models kept 5 min (`OLLAMA_KEEP_ALIVE`); no GPU for Docker Desktop on macOS; ngrok/Cloudflare Tunnel recipes exist (we warn against them) | https://docs.ollama.com/faq | Ollama MIT (catalog) | MODEL-SERVER.md, mac_profile.py, COLIMA.md |
| `DELETE /api/delete` deletes a model (no auth shown in the API) | https://docs.ollama.com/api/delete | — | MODEL-SERVER.md security caveat |
| qwen2.5 Q4_K_M sizes: 1.5b 986 MB, 3b 1.9 GB, 7b 4.7 GB, 14b 9.0 GB, 32b 20 GB, 72b 47 GB | https://ollama.com/library/qwen2.5/tags | Qwen2.5 tags | mac_profile.py (3b, 32b added; others from ai-agents L400 #19 cost_model.py) |
| Qwen2.5-3B: 36 layers, 2 KV heads, hidden 2048 / 16 heads = 128; Qwen2.5-32B: 64 layers, 8 KV heads, 5120 / 40 = 128 | https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/raw/main/config.json , https://huggingface.co/Qwen/Qwen2.5-32B-Instruct/raw/main/config.json | — | mac_profile.py KV maths |
| launchd is the preferred timed-job mechanism; `StartCalendarInterval` dict (Hour, Minute); a job missed while **asleep** runs at wake, while **off** it waits for the next time | https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html | Apple docs (archive, 2016) | README nightly, plist template |
| `launchctl bootstrap gui/<uid> <plist>`, `bootout gui/<uid>/<label>`, `kickstart`, `print`; legacy load/unload | `man launchctl` (Apple); summarised at https://www.thrysoee.dk/launchctl/ (secondary, consistent with the man page) | — | install_nightly.sh |
| Self-hosted runners: recommended only for private repositories (forks can run code via PRs); `config.sh --url --token` (token expires after 1 h); macOS 11+ supported, ARM64 supported | https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners , https://docs.github.com/en/actions/reference/runners/self-hosted-runners | GitHub runner is open source (actions/runner) | RUNNER.md, workflow header |
| Default labels `self-hosted`, `linux/windows/macOS`, `x64/ARM/ARM64`; `runs-on: [self-hosted, ...]` matches all labels | https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/use-in-a-workflow | — | mac-mini.yml |
| Runner as a service: `./svc.sh install|start|status|stop|uninstall`; macOS uses a launchd plist template | https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application | — | RUNNER.md |
| Queued job with no matching runner fails after 24 h; `--disableupdate` → update within 30 days | runner reference (above) | — | RUNNER.md, `if: vars.MAC_MINI_RUNNER == 'true'` |
| Colima: MIT; `brew install colima`, MacPorts `sudo port install colima`, Nix `nix-env -iA nixpkgs.colima`; default VM 2 CPU / 2 GiB / 100 GiB; `colima start --cpu --memory` | https://github.com/abiosoft/colima | MIT | COLIMA.md |
| macOS firewall: System Settings → Network → Firewall → Options (allow an app, block all incoming, stealth mode) | https://support.apple.com/guide/mac-help/change-firewall-settings-on-mac-mh11783/mac | — | MODEL-SERVER.md |

Computed, not quoted: every RAM/model/qubit number in `integrated/mac-mini/README.md` is the output of
`scripts/mac_profile.py --table 16 24 32 64 --markdown` (assumptions printed: 6 GB reserved, 10 % headroom, 2 statevector
copies, ctx 4096). Unverified / pendingMac: `sysctl hw.perflevel0.physicalcpu` (performance cores) was not run on a Mac;
the `./svc.sh` macOS service commands are taken from the docs page's Mac tab, not executed; `caffeinate -i` per its man page.
Ran here: `python -m unittest discover -s integrated/mac-mini/tests` (9 tests OK: profile maths, nightly.sh against fake labs
incl. a failure lab that wrongly passes and 30-day retention, plist rendered and parsed with plistlib).

## 03 — agent-driven-simulation (agent A, retrieved 2026-11-02)

| Fact used | Source (primary) | Licence / version | Used in |
|---|---|---|---|
| Ollama serves an OpenAI-compatible `/v1/chat/completions` with tools; default endpoint `http://localhost:11434/v1` | `shared/WORKSTATION-SETUP.md` (verified there against ollama.com) and https://docs.ollama.com/faq | MIT | compare_models.py, `--real-model` |
| Model sizes for the comparison come from `mac_profile.py` (Qwen2.5 tags and config.json, shared section above) | computed | — | `--auto`, README, macMini |
| mlx-lm LoRA: `pip install "mlx-lm[train]"`; `mlx_lm.lora --model <path or HF repo> --train --data <dir> --iters 600`; `train.jsonl` required, `valid.jsonl` optional; jsonl supports chat, tools, completions and text formats; Qwen2 family supported; `mlx_lm.fuse` fuses adapters | https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md | MIT (https://raw.githubusercontent.com/ml-explore/mlx-lm/main/LICENSE, © Apple) | export_rejections.py, README optional experiment |
| Saltelli/Jansen Sobol' design costs n(d + 2) runs; Morris r(d + 1) | `simulation/labs/L300/14-global-sensitivity/sensitivity.py` and `pipeline._screening` (read in place) | — | Experiment 3, Q1, Q7 |
| multiprocessing "spawn" start method: children re-import the main module; used on every OS so the sandbox matches macOS | Python docs, multiprocessing "Contexts and start methods" (https://docs.python.org/3/library/multiprocessing.html) | PSF | overnight_sweep.py |
| `caffeinate -i <command>` prevents idle sleep while the command runs | `man caffeinate` (macOS) — not executed here | — | README overnight commands |

Ran here (Linux, Python 3.12.15, numpy 2.5.3): `mac_mini/tests` 7 tests OK; `compare_models.py --here` (fake: contract_rejected 1,
budget_rejected 1, claims_dropped 1, budget_spent 270,000, 7/7 published numbers traced); `overnight_sweep.py --here` with 2 and
1 workers (identical `values_sha256_16` 27b33eda727fc8ad and `st_sha256_16` 8ede56e62fdbe4e8); `export_rejections.py --here`
(1 contract rejection; the budget refusal skipped); `checks_03_mac.py` OK. Not run (pendingMac): any real model, mlx-lm, the
full-size overnight runs. The mlx-lm chat field layout (`{"messages": [...]}`) follows the LORA.md "chat" example; the
page body was read via search snippets, not a full fetch.

## 05 — observatory-scheduler (agent A, retrieved 2026-11-02)

| Fact used | Source (primary) | Licence / version | Used in |
|---|---|---|---|
| INDI standard properties: `CONNECTION` (CONNECT/DISCONNECT), `GEOGRAPHIC_COORD` (LAT, LONG 0..360 +E, ELEV m), `EQUATORIAL_COORD` (J2000) vs `EQUATORIAL_EOD_COORD` (JNow, RA hours, DEC degrees), `ON_COORD_SET` (SLEW/TRACK/SYNC; prepares the next *_COORD action), `TELESCOPE_PARK` (PARK/UNPARK), `CCD_EXPOSURE.CCD_EXPOSURE_VALUE` (seconds) | https://github.com/indilib/docs/blob/master/drivers/standard-properties.md (= https://docs.indilib.org/drivers/standard-properties/) | INDI docs | indi_export.py |
| `indi_setprop [options] device.property.e1[;e2...]=v1[;v2...]` (atomic multi-element; RA/DEC must be sent together; quote names with spaces); `indi_getprop` (`-1` value only, `_STATE`/`_TS` attributes); `indi_eval -t secs -w expr` (wait until true; `_STATE` Idle/Ok/Busy/Alert = 0/1/2/3; switch On/Off = 1/0); default port 7624 | https://docs.indilib.org/scripting/ | INDI docs | indi_export.py, README |
| `indiserver` runs drivers, e.g. `indi_simulator_telescope`, `indi_simulator_ccd`; device names "Telescope Simulator", "CCD Simulator" | https://docs.indilib.org/indiserver/ ; https://docs.indilib.org/clients/ (DRIVER_INFO of Telescope Simulator); https://github.com/indilib/pyindi-client/blob/master/examples/tuto-scripts/tuto-ccd.py ("CCD Simulator") | — | indi_export.py |
| INDI core licence LGPL-2.1 (repo also ships COPYING.GPL, COPYING.BSD); build with cmake; macOS: install prefix /usr/local | https://github.com/indilib/indi (LICENSE, README) | LGPL-2.1, v2.2.6 in repo | macMini needs |
| Debian `indi-bin` 1.9.9+dfsg-3 (trixie, arm64 available): INDI server, drivers and tools | https://packages.debian.org/stable/indi-bin | LGPL/GPL (Debian copyright) | container route |
| KStars 3.8.5 (macOS download), Ekos = its INDI client; licence files include GPL-2.0-or-later | https://kstars.kde.org/download/ ; https://github.com/KDE/kstars/tree/master/LICENSES ; FSF directory (GPLv2 or later) | GPL-2.0-or-later | macMini needs (optional, visual) |
| Stellarium scripting: `core.setObserverLocation(lon, lat, alt, duration, name)`, `core.setDate(dateStr, spec="utc")`, `core.setTimeRate`, `core.selectObjectByName(name, pointer)`, `core.moveToSelectedObject`, `core.getObjectInfo(name)` keys `altitude`, `altitude-geometric`; `core.output` / `resetOutput` write output.txt; F12 script console | https://stellarium.org/doc/26.0/classStelMainScriptAPI.html ; https://stellarium.org/doc/26.0/scripting.html | Stellarium GPL-2.0 (catalog) | stellarium_export.py |
| astropy AltAz frame with `pressure=0` (no refraction); astroplan `Observer.altaz` | astronomy L300 #12 `plan_astroplan.py` (same API, pending-ci there); astropy BSD-3-Clause 8.0.2, astroplan BSD-3 0.10.1 (astronomy/documentation, PyPI) | BSD-3-Clause | astropy_check.py |
| Rigorous precession IAU 1976 (zeta, z, theta polynomials; Meeus eq. 21.2-21.4), checked against Meeus Example 21.b (theta Persei → α 41.547214°, δ 49.348483°) | Meeus, *Astronomical Algorithms*, 2nd ed., ch. 21 (test: `test_meeus_example_21b`) | — | indi_export.precess |

Ran here: `mac_mini/tests` 16 tests OK; `agent_trials.py --here`, `indi_export.py --here` (39 commands, `bash -n` OK), `astropy_check.py`
(SKIP, astropy missing) and `--here` (LST route, max 0.0019°), `stellarium_export.py --here`, `weather_overnight.py --here` (2,000
nights, 2 spawn workers); `checks_05_mac.py` OK. Unverified / pendingMac: the INDI tools and simulators were not run (no INDI here);
the "Busy before Ok" race the exporter guards against is a design precaution, not an observed failure; the Stellarium output.txt
location on macOS (`~/Library/Application Support/Stellarium`) and Ekos remote-server profile steps were not checked against
current docs; whether Debian's indi-bin 1.9.9 ships `indi_eval` was inferred from the package description ("other INDI tools").

## 08 — secure-agent-tools (agent A, retrieved 2026-11-02)

| Fact used | Source (primary) | Licence / version | Used in |
|---|---|---|---|
| Ollama binds 127.0.0.1:11434 by default; `OLLAMA_HOST` changes the bind address (LAN exposure is opt-in on the server side too) | https://docs.ollama.com/faq | MIT | model_endpoint.py rationale, Experiment 2 |
| The Ollama API includes model deletion (`DELETE /api/delete`) and shows no authentication | https://docs.ollama.com/api/delete | — | MODEL-SERVER.md caveat referenced by 08 |
| `ipaddress.ip_address(h).is_loopback`: True for 127.0.0.0/8 and ::1; 0.0.0.0 is the unspecified address (is_loopback False) | Python docs, https://docs.python.org/3/library/ipaddress.html (behaviour executed in checks_08_mac.py Q4) | PSF | model_endpoint.py, Q4 |
| Wilson score interval for a binomial proportion (centre (p + z²/2n)/(1 + z²/n)) | Wilson (1927), JASA 22:209-212; formula as in NIST/SEMATECH e-Handbook §7.2.4.1 | — | injection_eval.wilson, Q1 |
| Corpus phrasings come from ai-agents L300 #16 `attacks.json`; the fake model obeys only the `call <tool> with {json}` form (shared fake rule 1b) | `08-secure-agent-tools/corpus.py`, `kb/shared/local_agent/fake_model_server.py` (read in place) | — | why the fake obeys 24/40 |

Hooks (backward compatible, delete-then-write): `adapters.py` — `HttpModel(base_url, model=None, timeout=None, allow_remote=None)`
with module defaults `DEFAULT_MODEL="fake-model"`, `DEFAULT_TIMEOUT=30`, `ALLOW_REMOTE=False` and a `check_model_url` call;
`run_project.py` — `--real-model`, `--allow-remote-model`, and a `"model"` key in the final card only with `--real-model`.
New file: `model_endpoint.py`. Ran here after the hooks: `python run_project.py` 13/13 PASS, `--inject naive-host` 4/13 exit 1,
`python -m unittest discover -s tests` 44 tests OK (all unchanged); `mac_mini/tests` 9 tests OK (incl. `--real-model` pointed at the
fake on loopback = 13/13); `injection_eval.py --here --naive` (24/40 obeyed, 0 executed, 0 effects; naive 24 executed, 16 effects);
`checks_08_mac.py` OK. pendingMac: every real-model obey rate, the LAN run from Windows, the 1,000-item overnight run.


## 01 — pq-replicated-messaging (agent B, retrieved 2026-11-02)

| Fact used | Source (primary) | Licence / version | Used in |
|---|---|---|---|
| `MLKEM768PrivateKey.generate()`, `public_key().encapsulate()` → (32-byte secret, 1,088-byte ciphertext), `decapsulate`; 1,184-byte public key; ML-KEM-1024: 1,568-byte key and ciphertext; added in cryptography 47.0.0; raises `UnsupportedAlgorithm` if the backend lacks it | https://cryptography.io/en/latest/hazmat/primitives/asymmetric/mlkem/ (also executed here with 50.0.2) | Apache-2.0 OR BSD-3-Clause (installed package metadata, as recorded by the cryptography topic) | bench_crypto.py |
| Random 96-bit GCM IVs: at most 2^32 invocations per key | NIST SP 800-38D §8.3, as already cited by `pqmsg.MAX_MSGS_PER_EPOCH` (not re-fetched) | — | bench_crypto.budgets, Q2 |
| `Popen.kill()` sends SIGKILL on POSIX and calls `TerminateProcess` on Windows; `os.fsync` forces the file to disk | Python docs: subprocess (Popen.kill), os (fsync) — standard library behaviour, not re-fetched | PSF | multiproc.py, replica.py |
| Colima: MIT; Apple silicon supported; `brew install colima`, MacPorts `sudo port install colima`, Nix, Mise; Docker runtime needs the docker client (`brew install docker`); `colima start --runtime containerd` + `colima nerdctl` works without it; `colima start --cpu N --memory N` | https://github.com/abiosoft/colima (README) | MIT | README experiment 3, macMini tools |
| docker CLI licensed Apache-2.0 | https://github.com/docker/cli (README "Licensing") | Apache-2.0 | macMini tools |
| `tc qdisc add dev <if> root netem delay 100ms 10ms`, `loss 0.3%`, seeds, needs a real qdisc on the interface (NET_ADMIN in a container) | https://man7.org/linux/man-pages/man8/tc-netem.8.html | iproute2 | README experiment 3 |

Ran here (Linux, Python 3.12.15, cryptography 50.0.2): `bench_crypto.py --here` (welcome 165.61 µs, seal 24.28 µs → 603 members
in 100 ms, 1.2 days to 2^32 at one core — sandbox numbers); `multiproc.py --here` random (300 msgs, 4 kills, 301 ciphertexts on the
wire, 0 reused, F2 pass, exit 0), `--nonce leader-counter` (62 reused, first `000000000000000000000001`, exit 1), `--nonce derived`
(0 reused, exit 0); `mac_mini/tests` 7 tests OK; `checks_01_mac.py` OK. Unverified / pendingMac: any Apple-silicon timing; fsync
cost on APFS; the Colima + netem command (written from the Colima README and tc-netem(8), not executed: no containers here);
`python:3.12-slim` lacking `tc` until `iproute2` is installed is from Debian slim image practice, not checked.

## 02 — quantum-safe-migration (agent B, retrieved 2026-11-02)

| Fact used | Source (primary) | Licence / version | Used in |
|---|---|---|---|
| qiskit 2.6.1 (2026-10-22): Apache-2.0, Python ≥ 3.10, wheel `qiskit-2.6.1-cp310-abi3-macosx_11_0_arm64.whl` published (and win_amd64) | https://pypi.org/project/qiskit/ (release files) | Apache-2.0 | qiskit_crosscheck.py, macMini |
| qiskit-aer 0.18.2 (2026-10-26): Apache-2.0, Python ≥ 3.11, classifiers MacOS / Windows / Linux, 36 files with provenance; "reduced maintenance mode"; GPU package x86_64 Linux only | https://pypi.org/project/qiskit-aer/ | Apache-2.0 | qiskit_crosscheck.py; the arm64 wheel file name was NOT visible → the `pip install --dry-run --only-binary=:all:` step checks it on the Mac |
| Pins qiskit 2.6.1 / qiskit-aer 0.18.2 | `quantum-computing/documentation/README.md` (stack line) | — | all commands |
| `AerSimulator(method="statevector", seed_simulator=…)`; statevector of n qubits = 2^n complex values of 16 bytes; `max_memory_mb`; precision "double" by default | https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html (0.18.2) | — | qiskit_crosscheck.py |
| ML-KEM: only 768 and 1024 classes in cryptography (no MLKEM512*) | https://cryptography.io/en/latest/hazmat/primitives/asymmetric/mlkem/ + `hasattr(mlkem, "MLKEM512PrivateKey")` False on 50.0.2 | — | pq_bench.py, macMini |
| ML-DSA-44/65/87: signatures 2,420 / 3,309 / 4,627 B, public keys 1,312 / 1,952 / 2,592 B, optional context ≤ 255 B, added 47.0.0 | https://cryptography.io/en/latest/hazmat/primitives/asymmetric/mldsa/ (sizes also read from the library in pq_bench.py) | — | pq_bench.py, Q4 |
| ML-DSA signing repeats until a candidate passes its bounds (rejection sampling), so signing time varies | FIPS 204 (signing algorithm loop) — from the standard's structure, not re-fetched | — | Q8 |

Ran here: `pq_bench.py --here`, `order_wall.py --here` (N = 15, 21, 35; 121.9 B/amplitude measured with tracemalloc; predictions
16 GB → N = 143, 24/32/64 GB → N = 323), `qiskit_crosscheck.py --here` (skipped, exit 0; exit 2 without `--here`); sampling-only TVD
for N = 35 recomputed in `checks_02_mac.py` (≈0.026 at 20k shots, < 0.016 at 100k → threshold 0.025); `mac_mini/tests` 12 OK (1 skipped);
`checks_02_mac.py` OK. pendingMac: every Qiskit/Aer result, Apple-silicon timings, N > 35.

## 04 — microbit-sensor-fleet (agent B, retrieved 2026-11-02)

| Fact used | Source (primary) | Licence / version | Used in |
|---|---|---|---|
| MicroPython micro:bit V2 simulator: MIT; embed URL `https://python-simulator.usermbit.org/v/0.1/simulator.html`; messages `flash`, `serial_output`, `radio_output` (bytes), `radio_input` ("assumed to be sent to the currently configured radio group"); "embedding API and URLs are not yet stable" | https://github.com/microbit-foundation/micropython-microbit-v2-simulator (README) | MIT | sim/fleet-node.spec.js via microbit/harness |
| The topic's harness (host.html two-board radio bridge, serve.js on 127.0.0.1, sim-helpers.js, `@playwright/test` 1.64.1) | `microbit/harness/README.md`, `package.json` (read in place, reused by path, not copied) | MIT (harness package.json) | sim/ |
| Playwright: Apache-2.0; `npm i -D @playwright/test`, `npx playwright install`, `npx playwright test`; Chromium/WebKit/Firefox on macOS | https://github.com/microsoft/playwright (README) | Apache-2.0 | sim/package.json, macMini tools |
| Renode in the microbit topic is used only for the Rust interrupt-race lab (L300 #16) | `microbit/labs/L300/16-interrupt-race/renode/`, `microbit/documentation/CONCEPTS-PRIMER.md` (read in place) | — | README (why not Renode) |
| Radio sender truncates to the configured `length` (default 32, max 251) | `microbit/labs/sim_stub/radio.py` header (from MicroPython modradio source, per the topic) | — | test 3 expectation |
| Python `bytes()` accepts integers 0-255 only (ValueError otherwise) | executed here (`soak.dev_id_limit`, checks_04_mac Q5) | PSF | soak.py, Q3/Q5 |

Ran here: `make_sim_programs.py --here` (programs on two CPython-stub boards: 30/30 acked; oversize 102 B → 32 B on air);
`soak.py --here` (20 boards × 12 h: 14,400 sampled, 0 lost, life_h_min 2,419.7 h; device id limit 255; seq wrap 45.5 days);
`node --check` on the Playwright files; `mac_mini/tests` 6 OK; `checks_04_mac.py` OK. pendingMac: the Playwright run in the
simulator (needs internet), the 250- and 500-board week soaks, memory per board-hour at fleet size. Unverified: whether the
simulator delivers radio between iframes within 50 ms (test 2 records it), and how its radio treats an oversize frame (test 3).

## 06 — signed-science-data (agent B, retrieved 2026-11-02)

| Fact used | Source (primary) | Licence / version | Used in |
|---|---|---|---|
| `http.server` "is not recommended for production. It only implements basic security checks."; `ThreadingHTTPServer` (3.7+); `--bind 127.0.0.1` binds to localhost only | https://docs.python.org/3/library/http.server.html | PSF | mirror_server.py, README limits |
| RFC 8785 sample input/output (numbers 333333333.3333333, 1e+30, 4.5, 0.002, 1e-27; escaped string) and the list of implementations (JavaScript: npm `canonicalize`) | https://github.com/cyberphone/json-canonicalization (README, Apache-2.0) | Apache-2.0 | jcs_crosscheck.py (sample reproduced by canonical.dumps) |
| npm `canonicalize`: Apache-2.0, "canonicalization of JSON as defined by RFC8785", `import canonicalize from 'canonicalize'`, package.json 5.1.0, CommonJS via `require('canonicalize').default` (Node ≥ 22.12) | https://github.com/erdtman/canonicalize (README) | Apache-2.0, 5.1.0 | jcs_node/package.json, jcs_check.mjs |
| JCS = JSON.stringify serialisation of primitives + properties sorted by UTF-16 code units (ECMAScript default sort) | RFC 8785 §3.2 (as implemented in `canonical.py`, whose evidence is in 06-evidence.md) | — | jcs_check.mjs builtin |
| RFC 9162 tree: split at the largest power of two < n; inclusion proof ≤ ceil(log2 n) hashes | `merkle.py` (RFC 9162 §2.1, cited there); bottom-up and streaming builds checked against `merkle.mth` / `inclusion_proof` in tests | — | scale_bench.py |
| Node.js 24 install | `shared/WORKSTATION-SETUP.md` (verified there) | MIT | macMini tools |

Ran here (Node v24.7.0 present in the sandbox): `http_world.py --here` (4 mirror processes; rounds 2/2/2/3; H1-H3 pass) and
`--inject float-format` (H1/H2 fail; 4,839,263 vs 174,951 bytes moved); `scale_bench.py --here` (10,000 rows, root
8923a7bff6a28e32 = merkle.mth = streaming root; 100 proofs valid); `jcs_crosscheck.py --here` (built-in recipe 8/8 identical; 6/8
vectors differ under platform_dumps); `mac_mini/tests` 7 OK; `checks_06_mac.py` OK. pendingMac: the npm package (no network
here), 8 mirrors × 40 releases, 10^5–10^7 rows (RSS per row is only reliable from 10^5 rows).

## 07 — quantum-job-service (agent B, retrieved 2026-11-02)

| Fact used | Source (primary) | Licence / version | Used in |
|---|---|---|---|
| AerSimulator methods `statevector`, `density_matrix`; `max_memory_mb` ("If quantum states need more, an error is thrown"); 16 bytes per amplitude; `seed_simulator` run option; `precision` default "double" | https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html (0.18.2) | Apache-2.0 | aer_backend.py, qubit_sweep.py |
| `NoiseModel.add_all_qubit_quantum_error`, `add_all_qubit_readout_error`, `depolarizing_error(p, n)` = (1 - p)ρ + p I/2^n, `amplitude_damping_error`, `ReadoutError` rows = true outcome; `QuantumError.compose` applies self first | Qiskit Aer API reference (qiskit_aer.noise) — signatures from the Aer docs family, NOT fetched page by page here; the agreement check `exact_tvd_vs_numpy ≤ 1e-6` on the Mac is what verifies the mapping | Apache-2.0 | aer_backend.noise_model (pendingMac) |
| Depolarising convention of the numpy model: weight 1 - p + p/4^k on identity = (1 - p)ρ + p I/2^k | `quantum-computing/labs/_shared/qsim/density.py` `depolarizing_kraus` (read in place) | — | aer_backend docstring |
| `numpy.random.SeedSequence(list).generate_state(1)` is deterministic in its entropy | NumPy docs (SeedSequence) — behaviour executed in checks_07_mac.py Q6 | BSD-3-Clause | aer_backend.execute |
| multiprocessing "spawn" is the macOS default start method | Python docs, multiprocessing (as recorded in section 03) | PSF | overnight_load.py, soak.py |

Ran here: `aer_backend.py --here` (conformance true on the numpy backend; Aer skipped; exit 2 without `--here`), `qubit_sweep.py
--here` (walls 29/30/30/31 statevector and 14/15/15/15 density matrix for 16/24/32/64 GB from mac_profile budgets), `overnight_load.py
--here` (seed 7 p95 18.38 s pass, seed 8 p95 170.49 s FAIL with 3 backends, 19.2 s pass with 6; 0 contract violations); `mac_mini/tests`
7 OK (1 skipped); `checks_07_mac.py` OK. pendingMac: every Aer result (adapter agreement, Aer sweeps), the 40-seed overnight run.
