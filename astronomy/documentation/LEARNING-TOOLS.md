# Learning tools: Astronomy & Astrophysics

Checked 2026-10-29 against official sites, Homebrew, winget-pkgs and GitHub (URLs in `LEARNING-TOOLS-DATA.json` and VERIFIED-RESOURCES.md). These tools are not in `../../shared/learning-tools.json` yet; `LEARNING-TOOLS-DATA.json` uses the same schema so they can be merged.

| Tool | Role | Licence (OSI) | Mac mini install | Windows install | Lessons |
|---|---|---|---|---|---|
| Stellarium 26.3 | SEE / CHECK | GPL-2.0 (yes)¹ | `brew install --cask stellarium` | `winget install -e --id Stellarium.Stellarium` or the stellarium.org installer | 1-6, 11, 12, 14, 22 |
| TOPCAT 4.10-8 (+ STILTS) | CHECK / SEE | GPL, some LGPL (yes) | `brew install --cask topcat` (also installs `stilts`) | `java -jar topcat-full.jar` (Java 8+) | 7, 10, 19, 21, 22 |
| SAOImage DS9 8.8 | INSPECT | GPL-3.0-only (yes)¹ | Aqua .dmg from the DS9 download page | Installer from the DS9 download page | 8, 13 |
| AstroImageJ 6.0.11.00 | CHECK | GPL-3.0 (yes)¹ | `AstroImageJ-6.0.11.00-mac-aarch64.pkg` (GitHub releases) | `AstroImageJ-6.0.11.00-windows-x64.msi` | 9 |
| Siril 1.4.5 | CHECK | GPL-3.0 (yes) | DMG from siril.org/download (macOS 13+) | Installer from siril.org/download | 13 |
| astrometry.net 0.97 (`solve-field`) | CHECK | BSD-3 own code; whole work GPL-3.0+ (yes)¹ | `brew install astrometry-net` + index files | WSL2 only: `sudo apt install astrometry.net` | 14 |
| JupyterLab 4.6.4 (+ Desktop) | CHECK | BSD-3-Clause (yes) | `pip install jupyterlab` | `pip install jupyterlab` / `winget install jupyterlab` | 15, 17, 18, 20, 22 |

¹ Licence sources disagree in wording: Stellarium's GitHub repo shows GPL-2.0 (the first pass recorded GPL-2.0-or-later); DS9 is GPL-3.0-only on its Zenodo record and "licensed in part" in the repo README; astrometry.net is BSD-3 on Homebrew but GPL-3.0-or-later as a whole in its README; AstroImageJ's licence file was not re-read (KNOWN-GAPS).

## How to use these tools
They complement the code labs; you still write the code. Use a tool to **see** a concept or to **check** your result against independent software:
- Stellarium shows the sky your altitude table describes (Deneb at 56.27° from Gurgaon, lesson 2), the night you plan (lesson 12), RA lines bunching near Cassiopeia (lesson 14) and why π Men never rises at Gurgaon (capstone).
- TOPCAT pair-matches catalogues (1842 vs 1817 pairs, lesson 7), runs the lesson 19 ADQL cone on the Gaia TAP service, and validates the lesson 21 VOTable with `stilts votlint`.
- DS9 and Siril read the lesson 13 master flat (min 0.8527, max 1.0792 shipped); AstroImageJ repeats lesson 9's aperture photometry (20,006 e⁻).
- `solve-field` plate-solves a real image the way lesson 14 solves a synthetic one.
- JupyterLab re-runs the L300/L400 code step by step and plots posteriors, throughput, difference images and rotation curves.

`--export` options (lessons 7, 9, 10) and the files the labs write (`star_field.fits`, `master_flat.fits`, `release/catalogue.vot`, capstone `data/*.csv`) are the inputs. Each exercise names the lab value to compare with. The GUI exercises were not run here: each `expected` says "pending a manual run". Planetariums show apparent places of date with refraction; turn the atmosphere off and expect differences of a few tenths of a degree from the J2000 labs (lesson 2 explains why).

## Not recommended / changed
- **SAOImage DS9 via Homebrew:** the `saoimageds9` cask fails the Gatekeeper check and has been disabled since 2026-09-01. Use the Aqua .dmg.
- **astrometry.net on Windows:** no native build; use WSL2 and download index files that match your image scale.
- **Celestia:** the Homebrew cask is at 1.6.4, an old stable release; not used.
- **KStars, Aladin Desktop/Lite, JS9, Gnuastro:** not verified in either pass. They are credible open-source candidates.
- **Gaia archive, ESASky, NASA Exoplanet Archive, MAST:** data services, not learning tools. Their data terms matter: Gaia data are CC BY-NC 3.0 IGO (ESA's licence page) and most MAST data are public domain with a requested acknowledgement. Lesson 21 turns this into a release gate.
