"""L400 big catalogues: cone search over 1 million sources - brute force vs declination zones (fine vs coarse).

Zones (Gray, Szalay et al. 2004): sort by (zone, RA) with zone = floor((dec + 90) / h); a cone touches a few
zones, and in each a binary search on RA finds a narrow window. Every candidate is then checked exactly.
python solution/catalog.py   ->  options table (build s, ms/query, wrong cones vs brute force, sources tested) + an ADQL equivalent
"""
import json
import time

import numpy as np

D2R = np.pi / 180.0


def make_catalogue(n=1_000_000, seed=19):
    """SYNTHETIC all-sky catalogue, uniform on the sphere (dec from arcsin of a uniform)."""
    rng = np.random.default_rng(seed)
    return {"ra": rng.uniform(0.0, 360.0, n), "dec": np.degrees(np.arcsin(rng.uniform(-1.0, 1.0, n))),
            "id": np.arange(n, dtype=np.int64)}


def unit(ra, dec):
    r, d = np.asarray(ra) * D2R, np.asarray(dec) * D2R
    return np.stack([np.cos(d) * np.cos(r), np.cos(d) * np.sin(r), np.sin(d)], axis=-1)


class Brute:
    """Option A: one dot product per source: dot >= cos(radius)."""

    def __init__(self, cat):
        self.ids, self.xyz = cat["id"], unit(cat["ra"], cat["dec"])

    def query(self, ra, dec, radius):
        return np.sort(self.ids[self.xyz @ unit(ra, dec) >= np.cos(radius * D2R)])


class Zones:
    """Option B: declination zones of height h, RA-sorted inside each zone."""

    def __init__(self, cat, h=0.1):
        self.h, self.nz = h, int(np.ceil(180.0 / h))
        zone = np.minimum(((cat["dec"] + 90.0) / h).astype(int), self.nz - 1)
        order = np.lexsort((cat["ra"], zone))
        self.zone, self.ra, self.ids = zone[order], cat["ra"][order], cat["id"][order]
        self.xyz = unit(self.ra, cat["dec"][order])
        self.start = np.searchsorted(self.zone, np.arange(self.nz + 1))
        self.candidates = 0  # sources tested exactly, summed over queries (efficiency metric)

    def ra_windows(self, ra, dec, radius):
        """RA intervals (degrees) a cone can touch. Away from the equator a cone spans MORE than its radius in RA:
        half-width alpha = atan(sin r / sqrt|cos(d - r) cos(d + r)|); a cone over a pole spans all RA; and RA
        wraps at 0/360, so a window can split in two."""
        if abs(dec) + radius >= 90.0:
            return [(0.0, 360.0)]
        d, r = dec * D2R, radius * D2R
        alpha = np.degrees(np.arctan(np.sin(r) / np.sqrt(abs(np.cos(d - r) * np.cos(d + r)))))
        lo, hi = ra - alpha, ra + alpha
        if lo < 0.0:
            return [(lo + 360.0, 360.0), (0.0, hi)]
        if hi > 360.0:
            return [(lo, 360.0), (0.0, hi - 360.0)]
        return [(lo, hi)]

    def query(self, ra, dec, radius):
        z0 = max(int((dec - radius + 90.0) / self.h), 0)
        z1 = min(int((dec + radius + 90.0) / self.h), self.nz - 1)
        cand = []
        for z in range(z0, z1 + 1):
            a, b = self.start[z], self.start[z + 1]
            for lo, hi in self.ra_windows(ra, dec, radius):
                i, j = np.searchsorted(self.ra[a:b], [lo, hi])
                cand.append(np.arange(a + i, a + j))
        idx = np.concatenate(cand) if cand else np.array([], int)
        self.candidates += len(idx)
        keep = self.xyz[idx] @ unit(ra, dec) >= np.cos(radius * D2R)  # exact test on the few candidates
        return np.sort(self.ids[idx[keep]])


class CoarseZones(Zones):
    """Option C: the same zones, 1 degree high - fewer Python-level zone loops, more candidates to test."""

    def __init__(self, cat):
        super().__init__(cat, h=1.0)


def adql_cone(ra, dec, radius, table="gaiadr3.gaia_source"):
    """The same question for a TAP service (ADQL 2.1; the coordinate-system argument is optional since 2.1)."""
    return (f"SELECT source_id, ra, dec FROM {table} "
            f"WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra}, {dec}, {radius}))")


def test_cones(n=600, seed=7):
    """Random cones plus the hard cases: 50 near the poles (|dec| > 80) and 50 straddling RA = 0/360."""
    rng = np.random.default_rng(seed)
    ra, dec = rng.uniform(0, 360, n), np.degrees(np.arcsin(rng.uniform(-1, 1, n)))
    dec[:50] = rng.choice([-1, 1], 50) * rng.uniform(80, 89.9, 50)
    ra[50:100] = rng.uniform(-0.3, 0.3, 50) % 360.0
    return list(zip(ra, dec, rng.uniform(0.1, 1.0, n)))


def measure(index, cones, reference=None):
    t0 = time.perf_counter()
    results = [index.query(*c) for c in cones]
    ms = 1000 * (time.perf_counter() - t0) / len(cones)
    wrong = sum(not np.array_equal(a, b) for a, b in zip(results, reference)) if reference else 0
    return results, round(ms, 4), wrong


def main(n=1_000_000):
    cat, cones = make_catalogue(n), test_cones()
    rows, ref = [], None
    for name, cls in (("A brute force", Brute), ("B zones h=0.1", Zones), ("C zones h=1.0", CoarseZones)):
        t0 = time.perf_counter()
        index = cls(cat)
        build = time.perf_counter() - t0
        res, ms, wrong = measure(index, cones, ref)
        ref = ref or res
        rows.append({"option": name, "build_s": round(build, 2), "ms_per_query": ms, "wrong_cones": wrong,
                     "sources_found": int(sum(len(r) for r in res)),
                     "tested_per_query": round(getattr(index, "candidates", n * len(cones)) / len(cones))})
    return rows


if __name__ == "__main__":
    for row in main():
        print(json.dumps(row))
    print(adql_cone(83.82, -5.39, 0.05))
