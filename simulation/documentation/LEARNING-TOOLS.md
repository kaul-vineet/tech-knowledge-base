# Learning tools: Simulation

Facts come from `../../shared/LEARNING-TOOLS-CATALOG.md` (checked 2026-10-28). Exercises: the `learningTools` field of each lesson.

| Tool | Role | Licence (OSI) | Mac mini install | Windows install | Lessons |
|---|---|---|---|---|---|
| NetLogo 7.0.4 | SEE | GPL-2.0-or-later (yes) | `brew install --cask netlogo` | Installer (bundles Java 17) | 5; 10 optional (BehaviorSpace) |
| JaamSim 2026-07 | BUILD WITHOUT CODE | Apache-2.0 (yes) | Partial: `java -jar JaamSim2026-07.jar` (Java 17+) | `JaamSim2026-07.exe` | 3, 8, 22 |
| Mesa 3.5.1 (SolaraViz) | SEE / CHECK | Apache-2.0 (yes) | `pip install mesa` (pin `>=3.5,<4`) | same | 5 |
| SimPy 4.1.2 | CHECK | MIT (yes) | `pip install simpy` | same | 3, 8, 11, 18, 22 |
| Scilab + Xcos 2027.0.0 | BUILD WITHOUT CODE | GPL-2.0 (yes) | Native ARM64 .dmg | 64-bit .exe | 4, 9, 15 |
| OpenModelica (OMEdit) 1.27.1 | BUILD WITHOUT CODE / CHECK | OSMC-PL 1.8 (yes) | Partial: Docker image + XQuartz | Official installer | 9, 15, 17 |
| Orange 3.40.0 | BUILD WITHOUT CODE / SEE | GPL-3.0-or-later (yes) | arm64 .dmg | `winget install --id UniversityofLjubljana.Orange` | 7, 10, 19 |
| KNIME 5.12 | BUILD WITHOUT CODE | GPL-3.0 + KNIME permissions (yes) | `brew install --cask knime` | Installer | 2, 20 |
| JupyterLab (+ JupyterLab Desktop) 4.6.4 | CHECK / SEE | BSD-3-Clause (yes) | `pip install jupyterlab` | same, or `winget install jupyterlab` | 10, 13, 16, 18, 20 |
| marimo 0.25.2 | CHECK / SEE | Apache-2.0 (yes) | `pip install marimo` | same | 2, 12, 14, 17, 19, 21; 9 optional |
| SALib 1.6.0 | CHECK / SEE | MIT (yes) | `pip install SALib` (Python >=3.10) | `pip install SALib` | 14, 21, 22 |
| Apache Superset 6.1.0 | SEE | Apache-2.0 (yes) | `pip install apache_superset` or Docker Compose | Partial: no official Windows support | 10 optional |
| Rattle 6.5 | SEE | GPL-3.0 (yes) | Partial: macOS zip + R | Installer + R | 7 optional |

Also verified, optional: Ciw 3.2.7 (MIT, M/M/c networks) and GAMA 2025.06.4 (GPL-3.0, agent-based GUI).

## How to use these tools

They complement the code labs: you still write the code. Then use a tool to **see** the concept (NetLogo, Mesa), **prototype** it without code (JaamSim, Xcos, OpenModelica), or **check** your result (SimPy, KNIME, Orange, JupyterLab, marimo, SALib). Each exercise names the lab value to compare with, e.g. 75.4% similar (lesson 5). `export_csv.py` in labs 2 and 10 writes the lab's seeded output as CSV for the no-code tools. The GUI exercises were not run here: each `expected` says "pending a manual run". In lesson JSON, `learningTools.name` is the exact catalog name; the version sits in the install fields.

## Not recommended / changed

- **AnyLogic PLE**: proprietary (capped free learning edition).
- **Insight Maker**: dropped. No official repo or licence found, and system dynamics is not in our lessons.
- **RapidMiner**: now proprietary; the AGPL repos are frozen at 9.7 / 9.10.
- **WEKA**: verified, but no fit here; use Orange.
- **FMPy 0.3.32 (GUI + CLI)**: not added. Its licence is BSD-2-Clause plus an extra clause (modifications only under the same licence), which is not OSI-approved. Lesson 15 already has two tools; FMPy stays only as the pinned library behind `fmpy_cosim.py`.
- **Changed:** SALib added to lesson 14; L400 lessons 17-22 reuse catalog tools only (2026-10-28). OpenModelica: no native macOS build since 1.16 (use the Windows PC). Mesa 4.0 alpha removes `batch_run`, `mesa.space` and `seed`: keep `mesa<4`.
