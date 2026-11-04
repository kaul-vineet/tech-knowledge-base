"""L500 checks: python research/l500_checks.py   -> prints OK and exits 0 when

1. every theorem's `check` command (labs/L500/...) runs and prints exactly the stored `checkOutput`, and
2. every calculation problem's stored `answer` equals the value recomputed here AND appears in its worked solution,
3. every number in the midterm/final model answers (content/assessment) matches a recomputation (EXAMS).

Each PROBLEMS entry: problem id -> function returning the exact answer string.
"""
import json
import math
import shlex
import subprocess
import sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent


# ---------- lesson 23 ----------
def p23_scenario():
    """P1: a local, b send m1 -> P2, c local. P2: d local, e recv m1, f send m2 -> P3. P3: g, h local, i recv m2."""
    lam = [0, 0, 0]
    vec = [[0, 0, 0] for _ in range(3)]
    stamps = {}

    def ev(p, kind, msg=None):
        if kind == "recv":
            t, v = stamps[msg]
            lam[p] = max(lam[p], t) + 1
            vec[p] = [max(x, y) for x, y in zip(vec[p], v)]
        else:
            lam[p] += 1
        vec[p][p] += 1
        if kind == "send":
            stamps[msg] = (lam[p], list(vec[p]))
        return lam[p], tuple(vec[p])

    ev(0, "local"); ev(0, "send", "m1"); c = ev(0, "local")
    ev(1, "local"); ev(1, "recv", "m1"); ev(1, "send", "m2")
    ev(2, "local"); ev(2, "local"); i = ev(2, "recv", "m2")
    leq = all(x <= y for x, y in zip(c[1], i[1]))
    geq = all(x >= y for x, y in zip(c[1], i[1]))
    rel = "concurrent" if not leq and not geq else "ordered"
    return f"L(i) = {i[0]}, V(i) = {i[1]}; c and i are {rel}"


def p23_vectors():
    x, y, z = (2, 0, 1), (1, 1, 1), (2, 1, 1)

    def rel(a, b, na, nb):
        if a != b and all(p <= q for p, q in zip(a, b)):
            return f"{na} -> {nb}"
        if a != b and all(p >= q for p, q in zip(a, b)):
            return f"{nb} -> {na}"
        return f"{na} || {nb}"
    return ", ".join([rel(x, y, "x", "y"), rel(y, z, "y", "z"), rel(x, z, "x", "z")])


def p23_sync_timeout(delta_ms=50, proc_ms=5):
    return f"{2 * delta_ms + proc_ms} ms"


def p23_skew(ppm=50, resync_s=60, err_ms=1):
    return f"{err_ms + 2 * ppm * 1e-6 * resync_s * 1000:g} ms"


