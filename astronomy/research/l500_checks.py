"""Verify content/L500.json: every theorem check re-runs and matches its recorded checkOutput, every numeric answer in a
calculation problem (and every number in the midterm/final model answers) is recomputed here and found in the text, and
the lesson structure follows L500-SPEC.

python research/l500_checks.py      (from the astronomy folder; prints OK and exits 0)
Needs Python 3.12+ and numpy. Numbers in checkOutput are compared with a tolerance of 2 units in the last printed digit,
and round-off residuals below 1e-9 always match, so a libm difference on macOS/Windows does not fail the check
while any real change does.
"""
import importlib
import json
import math
import re
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parents[1]
L500 = json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))

AU = 149_597_870_700.0
PC = AU * 648_000.0 / math.pi
MPC_M = PC * 1e6
GM_SUN, GM_EARTH, G = 1.3271244e20, 3.986004e14, 6.67408e-11
C_KM = 299_792.458
GYR = 365.25 * 86_400.0 * 1e9
SIDEREAL_DAY = 86_400.0 * 24.0 / 24.065709824279


def f(x, nd):
    return f"{x:.{nd}f}"


def hubble_time(h0):
    return MPC_M / 1000 / h0 / GYR


def sep_cos_rule_arcsec(sep_arcsec, dec_deg=60.0):
    d = math.radians(dec_deg)
    dra = math.radians(sep_arcsec / 3600) / math.cos(d)
    return math.degrees(math.acos(math.sin(d) ** 2 + math.cos(d) ** 2 * math.cos(dra))) * 3600


def sep_vincenty_arcsec(sep_arcsec, dec_deg=60.0):
    d = math.radians(dec_deg)
    dra = math.radians(sep_arcsec / 3600) / math.cos(d)
    num = math.hypot(math.cos(d) * math.sin(dra), math.cos(d) * math.sin(d) - math.sin(d) * math.cos(d) * math.cos(dra))
    return math.degrees(math.atan2(num, math.sin(d) ** 2 + math.cos(d) ** 2 * math.cos(dra))) * 3600


def hohmann():
    at = (1 + 1.524) / 2
    v = lambda r, a: math.sqrt(GM_SUN * (2 / (r * AU) - 1 / (a * AU))) / 1000
    ve, vm = math.sqrt(GM_SUN / AU) / 1000, math.sqrt(GM_SUN / (1.524 * AU)) / 1000
    return [f(at, 3), f(ve, 2), f(v(1, at), 2), f(v(1, at) - ve, 2), f(v(1.524, at), 2), f(vm, 2), f(vm - v(1.524, at), 2),
            f(0.5 * at ** 1.5, 3), f"{0.5 * at ** 1.5 * 365.25:.0f} days"]


def flat_age(h0=67.4, om=0.315):
    ol = 1 - om
    return 2 / (3 * math.sqrt(ol)) * math.asinh(math.sqrt(ol / om)) * hubble_time(h0)


def posterior(d, v, s, prior=None):
    prec = sum(x * x for x in d) / s ** 2
    num = sum(a * b for a, b in zip(d, v)) / s ** 2
    if prior:
        prec, num = prec + 1 / prior[1] ** 2, num + prior[0] / prior[1] ** 2
    return num / prec, 1 / math.sqrt(prec)


def geo():
    r = (GM_EARTH * (SIDEREAL_DAY / (2 * math.pi)) ** 2) ** (1 / 3) / 1000
    return [f(SIDEREAL_DAY, 4), f(r, 1), f(r - 6378.1, 1)]


def lcar():
    d = 1000 / 2.01
    mu = 5 * math.log10(d) - 5
    return [f(d, 1), f(mu, 2), f(0.20 / 2.01, 3), f(3.724 - 0.52 - mu, 2), f(3.724 - 0.52 - mu - 0.08, 2)]


