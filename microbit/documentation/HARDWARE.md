# Hardware — Mac mini (Apple silicon) and Windows 11 PC

**No micro:bit board is needed.** Every L100 lab runs in the MicroPython micro:bit V2
simulator inside the browser (python.microbit.org). A board is optional
(the same `main.py` files flash to it).

| Task | Mac mini (macOS) | Windows 11 PC |
|---|---|---|
| Editor + simulator | Chrome or Edge (recommended); Safari 17+ / Firefox 128+ lack WebUSB only | Chrome or Edge (recommended); Firefox 128+ lacks WebUSB only |
| Flash a real board by WebUSB (optional) | Chrome or Edge only | Chrome or Edge only |
| Logic tests (`labs/run_tests.py`) | `python3` (Homebrew `python@3.12`) | `py -3.12` (`winget install -e --id Python.Python.3.12`) |
| Simulator harness (Playwright, optional) | Node 24 (`brew install node@24`); needs macOS 14+ | Node 24 (Maintenance LTS), pinned: `winget install -e --id OpenJS.NodeJS.LTS --version 24.19.0`; needs Windows 11 |
| Local agent (optional, lab 05) | Ollama (`brew install ollama` → `brew services start ollama`), Metal GPU on M-series | Ollama (`OllamaSetup.exe` from ollama.com/download; winget `Ollama.Ollama` lags behind), NVIDIA/AMD GPU or CPU |

**RAM / disk.** Browser + simulator: any machine that runs a modern browser. Python tests:
stdlib only, nothing else to install. Playwright downloads a Chromium
build (a few hundred MB; not measured here). Ollama needs at least 4 GB for the Windows
install and extra space per model; the suggested `qwen2.5:1.5b` is 986 MB. RAM for the
model was not measured (see KNOWN-GAPS).

**Simulator notes.** Sensors (temperature, light, accelerometer, gestures) are sliders and
buttons, not physics. The simulator is a V2; V2-only APIs (speaker, logo touch, SoundEffect)
would fail on a V1 board.

**GPU.** Not needed for any lab. Only the optional local model uses one: Apple-silicon
Macs via Metal; Windows via NVIDIA (driver 551.61+), AMD (ROCm v7 or Vulkan) or CPU.
WSL2 is not needed for anything in this topic.

Canonical install commands for both machines: `../../shared/WORKSTATION-SETUP.md`. Learning tools: `LEARNING-TOOLS.md`. L400 labs need only Python's standard library.
