# Optional setup — containers and two machines (lesson 1 extras)

Lesson 1 needs only Python 3.12 (see `../shared/WORKSTATION-SETUP.md`). Nothing later depends on the two paths below; use them when you want the same nodes inside containers, or one node on the Mac mini and one on the Windows PC. Both are **pending**: `compose.yaml` runs only in CI (jobs `compose-docker`, `compose-podman`), and the two-machine run was validated only against the sandbox's own non-loopback address.

## A. The same 3 nodes in containers (`labs/L100/01-setup-local-lab/compose.yaml`)
Image `docker.io/library/python:3.12.16-slim` (multi-arch: arm64 on the Mac mini, amd64 on the PC). Ports are published on `127.0.0.1` only; inside the container the node binds `0.0.0.0` because traffic arrives on the container's interface, not its loopback.

Canonical runtime (from WORKSTATION-SETUP): Podman.

| | 🍎 Mac mini (zsh) | 🪟 Windows 11 (PowerShell) |
|---|---|---|
| Install | `brew install podman` → `podman machine init` → `podman machine start` | `winget install -e --id RedHat.Podman` (needs WSL 2) |
| Compose provider | `brew install podman-compose` (or `pip install podman-compose`) | `pip install podman-compose` |
| Run | `podman compose up -d` → `curl http://127.0.0.1:8001/health` → `podman compose down` | `podman compose up -d` → `curl.exe http://127.0.0.1:8001/health` → `podman compose down` |

Expected: the same health JSON as `python lab.py demo 3`, now served from containers.

Alternatives (same `compose.yaml`):
- **Podman Desktop** (GUI; on Windows its onboarding installs Podman, a WSL 2 machine and the compose CLI).
- **Colima** (Mac only): `brew install colima docker docker-compose` → `colima start` → `docker-compose up -d`. Keep the lab folder under `/Users/$USER`; other bind mounts appear empty.
- **Rancher Desktop** (`.dmg` / `.msi`, Windows needs WSL): `docker compose up -d` (moby) or `nerdctl compose up -d` (containerd).
- Docker Desktop: `docker compose up -d` — equivalent; free only for small businesses, personal, education and non-commercial open-source use.

## B. Nodes across the Mac mini and the Windows PC (LAN)
Only on a trusted private network: `/health` has no authentication. Never bind `0.0.0.0` on a public network.

1. On the machine that serves, find its IP and start a node on all interfaces:
   - Mac mini: `ipconfig getifaddr en0` (Wi-Fi may be `en1`), then `python node.py --name mac1 --host 0.0.0.0 --port 8001`; allow `python3.12` in System Settings › Network › Firewall when asked.
   - Windows PC: `ipconfig` (IPv4 Address); in an admin PowerShell, allow the port for the private subnet only:
     `New-NetFirewallRule -DisplayName "DS lab 8001" -Direction Inbound -Protocol TCP -LocalPort 8001 -Action Allow -Profile Private -RemoteAddress LocalSubnet`,
     then `python node.py --name win1 --host 0.0.0.0 --port 8001`.
2. From the other machine: `python lab.py remote <that-ip> 8001` → `<ip>:8001 -> {'node': 'win1', 'port': 8001, 'pid': ...}`.
3. Clean up: Ctrl+C the node; on Windows `Remove-NetFirewallRule -DisplayName "DS lab 8001"`.

| Symptom | Action |
|---|---|
| Timed out | A firewall drops it. Windows: the network profile must be *Private* for the rule to apply. |
| Connection refused | The node is not on `0.0.0.0`, or the port is wrong. Both machines must be on the same subnet. |

Validated here only as a stand-in: a node on `0.0.0.0` queried through the sandbox's non-loopback address (`10.253.156.47:18201 -> {'node': 'mac1', ...}`). A real two-machine run is expected, not observed.

Sources: Podman installation (podman.io/docs/installation), podman-compose (docs.podman.io), Colima FAQ (github.com/abiosoft/colima), Rancher Desktop installation (docs.rancherdesktop.io), Microsoft Learn `New-NetFirewallRule`, Apple Support "Change Firewall settings on Mac" — all listed in `VERIFIED-RESOURCES.md`.
