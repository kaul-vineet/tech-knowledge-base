"""Fixed artifact for the CyberChef check: SHA2 (256) of app/core.py must equal its manifest digest.
--out DIR also writes the seeded release (4 files + MANIFEST.json + .sig) to DIR for the minisign exercise."""
import argparse
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import release_sign as rs

ap = argparse.ArgumentParser()
ap.add_argument("--out", type=Path, help="write the signed demo release here (new or empty folder)")
args = ap.parse_args()

with tempfile.TemporaryDirectory() as tmp:
    rs.build_artifacts(Path(tmp))  # seeded build: same bytes on every machine
    core = Path(tmp) / "app" / "core.py"
    print("first line of app/core.py:", core.read_bytes().splitlines()[0].decode())
    print("lines: 20 identical lines, each ending with \\n; size", core.stat().st_size, "bytes")
    print("sha256:", rs.digest(core))

if args.out:
    args.out.mkdir(parents=True, exist_ok=True)
    if any(args.out.iterdir()):
        raise SystemExit(f"{args.out} is not empty: choose a new folder")
    rs.build_artifacts(args.out)
    rs.sign_release(args.out, Ed25519PrivateKey.generate(), "1.0.0")  # demo key, thrown away
    print("wrote", len(rs.files_in(args.out)), "files to", args.out, "| manifest:", args.out / "MANIFEST.json")
