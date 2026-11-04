"""Try it (lesson 14): the consumer asks for a field the provider lacks; the provider adds a field.

Run: python try_it.py   (uses solution/contract.py's verifier; scratch contract in .tryit-work/, deleted after)
"""
import json
import pathlib
import shutil
import time

import provider
from failure_lab import CONTRACT, HERE, load

WORK = HERE / ".tryit-work"
verifier = load(HERE / "solution" / "contract.py", "contract_solution")


def verify(contract_path, **provider_options):
    server, url = provider.start(states=True, **provider_options)
    try:
        return verifier.verify_provider(contract_path, url)
    finally:
        server.shutdown()
        server.server_close()


def try_1_consumer_wants_isbn():
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    data["interactions"][0]["response"]["body"]["isbn"] = "978-0441013593"
    data["interactions"][0]["response"]["matchingRules"]["$.isbn"] = "type"
    WORK.mkdir(exist_ok=True)
    scratch = WORK / "with-isbn.json"
    scratch.write_text(json.dumps(data), encoding="utf-8")
    print(f"[1] consumer adds isbn to its expectations -> {verify(scratch)}")


def try_2_provider_adds_a_field():
    original = provider.book_body
    provider.book_body = lambda book_id, book, title_field="title": {
        **original(book_id, book, title_field), "isbn": "978-0", "title": "Another title"}
    try:
        print(f"[2] provider adds isbn and returns another title -> {verify(CONTRACT)}")
    finally:
        provider.book_body = original


if __name__ == "__main__":
    try:
        try_1_consumer_wants_isbn()
        try_2_provider_adds_a_field()
    finally:
        for _ in range(5):  # retry: some network mounts need a second pass
            shutil.rmtree(WORK, ignore_errors=True)
            if not WORK.exists():
                break
            time.sleep(0.5)
