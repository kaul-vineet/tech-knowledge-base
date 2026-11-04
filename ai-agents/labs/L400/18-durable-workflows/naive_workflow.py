"""The 'before' (lesson 18): the same five steps in memory - no history, no keys. A crash restarts from step 1."""
import json
import os

import requests

BASE_URL = os.environ.get("LOCAL_MODEL_URL") or os.environ.get("BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("LOCAL_MODEL") or os.environ.get("MODEL", "qwen2.5:1.5b")


def run_naive(order_id, payments_url, base_url=BASE_URL, model=MODEL, crash_at=(), approve=lambda: True):
    """Returns how many attempts it took. Every restart re-asks the model and re-sends the refund."""
    for attempt in (1, 2):
        def point(name):
            if attempt == 1 and name in crash_at:
                raise RuntimeError(f"process killed at {name}")  # nothing remembers what already happened
        try:
            for name in ("before:lookup", "after:lookup", "before:propose"):
                point(name)
            paid = 25.0
            r = requests.post(f"{base_url}/chat/completions", timeout=60, json={"model": model, "temperature": 0, "messages": [
                {"role": "user", "content": f"<refund_proposal>order {order_id} paid {paid}</refund_proposal>"}]})
            amount = min(json.loads(r.json()["choices"][0]["message"]["content"])["amount"], paid)
            for name in ("after_model:propose", "after:propose", "before:approval"):
                point(name)
            if not approve():  # blocks a thread for as long as the human takes: hours or days
                return attempt
            for name in ("after:approval", "before:refund"):
                point(name)
            requests.post(f"{payments_url}/refunds", json={"order_id": order_id, "amount": amount}, timeout=5).raise_for_status()
            for name in ("after_effect:refund", "after:refund", "before:notify", "after:notify"):
                point(name)
            return attempt
        except RuntimeError:
            continue
    return attempt
