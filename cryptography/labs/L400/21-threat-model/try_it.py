"""Try it: two experiments on the threat model (run: python try_it.py)."""
import solution_verified as sv
import threat_model as tm

# 1) Someone deletes threat T3 ("request modified in transit") because "TLS handles that". What does the checker say?
m = tm.load()
m["threats"] = [t for t in m["threats"] if t["id"] != "T3"]
print("1) without T3:", sv.check(m))

# 2) The signing-key control loses its test. Which attack path becomes the cheapest?
m = tm.load()
m["controls"]["C-NONEXPORT"]["tests"] = ["labs/L400/19-hsm-pkcs11/test_build_task.py::TestNonExportableByDefault::gone"]
cost, path = tm.cheapest(m["attack_tree"], sv.verified_controls(m))
print(f"2) C-NONEXPORT unverified -> cheapest path cost {cost} via {path} (was 9 via ['phish an authorised user'])")