def cepheid():
    m_abs = -2.43 * 0.5 - 4.05
    mu = 25.0 - m_abs
    return [f(m_abs, 3), f(mu, 3), f"{10 ** (mu / 5 + 1) / 1e6:.2f} Mpc"]


def sn_ia():
    mu = 15.0 + 19.3
    d = 10 ** (mu / 5 + 1) / 1e6
    v = C_KM * 0.0165
    return [f(mu, 1), f"{d:.2f} Mpc", f"{v:.1f} km/s", f"H0 = cz/d = {v / d:.1f}"]


def rho_c():
    h = 67.4 * 1000 / MPC_M
    rho = 3 * h * h / (8 * math.pi * G)
    return [f"{rho:.2e} kg/m^3", f"{rho * MPC_M ** 3 / (GM_SUN / G):.2e} M_sun/Mpc^3"]


def bayes(prior):
    return 0.9 * prior / (0.9 * prior + 0.05 * (1 - prior))


def post3():
    d, v = [10, 20, 40], [750, 1350, 2900]
    m1, s1 = posterior(d, v, 300)
    m2, s2 = posterior(d, v, 300, (67.4, 0.5))
    return [str(sum(a * b for a, b in zip(d, v))), str(sum(x * x for x in d)), f(m1, 3), f(s1, 3), f(m2, 3), f(s2, 3)]


def shadow(h):
    return math.degrees(math.acos(6378.1 / (6378.1 + h)))


# problem id -> strings that must appear verbatim in the worked solution (each recomputed here, never typed by hand)
PROBLEMS = {
    "23.2": geo,
    "23.3": hohmann,
    "23.4": lambda: [f(math.sqrt(2 * GM_EARTH / 6.3781e6) / 1000, 2), f(math.sqrt(2 * GM_SUN / AU) / 1000, 1), f(math.sqrt(GM_SUN / AU) / 1000, 2)],
    "23.6": lambda: [f"{5 * 1e6 ** 2 * MPC_M / GM_SUN:.3e}", f"{MPC_M:.4e}".replace("e+", "e")],
    "23.7": lambda: [f(90 - abs(28.46 - 38.7837), 2), f(90 - (89.2641 - 28.46), 2), f(28.46 - (90 - 89.2641), 2)],
    "23.9": lambda: [f(sep_cos_rule_arcsec(1.0), 6), f(sep_vincenty_arcsec(1.0), 6), f(sep_cos_rule_arcsec(0.01), 6),
                     f"{abs(sep_cos_rule_arcsec(1.0) - 1):.1e}"],
    "24.1": lambda: [f(1.711 ** 2 * (9940 / 5772) ** 4, 1)],
    "24.2": lambda: [f"{math.sqrt(1e5) * (5772 / 3600) ** 2:.0f} R_sun", f"{math.sqrt(1e5) * (5772 / 3600) ** 2 * 6.957e8 / AU:.2f} au"],
    "24.4": lambda: [f(10 * 2 ** -2.5, 2), f(10 * 10 ** -2.5 * 1000, 1)],
    "24.5": lcar,
    "24.6": cepheid,
    "24.7": sn_ia,
    "25.1": lambda: [f(hubble_time(67.4), 2), f(hubble_time(73.0), 2), f"{MPC_M / 1000 / 67.4:.3e} s".replace("e+", "e")],
    "25.2": lambda: [f(3910 / 500, 2), f(3910 / 67.4, 1)],
    "25.3": rho_c,
    "25.4": lambda: [f(flat_age(), 2), f(2 / 3 * hubble_time(67.4), 2)],
    "25.7": lambda: [f(bayes(0.01), 4), f(bayes(0.5), 4)],
    "25.8": post3,
    "26.1": lambda: [f(10 ** 0.8, 2), f(10 ** 1.2, 2)],
    "26.2": lambda: [f(shadow(550), 1), f(shadow(350), 1)],
    "27.1": lambda: [f(hubble_time(500), 2), f"{MPC_M / 1000 / 500:.2e} s".replace("e+", "e")],
    "27.2": lambda: [f(3910 / 500, 2), f(11.8 - (5 * math.log10(7.8e6) - 5), 2)],
    "27.3": lambda: [f"{745 / 1.4:.0f}"],
    "27.5": lambda: [f"{33 / 1500:.1%}".replace("%", " %"), f(34 / 12, 2)],
}

