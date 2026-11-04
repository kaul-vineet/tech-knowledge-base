# 01 – Set up your environment

Two interchangeable back ends, same chat-completions URL shape (`<base>/v1/chat/completions`):

| Back end | Base URL | Model name | Use for |
|---|---|---|---|
| `fake_model_server.py` (this folder, stdlib only) | `http://127.0.0.1:8765/v1` | `fake-model` | tests, CI, learners without a model |
| Ollama 0.40.12 + `qwen2.5:1.5b` (986 MB) on the Mac mini or Windows PC | `http://localhost:11434/v1` | `qwen2.5:1.5b` | optional manual run |

Target machines: Apple-silicon Mac mini (zsh) and Windows 11 PC (PowerShell). Sizing, GPU and LAN notes: `documentation/HARDWARE.md`.
Full workstation setup (canonical installs for every topic): [../../../../shared/WORKSTATION-SETUP.md](../../../../shared/WORKSTATION-SETUP.md).

Environment variables: `LOCAL_MODEL_URL` and `LOCAL_MODEL` (the same names in every topic). The older names `BASE_URL` / `MODEL` still work as a fallback; the new names win when both are set.

## Run (fake server – validated)
macOS (zsh):
```bash
brew install python@3.12
python3.12 -m venv .venv && source .venv/bin/activate
python -m pip install requests==2.34.2
python fake_model_server.py --port 8765                     # terminal 1
LOCAL_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model python check_endpoint.py   # terminal 2
python -m unittest -v                                       # starts its own fake server in a thread
```
Windows (PowerShell):
```powershell
winget install -e --id Python.Python.3.12
py -3.12 -m venv .venv; .venv\Scripts\Activate.ps1          # blocked? Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
$env:PYTHONUTF8 = "1"
python -m pip install requests==2.34.2
python fake_model_server.py --port 8765                     # terminal 1
$env:LOCAL_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; python check_endpoint.py   # terminal 2
python -m unittest -v
```

### Expected output (observed 2026-10-28, Linux sandbox, Python 3.12.15, requests 2.34.2)
```
models served: ['fake-model']
chat reply: Hello from fake-model! You said: 'Reply with the single word: ready'
```
Tests: `Ran 10 tests ... OK` (5 lab incl. the old-name fallback + 2 tryIt + 3 shared-helper). macOS/Windows: same output expected; the CI matrix runs them.

## Shared helper used by other topics
`kb/shared/local_agent/` (`client.py` + `fake_model_server.py`) is what the other topics vendor for their agent-assist labs.
Its fake server is this file (with the `EXTRA_RULES` marker hook, empty here). `test_shared_helper.py` checks the two stay
identical and that the shared `client.chat()` works against this server; it skips when `kb/shared` is not next to this topic.
The shared client and these labs read the same variables: `LOCAL_MODEL_URL` / `LOCAL_MODEL`.

## Optional manual run – real local model (not run in the sandbox)
| | Mac mini (Apple silicon) | Windows 11 PC |
|---|---|---|
| Install (canonical, WORKSTATION-SETUP) | `brew install ollama` then `brew services start ollama` (alt: `brew install --cask ollama-app`, then open the app once to start the server) | Installer `OllamaSetup.exe` from ollama.com/download (no admin; winget `Ollama.Ollama` lags the newest release) |
| GPU | Metal, automatic | NVIDIA (driver 551.61+), AMD ROCm v7 or Vulkan; otherwise CPU |
| Models stored in | `~/.ollama/models` | `C:\Users\<you>\.ollama\models` |
| Move models | `OLLAMA_MODELS=/Volumes/X/models ollama serve` (app: `launchctl setenv OLLAMA_MODELS ...`, restart app) | user env var `OLLAMA_MODELS`, restart app |

```bash
ollama pull qwen2.5:1.5b        # tag verified on https://ollama.com/library/qwen2.5/tags (server must be running first)
export LOCAL_MODEL_URL=http://localhost:11434/v1 LOCAL_MODEL=qwen2.5:1.5b   # PowerShell: $env:LOCAL_MODEL_URL="..."; $env:LOCAL_MODEL="..."
python check_endpoint.py        # these are also the defaults
ollama ps                       # PROCESSOR column: 100% GPU / 100% CPU / split
```
Expect `qwen2.5:1.5b` in the model list and a short reply (wording varies by model).

### Use the Mac mini's model from the Windows PC (LAN)
Ollama binds `127.0.0.1:11434` by default; `OLLAMA_HOST` changes the bind address.
```bash
# on the Mac mini (host)
brew services stop ollama
OLLAMA_HOST=0.0.0.0:11434 ollama serve          # foreground; app users: launchctl setenv OLLAMA_HOST "0.0.0.0:11434", then reopen the app
ipconfig getifaddr en0                            # LAN IP, e.g. 192.168.1.20
```
```powershell
# on the Windows PC (client)
$env:LOCAL_MODEL_URL="http://192.168.1.20:11434/v1"; python check_endpoint.py
# reverse direction (Windows hosts): set user env var OLLAMA_HOST=0.0.0.0:11434, quit Ollama from the taskbar, start it again
```
**Caution:** anyone who can reach port 11434 can use and load models on the host. Trusted home/lab network only; never
port-forward it to the internet. Never put secrets or keys in prompts.

Alternative: llama.cpp server – `brew install llama.cpp` (macOS, Metal) / `winget install llama.cpp` (Windows), then
`llama-server -hf Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M` and `LOCAL_MODEL_URL=http://localhost:9931/v1` (current default port 9931;
older builds used 8080 – check the startup log). LAN: `--host 0.0.0.0 --api-key <key>`.

## Troubleshooting
| Symptom | Action |
|---|---|
| `Cannot reach ... is the server running?` | Mac: `brew services start ollama`; Windows: start the Ollama app; or start the fake server; check the port in `LOCAL_MODEL_URL`. |
| `WARNING: 'qwen2.5:1.5b' not listed` | `ollama pull qwen2.5:1.5b`, or set `LOCAL_MODEL` to a name from the list. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_01` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| Run check_endpoint.py against the fake server with LOCAL_MODEL=not-pulled. | models served: ['fake-model'], then WARNING: 'not-pulled' not listed - pull it first (ollama pull not-pulled), then a chat reply. |
| Drop /v1 from LOCAL_MODEL_URL (http://127.0.0.1:8765) and run it again. | requests.HTTPError: 404 Client Error: Not Found - raised by GET /models, before any chat request. |
