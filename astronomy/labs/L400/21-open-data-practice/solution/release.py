"""L400 open-data practice: build a citable, licence-correct data release and check it like CI would.

A release folder holds catalogue.vot (VOTable 1.5), CITATION.cff (Citation File Format 1.2.0), LICENSE.txt,
ACKNOWLEDGEMENTS.md (every input's credit text, verbatim), metadata.json (inputs + licences) and MANIFEST.json
(SHA-256 of every file). check() is the fitness function: a list of problems, empty = publishable.
Not legal advice: licence rules here are conservative defaults that flag a release for human review.
python solution/release.py   ->  builds release/ and prints the check
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # helpers live in the lab folder
import inputs  # noqa: E402
import votable  # noqa: E402

HERE = Path(__file__).resolve().parents[1]  # release/ is written in the lab folder
SPDX_OK = {"CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "CC-BY-NC-4.0", "CC-BY-NC-SA-4.0", "MIT", "BSD-3-Clause"}
RESTRICTIVE = ["NC", "SA"]  # restrictions a derived product must keep (CC deeds: NonCommercial, ShareAlike)


def release_licence(ins):
    """Licence of the derived product: keep every restriction an input carries (NonCommercial, ShareAlike) - the
    conservative default; anything the table cannot express goes to a human, never silently to CC-BY."""
    keep = [r for r in RESTRICTIVE if any(r in i["family"].split("-") for i in ins)]
    if keep == ["NC", "SA"]:  # a BY-SA adaptation must stay BY-SA, which allows commercial use: no licence fits both
        raise ValueError("NonCommercial and ShareAlike inputs conflict: needs human review")
    lic = "-".join(["CC-BY", *keep, "4.0"])
    if lic not in SPDX_OK:
        raise ValueError(f"no standard licence keeps {keep}: needs human review")
    return lic


def citation_cff(licence):
    return "\n".join(["cff-version: 1.2.0", 'message: "If you use this catalogue, please cite it as below."',
                      'title: "Astro KB lab 21 example release"', "authors:", '  - family-names: "Learner"',
                      '    given-names: "A."', 'version: "1.0.0"', 'date-released: "2026-10-29"',
                      f"license: {licence}"]) + "\n"


def build(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    lic = release_licence(inputs.INPUTS)
    votable.write(out / "catalogue.vot", inputs.rows())
    (out / "CITATION.cff").write_text(citation_cff(lic), encoding="utf-8")
    (out / "LICENSE.txt").write_text(f"{lic}\n", encoding="utf-8")
    (out / "ACKNOWLEDGEMENTS.md").write_text("\n\n".join(i["credit"] for i in inputs.INPUTS) + "\n", encoding="utf-8")
    meta = {"inputs": [{k: i[k] for k in ("name", "licence", "family")} for i in inputs.INPUTS], "licence": lic}
    (out / "metadata.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    files = sorted(p.name for p in out.iterdir() if p.name != "MANIFEST.json")
    manifest = {f: hashlib.sha256((out / f).read_bytes()).hexdigest() for f in files}
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return out


def cff_keys(text):
    return {line.split(":")[0] for line in text.splitlines() if line and not line.startswith(" ") and ":" in line}


def check(folder):
    """Every problem a reviewer (or CI) would raise; [] = ready to publish."""
    d, problems = Path(folder), []
    manifest = json.loads((d / "MANIFEST.json").read_text(encoding="utf-8"))
    for name, digest in manifest.items():
        if not (d / name).exists() or hashlib.sha256((d / name).read_bytes()).hexdigest() != digest:
            problems.append(f"manifest: {name} missing or changed")
    cff = (d / "CITATION.cff").read_text(encoding="utf-8")
    problems += [f"citation: required key {k!r} missing" for k in ("cff-version", "message", "title", "authors")
                 if k not in cff_keys(cff)]
    meta = json.loads((d / "metadata.json").read_text(encoding="utf-8"))
    lic = (d / "LICENSE.txt").read_text(encoding="utf-8").strip()
    if lic not in SPDX_OK and not lic.startswith("LicenseRef-"):
        problems.append(f"licence: {lic!r} is not an SPDX id")
    for i in meta["inputs"]:
        for r in RESTRICTIVE:
            if r in i["family"].split("-") and f"-{r}" not in lic:
                problems.append(f"licence: release {lic} drops the {r} condition of input {i['name']} ({i['licence']})")
    ack = (d / "ACKNOWLEDGEMENTS.md").read_text(encoding="utf-8")
    problems += [f"credit: verbatim acknowledgement for {i['name']} missing" for i in inputs.INPUTS
                 if i["credit"] not in ack]
    return problems + votable.check(d / "catalogue.vot")


if __name__ == "__main__":
    folder = build(HERE / "release")
    problems = check(folder)
    print("release licence:", (folder / "LICENSE.txt").read_text(encoding="utf-8").strip())
    print(json.dumps({"files": sorted(p.name for p in folder.iterdir()), "problems": problems}, indent=1))
