# Hardware: Mac mini (Apple silicon) and Windows 11 PC

**Both machines run every L100–L300 lab natively** with Python packages and local CPU simulators; no container, WSL or quantum hardware. Status is "expected" until the CI matrix (`ubuntu-latest`, `macos-latest` arm64, `windows-latest`) has run.

| | Mac mini (macOS, Apple silicon) | Windows 11 PC (x64) |
|---|---|---|
| Python | `brew install python@3.12` (bottle for Apple silicon) | `winget install -e --id Python.Python.3.12`, then the `py -3.12` launcher |
| Quantum SDKs | qiskit, cirq, qiskit-aer (L300 noise), scipy (L300) via pip; Mitiq and PennyLane (L300, own venv) are pure-Python wheels | same via pip (PyPI lists Windows) |
| Local model (optional, lessons 5, 8, 15) | Ollama (`brew install ollama` → `brew services start ollama`), GPU via Metal | Ollama (`OllamaSetup.exe` from ollama.com/download; winget `Ollama.Ollama` lags behind), NVIDIA CUDA, Vulkan or CPU |

**RAM and disk**
- Lab circuits have 1–10 qubits (19 physical on heavy-hex); L300 density matrices stay ≤ 4 qubits. Memory is negligible.
- Statevector memory doubles with every qubit (16 bytes per amplitude). 30 qubits need 16 GiB, so stay below about 28 qubits on a 16 GB machine.
- The optional `qwen2.5:1.5b` model is a 986 MB download.

**GPU**
- **Simulators: CPU only on both machines.** `qiskit-aer-gpu` is x86_64-Linux-only; Aer has no Metal backend.
- **Local model:** Ollama documents Metal acceleration on Apple silicon. On Windows it uses NVIDIA GPUs (compute capability 5.0+, driver 550+), Vulkan, or the CPU.

**Windows specifics**
- Set `$env:PYTHONUTF8 = "1"` before running labs. Otherwise piped output uses the locale code page, which cannot encode Qiskit's box-drawing characters.
- If venv activation is blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- Windows 11 on Arm is not covered: wheel availability for win-arm64 (qiskit, optional qiskit-aer) was not checked.
