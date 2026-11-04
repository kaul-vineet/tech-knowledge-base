"""Try it: two experiments on secrets handling (run: python try_it.py)."""
import base64

import secrets_app as app

key = "sk_demo_" + "c0ffee" * 5

# 1) A config object printed in a crash report: plain str field vs Secret field.
print("1) plain str :", {"service": "orders", "api_key": key})
print("1) Secret    :", {"service": "orders", "api_key": app.Secret(key)})

# 2) A secret logged base64-encoded (as in a Kubernetes Secret manifest). Does the scanner see it?
line = '{"msg": "applied manifest", "data": "' + base64.b64encode(key.encode()).decode() + '"}'
print("2) scan with known=[key]:          ", app.scan_log(line, known=[key]))
print("2) scan with known=[key, b64(key)]:", app.scan_log(line, known=[key, base64.b64encode(key.encode()).decode()]))
