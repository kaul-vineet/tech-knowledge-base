"""L500 checks for the micro:bit topic (content/L500.json, lessons 23-27).

1. Runs every theorem check (labs/L500/*/foundations*.py) and asserts it passes AND that its output
   equals the `checkOutput` quoted in content/L500.json (the JSON never carries stale numbers).
2. Recomputes every numeric answer in the problem sets with code and asserts the value appears in the
   written solution; every `calculation` problem must have a recompute entry here.
3. Midterm and final (content/assessment/): every numeric model answer is recomputed.
4. Structure: theorem/problem counts, learning objectives, rubric weights, case study, readings,
   concept-note word ranges, and that every seeAlso names an existing lesson by its exact title.

Run from the topic root:  python research/l500_checks.py    (Windows: py research\\l500_checks.py)  -> OK, exit 0
"""
import importlib.util
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOPIC = os.path.dirname(HERE)
L500 = os.path.join(TOPIC, "labs", "L500")


def load(rel, name):
    path = os.path.join(L500, rel, name + ".py")
    sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


F1 = load("23-digital-foundations", "foundations1")
F2 = load("24-sampling-filters", "foundations2")
F3 = load("25-control-realtime", "foundations3")


def run_check(ref):
    """'labs/.../foundations1.py::check_a and ::check_b' -> list of (ok, line)."""
    mod = {"foundations1.py": F1, "foundations2.py": F2, "foundations3.py": F3}[ref.split("::")[0].split("/")[-1]]
    names = re.findall(r"::(\w+)", ref)
    return [getattr(mod, n)() for n in names]


# ------------------------------------------------------------------ problem-set recomputation
def f(x, nd):
    return "{:,.{}f}".format(x, nd)


def p23_1():
    return [str(F1.decode(0xFE0C, 16))]


def p23_3():
    r_exact, r, i, p_r, p_led = F1.led_resistor(3.3, 1.8, 0.008)
    return [f(r_exact, 1) + " ohm", "%d ohm" % r, f(i * 1e3, 2) + " mA", f(p_r * 1e3, 2) + " mW", f(p_led * 1e3, 2) + " mW",
            f(3.3 * i * 1e3, 2) + " mW"]


def p23_4():
    step = 3.3 / 1024
    n = next(n for n in range(1, 32) if 3.3 / 2 ** n / math.sqrt(12) < 1e-4)
    return [f(step * 1e3, 4) + " mV", f(step / math.sqrt(12) * 1e3, 4) + " mV", f(6.02 * 10 + 1.76, 2) + " dB",
            "N = %d gives %s mV" % (n - 1, f(3.3 / 2 ** (n - 1) / math.sqrt(12) * 1e3, 4)),
            "N = %d gives %s mV" % (n, f(3.3 / 2 ** n / math.sqrt(12) * 1e3, 4)), "so %d bits" % n]


def p23_5():
    return [f(0.25 * 3.3, 3) + " V", f(math.sqrt(0.25) * 3.3, 2) + " V"]


def p23_6():
    avg = 0.002 * 30 + 0.998 * 0.5
    return [f(avg, 3) + " mA", f(1250 / avg, 1) + " h"]


def p23_7():
    good = F1.battery_life_h(1250.0, 30.0, 0.05, 483 * 20, 3600000)
    bad = F1.battery_life_h(1250.0, 30.0, 0.05, 483 * 20, 3607400)
    head_old = F1.battery_life_h(1250.0, 30.0, 0.5, 483 * 20, 3607400)
    head_new = F1.battery_life_h(1250.0, 30.0, 0.5, 483 * 20, 3600000)
    avg = 1250.0 / good
    return [f(avg, 5) + " mA", f(good, 1) + " h", f(bad, 1) + " h", f(head_old, 1) + " h", f(head_new, 1) + " h",
            "{:,}".format(483 * 20) + " ms"]


def p23_8():
    step = 3.3 / 1024
    code = round(1.0 / step)
    return [f(1.0 / step, 1) + " steps", "code %d" % code, f(code * step, 5) + " V", f((code * step - 1.0) * 1e3, 2) + " mV"]


def p24_1():
    return ["= %g Hz" % F2.apparent_frequency(100, fs) for fs in (30, 45, 60)]


