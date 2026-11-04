# Hardware – Applied Cryptography L100-L300

Target machines: an Apple-silicon **Mac mini** (macOS, zsh) and a **Windows 11 PC** (PowerShell). No special hardware or simulator is needed; containers are optional (L300 lesson 12).

| Task | Mac mini | Windows PC |
|---|---|---|
| Labs 1-6 (Python 3.12 + `cryptography==50.0.2`) | yes, arm64 wheel | yes, x64 wheel |
| Labs 7-11, 12-16 | yes | yes |
| L300 optional | `brew install podman minisign` (OpenBao container, minisign) | `winget install -e --id RedHat.Podman` (WSL 2), `winget install -e --id jedisct1.minisign` |
| L200 optional CLIs | `brew install age openssl@3` | `winget install --id FiloSottile.age` |
| Python install | `brew install python@3.12` | `winget install -e --id Python.Python.3.12` |
| OpenSSL CLI (optional) | `/usr/bin/openssl` is LibreSSL; `brew install openssl@3` for OpenSSL | none built in; `winget install -e --id ShiningLight.OpenSSL.Light`, or Git Bash's copy |
| OS SHA-256 tool (lab 2) | `shasum -a 256` | `certutil -hashfile` / `Get-FileHash` |
| Agent assist (labs 6, 9, 16, optional) | Ollama (`brew install ollama` + `brew services start ollama`), Metal GPU | Ollama (`OllamaSetup.exe` from ollama.com/download; winget lags), NVIDIA CUDA, AMD ROCm, Vulkan or CPU |

The `cryptography` wheels bundle OpenSSL; the labs never use the system copy.

**RAM / disk.** Labs: under 100 MB for the venv (OpenBao image: about 76 MB). Lab 5 (Argon2id) uses about 19 MiB RAM per hash; benchmark your own timings. Agent assist with `qwen2.5:1.5b`: 986 MB download, about 2 GB free RAM (estimate); the fake server needs nothing.

**GPU.** Only the optional local model uses one: Metal on Apple silicon; NVIDIA (compute capability 5.0+), AMD ROCm, Vulkan or CPU on Windows (Ollama docs).

Status: Mac and Windows paths are **expected** until CI confirms them.

Installs: `../../shared/WORKSTATION-SETUP.md`; tools: `LEARNING-TOOLS.md`.
