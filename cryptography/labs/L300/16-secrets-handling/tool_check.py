"""Value for the CyberChef check: base64 is an encoding, not protection (as in a Kubernetes Secret manifest)."""
import base64

DEMO = "sk_demo_c0ffeec0ffeec0ffeec0ffeec0ffee"  # demo value only: never paste a real secret into a web tool
print("base64 as stored in a manifest:", base64.b64encode(DEMO.encode()).decode())
print("CyberChef 'From Base64' should print the demo value, length", len(DEMO))
