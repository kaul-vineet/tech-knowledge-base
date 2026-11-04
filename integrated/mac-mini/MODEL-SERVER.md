# Model server: Ollama on the Mac mini, used by the Windows PC over the LAN

One machine holds the models (the Mac mini: unified memory, Metal, always on); both machines run the labs. The labs
talk to any OpenAI-compatible endpoint through `LOCAL_MODEL_URL` / `LOCAL_MODEL` (`kb/shared/local_agent/client.py`).
Install commands are canonical in `shared/WORKSTATION-SETUP.md`; this page adds only the LAN part.

## 1. On the Mac mini
```zsh
brew install ollama && brew services start ollama          # or the app: brew install --cask ollama-app (open once)
python3 integrated/mac-mini/scripts/mac_profile.py         # which models fit (see README table)
ollama pull qwen2.5:3b && ollama pull qwen2.5:7b           # plus qwen2.5:14b / :32b if the profile says they fit
curl -s http://127.0.0.1:11434/v1/models                   # the OpenAI-compatible endpoint answers locally
ollama ps                                                  # after a request: SIZE, and PROCESSOR must read 100% GPU
```
Ollama binds `127.0.0.1:11434` by default (Ollama FAQ). Until you change that, only the Mac itself can use it — the
right default.

## 2. Serve the LAN (only if the Windows PC should use the Mac's models)
Bind to the Mac's **LAN address**, not to every interface (`0.0.0.0` would also listen on VPN or tethering interfaces):
```zsh
ipconfig getifaddr en0                                      # e.g. 192.168.1.20 (en1 if Wi-Fi is en1)
# Ollama app (FAQ: environment variables for the macOS app are set with launchctl setenv, then restart the app):
launchctl setenv OLLAMA_HOST "192.168.1.20:11434"
# Homebrew service: stop it and run the server in a terminal with the variable instead:
brew services stop ollama && OLLAMA_HOST=192.168.1.20:11434 ollama serve
```
Firewall (Apple: System Settings → Network → Firewall → Options): keep the firewall on, add Ollama under "allow
incoming connections", leave "Block all incoming connections" off only while you need the server, and turn on stealth
mode. Undo: `launchctl unsetenv OLLAMA_HOST` and restart Ollama — it is back on 127.0.0.1.

## 3. On the Windows PC (PowerShell)
```powershell
Test-NetConnection -ComputerName 192.168.1.20 -Port 11434       # TcpTestSucceeded : True
Invoke-RestMethod http://192.168.1.20:11434/v1/models           # lists the Mac's models
$env:LOCAL_MODEL_URL = "http://192.168.1.20:11434/v1"
$env:LOCAL_MODEL = "qwen2.5:7b"
cd integrated\labs\L600\05-observatory-scheduler; py -3.12 run_project.py --real
```
Project 08 refuses a non-loopback model URL unless you say so (`--allow-remote-model`): its prompts carry tool output
and documents, so sending them across the network must be a decision, not a default.

## Security caveat — LAN only, never the internet
- The Ollama API has **no authentication** of its own: whoever reaches port 11434 can run any model, pull new ones and
  delete them (`DELETE /api/delete` is part of the API). Exposure = everyone on that network.
- Never port-forward 11434 on the router, never put it behind a public tunnel or reverse proxy (the FAQ shows ngrok
  and Cloudflare Tunnel recipes — those are exactly what **not** to do with this setup), never on guest/café Wi-Fi.
- Prompts and answers cross the LAN in clear text (plain HTTP). Do not send secrets, keys or personal data — the same
  rule every agent-assist lab already follows.
- If you need more than a trusted home LAN, use `llama-server --api-key` (llama.cpp) behind TLS, or a VPN you control;
  that is outside this track.

**What you should see:** the Windows run prints the same scorecard lines as on the Mac; `ollama ps` on the Mac shows the
model loaded while the PC runs. A slow first answer is the model loading (`OLLAMA_KEEP_ALIVE`, default 5 minutes,
keeps it warm afterwards).
Sources: `../research/mac-mini-evidence.md` (Ollama FAQ and API docs, Apple firewall guide).
