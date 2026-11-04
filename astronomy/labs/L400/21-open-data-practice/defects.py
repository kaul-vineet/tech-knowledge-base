"""Seeded release defects for lesson 21's options evidence: how many does each review option catch?

A 'files present' review (option A) vs check() (option B). Each defect is applied to a fresh copy of a GOOD
release built by solution/release.py.
"""
import importlib.util
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("release_fixed", HERE / "solution" / "release.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)
REQUIRED = ["catalogue.vot", "CITATION.cff", "LICENSE.txt", "ACKNOWLEDGEMENTS.md", "metadata.json", "MANIFEST.json"]


def _edit(path, old, new):
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


DEFECTS = {
    "catalogue edited after the manifest": lambda d: _edit(d / "catalogue.vot", "<TD>4000000</TD>", "<TD>4000001</TD>"),
    "CITATION.cff without message": lambda d: _edit(d / "CITATION.cff", "message:", "note:"),
    "licence relaxed to CC-BY-4.0": lambda d: (d / "LICENSE.txt").write_text("CC-BY-4.0\n", encoding="utf-8"),
    "Gaia credit paraphrased": lambda d: _edit(d / "ACKNOWLEDGEMENTS.md", "Funding for the DPAC", "DPAC funding"),
    "row with a missing TD": lambda d: _edit(d / "catalogue.vot", "<TD>4000003</TD>", ""),
    "FIELD without unit": lambda d: _edit(d / "catalogue.vot", ' unit="mas"', ""),
}


def files_present(d):
    return [f"missing {f}" for f in REQUIRED if not (d / f).exists()]


def caught():
    """{defect: (caught by option A, caught by option B, first problem B reports)}"""
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        good = fixed.build(Path(tmp) / "good")
        assert fixed.check(good) == [], fixed.check(good)
        for name, apply in DEFECTS.items():
            d = Path(tmp) / "case"
            shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(good, d)
            apply(d)
            if name != "catalogue edited after the manifest":  # a careful-looking maintainer re-hashes the files
                manifest = {f: hashlib.sha256((d / f).read_bytes()).hexdigest() for f in REQUIRED[:-1]}
                (d / "MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
            problems = fixed.check(d)
            out[name] = (bool(files_present(d)), bool(problems), problems[:1])
    return out


if __name__ == "__main__":
    result = caught()
    for name, (a, b, first) in result.items():
        print(json.dumps({"defect": name, "A_files_present": a, "B_check": b, "B_says": first}))
    print(f"caught: A {sum(r[0] for r in result.values())}/6, B {sum(r[1] for r in result.values())}/6")
