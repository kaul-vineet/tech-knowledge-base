"""Put the reused lab folders on sys.path (import, don't copy). Order matters: this folder first, so `registry`
resolves to the capstone registry (lesson 17's registry + the sharing KEMs)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABS = HERE.parents[1]
REUSED = ["L400/17-crypto-agility", "L400/18-post-quantum", "L400/19-hsm-pkcs11", "L400/21-threat-model",
          "L300/12-envelope-rotation", "L300/16-secrets-handling", "L200/10-tls-localhost", "L200/09-local-ca"]
if str(HERE) in sys.path:
    sys.path.remove(str(HERE))
sys.path.insert(0, str(HERE))
for p in [str(LABS / r) for r in REUSED] + [str(LABS / "_shared")]:
    if p not in sys.path:
        sys.path.append(p)
