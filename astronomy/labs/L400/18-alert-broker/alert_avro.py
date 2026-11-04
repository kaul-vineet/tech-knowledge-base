"""Library equivalent (pending-ci): the same packet as an Avro record, validated and round-tripped with fastavro.

pip install -r ../requirements.txt   (fastavro 1.13.1)        python alert_avro.py
Avro is what ZTF and Rubin use on the wire; schema.py validates the JSON form locally.
"""
import importlib.util
import io
from pathlib import Path

from fastavro import parse_schema, reader, writer
from fastavro.validation import validate

HERE = Path(__file__).resolve().parent
AVRO = parse_schema({
    "type": "record", "name": "alert", "namespace": "astro_kb",
    "fields": [{"name": "schemavsn", "type": "string"}, {"name": "candid", "type": "long"},
               {"name": "objectId", "type": "string"}, {"name": "class", "type": "string"},
               {"name": "candidate", "type": {"type": "record", "name": "candidate", "fields": [
                   {"name": n, "type": "double"} for n in ("mjd", "x", "y", "flux", "sigmaflux", "rb", "fwhm")]
                   + [{"name": "isdiffpos", "type": "string"}]}},
               {"name": "prv_candidates", "type": {"type": "array", "items": {"type": "map", "values": "double"}}}]})


def round_trip():
    spec = importlib.util.spec_from_file_location("alerts_fixed", HERE / "solution" / "alerts.py")
    alerts = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(alerts)
    packets = [p for _, _, p in alerts.run("C")]
    assert all(validate(p, AVRO) for p in packets)
    buf = io.BytesIO()
    writer(buf, AVRO, packets, codec="deflate")
    buf.seek(0)
    return len(packets), len(list(reader(buf))), len(buf.getvalue())


if __name__ == "__main__":
    n, back, size = round_trip()
    print(f"{n} alerts validated, {back} read back from a {size}-byte Avro container (deflate)")
