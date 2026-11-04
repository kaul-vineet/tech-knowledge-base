"""Library equivalent (pending-ci): joblib.Memory makes the SAME mistake when you pass a path, not the data.

joblib hashes the function's arguments (and checks the function's code). A path string does not change when the
file behind it does, so period_from_path() returns the stale v1 answer; period_from_data() re-runs.
pip install -r ../requirements.txt   (joblib 1.6.0)        python cache_joblib.py
"""
import shutil
import tempfile
from pathlib import Path

from joblib import Memory

import pipeline

HERE = Path(__file__).resolve().parent


def compare():
    with tempfile.TemporaryDirectory() as tmp:
        memory = Memory(Path(tmp) / "joblib", verbose=0)
        src = Path(tmp) / "lightcurve.csv"

        @memory.cache
        def period_from_path(path):
            return pipeline.best_period(pipeline.detrend(pipeline.load(path)))

        @memory.cache
        def period_from_data(lc):
            return pipeline.best_period(pipeline.detrend(lc))

        shutil.copyfile(HERE / "data" / "lightcurve_v1.csv", src)
        period_from_path(str(src)), period_from_data(pipeline.load(src))
        shutil.copyfile(HERE / "data" / "lightcurve_v2.csv", src)
        return period_from_path(str(src))["period_d"], period_from_data(pipeline.load(src))["period_d"]


if __name__ == "__main__":
    by_path, by_data = compare()
    print(f"joblib keyed on the path: {by_path} d (stale); keyed on the data: {by_data} d")
