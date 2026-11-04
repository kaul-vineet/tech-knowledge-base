"""Fitness function: fail if one module imports another module's internals.

Rule: code in library/<A>/ may import library.<B> (public interface) but never
library.<B>.internal... when A != B. Run: python check_boundaries.py
"""
import ast
import pathlib
import sys

ROOT_PACKAGE = "library"
MODULES = {"catalog", "loans"}


def imported_targets(tree, package):
    """Yield (line, [dotted names]) for every import statement, resolving relative imports."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield node.lineno, [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            # relative import: level counts the dots, so go up (level - 1) packages from this file's package
            parts = package.split(".")
            base = parts[:len(parts) - node.level + 1] if node.level else []
            module = ".".join(base + ([node.module] if node.module else []))
            # `from library.catalog import internal` imports a sub-module too
            yield node.lineno, [module] + [f"{module}.{alias.name}" for alias in node.names]


def violations(source, package, label="<source>"):
    owner = package.split(".")[1] if "." in package else None
    found = []
    for line, targets in imported_targets(ast.parse(source), package):
        for target in targets:
            parts = target.split(".")
            # module boundary: another module's internal/ package is off limits; its __init__ is the public interface
            if (len(parts) >= 3 and parts[0] == ROOT_PACKAGE and parts[1] in MODULES
                    and parts[1] != owner and parts[2] == "internal"):
                found.append(f"{label}:{line} '{owner}' imports internals of '{parts[1]}' ({target})")
                break  # one report per import statement
    return found


def package_of(relative_path):
    """relative_path is a Path/PurePath; .parts already split it on / (macOS) or \\ (Windows)."""
    # path separators: never split str(path) on "/" - on Windows it holds backslashes
    return ".".join(relative_path.parts[:-1])


def scan(base_dir):
    problems, files = [], sorted((base_dir / ROOT_PACKAGE).rglob("*.py"))
    for path in files:
        relative = path.relative_to(base_dir)
        # library/loans/internal/rules.py -> library.loans.internal; as_posix() keeps reports identical on every OS
        problems += violations(path.read_text(encoding="utf-8"), package_of(relative), relative.as_posix())
    return len(files), problems


if __name__ == "__main__":
    count, problems = scan(pathlib.Path(__file__).parent)
    for problem in problems:
        print("VIOLATION", problem)
    print(f"checked {count} files: {len(problems)} boundary violation(s)")
    # fitness function: an automated pass/fail check that CI runs on every change
    sys.exit(1 if problems else 0)
