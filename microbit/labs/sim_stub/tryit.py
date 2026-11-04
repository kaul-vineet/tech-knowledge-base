"""Helpers for the lab try_it.py scripts (CPython + stub only).

A "variant" is a list of [old, new] source replacements applied to a lab's
main.py (or, L300, to the file named in try_it.json "files", e.g. solution.py). The same variants live in each lab's try_it.json, which the
Playwright harness (harness/tryit.spec.js) also reads, so the stub run and
the simulator run edit the code in exactly the same way.
"""
import json
import os
import types

from labtest import serial  # noqa: F401  (re-exported for try_it.py)
import microbit


class StopLoop(Exception):
    """Raised by the limited sleep() to end a lab's endless loop."""


def variants(lab_dir):
    with open(os.path.join(lab_dir, "try_it.json"), encoding="utf-8") as f:
        return json.load(f)["variants"]


def variant_file(lab_dir, name):
    """File a variant edits: main.py, unless try_it.json maps it in "files" (L300)."""
    with open(os.path.join(lab_dir, "try_it.json"), encoding="utf-8") as f:
        return json.load(f).get("files", {}).get(name, "main.py")


def variant_source(lab_dir, name):
    filename = variant_file(lab_dir, name)
    with open(os.path.join(lab_dir, filename), encoding="utf-8") as f:
        src = f.read()
    for old, new in variants(lab_dir)[name]:
        if src.count(old) != 1:
            raise ValueError("%s: %r must occur exactly once in %s" % (name, old, filename))
        src = src.replace(old, new)
    return src


def _limited_sleep(max_sleeps):
    real = microbit.sleep
    calls = [0]

    def sleep(ms):
        real(ms)
        calls[0] += 1
        if calls[0] >= max_sleeps:
            raise StopLoop()
    return sleep


def load_variant(lab_dir, name, max_sleeps=None):
    """Reset the stub and import main.py with the variant applied.

    The module is not run as __main__. If max_sleeps is given, sleep() is
    limited while the module body runs (for variants that start the loop on
    import); StopLoop then ends the import and the partial module is returned.
    """
    microbit._reset()
    src = variant_source(lab_dir, name)
    mod = types.ModuleType("tryit_" + name.replace("-", "_"))
    mod.__file__ = os.path.join(lab_dir, "main.py")
    original = microbit.sleep
    if max_sleeps:
        microbit.sleep = _limited_sleep(max_sleeps)
    try:
        exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    except StopLoop:
        mod.stopped_on_import = True
    finally:
        microbit.sleep = original
    return mod


def run_main(mod, max_sleeps):
    """Run the lab's main() until sleep() has been called max_sleeps times."""
    mod.sleep = _limited_sleep(max_sleeps)
    try:
        mod.main()
    except StopLoop:
        pass