def exam_values():
    """Numbers quoted in the exam model answers that are not already problem-set answers."""
    v_at = lambda r_au: math.sqrt(GM_SUN * (2 / (r_au * AU) - 1 / AU)) / 1000
    t_bound = 365.25 * 24 * (6.957e8 / AU) / math.pi
    d, v = [10, 20, 40], [700, 1500, 2800]
    m1, s1 = posterior(d, v, 300)
    m2, s2 = posterior(d, v, 300, (70.0, 5.0))
    return {
        "midterm.md": [f"{v_at(1):.2f} km/s", f"{v_at(0.1):.1f} km/s", f"{90 - (89.2641 - 28.46):.2f}°", f"{28.46 - (90 - 89.2641):.2f}°",
                       f"{sep_cos_rule_arcsec(0.01):.5f}″", f"{1.711 ** 2 * (9940 / 5772) ** 4:.1f}", f"{2.897771955e-3 / 9940 * 1e9:.1f} nm"]
                      + cepheid() + [f"{math.log(10) / 5 * 0.10 * 100:.1f} %"],
        "final.md": [f"{t_bound:.2f} h", f"{t_bound * (6.27 / 365.25) ** (1 / 3):.2f} h", f"{math.sqrt(4.13):.2f} ×",
                     f"{hubble_time(67.4):.2f} Gyr", f"{flat_age():.2f} Gyr", f"{2 / 3 * hubble_time(67.4):.2f} Gyr",
                     f"{m1:.2f}", f"{s1:.2f}", f"{m2:.2f} ± {s2:.2f}", f"{hubble_time(500):.2f} Gyr", f"{745 / 1.4:.0f}",
                     f"{11.8 - (5 * math.log10(7.8e6) - 5):.2f}", f"{3910 / 500:.2f} Mpc"],
    }


BLOOM = re.compile(r"^(Derive|Prove|Explain|Evaluate|Critique|Analyze|Analyse|Compare|Justify)\b")
NOTE_WORDS = {23: (900, 1300), 24: (900, 1300), 25: (900, 1300), 26: (700, 1000), 27: (500, 800)}
NUM = re.compile(r"[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?")


def numbers_match(expected, actual):
    """Same text between numbers; each number within 2 units of its last printed digit."""
    if NUM.sub("#", expected) != NUM.sub("#", actual):
        return False
    for a, b in zip(NUM.findall(expected), NUM.findall(actual)):
        mant = a.split("e")[0]
        step = 10 ** -(len(mant.split(".")[1]) if "." in mant else 0)
        scale = 10 ** int(a.split("e")[1]) if "e" in a else 1
        if abs(float(a)) < 1e-9 and abs(float(b)) < 1e-9:
            continue  # round-off residuals (e.g. 2.7e-14): any value this small is a pass on every platform
        if abs(float(a) - float(b)) > 2 * step * scale + 1e-12:
            return False
    return True


def earlier_titles():
    titles = {}
    for lv in ("L100", "L200", "L300", "L400"):
        for les in json.loads((TOPIC / "content" / f"{lv}.json").read_text(encoding="utf-8")):
            titles[les["number"]] = les["title"]
    return titles


