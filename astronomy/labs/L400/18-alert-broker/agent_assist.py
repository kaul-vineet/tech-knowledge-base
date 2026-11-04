"""Agent assist (lesson 18): a LOCAL model explains an alert to an observer; code has already classified it.

The model sees only the alert's facts (no images, no keys). Code then checks the explanation: it must name
code's class and no other class, and every number must be one of the facts. Anything else -> not published.
python agent_assist.py            (fake model server, deterministic)
python agent_assist.py --real     (LOCAL_MODEL_URL / LOCAL_MODEL, e.g. Ollama qwen2.5:1.5b)
"""
import argparse
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_agent"))
from client import chat  # noqa: E402

MARKER = "[[ASTRO-ALERT]]"
WORDS = {"transient": ["transient", "supernova"], "known_variable": ["known variable", "variable star"],
         "moving": ["moving", "asteroid"], "bogus": ["bogus", "artefact", "artifact"]}
SYSTEM = "You explain astronomical alerts to observers. You never change the classification."


def facts(p):
    c = p["candidate"]
    return {"candid": p["candid"], "objectId": p["objectId"], "class": p["class"], "flux": c["flux"],
            "sigmaflux": c["sigmaflux"], "magpsf": round(25.0 - 2.5 * math.log10(max(c["flux"], 1e-3)), 2),
            "rb": c["rb"], "fwhm": c["fwhm"], "n_prv": len(p["prv_candidates"])}


def check(text, f):
    """Deterministic gate: class words and numbers. Returns (class_ok, unverified_numbers)."""
    low = text.lower()
    named = {cls for cls, words in WORDS.items() if any(w in low for w in words)}
    known = {re.sub(r"\.0$", "", str(v)) for v in f.values()}
    known |= {n for v in f.values() for n in re.findall(r"\d+(?:\.\d+)?", str(v))}
    tokens = [re.sub(r"\.0$", "", t) for t in re.findall(r"(?<![\w.])\d+(?:\.\d+)?", text)]
    return named == {f["class"]}, [t for t in tokens if t not in known]


def explain(p, base_url=None, model=None):
    f = facts(p)
    block = "\n".join(f"{k}: {v}" for k, v in f.items())
    text = chat([{"role": "system", "content": SYSTEM},
                 {"role": "user", "content": f"{MARKER} Explain this alert in 3 sentences. <facts>\n{block}\n</facts>"}],
                base_url=base_url, model=model)
    class_ok, unverified = check(text, f)
    return {"candid": p["candid"], "code_class": p["class"], "class_ok": class_ok, "unverified": unverified,
            "publish": class_ok and not unverified, "text": text}


def demo_alerts():
    spec = importlib.util.spec_from_file_location("alerts_fixed", HERE / "solution" / "alerts.py")
    alerts = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(alerts)
    out = alerts.run("C")
    picks = {}
    for _, _, p in out:  # the last alert of each class
        picks[p["class"]] = p
    return [picks[c] for c in sorted(picks)]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true")
    args = ap.parse_args()
    server, url = None, None
    if not args.real:
        import fake_model_server
        server, url = fake_model_server.start_in_thread()
    try:
        for p in demo_alerts():
            r = explain(p, base_url=url)
            print(json.dumps({k: r[k] for k in ("candid", "code_class", "class_ok", "unverified", "publish")}))
    finally:
        if server:
            server.shutdown()
            server.server_close()
