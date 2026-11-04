# Workstation setup — Apple-silicon Mac mini + Windows 11 PC (all topics)

One canonical install recipe for every topic in this knowledge base. Each topic's setup lesson (lesson 1) links here and
uses exactly these commands. Ids below were checked against Homebrew / winget-pkgs during the L100–L200 review
(2026-10-28); re-check before a fresh install.

| Need | 🍎 Mac mini (zsh) | 🪟 Windows 11 (PowerShell) | Notes |
|---|---|---|---|
| Package manager | Homebrew (`brew`) | winget (built into Windows 11) | |
| Python 3.12 | `brew install python@3.12` | `winget install -e --id Python.Python.3.12` | Windows: use the `py -3.12` launcher. winget's newest 3.12 manifest is 3.12.10 (the last 3.12 release with a python.org Windows installer); Homebrew ships 3.12.16. Both are fine for the labs. |
| Virtual env | `python3.12 -m venv .venv && source .venv/bin/activate` | `py -3.12 -m venv .venv; .venv\Scripts\Activate.ps1` | Windows: if scripts are blocked, `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. |
| UTF-8 output | (default) | `$env:PYTHONUTF8 = "1"` | Prevents crashes when labs print box-drawing/Unicode. |
| Node.js 24 (only for simulator harness / diagram tools) | `brew install node@24` then add `$(brew --prefix node@24)/bin` to PATH | `winget install -e --id OpenJS.NodeJS.LTS --version 24.19.0` | Pinned: the LTS id moves to Node 26 once 26 becomes LTS. `node@24` is keg-only in Homebrew, hence the PATH step (Homebrew is at 24.22.1; any 24.x works). |
| Containers (optional labs) | `brew install podman` → `podman machine init` → `podman machine start` | `winget install -e --id RedHat.Podman` (needs WSL 2) → `podman machine init` → `podman machine start` | Versions differ: Homebrew `podman` is 6.1.4, winget `RedHat.Podman` is 5.8.3 (checked 2026-10-28). Podman Desktop / Colima / Rancher Desktop are fine alternatives; Docker Desktop is an equivalent with its own licence terms. |
| Local model runtime (Ollama) | `brew install ollama` → `brew services start ollama` | Installer `OllamaSetup.exe` from ollama.com/download/windows (or, in PowerShell, `irm https://ollama.com/install.ps1 \| iex`); it starts the server in the background. winget `Ollama.Ollama` lags behind (0.34.2 vs 0.40.x on 2026-10-28). | The server must be running before `ollama pull`. Mac alternative: the Ollama app (`brew install --cask ollama-app`) — open it once to start the server. Install either the formula or the cask, not both (both provide `ollama` in the Homebrew bin). |
| Default model | `ollama pull qwen2.5:1.5b` | same | ≈1 GB download; CPU-friendly. Bigger models: see ai-agents HARDWARE.md (by RAM). |
| Model endpoint (all topics) | `export LOCAL_MODEL_URL=http://localhost:11434/v1`<br>`export LOCAL_MODEL=qwen2.5:1.5b` | `$env:LOCAL_MODEL_URL="http://localhost:11434/v1"`<br>`$env:LOCAL_MODEL="qwen2.5:1.5b"` | Any OpenAI-compatible server works (llama.cpp `llama-server`, vLLM). |
| GPU | Metal is used automatically on Apple silicon | NVIDIA (CUDA) / AMD supported by Ollama; otherwise CPU | Check with `ollama ps` (shows GPU/CPU split). |

## Check your machine (both OSes)
```
python --version        # 3.12.x inside the venv
python -m unittest -h   # unittest available (labs use it; no pytest needed)
node --version          # v24.x (only if you need it)
ollama --version        # only for agent-assist sections
```

## Rules used by every lab
- Labs bind to `127.0.0.1` only. Expose a model or node to the other machine only on a trusted network, and never to the internet.
- Never paste real keys, passwords or tokens into a model prompt.
- Tests always run against the bundled stand-in model server; a real local model is optional.

## Sources
Retrieved 2026-10-28 to check the commands above:
- https://formulae.brew.sh/formula/python@3.12 — `brew install python@3.12`, stable 3.12.16, binary `python3.12`.
- https://formulae.brew.sh/formula/node@24 — `brew install node@24`, stable 24.22.1, keg-only.
- https://formulae.brew.sh/formula/podman — `brew install podman`, stable 6.1.4, Linux VM via `podman machine`.
- https://formulae.brew.sh/formula/ollama — `brew install ollama`, stable 0.40.11; service: `brew services start ollama`.
- https://formulae.brew.sh/cask/ollama-app — `brew install --cask ollama-app`, 0.40.12, macOS ≥ 14.
- https://github.com/microsoft/winget-pkgs/tree/master/manifests/p/Python/Python/3/12 — `Python.Python.3.12`, newest 3.12.10.
- https://github.com/microsoft/winget-pkgs/tree/master/manifests/o/OpenJS/NodeJS/LTS — `OpenJS.NodeJS.LTS` 24.19.0 present (newest).
- https://github.com/microsoft/winget-pkgs/tree/master/manifests/r/RedHat/Podman — `RedHat.Podman`, newest 5.8.3.
- https://github.com/microsoft/winget-pkgs/tree/master/manifests/o/Ollama/Ollama — `Ollama.Ollama`, newest 0.34.2.
- https://ollama.com/download/windows — Windows download and `irm https://ollama.com/install.ps1 | iex`.
- https://docs.ollama.com/windows — `OllamaSetup.exe`, no admin rights needed, server runs in the background on localhost:11434.
