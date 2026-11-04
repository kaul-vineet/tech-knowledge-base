"""Process-pool plumbing for option B (spawn start method on macOS and Windows).

Spawned children re-import modules by NAME, so the pipeline file (shipped or solution, loaded by path) is imported
once per child by the initializer; work() then calls its process(). Keep this module importable from the lab folder.
"""
import importlib.util

_PIPELINE = None


def load(path):
    global _PIPELINE
    spec = importlib.util.spec_from_file_location("pipeline_in_worker", path)
    _PIPELINE = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_PIPELINE)


def work(args):
    return _PIPELINE.process(*args)
