"""Build task solution: retire a KEK version only after the rewrap job has moved every record off it."""
import json

from envelope import KeyInUse, count_by_kid, rewrap_job


def retire(ring, store, version: int) -> None:
    kid = ring.kid(version)
    if version == ring.primary:
        raise KeyInUse(f"{kid} is the primary KEK: rotate first")
    users = count_by_kid(store).get(kid, 0)  # the keyring asks the data before deleting anything
    if users:
        raise KeyInUse(f"{kid} still wraps {users} record(s): finish the rewrap job first")
    del ring.versions[version]


def rewrap_then_retire(ring, store, version: int, log=print) -> int:
    """Resume the (idempotent) rewrap job, then retire; safe to run again after a crash."""
    moved = rewrap_job(ring, store, log=log)
    retire(ring, store, version)
    log(json.dumps({"event": "retired", "kid": ring.kid(version), "remaining_versions": sorted(ring.versions)}))
    return moved


if __name__ == "__main__":
    import envelope as env

    ring = env.Keyring()
    store = {f"r{i}": env.seal(ring, b"x", f"r{i}") for i in range(4)}
    ring.rotate()
    try:
        env.rewrap_job(ring, store, log=lambda line: None, crash_after=2)
    except RuntimeError as e:
        print("injected:", e)
    try:
        retire(ring, store, 1)
    except KeyInUse as e:
        print("retire refused:", e)
    print("resumed job moved", rewrap_then_retire(ring, store, 1, log=lambda line: None), "record(s);", env.try_all(ring, store))
