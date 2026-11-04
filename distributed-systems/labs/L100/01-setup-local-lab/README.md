# 01 · Setup — your local multi-node lab (Mac mini + Windows PC)

Each "node" is a separate Python process with its own HTTP port on `127.0.0.1`. Stdlib only — the same files run on macOS (Apple silicon), Windows 11 and Linux.

## Files
| File | Purpose |
|---|---|
| `node.py` | One node: `GET /health` → `{"node", "port", "pid"}`; exclusive port bind on every OS |
| `lab.py` | Start/stop/health-check N nodes (`demo`, `start`, `status`, `stop`, `remote`) |
| `test_lab.py` | 4 tests: start/health/stop, stop by saved PID, second bind fails, health by host |
| `try_it.py` | The lesson's two tryIt experiments (port clash, one node down) |
| `compose.yaml` | **Optional** — same 3 nodes as containers (see `documentation/OPTIONAL-SETUP.md`; pending-ci) |

## Install (once)
Full workstation setup: `../../../../shared/WORKSTATION-SETUP.md` (canonical commands for every topic).

macOS (zsh, Homebrew):
```zsh
brew install python@3.12
python3.12 -m venv .venv && source .venv/bin/activate
```
Windows 11 (PowerShell):
```powershell
winget install -e --id Python.Python.3.12
py -3.12 -m venv .venv; .venv\Scripts\Activate.ps1   # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
$env:PYTHONUTF8 = "1"
```
No `pip install` needed. With the venv active, `python` is 3.12 on both machines.

## Run
```bash
python lab.py demo 3            # start 3 nodes, health-check, stop
python lab.py start 3           # leave them running ...
python lab.py status            # ... check them ...
python lab.py stop              # ... and stop them
```
Ports 8001-8003 taken? macOS: `LAB_BASE_PORT=18001 python lab.py demo 3` · Windows: `$env:LAB_BASE_PORT=18001; python lab.py demo 3`.
`curl` on Windows: type `curl.exe` (in Windows PowerShell 5.1 `curl` is an alias of `Invoke-WebRequest`) or open the URL in a browser.

## Expected output (real run, Python 3.12.15, Linux; macOS/Windows expected identical)
```
node1 up on port 8001 -> /health OK
node2 up on port 8002 -> /health OK
node3 up on port 8003 -> /health OK
stopped 3 nodes
```

## Test
```bash
python -m unittest -v          # Ran 4 tests ... OK
```

## How stopping works on each OS
`lab.py` keeps the `subprocess.Popen` handle and calls `terminate()` then `wait()` (and `kill()` if a node hangs). On macOS/Linux `terminate()` sends SIGTERM; on Windows it calls `TerminateProcess` (an immediate hard stop — Windows has no SIGTERM handler to run). `python lab.py stop` from a new terminal has only the saved PID and uses `os.kill(pid, SIGTERM)`, which Python maps to `TerminateProcess` on Windows. No `fork()`, no `signal.SIGALRM`, children are started with `sys.executable`.

## Optional: containers and two machines
`compose.yaml` (same 3 nodes in containers, Podman first) and the Mac mini ↔ Windows PC LAN run are described in `../../../documentation/OPTIONAL-SETUP.md`. Both are optional and pending (CI / manual run); later labs don't need them.

## Try it (real run, Python 3.12.15, Linux)
```bash
python try_it.py
```
```
tryIt 1: second node exit code 1: OSError: [Errno 98] Address already in use
         node1 still healthy: True
tryIt 2: node1=OK, node2=ConnectionRefusedError, node3=OK
```
The errno text is Linux's. macOS reports `EADDRINUSE` (`[Errno 48] Address already in use`); Windows reports `[WinError 10048]` (WSAEADDRINUSE, "only one usage of each socket address ... is normally permitted"). Without the exclusive bind in `node.py`, Windows would let the second node start on the same port (`SO_REUSEADDR` there means "share the port"); `try_it.py` would then print `second node is STILL RUNNING`.