def main():
    errors, n_theorems, n_numbers = [], 0, 0
    titles = earlier_titles()
    seen_calc = set()
    for les in L500:
        num = les["number"]
        if les["level"] != "L500" or not 23 <= num <= 27:
            errors.append(f"{les['id']}: bad level/number")
        objs = les.get("learningObjectives", [])
        if not 3 <= len(objs) <= 5 or not all(BLOOM.match(o) for o in objs):
            errors.append(f"#{num}: learningObjectives must be 3-5 and start with an understand/analyze/evaluate verb")
        probs = les.get("problemSet", [])
        if not 6 <= len(probs) <= 10:
            errors.append(f"#{num}: {len(probs)} problems (need 6-10)")
        if sum(r["weight"] for r in les.get("rubric", [])) != 100:
            errors.append(f"#{num}: rubric weights do not sum to 100")
        if num <= 25:
            ths = les.get("theorems", [])
            if not 2 <= len(ths) <= 4:
                errors.append(f"#{num}: {len(ths)} theorems (need 2-4)")
            for th in ths:
                path, fn = re.match(r"(\S+) \((\w+)\)", th["check"]).groups()
                lab = TOPIC / Path(path).parent
                sys.path.insert(0, str(lab))
                mod = importlib.import_module(Path(path).stem)
                lines, ok = getattr(mod, fn)()
                n_theorems += 1
                if not ok:
                    errors.append(f"#{num} {th['name']}: check reports FAIL")
                if not numbers_match(th["checkOutput"], "\n".join(lines)):
                    errors.append(f"#{num} {th['name']}: recorded checkOutput differs from a fresh run")
        if num == 26:
            cs = les.get("caseStudy", {})
            if not all(cs.get(k) for k in ("case", "stakeholders", "questions", "frameworks", "modelAnswer")):
                errors.append("#26: caseStudy incomplete")
        if num == 27:
            rd = les.get("readings", [])
            if len(rd) != 2 or any(len(r["guidingQuestions"]) != 5 or not r.get("responsePrompt") for r in rd):
                errors.append("#27: need 2 readings with 5 guiding questions and a response prompt each")
        for p in probs:
            if p["type"] not in {"derivation", "proof", "calculation", "short-answer", "essay"} or p["difficulty"] not in (1, 2, 3):
                errors.append(f"{p['id']}: bad type/difficulty")
            if p["type"] == "calculation":
                seen_calc.add(p["id"])
                if p["id"] not in PROBLEMS:
                    errors.append(f"{p['id']}: calculation without a recomputation")
                    continue
                for s in PROBLEMS[p["id"]]():
                    n_numbers += 1
                    if s not in p["solution"]:
                        errors.append(f"{p['id']}: recomputed {s!r} not found in the solution")
        note = TOPIC / les["conceptNote"]
        if not note.exists():
            errors.append(f"#{num}: missing {les['conceptNote']}")
        else:
            words = len(note.read_text(encoding="utf-8").split())
            lo, hi = NOTE_WORDS[num]
            if not lo <= words <= hi:
                errors.append(f"#{num}: concept note has {words} words (want {lo}-{hi})")
        for ref in les.get("seeAlso", []):
            m = re.match(r"astronomy L\d00 #(\d+) ", ref)
            if not m or not ref[m.end():].startswith(f"{titles.get(int(m.group(1)))}: "):
                errors.append(f"#{num}: seeAlso title mismatch: {ref[:70]}")
        for pf in les.get("projectFiles", []):
            if not (TOPIC / pf["path"]).exists():
                errors.append(f"#{num}: missing project file {pf['path']}")
    for name, values in exam_values().items():
        text = (TOPIC / "content" / "assessment" / name).read_text(encoding="utf-8").replace("\u2212", "-")
        for val in values:
            n_numbers += 1
            if val not in text:
                errors.append(f"assessment/{name}: recomputed {val!r} not found in the model answers")
    for pid in sorted(set(PROBLEMS) - seen_calc):
        errors.append(f"{pid}: in PROBLEMS but not a calculation problem")
    print(f"lessons {len(L500)} | theorem checks re-run and matched: {n_theorems} | problem numbers recomputed: {n_numbers} "
          f"in {len(seen_calc)} calculation problems + 2 exams | problems total {sum(len(x['problemSet']) for x in L500)}")
    for e in errors:
        print("ERROR", e)
    if errors:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
