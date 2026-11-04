# Hardware – Application Architecture (L100–L300)

Both machines run every lab: Python 3.12 standard library only, no GPU or simulator.

| Task | Mac mini (Apple silicon) | Windows 11 PC |
|---|---|---|
| Labs 1–11 (stdlib, unittest) | `brew install python@3.12` | `winget install -e --id Python.Python.3.12` |
| Shell | zsh: `export VAR=value` | PowerShell: `$env:VAR = "value"` |
| Node.js 24 (Maintenance LTS; lesson 6 mermaid-cli, lesson 9 AsyncAPI CLI; optional) | `brew install node@24` (keg-only) | `winget install -e --id OpenJS.NodeJS.LTS --version 24.19.0` |
| Containers (Structurizr, Keycloak 26.8.1, Testcontainers; optional) | Podman machine; images have linux/arm64 builds | Podman machine on WSL 2 |
| Real local model (optional) | Ollama on Metal | Ollama on CUDA, ROCm/Vulkan or CPU |

**RAM and disk.** Labs need no notable RAM. Optional extras: Structurizr image about 270 MB compressed,
a Podman VM disk, mermaid-cli's headless Chrome, `qwen2.5:1.5b` (986 MB). Keycloak and PostgreSQL
container sizes were not measured.

**GPU.** Only the optional local model uses one: Apple Metal, NVIDIA compute capability 5.0+ (driver 550+),
some AMD cards via ROCm v7 or Vulkan; otherwise CPU. The fake model server needs neither.

**Behaviour differences:** env-var names are case-insensitive on Windows only (lesson 5); lesson 3 uses
`Path.parts` for `\` paths; the busy-port error is `[Errno 48]` on macOS and `[WinError 10048]` on Windows;
test timings (lessons 11–16) differ per machine; Windows' coarser timer shifts sleeps and lags, but L300's counts,
drift lists, alerts and query counts are timing-independent. k6 (lessons 16, 21) runs natively on both machines;
L400 needs no GPU; OPA (lesson 19) is one binary on both.

**Status:** validated on Linux; macOS (arm64) and Windows are `expected` until the CI matrix runs. Container
jobs (Structurizr, Keycloak, Testcontainers, k6 image) and Pact run on Linux CI only.
