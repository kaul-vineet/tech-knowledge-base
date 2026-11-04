# Hardware – Mac mini + Windows PC (AI agents)

**What runs where.** Every lab and test runs on both machines with Python 3.12 + `requests` against the stdlib fake server – no GPU, no model download. The optional real model (Ollama 0.40.12 or llama.cpp `llama-server`) can run on either machine; one machine can serve the other over the LAN.

| | Mac mini (Apple silicon) | Windows 11 PC |
|---|---|---|
| Ollama install (canonical: `../../shared/WORKSTATION-SETUP.md`) | `brew install ollama` → `brew services start ollama` (alt: `brew install --cask ollama-app`, open it once) | `OllamaSetup.exe` from ollama.com/download (winget `Ollama.Ollama` lags) |
| GPU | Metal (M-series: CPU + GPU; Intel Macs: CPU only) | NVIDIA compute capability 5.0+ (driver 551.61+), AMD ROCm v7 or Vulkan; else CPU |
| Models | `~/.ollama/models` | `C:\Users\<you>\.ollama\models` |

`ollama ps` shows where a loaded model sits (`100% GPU`, `100% CPU`, or a split). No GPU in Docker Desktop on macOS – run Ollama natively. llama.cpp has Metal, CUDA, HIP (AMD) and Vulkan backends.

**Sizing by RAM (from official sources).**
- Q4_K_M download sizes (ollama.com): `qwen2.5:1.5b` 986 MB, `:7b` 4.7 GB, `:14b` 9.0 GB, `:32b` 20 GB – a lower bound for free RAM/VRAM.
- No official per-size RAM table: L400 #19 `sizing.py` estimates weights + KV; check `SIZE` in `ollama ps`.
- Memory grows with context: default context is 4096 tokens; required RAM scales with `OLLAMA_NUM_PARALLEL` × `OLLAMA_CONTEXT_LENGTH`.
- Disk: the Windows install needs ≥ 4 GB; models can reach tens to hundreds of GB – move them with `OLLAMA_MODELS`.

**LAN.** Ollama binds `127.0.0.1:11434`; set `OLLAMA_HOST=0.0.0.0:11434` on the host (macOS app: `launchctl setenv`; Windows: user environment variable) and restart it. Anyone on that network can then use the server: trusted LAN only, no port forwarding. `llama-server` supports `--api-key`.

**Simulator notes.** No hardware simulator: `fake_model_server.py` stands in for the model server.
