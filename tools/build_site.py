"""Build the knowledge-base website: one self-contained HTML file (works offline, double-click to open,
or host on GitHub Pages). Usage: python tools/build_site.py [--out site/index.html]"""
import base64, gzip, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS = [("quantum-computing", "Quantum Computing"), ("cryptography", "Cryptography"),
          ("ai-agents", "AI Agents"), ("distributed-systems", "Distributed Systems"),
          ("application-architecture", "Application Architecture"), ("microbit", "micro:bit (simulator)"),
          ("simulation", "Simulation"), ("astronomy", "Astronomy & Astrophysics"),
          ("integrated", "Integrated Projects (L600)")]
LEVELS = ["L100", "L200", "L300", "L400", "L500", "L600"]

def read(p):
    p = ROOT / p
    return p.read_text(encoding="utf-8") if p.exists() else ""

def build_data():
    data = {"topics": [], "shared": {"setup": read("shared/WORKSTATION-SETUP.md")}, "meta": json.loads(read("shared/topics.json") or "{}")}
    for slug, name in TOPICS:
        lessons = []
        for lv in LEVELS:
            for l in json.loads(read(f"{slug}/content/{lv}.json") or "[]"):
                l = dict(l)
                l["conceptText"] = read(f"{slug}/{l['conceptNote']}") if l.get("conceptNote") else ""
                l["explainText"] = read(f"{slug}/content/explain/{int(l['number']):02d}.md") if lv != "L600" else ""
                l.pop("conceptNote", None); l.pop("projectFiles", None)
                lessons.append(l)
        qbank = []
        for lv in LEVELS:
            qp = ROOT / slug / "content" / "qbank" / f"{lv}.json"
            if qp.exists():
                qbank += json.loads(qp.read_text(encoding="utf-8"))
        data["topics"].append({"slug": slug, "name": name, "lessons": lessons, "qbank": qbank,
            "primer": read(f"{slug}/documentation/CONCEPTS-PRIMER.md"),
            "tools": read(f"{slug}/documentation/LEARNING-TOOLS.md"),
            "assessment": {k: read(f"{slug}/content/assessment/{k}.md") for k in ("syllabus", "midterm", "final", "capstone-oral-defence", "peer-review-adr", "team-roles")},
            "inventory": json.loads(read(f"{slug}/content/assessment/concept-inventory.json") or "[]"),
            "hardware": read(f"{slug}/documentation/HARDWARE.md")})
    return data

def main():
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else ROOT / "site" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(build_data(), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    blob = base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode("ascii")
    html = (ROOT / "tools" / "site_template.html").read_text(encoding="utf-8").replace("__KB_DATA__", blob)
    if out.exists(): out.unlink()
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size/1e6:.2f} MB)")

if __name__ == "__main__":
    main()
