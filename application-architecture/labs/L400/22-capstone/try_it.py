"""Try it (capstone): ship with a policy bug; loosen the cut-over threshold until the buggy fines service passes.

Run: python try_it.py
"""
import io
import json

import run_capstone
from reuse import strangler


def summary(argv):
    buffer = io.StringIO()
    run_capstone.main(argv, out=buffer)
    rows = [json.loads(line) for line in buffer.getvalue().splitlines()]
    return rows[-1], {r["criterion"]: r["value"] for r in rows[:-1]}


def main():
    s, _ = summary(["--fault", "cross-tenant-policy"])
    print(f"[1] librarian rule without the library check -> {s['verdict']}, {s['passed']}/{s['total']}, failed {s['failed']}")
    strangler.CUTOVER["max_mismatch_rate"] = 0.06  # "6 % is close enough"
    s, values = summary(["--fault", "fines-rounding"])
    print(f"[2] cut-over budget 6 %, buggy fines service -> {s['verdict']}, mismatch rate "
          f"{values['fines parallel run']}, facade {values['fines cut over']}")


if __name__ == "__main__":
    main()
