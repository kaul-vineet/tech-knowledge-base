"""Minimal VOTable (TABLEDATA serialisation) writer and checker - stdlib xml only.

Checks what a reader relies on: FIELD name/datatype/unit/ucd, as many TD per TR as FIELDs, values parse as their
datatype. STILTS votlint and astropy.io.votable do the full schema validation in CI (pending-ci).
"""
import xml.etree.ElementTree as ET

NS = "http://www.ivoa.net/xml/VOTable/v1.3"
FIELDS = [("source_id", "long", "", "meta.id;meta.main"), ("ra", "double", "deg", "pos.eq.ra;meta.main"),
          ("dec", "double", "deg", "pos.eq.dec;meta.main"), ("parallax", "double", "mas", "pos.parallax"),
          ("tmag", "double", "mag", "phot.mag"), ("period_d", "double", "d", "time.period")]
PARSE = {"long": int, "int": int, "double": float, "float": float, "char": str}


def write(path, rows, fields=FIELDS):
    root = ET.Element("VOTABLE", {"version": "1.5", "xmlns": NS})
    table = ET.SubElement(ET.SubElement(root, "RESOURCE"), "TABLE", {"name": "release"})
    for name, dtype, unit, ucd in fields:
        attrs = {"name": name, "datatype": dtype, "ucd": ucd}
        if unit:
            attrs["unit"] = unit
        ET.SubElement(table, "FIELD", attrs)
    data = ET.SubElement(ET.SubElement(table, "DATA"), "TABLEDATA")
    for r in rows:
        tr = ET.SubElement(data, "TR")
        for name, *_ in fields:
            ET.SubElement(tr, "TD").text = str(r[name])
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def check(path):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        return [f"votable: not well-formed XML ({e})"]
    q = lambda tag: f"{{{NS}}}{tag}"  # noqa: E731
    problems, fields = [], root.findall(f".//{q('FIELD')}")
    for f in fields:
        if f.get("datatype") not in PARSE:
            problems.append(f"votable: FIELD {f.get('name')} has datatype {f.get('datatype')!r}")
        if f.get("datatype") != "char" and not f.get("unit") and "meta.id" not in (f.get("ucd") or ""):
            problems.append(f"votable: FIELD {f.get('name')} has no unit")
        if not f.get("ucd"):
            problems.append(f"votable: FIELD {f.get('name')} has no ucd")
    for i, tr in enumerate(root.findall(f".//{q('TR')}")):
        tds = tr.findall(q("TD"))
        if len(tds) != len(fields):
            problems.append(f"votable: row {i} has {len(tds)} TD for {len(fields)} FIELD")
            continue
        for f, td in zip(fields, tds):
            try:
                PARSE.get(f.get("datatype"), str)(td.text)
            except (TypeError, ValueError):
                problems.append(f"votable: row {i} {f.get('name')}={td.text!r} is not {f.get('datatype')}")
    return problems
