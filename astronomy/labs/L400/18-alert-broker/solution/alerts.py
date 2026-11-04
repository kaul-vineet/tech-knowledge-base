"""L400 time-domain alerts: difference images -> detections -> alert packets -> broker filter + association.

Options: A firehose (every detection is an alert) | B broker classifies and drops bogus | C B + one alert per
object per night with its history (prv_candidates). Code classifies; a local model may only EXPLAIN (agent_assist.py).
python solution/alerts.py   ->  options table + the alerts of the last night as JSON lines
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # helpers live in the lab folder
import alert_sim as sim  # noqa: E402
from schema import validate  # noqa: E402

NSIG, KNOWN_R, MOVE_MIN, MOVE_MAX = 5.0, 1.5, 2.0, 8.0


def blur(img, sigma):
    r = int(np.ceil(4 * sigma))
    k = np.exp(-np.arange(-r, r + 1) ** 2 / (2 * sigma ** 2))
    k /= k.sum()
    tmp = np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode="edge"), k, "valid"), 1, img)
    return np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode="edge"), k, "valid"), 0, tmp)


def difference(new, ref, sigma_new):
    """PSF- and flux-matched difference (Alard & Lupton 1998 with a single Gaussian kernel): blur the sharper
    reference to the new seeing, fit new = a * ref_blurred + b by least squares, subtract. Otherwise every star
    leaves a ring (seeing) and a residual (transparency)."""
    k = np.sqrt(max(sigma_new ** 2 - sim.REF_SIGMA ** 2, 1e-6))
    refc = blur(ref, k)
    A = np.column_stack([refc.ravel(), np.ones(refc.size)])
    (a, b), *_ = np.linalg.lstsq(A, new.ravel(), rcond=None)
    return new - (a * refc + b)


def detect(diff):
    """Positive and negative 3x3 extrema beyond NSIG robust sigmas: x, y, flux (5x5), sharpness, isdiffpos."""
    noise = 1.4826 * np.median(np.abs(diff - np.median(diff)))
    out = []
    for sign in (1, -1):
        d = sign * diff
        p = np.pad(d, 1, constant_values=-np.inf)
        peak = d > NSIG * noise
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy or dx:
                    peak &= d >= p[1 + dy:1 + dy + d.shape[0], 1 + dx:1 + dx + d.shape[1]]
        for y, x in zip(*np.nonzero(peak[3:-3, 3:-3])):
            y, x = y + 3, x + 3
            nb = (d[y - 1, x] + d[y + 1, x] + d[y, x - 1] + d[y, x + 1]) / 4
            out.append({"x": int(x), "y": int(y), "flux": float(sign * d[y - 2:y + 3, x - 2:x + 3].sum()),
                        "sigmaflux": float(5 * noise), "sharp": float(d[y, x] / max(nb, 1e-9)),
                        "isdiffpos": "t" if sign > 0 else "f"})
    return out


def classify(det, other, known):
    """Broker filter: bogus (too sharp / negative), known variable (cross-match), moving (shifted in the other
    exposure of the same night), else transient."""
    if det["sharp"] > 3.0 or det["isdiffpos"] == "f":
        return "bogus"
    if any(np.hypot(det["x"] - kx, det["y"] - ky) < KNOWN_R for _, kx, ky in known):
        return "known_variable"
    gaps = [np.hypot(det["x"] - o["x"], det["y"] - o["y"]) for o in other if o["isdiffpos"] == "t"]
    if not any(g < KNOWN_R for g in gaps) and any(MOVE_MIN <= g <= MOVE_MAX for g in gaps):
        return "moving"
    return "transient"


def packet(candid, det, exp, cls, history):
    return {"schemavsn": "astro-kb-1.0", "candid": candid, "objectId": f"AKB{det['x'] // 2:03d}{det['y'] // 2:03d}",
            "candidate": {"mjd": exp["mjd"], "x": float(det["x"]), "y": float(det["y"]), "flux": round(det["flux"], 1),
                          "sigmaflux": round(det["sigmaflux"], 1), "isdiffpos": det["isdiffpos"],
                          "rb": 0.1 if det["sharp"] > 3.0 else 0.9, "fwhm": round(2.355 * exp["sigma"], 2)},
            "prv_candidates": history, "class": cls}


def run(option, exposures=None, ref=None):
    exposures = exposures or sim.nights()
    ref = sim.reference() if ref is None else ref
    known, alerts, history, candid = sim.known_variables(), [], {}, 0
    for i in range(0, len(exposures), 2):
        pair = exposures[i:i + 2]
        dets = [detect(difference(e["image"], ref, e["sigma"])) for e in pair]
        night_seen = set()
        for k, e in enumerate(pair):
            for d in dets[k]:
                cls = classify(d, dets[1 - k], known)
                if option != "A" and cls == "bogus":
                    continue
                candid += 1
                p = packet(candid, d, e, cls, list(history.get(f"AKB{d['x'] // 2:03d}{d['y'] // 2:03d}", []))[-5:])
                if option == "C":
                    if p["objectId"] in night_seen:
                        continue  # one alert per object per night; the a/b detection is already in history
                    night_seen.add(p["objectId"])
                history.setdefault(p["objectId"], []).append({"mjd": e["mjd"], "flux": p["candidate"]["flux"]})
                alerts.append((e["night"], e["exposure"], p))
    return alerts


def summary(option, alerts, exposures):
    """Alerts per night and the fraction that is real (truth: supernova, variable star, asteroid)."""
    (vx, vy), real = sim.known_variables()[0][1:], 0
    truth = {(e["night"], e["exposure"]): e["truth_asteroid"] for e in exposures}
    for night, expo, p in alerts:
        x, y = p["candidate"]["x"], p["candidate"]["y"]
        ax, ay = truth[(night, expo)]
        real += (night >= 3 and np.hypot(x - sim.SN_POS[0], y - sim.SN_POS[1]) < 2) or np.hypot(x - vx, y - vy) < 2 \
            or np.hypot(x - ax, y - ay) < 2
    nights = len(exposures) // 2
    classes = {}
    for _, _, p in alerts:
        classes[p["class"]] = classes.get(p["class"], 0) + 1
    return {"option": option, "alerts_per_night": round(len(alerts) / nights, 1),
            "real_fraction": round(real / max(len(alerts), 1), 3), "classes": dict(sorted(classes.items())),
            "schema_errors": sum(len(validate(p)) for _, _, p in alerts)}


if __name__ == "__main__":
    exposures, ref = sim.nights(), sim.reference()
    results = {o: run(o, exposures, ref) for o in "ABC"}
    for o in "ABC":
        print(json.dumps(summary(o, results[o], exposures)))
    last = [(n, e, p) for n, e, p in results["C"] if n == 7]
    print(f"option C, night 7: {len(last)} alerts; first 5:")
    for night, expo, p in last[:5]:
        print(json.dumps({"night": night, "exposure": expo, "objectId": p["objectId"], "class": p["class"],
                              "flux": p["candidate"]["flux"], "n_prv": len(p["prv_candidates"])}))
