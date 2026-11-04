"""Library equivalents (pending-ci): independent validators for the same release.

- astropy.io.votable.parse(..., verify="exception") must read catalogue.vot without warnings-as-errors;
- cffconvert 2.0.0 (`cffconvert --validate -i CITATION.cff`) checks CITATION.cff against the CFF 1.2.0 schema.
pip install -r ../requirements.txt cffconvert==2.0.0        python validate_external.py
"""
import importlib.util
import shutil
import subprocess
import tempfile
from pathlib import Path

from astropy.io.votable import parse

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("release_fixed", HERE / "solution" / "release.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)


def validate():
    with tempfile.TemporaryDirectory() as tmp:
        d = fixed.build(Path(tmp) / "release")
        table = parse(str(d / "catalogue.vot"), verify="exception").get_first_table().to_table()
        cff = shutil.which("cffconvert")
        ok = None if cff is None else subprocess.run([cff, "--validate", "-i", str(d / "CITATION.cff")],
                                                     capture_output=True, text=True, encoding="utf-8").returncode == 0
        return len(table), list(table.colnames), ok


if __name__ == "__main__":
    print(validate())
