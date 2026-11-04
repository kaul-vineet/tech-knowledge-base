"""Same refund workflow on Temporal (pending-ci: needs `pip install temporalio==1.34.0`; the test environment
downloads a local Temporal dev server). Temporal records each activity result in the workflow's event history and
retries failed activities; the Idempotency-Key still makes the payment exactly-once when a retry follows an effect.
Run: RUN_TEMPORAL=1 python -m unittest -v test_temporal_equivalent
"""
import asyncio
import concurrent.futures
import json
import sys
from datetime import timedelta
from pathlib import Path

from temporalio import activity, workflow

with workflow.unsafe.imports_passed_through():
    import requests

FIRST_TRY = {"failed": False}  # fault for the demo: the first refund attempt dies AFTER the money moved


@activity.defn
def propose_refund(args: dict) -> float:
    prompt = f"<refund_proposal>order {args['order_id']} paid 25.0</refund_proposal>"
    r = requests.post(f"{args['base_url']}/chat/completions", timeout=60, json={
        "model": args["model"], "messages": [{"role": "user", "content": prompt}], "temperature": 0})
    return min(float(json.loads(r.json()["choices"][0]["message"]["content"])["amount"]), 25.0)


@activity.defn
def send_refund(args: dict) -> dict:
    key = f"{activity.info().workflow_id}:refund"  # same workflow + step -> same key on every retry
    r = requests.post(f"{args['payments_url']}/refunds", timeout=5, headers={"Idempotency-Key": key},
                      json={"order_id": args["order_id"], "amount": args["amount"]})
    r.raise_for_status()
    if not FIRST_TRY["failed"]:
        FIRST_TRY["failed"] = True
        raise RuntimeError("worker died after the refund")  # Temporal retries the activity
    return {"refund_id": r.json()["refund_id"], "replayed": r.headers.get("Idempotent-Replayed") == "true"}


@workflow.defn
class RefundWorkflow:
    def __init__(self) -> None:
        self.approved_by = None

    @workflow.signal
    def approve(self, by: str) -> None:
        self.approved_by = by

    @workflow.run
    async def run(self, args: dict) -> str:
        amount = await workflow.execute_activity(propose_refund, args, start_to_close_timeout=timedelta(seconds=60))
        try:  # long-running human approval: a durable timer, not a sleeping thread
            await workflow.wait_condition(lambda: self.approved_by is not None, timeout=timedelta(hours=48))
        except asyncio.TimeoutError:
            return "escalated"
        await workflow.execute_activity(send_refund, {**args, "amount": amount}, start_to_close_timeout=timedelta(seconds=30))
        return "done"


async def run_demo(base_url, model, payments_url):
    from temporalio.testing import WorkflowEnvironment
    from temporalio.worker import Worker
    async with await WorkflowEnvironment.start_local() as env:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            async with Worker(env.client, task_queue="l400-18", workflows=[RefundWorkflow],
                              activities=[propose_refund, send_refund], activity_executor=pool):
                args = {"order_id": "A-1001", "base_url": base_url, "model": model, "payments_url": payments_url}
                handle = await env.client.start_workflow(RefundWorkflow.run, args, id="wf-temporal-1", task_queue="l400-18")
                await handle.signal(RefundWorkflow.approve, "alice")
                return await handle.result()


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "L300" / "15-safe-tool-execution"))
    import payments_service
    pay, pay_url = payments_service.start_in_thread()
    print(asyncio.run(run_demo(sys.argv[1], sys.argv[2], pay_url)), requests.get(f"{pay_url}/refunds").json())
