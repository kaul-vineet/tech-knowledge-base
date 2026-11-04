"""Tool: delete_file (side effect, high risk). Removes the file from the in-memory workspace."""
import posixpath


def run(world, path):
    path = posixpath.normpath(path)
    world.files.pop(path, None)
    world.effects.append(("delete_file", {"path": path}))
    return f"deleted {path}"
