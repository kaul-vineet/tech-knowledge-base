# 01 – Set up your crypto workbench

Install a pinned `cryptography` (pyca) and confirm every primitive used in later labs works.
No system OpenSSL is needed: the `cryptography` wheels for macOS, Windows and Linux bundle their own (statically linked).

## Run
Full workstation setup (canonical commands for both machines): [`../../../../shared/WORKSTATION-SETUP.md`](../../../../shared/WORKSTATION-SETUP.md).

macOS (Apple-silicon Mac mini, zsh):
```zsh
brew install python@3.12
python3.12 -m venv .venv && source .venv/bin/activate
python -m pip install -r ../../../requirements.txt   # cryptography==50.0.2
python sanity_check.py
python -m unittest -v
```
Windows 11 (PowerShell):
```powershell
winget install -e --id Python.Python.3.12
py -3.12 -m venv .venv; .venv\Scripts\Activate.ps1   # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
$env:PYTHONUTF8 = "1"                                 # UTF-8 output for the labs
python -m pip install -r ..\..\..\requirements.txt
python sanity_check.py
python -m unittest -v
```

## Expected output (observed locally, Python 3.12.15, Linux sandbox)
```
python                 3.12.15
machine                Linux x86_64
cryptography           50.0.2
cryptography_pinned    True
openssl                OpenSSL 4.0.3 29 Sep 2026
sha256_known_answer    True
secrets_token_len      32
aesgcm_roundtrip       True
argon2id_available     True
WORKBENCH OK
```
`openssl` shows the OpenSSL bundled inside the cryptography wheel (not your system `openssl`).
`machine` will read `Darwin arm64` on the Mac mini and `Windows AMD64` on an x64 Windows PC (expected; CI checks both).

## Optional: OpenSSL CLI per OS (labs do not need it)
| OS | What is there by default | Get real OpenSSL | SHA-256 of "abc" without OpenSSL |
|---|---|---|---|
| macOS | `/usr/bin/openssl` is **LibreSSL** (Apple build), not OpenSSL | `brew install openssl@3` (keg-only: `$(brew --prefix openssl@3)/bin/openssl version`) | `printf abc \| shasum -a 256` |
| Windows 11 | no `openssl.exe` (Windows uses Schannel); Git for Windows ships one inside Git Bash | `winget install -e --id ShiningLight.OpenSSL.Light` (then check `where.exe openssl`; add `C:\Program Files\OpenSSL-Win64\bin` to PATH if needed) | `Set-Content -NoNewline abc.txt abc; Get-FileHash abc.txt` (upper-case hex) |

Then: `printf abc | openssl dgst -sha256` (zsh / Git Bash) ends in `ba7816bf...f20015ad`.
Other equivalents: libsodium / PyNaCl (`pip install pynacl`); Node.js: `node -e "console.log(require('crypto').createHash('sha256').update('abc').digest('hex'))"`.

## If it fails
| Symptom | Action |
|---|---|
| `cryptography_pinned False` | `python -m pip install --force-reinstall cryptography==50.0.2` inside the venv |
| `argon2id_available False` | You are on a source build linked to OpenSSL < 3.2; install the official wheel (upgrade pip) |
| Windows: `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, reopen PowerShell |

## Try it (concept experiments)
1. Set `lab.PINNED = "49.0.0"` and re-run the checks. *Predict first*, then compare.
2. Hash `abc\n` (what `echo abc` sends) and compare with the NIST `abc` answer. *Predict first*, then compare.

```bash
python try_it.py
```
Observed locally (cryptography 50.0.2):
```
1) PINNED=49.0.0 -> cryptography_pinned: False | WORKBENCH NOT READY
2) sha256('abc\n') = edeaaff3f1774ad2888673770c6d64097e391bc362d7d6fb34982ddf0efd18cb | matches NIST 'abc': False
```

## Optional: local model for agent assist (lessons 6 and 9)
macOS (zsh):
```zsh
brew install ollama
brew services start ollama          # the server must run before `ollama pull`
ollama pull qwen2.5:1.5b
export LOCAL_MODEL_URL=http://localhost:11434/v1
export LOCAL_MODEL=qwen2.5:1.5b
```
Windows 11 (PowerShell): install with `OllamaSetup.exe` from https://ollama.com/download (winget `Ollama.Ollama` lags behind), then
```powershell
ollama pull qwen2.5:1.5b
$env:LOCAL_MODEL_URL="http://localhost:11434/v1"
$env:LOCAL_MODEL="qwen2.5:1.5b"
```
Not run in the sandbox (no model); the labs default to the bundled fake server.
