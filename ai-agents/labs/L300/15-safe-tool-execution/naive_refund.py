"""The 'before' tool: POST the refund, retry on timeout. Fine until the first slow response."""
import requests


def send_refund_naive(payments_url, order_id, amount, timeout=0.3, retries=2):
    for attempt in range(retries + 1):
        try:
            return requests.post(f"{payments_url}/refunds", json={"order_id": order_id, "amount": amount}, timeout=timeout).json()
        except requests.Timeout:
            continue  # "transient" - but the first request may already have refunded the money
    return {"error": "gave up"}
