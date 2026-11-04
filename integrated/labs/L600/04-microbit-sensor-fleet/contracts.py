"""Consumer-driven contracts for the fleet API, with application-architecture L300 #14's ContractBuilder,
like() matcher and body-checking verify_provider() (its solution/contract.py), imported - not copied.

Two consumers: an old dashboard still on /v1 and the new one on /v2. The v2 contract pins the firmware-schema
seam: a schema-1 device (d17) must come back with "schema": 1 and "light": null - not 0, not missing.
"""
import json
import urllib.request
from pathlib import Path

import _kb

cdc = _kb.contract()
like = cdc.like
HERE = Path(__file__).resolve().parent
CONTRACTS = HERE / "contracts"


class Dashboard:
    """The consumer: reads only the fields it shows."""

    def __init__(self, base_url, version):
        self.base, self.v = base_url.rstrip("/"), version

    def tile(self, dev):
        with urllib.request.urlopen("%s/v%d/devices/%s/latest" % (self.base, self.v, dev), timeout=5) as resp:
            b = json.loads(resp.read().decode("utf-8"))
        if self.v == 1:
            return "%s #%d %d C" % (b["device"], b["seq"], b["tempC"])
        light = "n/a (fw %d)" % b["schema"] if b["light"] is None else str(b["light"])
        return "%s %d.%d %d C light %s" % (b["device"], b["boot"], b["seq"], b["tempC"], light)


def build():
    v1 = cdc.ContractBuilder("dashboard-v1", "fleet-api", "1.4.0").interaction(
        "latest reading, v1", "d01 has readings", "GET", "/v1/devices/d01/latest", 200,
        {"device": "d01", "seq": like(1), "tempC": like(20)})
    v2 = cdc.ContractBuilder("dashboard-v2", "fleet-api", "2.0.0").interaction(
        "latest reading of a schema-2 device", "d01 runs firmware schema 2", "GET", "/v2/devices/d01/latest", 200,
        {"device": "d01", "boot": like(1), "seq": like(1), "tempC": like(20), "light": like(100), "schema": 2}
    ).interaction(
        "latest reading of a schema-1 device", "d17 runs firmware schema 1", "GET", "/v2/devices/d17/latest", 200,
        {"device": "d17", "boot": like(1), "seq": like(1), "tempC": like(20), "light": None, "schema": 1})
    return {"v1": v1, "v2": v2}


def consumer_side(folder=CONTRACTS):
    """Run each dashboard against its mock provider (fails if it calls something undeclared), then write the file."""
    paths, tiles = [], []
    for name, builder in build().items():
        with builder.mock_provider() as url:
            dash = Dashboard(url, int(name[1]))
            tiles += [dash.tile(i["request"]["path"].split("/")[3]) for i in builder.contract["interactions"]]
        old = Path(folder) / ("%s--%s.json" % (builder.contract["consumer"], builder.contract["provider"]))
        old.unlink(missing_ok=True)                      # delete-then-write (no in-place overwrite)
        paths.append(builder.write(folder))
    return paths, tiles


def verify(url, folder=CONTRACTS):
    return {p.name: cdc.verify_provider(p, url) for p in sorted(Path(folder).glob("*.json"))}
