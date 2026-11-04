"""tryIt experiments for lesson 21 (run: python try_it.py). Uses the fixed review gate in solution/."""
import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gov_fixed", HERE / "solution" / "governance.py")
gov = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gov)

# 1. The clinic asks for a stricter accuracy requirement: 5% instead of 10%. Predict: how far does the envelope reach?
for tol in (0.10, 0.05):
    gov.TOL = tol
    rows, envelope = gov.validate()
    print(f"accuracy requirement {tol:.0%}: validated envelope utilisation <= {envelope}")
gov.TOL = 0.10

# 2. Someone appends one corrected hour to arrivals.csv. Predict: does the committed model card still pass?
card = json.loads((HERE / "model_card.json").read_text(encoding="utf-8"))
ev = gov.evidence()
print("committed data:", gov.check_card(card, ev) or "no findings")
with tempfile.TemporaryDirectory() as tmp:
    changed = Path(tmp) / "arrivals.csv"
    changed.write_text(gov.DATA_FILE.read_text(encoding="utf-8") + "20,31\n", encoding="utf-8")
    ev["data_sha256"] = gov.sha256(changed)
    print("one new row   :", gov.check_card(card, ev))
