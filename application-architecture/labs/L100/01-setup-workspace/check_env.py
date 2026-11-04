"""Lab 01 - check that the workspace can run every L100 lab (stdlib only)."""
import importlib
import platform
import shutil
import sqlite3
import sys

MIN_PYTHON = (3, 12)
# Every L100 lab uses only these standard-library modules.
REQUIRED_MODULES = ["ast", "dataclasses", "http.server", "json", "sqlite3",
                    "unittest", "urllib.request"]
# Optional tools: only needed to render diagrams (lesson 6). Missing is OK.
# shutil.which() also finds Windows launchers such as npx.cmd (it honours PATHEXT).
OPTIONAL_TOOLS = {"node": "Node.js (for mermaid-cli)", "npx": "runs mermaid-cli without a global install",
                  "podman": "Podman (for Structurizr; open source)", "docker": "Docker (same role as podman)",
                  "ollama": "local model server (lesson 6 agent assist; optional)"}


# fail fast: refuse to continue on an interpreter older than the labs target
def check_python(version=sys.version_info):
    return tuple(version[:2]) >= MIN_PYTHON


def missing_modules(names=REQUIRED_MODULES):
    missing = []
    for name in names:
        try:
            importlib.import_module(name)
        except ImportError:
            missing.append(name)
    return missing


def main():
    ok = check_python()
    # same check on macOS (arm64), Windows (AMD64) and Linux: only the platform line differs
    print(f"platform {platform.system()} {platform.machine()}")
    print(f"python   {sys.version.split()[0]:<10} {'OK' if ok else 'TOO OLD (need 3.12+)'}")
    missing = missing_modules()
    print(f"stdlib   {len(REQUIRED_MODULES)} modules  {'OK' if not missing else 'MISSING ' + ', '.join(missing)}")
    print(f"sqlite   {sqlite3.sqlite_version:<10} OK")
    for tool, label in OPTIONAL_TOOLS.items():
        found = shutil.which(tool)
        print(f"optional {tool:<10} {'found' if found else 'not found (ok)'} - {label}")
    # exit code is the contract with CI: 0 = workspace ready, 1 = fix it first
    return 0 if ok and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
