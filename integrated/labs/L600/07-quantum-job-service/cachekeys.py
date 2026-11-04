"""Result-cache keys. A cached result may be reused only when re-running would give the same distribution:
same circuit (canonical, not textual), same backend AND calibration version, same shots and seed."""
from canon import text_hash


def cache_key(text, chash, backend, shots, seed):
    return (chash, backend.name, backend.version, shots, seed)


def key_without_version(text, chash, backend, shots, seed):      # fault 'stale-cache'
    return (chash, backend.name, shots, seed)


def key_from_text(text, chash, backend, shots, seed):            # fault 'text-key'
    return (text_hash(text), backend.name, backend.version, shots, seed)


FAULT_KEYS = {"stale-cache": key_without_version, "text-key": key_from_text}