# ---------- lesson 24 ----------
def p24_quorum(n=7, r=3):
    w = max(n - r + 1, n // 2 + 1)
    return f"W = {w}"


def p24_tolerance():
    crash = {n: (n - 1) // 2 for n in (5, 6)}
    byz = 3 * 2 + 1
    return f"N = 5 and N = 6 both tolerate {crash[5]} crashes; {byz} nodes for f = 2 Byzantine" \
        if crash[5] == crash[6] else "mismatch"


def p24_paxos_value():
    accepted = {"A1": (2, "x"), "A2": (3, "y"), "A3": None}

    def pick(group):
        prior = [accepted[a] for a in group if accepted[a] is not None]
        return max(prior)[1] if prior else "free"
    return f"{pick(['A1', 'A3'])} with promises from A1 and A3; {pick(['A2', 'A3'])} with promises from A2 and A3"


def p24_raft(n=5):
    maj = n // 2 + 1
    return f"{maj} votes; {'yes' if n - 2 >= maj else 'no'} with 2 down; {'yes' if n - 3 >= maj else 'no'} with 3 down"


# ---------- lesson 25 ----------
def p25_mm1(lam=80, mu=100):
    rho = lam / mu
    big_l = rho / (1 - rho)
    w_ms = 1000 / (mu - lam)
    wq_ms = w_ms - 1000 / mu
    return f"rho = {rho:g}, L = {big_l:g}, W = {w_ms:g} ms, Wq = {wq_ms:g} ms"


def p25_little(rate=2000, latency_s=0.150, threads=64):
    in_flight = rate * latency_s
    return f"L = {in_flight:g} in flight; {math.ceil(in_flight / threads)} instances"


def p25_tail():
    return f"{1 - 0.99 ** 100:.1%} and {1 - 0.999 ** 50:.1%}"


def p25_leaf_quantile(n=100, q=0.99):
    return f"{q ** (1 / n):.6f} (p99.99)"


def p25_amdahl(sigma=0.05, p=16):
    return f"S(16) = {p / (1 + sigma * (p - 1)):.2f}; limit {1 / sigma:g}"


def p25_usl(sigma=0.02, kappa=0.0005):
    def c(p):
        return p / (1 + sigma * (p - 1) + kappa * p * (p - 1))
    best = max(range(1, 1000), key=c)
    return f"p* = {math.sqrt((1 - sigma) / kappa):.1f} (best integer {best}, C = {c(best):.2f})"


def p25_knee(factor=10):
    return f"rho = {1 - 1 / factor:g}"


# ---------- lesson 26 ----------
def p26_budget(avail=0.9995, days=30):
    return f"{(1 - avail) * days * 24 * 60:.1f} minutes"


def p26_aws_window():
    minutes = (14 * 60 + 22) - (7 * 60 + 30)
    budget = (1 - 0.9999) * 365 * 24 * 60
    return f"{minutes} minutes, {minutes / budget:.1f} times the {budget:.1f}-minute annual budget"


def p26_energy(it_kw=40, pue=1.4):
    mwh = it_kw * pue * 8760 / 1000
    return f"{mwh:.1f} MWh per year; {2 * mwh:.1f} MWh with a fully active standby"


# ---------- lesson 27 ----------
def p27_mutex(n=5):
    return f"{3 * (n - 1)} messages"


def p27_clock_bound(d=3, kappa=1e-6, tau_s=1.0, xi_s=0.001):
    return f"{d * (2 * kappa * tau_s + xi_s) * 1000:.3f} ms"


def p27_raft_cluster(n=5):
    return f"majority {n // 2 + 1}, tolerates {n - (n // 2 + 1)} failed servers"


PROBLEMS = {
    "23-P1": p23_scenario, "23-P4": p23_vectors, "23-P6": p23_sync_timeout, "23-P7": p23_skew,
    "24-P1": p24_quorum, "24-P3": p24_tolerance, "24-P6": p24_paxos_value, "24-P8": p24_raft,
    "25-P1": p25_mm1, "25-P2": p25_little, "25-P3": p25_tail, "25-P4": p25_leaf_quantile,
    "25-P5": p25_amdahl, "25-P6": p25_usl, "25-P8": p25_knee,
    "26-P1": p26_budget, "26-P2": p26_aws_window, "26-P5": p26_energy,
    "27-P1": p27_mutex, "27-P4": p27_clock_bound, "27-P5": p27_raft_cluster,
}



# ---------- exams (content/assessment/*.md): every number in a model answer, recomputed ----------
def ex_mid_clocks():
    a = 1; b = a + 1; c = max(0, a) + 1; d = c + 1; e = max(b, d) + 1
    vb, vd = (2, 0), (1, 2)
    ve = tuple(max(x, y) for x, y in zip(vb, vd))
    ve = (ve[0] + 1, ve[1])
    return f"e = max({b}, {d}) + 1 = {e}", f"tick = ({ve[0]},{ve[1]})"


def ex_mid_other():
    stay = sum(1 for k in range(20) if k % 4 == k % 5)
    return (f"3 x 3 x 3 = {3 ** 3} calls", f"reads survive {5 - 2} down, writes survive {5 - 4} down",
            f"{stay}/20 = 1/5 stay and 4/5 = {1 - stay / 20:.0%} move")


def ex_final():
    def usl(p):
        return p / (1 + 0.04 * (p - 1) + 0.001 * p * (p - 1))
    best = max(range(1, 200), key=usl)
    return (f"W = 1/(200 - 160) s = {1000 / (200 - 160):g} ms", f"W = 1/(200 - 80) s = {1000 / (200 - 80):.2f} ms",
            f"1 - 0.995^40 = {1 - 0.995 ** 40:.1%}", f"p <= 1 - 0.99^(1/40) = {1 - 0.99 ** (1 / 40):.6f}",
            f"p* = sqrt(0.96/0.001) = {(0.96 / 0.001) ** 0.5:.1f}", f"C({best}) = {best}/(1 + 0.04 x {best - 1} + 0.001 x {best} x {best - 1}) = {usl(best):.2f}",
            f"21.6 - 15 = {(1 - 0.9995) * 30 * 24 * 60 - 15:.1f} minutes")


EXAMS = {"midterm.md": lambda: ex_mid_clocks() + ex_mid_other(), "final.md": ex_final}

def run_check(cmd):
    parts = shlex.split(cmd)
    script = TOPIC / parts[0]
    out = subprocess.run([sys.executable, script.name, *parts[1:]], cwd=script.parent,
                         capture_output=True, text=True, encoding="utf-8", check=True)
    return out.stdout.strip()


def main():
    lessons = json.loads((TOPIC / "content" / "L500.json").read_text(encoding="utf-8"))
    errors, n_thm, n_calc, used = [], 0, 0, set()
    for lesson in lessons:
        for th in lesson.get("theorems", []):
            n_thm += 1
            got = run_check(th["check"])
            if got != th["checkOutput"].strip():
                errors.append(f"lesson {lesson['number']} {th['name']!r}: check output differs from checkOutput")
        for prob in lesson.get("problemSet", []):
            if prob["type"] != "calculation":
                continue
            fn = PROBLEMS.get(prob["id"])
            if fn is None:
                errors.append(f"{prob['id']}: calculation problem without a PROBLEMS entry")
                continue
            used.add(prob["id"]); n_calc += 1
            want = fn()
            if prob.get("answer") != want:
                errors.append(f"{prob['id']}: stored answer {prob.get('answer')!r} != computed {want!r}")
            if want not in prob["solution"]:
                errors.append(f"{prob['id']}: computed answer {want!r} not in the worked solution")
    n_exam = 0
    for name, fn in EXAMS.items():
        text = (TOPIC / "content" / "assessment" / name).read_text(encoding="utf-8")
        for want in fn():
            n_exam += 1
            if want not in text:
                errors.append(f"{name}: computed {want!r} not found in the model answers")
    for pid in PROBLEMS:
        if pid not in used:
            errors.append(f"PROBLEMS entry never used: {pid}")
    for e in errors:
        print("ERROR", e)
    if errors:
        sys.exit(1)
    print(f"OK: {n_thm} theorem checks reproduced their stored output, {n_calc} calculation answers recomputed, "
          f"{n_exam} exam model-answer numbers recomputed")


if __name__ == "__main__":
    main()