def p24_2():
    return ["= %g Hz" % (50 / 2), "= %g Hz" % F2.apparent_frequency(40, 50)]


def p24_3():
    _, line = F2.check_moving_average()
    m = re.search(r"std ([\d.]+) -> ([\d.]+)", line)
    return ["N = %d" % (30 // 10), "std %s to %s" % m.groups(), "(%d ms)" % round(1000 / 30)]


def p24_4():
    n = math.ceil((40 / 5) ** 2)
    return ["N >= (40/5)^2 = %d" % n, "%s samples = %s s" % (f((n - 1) / 2, 1), f((n - 1) / 2 / 50, 2))]


def p24_5():
    a, ts = 0.2, 0.1
    w = math.acos((1 + (1 - a) ** 2 - 2 * a * a) / (2 * (1 - a)))
    return [f(-ts / math.log(1 - a), 3) + " s", "N = (2 - alpha)/alpha = %d" % round((2 - a) / a),
            f(math.sqrt(a / (2 - a)), 3), f((1 + (1 - a) ** 2 - 2 * a * a) / (2 * (1 - a)), 3), f(w, 4) + " rad/sample",
            f(w / (2 * math.pi * ts), 4) + " Hz"]


def p24_8():
    a = 0.2
    return [f(-1 / math.log(1 - a), 2) + " samples", "about %d s" % round(-8 / math.log(1 - a)), "%d %%" % round(100 * (1 - (1 - a) ** 2))]


def p25_1():
    return ["a = e^{-1/60} = %s" % f(F3.A, 5), "b = 20(1 - a) = %s" % f(F3.B, 5), "(1 + a)/b = %s" % f((1 + F3.A) / F3.B, 3)]


def p25_2():
    return ["5/41 = %s C" % f(5 / 41, 3), "5/33 = %s C" % f(5 / 33, 4), "5(1 - 16/20) = %s C" % f(5 * (1 - 16 / 20), 3)]


def p25_4():
    return ["3(2^{1/3} - 1) = %s" % f(F3.ll_bound(3), 4), "5(2^{1/5} - 1) = %s" % f(F3.ll_bound(5), 4),
            "U = 5/20 + 20/1000 + 10/100 = %s" % f(5 / 20 + 20 / 1000 + 10 / 100, 2)]


def p25_5():
    a = [(10, 50), (20, 100), (90, 200)]
    b = [(2, 4), (5, 10)]
    assert F3.rm_first_jobs_meet_deadlines(a) and not F3.rm_first_jobs_meet_deadlines(b)
    finish = rm_finish_time(a, 2)
    return ["U = 0.2 + 0.2 + 0.45 = %s > %s" % (f(sum(c / t for c, t in a), 2), f(F3.ll_bound(3), 4)),
            "tau3 finishes at %d <= 200" % finish, "U = 0.5 + 0.5 = %s" % f(sum(c / t for c, t in b), 1)]


def rm_finish_time(tasks, idx):
    order = sorted(range(len(tasks)), key=lambda i: tasks[i][1])
    rem = {i: tasks[i][0] for i in order}
    for now in range(max(t for _, t in tasks)):
        for i in order:
            if now > 0 and now % tasks[i][1] == 0:
                rem[i] = tasks[i][0] if i != idx else rem[i]
        for i in order:
            if rem[i] > 0:
                rem[i] -= 1
                if i == idx and rem[i] == 0:
                    return now + 1
                break
    return None


def p25_6():
    return ["%d ms blocking + 5 ms own budget = %d ms" % (20 - 1, F3.nonpreemptive_worst_response((5, 20), (20, 1000)))]


def p25_7():
    _, line = F3.check_crc()
    m = re.search(r"length 17: (\d+) undetected in (\d+) positions", line)
    return ["2^{-15} = %.2e" % 2 ** -15, "2^{-16} = %.2e" % 2 ** -16, "each of %s positions" % m.group(2),
            "1 of {:,}".format(2 ** 15)]


def p26_4():
    h = 39 * 7 * 24
    on, ad = math.ceil(h / 41.7), math.ceil(h / 2158.3)
    return ["{:,} h".format(h), "6,552/41.7 = %s" % f(h / 41.7, 1), "%d sets = %d cells" % (on, 2 * on),
            "{:,} cells for 30 boards".format(30 * 2 * on), "6,552/2,158.3 = %s" % f(h / 2158.3, 2),
            "%d sets = %d cells" % (ad, 2 * ad), "%d cells for 30 boards" % (30 * 2 * ad)]


def p27_1():
    return [f(math.log2(1 + 10), 3), f(1e6 * math.log2(11) / 1e6, 3) + " Mbit/s"]


def p27_2():
    return ["5(2^{1/5} - 1) = %s" % f(F3.ll_bound(5), 4), "ln 2 = %s" % f(math.log(2), 4)]


PROBLEMS = {
    "23.1": p23_1, "23.3": p23_3, "23.4": p23_4, "23.5": p23_5, "23.6": p23_6, "23.7": p23_7, "23.8": p23_8,
    "24.1": p24_1, "24.2": p24_2, "24.3": p24_3, "24.4": p24_4, "24.5": p24_5, "24.8": p24_8,
    "25.1": p25_1, "25.2": p25_2, "25.4": p25_4, "25.5": p25_5, "25.6": p25_6, "25.7": p25_7,
    "26.4": p26_4, "27.1": p27_1, "27.2": p27_2,
}


# ------------------------------------------------------------------ exams (content/assessment)
def minus(s):
    return s.replace("-", "\u2212")


def exam_midterm():
    sys.path.insert(0, os.path.join(TOPIC, "labs", "sim_stub"))
    import labtest  # noqa: E402
    lab10 = labtest.load_lab(os.path.join(TOPIC, "labs", "L200", "10-i2c-sensor"), "solution.py")
    raw = (0xE7 << 4) | (0x00 >> 4)
    temp = lab10.decode_temp(0xE7, 0x00)
    avg = 0.003 * 25 + 0.997 * 0.3
    alpha = 2 / (4 + 1)
    return ["= %d" % raw, minus("= -%d steps" % (4096 - raw)), minus("**%.1f °C**" % temp),
            minus("**%.1f °C**" % (-2048 * lab10.LSB_C)), "**%g Hz**" % F2.apparent_frequency(12, 10),
            "k·10/5 = 2, 4 Hz", "the alias moves to %g Hz" % F2.apparent_frequency(13, 10),
            "**%.4f mA**" % avg, "**%s h**" % f(1250 / avg, 1), "(%d %%)" % round(100 * 0.997 * 0.3 / avg),
            "**%g**" % alpha, "%g/%g = %g" % (alpha, 2 - alpha, alpha / (2 - alpha)), "**%g**" % math.sqrt(alpha / (2 - alpha)),
            "**%.3f V**" % (767 / 1023 * 3.3), "%.1f ms of every 20 ms" % (767 / 1023 * 20)]


def exam_final():
    a, b = 0.95, 0.25
    k = b / (1 - a)
    u = 2 / 10 + 4 / 15 + 6 / 30
    return ["= **%g**" % round(k, 9), "%g/%g = **%g**" % (1 + a, b, (1 + a) / b), "3/11 = **%.3f °C**" % (3 / (1 + k * 2)),
            "1 of 2^7 = **1/%d ≈ %.4f**" % (2 ** 7, 2 ** -7), "**%.4f**" % u, "**%.4f**" % F3.ll_bound(3),
            "**%d ms**" % F3.nonpreemptive_worst_response((2, 10), (6, 30)), "= **%g Hz**" % F2.apparent_frequency(50, 8)]


EXAMS = {"content/assessment/midterm.md": exam_midterm, "content/assessment/final.md": exam_final}


# ------------------------------------------------------------------ structure
def lesson_titles():
    titles = {}
    for lv in ("L100", "L200", "L300", "L400", "L500"):
        with open(os.path.join(TOPIC, "content", lv + ".json"), encoding="utf-8") as fh:
            for les in json.load(fh):
                titles[les["number"]] = (lv, les["title"])        # file level (lesson 22 is "Capstone" in L400)
    return titles


def words(path):
    with open(os.path.join(TOPIC, path), encoding="utf-8") as fh:
        return len(fh.read().split())


def main():
    errors = []
    with open(os.path.join(TOPIC, "content", "L500.json"), encoding="utf-8") as fh:
        lessons = json.load(fh)
    titles = lesson_titles()
    n_theorems = n_problems = n_values = 0
    if [les["number"] for les in lessons] != [23, 24, 25, 26, 27]:
        errors.append("lessons must be numbered 23-27")
    for les in lessons:
        num = les["number"]
        if les.get("level") != "L500":
            errors.append("%d: level" % num)
        for key in ("id", "title", "category", "description", "outcome", "estimatedTime", "prerequisites", "glossary",
                    "conceptNote", "conceptSummary", "sources", "seeAlso", "next", "platforms", "validation",
                    "learningObjectives", "problemSet", "rubric"):
            if key not in les:
                errors.append("%d: missing %s" % (num, key))
        if not 3 <= len(les["learningObjectives"]) <= 5:
            errors.append("%d: learningObjectives count" % num)
        if sum(r["weight"] for r in les["rubric"]) != 100:
            errors.append("%d: rubric weights do not sum to 100" % num)
        lo, hi = {23: (900, 1300), 24: (900, 1300), 25: (900, 1300), 26: (700, 1000), 27: (500, 800)}[num]
        if not lo <= words(les["conceptNote"]) <= hi:
            errors.append("%d: concept note %d words (want %d-%d)" % (num, words(les["conceptNote"]), lo, hi))
        for ref in les["seeAlso"]:
            m = re.match(r"microbit (L\d00) #(\d+) (.+)", ref)
            if not m or int(m.group(2)) not in titles or not m.group(3).startswith(titles[int(m.group(2))][1]) \
                    or titles[int(m.group(2))][0] != m.group(1):
                errors.append("%d: seeAlso does not match an exact lesson title: %s" % (num, ref))
        if num <= 25:
            if not 2 <= len(les.get("theorems", [])) <= 4:
                errors.append("%d: need 2-4 theorems" % num)
            for th in les.get("theorems", []):
                n_theorems += 1
                results = run_check(th["check"])
                fresh = "\n".join(line for _, line in results)
                if not all(ok for ok, _ in results):
                    errors.append("%d: theorem check failed: %s" % (num, fresh))
                if fresh != th["checkOutput"]:
                    errors.append("%d: checkOutput is stale for %s\n  json:  %s\n  fresh: %s" % (num, th["name"], th["checkOutput"], fresh))
                for key in ("statement", "proof"):
                    if len(th.get(key, "")) < 40:
                        errors.append("%d: theorem %s too short" % (num, key))
        if num == 26:
            cs = les.get("caseStudy", {})
            for key in ("case", "stakeholders", "questions", "frameworks", "modelAnswer"):
                if not cs.get(key):
                    errors.append("26: caseStudy.%s missing" % key)
        if num == 27:
            rd = les.get("readings", [])
            if len(rd) != 2 or any(len(r["guidingQuestions"]) != 5 or not r["url"] or not r["responsePrompt"] for r in rd):
                errors.append("27: need 2 readings with url, 5 guiding questions and a response prompt")
        if not 6 <= len(les["problemSet"]) <= 10:
            errors.append("%d: problemSet has %d problems (want 6-10)" % (num, len(les["problemSet"])))
        for p in les["problemSet"]:
            n_problems += 1
            if p["type"] not in ("derivation", "proof", "calculation", "short-answer", "essay"):
                errors.append("%s: bad type" % p["id"])
            if p["difficulty"] not in (1, 2, 3) or not isinstance(p["marks"], int):
                errors.append("%s: difficulty/marks" % p["id"])
            if p["type"] == "calculation" and p["id"] not in PROBLEMS:
                errors.append("%s: calculation without a recompute function" % p["id"])
            if p["id"] in PROBLEMS:
                for value in PROBLEMS[p["id"]]():
                    n_values += 1
                    if value not in p["solution"]:
                        errors.append("%s: recomputed %r not found in the solution" % (p["id"], value))
    for path, fn in EXAMS.items():
        with open(os.path.join(TOPIC, path), encoding="utf-8") as fh:
            text = fh.read()
        for value in fn():
            n_values += 1
            if value not in text:
                errors.append("%s: recomputed %r not found" % (path, value))
    for e in errors:
        print("ERROR", e)
    print("lessons %d; theorems checked %d; problems %d; numeric values recomputed %d (incl. midterm/final)"
          % (len(lessons), n_theorems, n_problems, n_values))
    if errors:
        print("FAILED")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
