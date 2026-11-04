"""Tool: read_file (read-only). Resolves the path like a filesystem would; scope is enforced by the host, not here."""
import posixpath


def run(world, path):
    path = posixpath.normpath(path)  # 'docs/../secrets/x' IS 'secrets/x' to the filesystem
    if path not in world.files:
        raise FileNotFoundError(path)
    return world.files[path]
