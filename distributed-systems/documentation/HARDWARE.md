# Hardware — Mac mini (Apple silicon) + Windows 11 PC

**Everything runs on either machine.** All six labs are Python 3.12 stdlib only (no compiled packages, GPU or simulator) and finish in seconds.

| | Mac mini (macOS, arm64) | Windows 11 PC |
|---|---|---|
| Python | `brew install python@3.12` | `winget install -e --id Python.Python.3.12` (package was at 3.12.10 when checked) + `py -3.12` |
| Labs 1–6 | yes | yes (same commands in PowerShell; `curl.exe`, `$env:VAR=...`) |
| Optional containers (lab 1, `OPTIONAL-SETUP.md`) | Podman machine (canonical), Colima or Rancher Desktop (each runs a Linux VM) | Podman (`RedHat.Podman`, WSL 2), Podman Desktop or Rancher Desktop |
| Optional LAN step (lab 1, `OPTIONAL-SETUP.md`) | serves or calls | serves or calls (inbound firewall rule, Private profile) |
| Optional agent assist (lab 4) | Ollama, GPU via Metal | Ollama, NVIDIA (CUDA) / AMD GPU or CPU |

**RAM / disk.** Labs: under 1 GB RAM. Containers: the VM needs a few GB (Colima defaults to 2 CPUs, 2 GiB RAM, 100 GiB virtual disk; Podman Desktop asks for 6 GB RAM on Windows; Rancher Desktop recommends 8 GB) plus the `python:3.12.16-slim` image (not measured here). Agent assist: the default `qwen2.5:1.5b` is a small model; check its download size on the Ollama library page (not measured here).

**GPU.** Not needed; only the optional agent assist uses a model (tests use a fake server). Ollama documents Metal on Apple GPUs and NVIDIA (compute capability 5.0+, driver 550+), AMD ROCm and Vulkan on Windows; without a GPU it runs on the CPU (slower).

**Differences that matter** (lab 1/2 READMEs): error wording; Windows `SO_REUSEADDR` would share a port, so `node.py` binds exclusively; stopping a node is `TerminateProcess` on Windows. macOS/Windows status: expected until the CI matrix runs.
