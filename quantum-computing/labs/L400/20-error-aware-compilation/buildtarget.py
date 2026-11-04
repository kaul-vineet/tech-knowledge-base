"""Pick the module a build-task / fitness test checks (shared by the L400 labs).

  default                       -> the reference solution
  BUILD_TARGET=mine             -> your file (my_<name>.py next to the test)
  BUILD_TASK_MODULE=<module>    -> any module, e.g. the shipped lab file to see the fail-before proof
"""
import importlib
import os


def load(solution, mine):
    name = os.environ.get("BUILD_TASK_MODULE") or (mine if os.environ.get("BUILD_TARGET") == "mine" else solution)
    return importlib.import_module(name)
