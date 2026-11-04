#!/usr/bin/env python3
"""Regenerate kb/.github/workflows/<topic>.yml from <topic>/.github/workflows/labs.yml.

GitHub only runs workflows from <repo root>/.github/workflows. Each topic's labs.yml is written as if
the topic folder were the repository root; this script rewrites it so it runs with kb/ as the root:

  * header comment marks the file as generated; comments about "this folder is the repo root" are dropped
  * name: "<topic> labs"; push/pull_request get paths ['<topic>/**', 'shared/**', '<this workflow>']
  * a top-level DOMAIN_DIR / KB_DIR env var is set to the topic folder
  * every job gets defaults.run.working-directory = the topic folder unless it already has one
  * every working-directory (job default or step) and every path-like `with:` input of a `uses:` step
    (path, cache-dependency-path, *-version-file) is made relative to kb/; hashFiles() args likewise
  * ${{ github.workspace }} / $GITHUB_WORKSPACE point at the topic folder
  * per-topic env renames (ai-agents: BASE_URL -> LOCAL_MODEL_URL, MODEL -> LOCAL_MODEL, incl. $MODEL in scripts)

The rewrite is textual (comments and layout kept); the result is then parsed and compared with an
independent dict-level transformation of the topic file, so a bad rewrite fails loudly.
kb/.github/workflows/shared.yml is not generated and never touched.

Usage (from anywhere; needs PyYAML):
  python kb/tools/sync_root_ci.py            # regenerate all root workflows, then run the path check
  python kb/tools/sync_root_ci.py --check    # write nothing; exit 1 if a root workflow is stale or a path is missing
  python kb/tools/sync_root_ci.py --paths    # only the path check (expands matrices, resolves working dirs)
"""
import argparse
import difflib
import glob
import itertools
import json
import os
import re
import shlex
import sys

import yaml

KB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_VARS = ("DOMAIN_DIR", "KB_DIR")
RENAMES = {"ai-agents": {"BASE_URL": "LOCAL_MODEL_URL", "MODEL": "LOCAL_MODEL"}}
PATH_INPUTS = re.compile(r"^(path|cache-dependency-path|[a-z]+-version-file)$")
DROP = re.compile(r"repo(sitory)? root|Assumes this|If it is nested|If this domain folder|"
                  r"KB_DIR to the folder|move this file|copy this file", re.I)
HEADER = ("# Root-level CI for the {t} topic (GENERATED from {t}/.github/workflows/labs.yml by tools/sync_root_ci.py).\n"
          "# kb/ is the repository root; every job runs inside {t}/. Edit the topic file, then re-run the script.")


def topics():
    return sorted(d for d in os.listdir(KB) if os.path.isfile(os.path.join(KB, d, ".github", "workflows", "labs.yml")))


def indent(line):
    return len(line) - len(line.lstrip(" "))


def is_comment(line):
    return line.lstrip().startswith("#")


# ---------------------------------------------------------------- shared string rewrites
def ctx(topic, data):
    env = data.get("env") or {}
    dirvar = next((k for k in DIR_VARS if k in env), None)
    return {"topic": topic, "dirvar": dirvar,
            "ref": "${{ env.%s }}" % dirvar if dirvar else topic,
            "renames": RENAMES.get(topic, {})}


def prefix_path(v, c):
    s = v.strip()
    if s.startswith("!"):
        return "!" + prefix_path(s[1:], c)
    if s in (".", "./", ""):
        return c["ref"]
    keep = ("/", "~", "${{ github.workspace", "$GITHUB_WORKSPACE", "${GITHUB_WORKSPACE")
    if s.startswith(keep) or re.match(r"^[A-Za-z]:[\\/]", s) or s == c["ref"] or s.startswith(c["ref"] + "/"):
        return s
    if c["dirvar"] and s.startswith("${{ env.%s" % c["dirvar"]):
        return s
    if s.startswith("./"):
        s = s[2:]
    return c["ref"] + "/" + s


def rewrite_string(s, c):
    """Rewrites that apply to any string (run scripts, expressions, env values)."""
    s = s.replace("${{ github.workspace }}", "${{ github.workspace }}/" + c["ref"])
    s = re.sub(r"\$\{GITHUB_WORKSPACE\}|\$GITHUB_WORKSPACE\b", lambda m: m.group(0) + "/" + c["ref"], s)
    s = re.sub(r"hashFiles\(([^)]*)\)", lambda m: "hashFiles(%s)" % re.sub(
        r"'([^']*)'", lambda q: "'%s'" % prefix_path(q.group(1), c), m.group(1)), s)
    for old, new in c["renames"].items():
        s = re.sub(r"(\$\{?|env\.)%s\b" % old, lambda m: m.group(1) + new, s)
    return s


# ---------------------------------------------------------------- textual transformation
def split_value(rest):
    """'  "x"  # c' -> ('x', '"', '# c')"""
    m = re.match(r'^\s*(?:"([^"]*)"|\'([^\']*)\'|([^#]*?))\s*(#.*)?$', rest)
    if m.group(1) is not None:
        return m.group(1), '"', m.group(4) or ""
    if m.group(2) is not None:
        return m.group(2), "'", m.group(4) or ""
    return m.group(3), "", m.group(4) or ""


def join_value(v, q, comment):
    return "%s%s%s%s" % (q, v, q, ("   " + comment) if comment else "")


def transform(topic, text):
    data = yaml.safe_load(text)
    c = ctx(topic, data)
    src = text.splitlines()
    out = [[l] for l in src]           # out[i] = replacement lines for src[i]
    inserts = {}                       # i -> lines to add after src[i]
    top_defaults_wd = bool(((data.get("defaults") or {}).get("run") or {}).get("working-directory"))

    i = 0                              # leading comment block
    while i < len(src) and (not src[i].strip() or is_comment(src[i])):
        if DROP.search(src[i]):
            out[i] = []
        i += 1

    section, jobs_child, cur_job, job_lines = None, None, None, {}
    for i, line in enumerate(src):
        if not line.strip() or (is_comment(line) and section not in ("env",)):
            continue
        ind = indent(line)
        if ind == 0 and not is_comment(line):
            key, rest = line.split(":", 1)
            section = key.strip("'\"")
            if cur_job:
                job_lines[cur_job][1] = i
                cur_job = None
            if section == "name":
                out[i] = ["name: %s labs" % topic]
            elif section == "on" and rest.strip() and not rest.strip().startswith("#"):
                sys.exit("%s: inline 'on:' is not supported" % topic)
            continue
        if section == "on" and ind == 2:
            m = re.match(r"^  (push|pull_request):\s*(.*)$", line)
            if m:
                if m.group(2) and not m.group(2).startswith("#"):
                    sys.exit("%s: inline %s trigger value is not supported" % (topic, m.group(1)))
                j = i + 1
                while j < len(src) and (not src[j].strip() or indent(src[j]) > 2):
                    if re.match(r"^\s+paths(-ignore)?:", src[j]):
                        sys.exit("%s: %s already has a paths filter" % (topic, m.group(1)))
                    j += 1
                inserts.setdefault(i, []).append(
                    "    paths: ['%s/**', 'shared/**', '.github/workflows/%s.yml']" % (topic, topic))
        elif section == "env" and c["dirvar"]:
            if is_comment(line) and DROP.search(line):
                out[i] = []
            elif re.match(r"^\s+%s:" % c["dirvar"], line):
                out[i] = [" " * ind + "# Topic folder relative to the repository root (kb/).",
                          " " * ind + "%s: %s" % (c["dirvar"], topic)]
        elif section == "jobs":
            if jobs_child is None:
                jobs_child = ind
            if ind == jobs_child and re.match(r"^\s*[\w-]+:\s*(#.*)?$", line):
                if cur_job:
                    job_lines[cur_job][1] = i
                cur_job = line.strip().split(":")[0]
                job_lines[cur_job] = [i, len(src)]
    if cur_job:
        job_lines[cur_job][1] = len(src)

    # per-line rules (renames, working-directory, github.workspace, local actions)
    for i, line in enumerate(src):
        if out[i] != [line] or is_comment(line):
            continue
        new = rewrite_string(line, c)
        m = re.match(r"^(\s*(?:- )?)([A-Z_][A-Z0-9_]*)(:.*)$", new)
        if m and m.group(2) in c["renames"]:
            new = m.group(1) + c["renames"][m.group(2)] + m.group(3)
        m = re.match(r"^(\s*(?:- )?working-directory:)\s*(.*)$", new)
        if m:
            v, q, com = split_value(m.group(2))
            new = m.group(1) + " " + join_value(prefix_path(v, c), q, com)
        m = re.match(r"^\s*(?:- )?uses:\s*(\./\S+)", new)
        if m:
            new = new.replace(m.group(1), "./" + prefix_path(m.group(1), c), 1)
        out[i] = [new]

    # path-like `with:` inputs of `uses:` steps
    for i, line in enumerate(src):
        m = re.match(r"^(\s*)(- )?uses:\s*(\S+)", line)
        if not m:
            continue
        keyind = len(m.group(1)) + (2 if m.group(2) else 0)
        item = keyind - 2
        s = i
        while not re.match(r"^ {%d}- " % item, src[s]):
            s -= 1
        end = i + 1
        while end < len(src) and (not src[end].strip() or indent(src[end]) > item):
            end += 1
        for w in range(s, end):
            if not (re.match(r"^\s*(- )?with:\s*(#.*)?$", src[w]) and
                    indent(src[w]) + (2 if src[w].lstrip().startswith("- ") else 0) == keyind):
                continue
            k = w + 1
            while k < end and (not src[k].strip() or indent(src[k]) > keyind):
                km = re.match(r"^(\s*)([\w-]+):(.*)$", src[k])
                if km and PATH_INPUTS.match(km.group(2)):
                    if m.group(3).startswith("actions/checkout"):
                        sys.exit("%s: checkout with path: is not supported" % topic)
                    rest = km.group(3).strip()
                    if rest.startswith(("|", ">")):
                        k += 1
                        while k < end and (not src[k].strip() or indent(src[k]) > len(km.group(1))):
                            if src[k].strip():
                                out[k] = [" " * indent(src[k]) + prefix_path(rewrite_string(src[k], c), c)]
                            k += 1
                        continue
                    v, q, com = split_value(rewrite_string(km.group(3), c))
                    out[k] = ["%s%s: %s" % (km.group(1), km.group(2), join_value(prefix_path(v, c), q, com))]
                k += 1

    # job-level default working directory
    for job, (start, end) in job_lines.items():
        spec = data["jobs"][job] or {}
        if "uses" in spec or top_defaults_wd:
            continue
        if ((spec.get("defaults") or {}).get("run") or {}).get("working-directory"):
            continue
        p = next(indent(src[k]) for k in range(start + 1, end) if src[k].strip() and not is_comment(src[k]))
        d = next((k for k in range(start + 1, end) if re.match(r"^ {%d}defaults:\s*(#.*)?$" % p, src[k])), None)
        if d is not None:
            r = next((k for k in range(d + 1, end) if indent(src[k]) > p and re.match(r"^\s+run:\s*(#.*)?$", src[k])), None)
            if r is not None:
                ci = next(indent(src[k]) for k in range(r + 1, end) if src[k].strip())
                inserts.setdefault(r, []).append(" " * ci + "working-directory: " + c["ref"])
            else:
                ci = indent(src[d + 1])
                inserts.setdefault(d, []).extend([" " * ci + "run:", " " * (2 * ci - p) + "working-directory: " + c["ref"]])
        else:
            after = next((k for k in range(start + 1, end) if re.match(r"^ {%d}runs-on:" % p, src[k])), start)
            inserts.setdefault(after, []).extend([" " * p + "defaults:", " " * (p + 2) + "run:",
                                                  " " * (p + 4) + "working-directory: " + c["ref"]])

    lines = HEADER.format(t=topic).splitlines()
    for i in range(len(src)):
        lines += out[i] + inserts.get(i, [])
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- independent dict-level expectation
def expected(topic, data):
    c = ctx(topic, data)

    def walk(o):
        if isinstance(o, dict):
            return {c["renames"].get(k, k) if isinstance(k, str) else k: walk(v) for k, v in o.items()}
        if isinstance(o, list):
            return [walk(v) for v in o]
        return rewrite_string(o, c) if isinstance(o, str) else o

    d = walk(data)
    d["name"] = "%s labs" % topic
    on = d[True] if True in d else d["on"]                 # PyYAML reads the key `on` as True
    for ev in ("push", "pull_request"):
        if ev in on:
            on[ev] = dict(on[ev] or {}, paths=["%s/**" % topic, "shared/**", ".github/workflows/%s.yml" % topic])
    if c["dirvar"]:
        d["env"][c["dirvar"]] = topic
    top_wd = ((d.get("defaults") or {}).get("run") or {}).get("working-directory")
    if top_wd:
        d["defaults"]["run"]["working-directory"] = prefix_path(top_wd, c)
    for job in d["jobs"].values():
        if "uses" in job:
            continue
        run = (job.get("defaults") or {}).get("run") or {}
        if run.get("working-directory"):
            job["defaults"]["run"]["working-directory"] = prefix_path(run["working-directory"], c)
        elif not top_wd:
            job.setdefault("defaults", {}).setdefault("run", {})["working-directory"] = c["ref"]
        for st in job.get("steps", []):
            if "working-directory" in st:
                st["working-directory"] = prefix_path(st["working-directory"], c)
            if str(st.get("uses", "")).startswith("./"):
                st["uses"] = "./" + prefix_path(st["uses"], c)
            for k, v in (st.get("with") or {}).items():
                if PATH_INPUTS.match(k) and isinstance(v, str):
                    st["with"][k] = "\n".join(prefix_path(x, c) if x.strip() else x for x in v.split("\n"))
    return d


def generate(topic):
    with open(os.path.join(KB, topic, ".github", "workflows", "labs.yml"), encoding="utf-8") as f:
        src_text = f.read()
    new = transform(topic, src_text)
    got, want = yaml.safe_load(new), expected(topic, yaml.safe_load(src_text))
    if got != want:
        a = json.dumps(want, indent=1, sort_keys=True, default=str).splitlines()
        b = json.dumps(got, indent=1, sort_keys=True, default=str).splitlines()
        sys.exit("%s: textual rewrite disagrees with the dict-level expectation:\n%s"
                 % (topic, "\n".join(difflib.unified_diff(a, b, "expected", "generated", lineterm=""))))
    return new


# ---------------------------------------------------------------- path checker
EXT = re.compile(r"\.(py|txt|json|jsonl|js|mjs|robot|ya?ml|toml|sql|mmd|dsl|sh|qasm|html|cfg|ini|md|csv)$")
SEP = {"&&", "||", ";", "|", "&", ";;"}
OUT_OPS = {">", ">>", "&>", "2>", "1>"}


def matrix_combos(strategy):
    m = dict((strategy or {}).get("matrix") or {})
    if not m:
        return [{}]
    inc, exc = m.pop("include", None) or [], m.pop("exclude", None) or []
    keys = list(m)
    combos = [dict(zip(keys, vals)) for vals in itertools.product(*(m[k] for k in keys))] if keys else []
    combos = [cb for cb in combos if not any(all(cb.get(k) == v for k, v in e.items()) for e in exc)]
    for it in inc:
        hits = [cb for cb in combos if all(cb[k] == v for k, v in it.items() if k in keys)]
        for cb in hits:
            cb.update(it)
        if not hits:
            combos.append(dict(it))
    return combos


def subst(s, combo, env, root):
    def rep(m):
        e = m.group(1).strip()
        if e.startswith("matrix."):
            v = combo
            for part in e.split(".")[1:]:
                v = v.get(part, "") if isinstance(v, dict) else ""
            return str(v)
        if e.startswith("env."):
            return str(env.get(e[4:], ""))
        if e == "github.workspace":
            return root
        return "__EXPR__"
    return re.sub(r"\$\{\{(.*?)\}\}", rep, str(s))


def step_runs(cond, combo, os_name):
    """Evaluate simple `if:` conditions (matrix.*, runner.os, ==, !=, &&, ||, !); anything else counts as true."""
    if cond is None or isinstance(cond, bool):
        return cond is not False
    e = re.sub(r"^\$\{\{(.*)\}\}$", r"\1", str(cond).strip())
    runner = {"ubuntu": "Linux", "macos": "macOS", "windows": "Windows"}.get(os_name.split("-")[0], "Linux")

    def val(m):
        if m.group(0) == "runner.os":
            return repr(runner)
        v = combo
        for part in m.group(0).split(".")[1:]:
            v = v.get(part, "") if isinstance(v, dict) else ""
        return repr(v if isinstance(v, (str, int, float, bool)) else "")
    e = re.sub(r"\b(matrix(\.[\w-]+)+|runner\.os)\b", val, e)
    e = re.sub(r"\b(always|success|failure|cancelled)\(\)", "True", e)
    e = re.sub(r"\b(github|inputs|env|vars|needs|steps)(\.[\w-]+)+", "True", e)
    e = e.replace("&&", " and ").replace("||", " or ").replace("!=", "<>").replace("!", " not ").replace("<>", "!=")
    try:
        return bool(eval(e, {"__builtins__": {}}, {"True": True}))
    except Exception:
        return True


def check_run(script, cwd, root, shell, report, where):
    created = set()

    def exists(rel, base):
        p = os.path.normpath(os.path.join(base, rel))
        if any(p == x or p.startswith(x + os.sep) for x in created):
            report["runtime"].add("%s: %s" % (where, os.path.relpath(p, root)))
            return False
        if os.path.exists(p) or glob.glob(p):
            report["checked"] += 1
            return True
        report["missing"].append("%s: %s (cwd %s)" % (where, os.path.relpath(p, root), os.path.relpath(base, root)))
        return False

    def make(rel, base):
        if base and rel and "$" not in rel:
            created.add(os.path.normpath(os.path.join(base, rel)))

    script = re.sub(r"\\\n", " ", script)
    if shell and "pwsh" in shell:
        for tok in re.findall(r"[\w./-]+\.py\b", script):
            exists(tok, cwd)
        return
    cur = cwd
    for raw in script.split("\n"):
        try:
            lex = shlex.shlex(raw, posix=True, punctuation_chars=True)
            lex.whitespace_split = True
            toks = list(lex)
        except ValueError:
            continue
        stack, start, cmd, k = [], True, None, 0
        while k < len(toks):
            t = toks[k]
            if t == "(":
                stack.append(cur); start = True; k += 1; continue
            if t == ")":
                cur = stack.pop() if stack else cur; start = True; k += 1; continue
            if t in SEP:
                start = True; k += 1; continue
            nxt = toks[k + 1] if k + 1 < len(toks) else ""
            if t in OUT_OPS or (t == "tee" and start) or (t == "-o" and cmd == "curl"):
                make(nxt, cur); k += 2; start = False; continue
            if t == "<" and nxt == "(":
                k += 1; continue
            if start:
                start = False
                while re.match(r"^[A-Za-z_]\w*=", t) and k + 1 < len(toks):    # VAR=value cmd
                    k += 1; t = toks[k]
                cmd = t
                if t in ("if", "then", "else", "do", "!"):
                    start = True; k += 1; continue
                if t == "cd":
                    a = toks[k + 1] if k + 1 < len(toks) else ""
                    if cur is None or "$" in a or "__EXPR__" in a or not a:
                        cur = None
                    else:
                        cur = os.path.normpath(os.path.join(cur, a)) if exists(a, cur) else None
                    k += 2; continue
                if t in ("echo", "printf", "exit", "set", "sleep", "export", "for", "docker", "curl", "ollama",
                         "brew", "sudo", "winget", "rustup", "npm", "podman", "command", "ls", "cat"):
                    while k + 1 < len(toks) and toks[k + 1] not in SEP | OUT_OPS | {")", "<"}:
                        if toks[k + 1] == "-o" and k + 2 < len(toks):
                            make(toks[k + 2], cur)
                        k += 1
                k += 1; continue
            if cmd == "mkdir" and not t.startswith("-"):
                make(t, cur); k += 1; continue
            if cmd == "tar" and t == "-C":
                make(nxt, cur); k += 2; continue
            if t.startswith("--") and re.search(r"out|baseline|write|save", t) and nxt and not nxt.startswith("-"):
                make(nxt, cur); k += 2; continue
            if t == "-c" and cmd and cmd.startswith("python"):
                k += 2; continue
            if t == "-m" and nxt == "unittest":
                k += 2
                while k < len(toks) and toks[k] not in SEP | OUT_OPS | {")"}:
                    a = toks[k]
                    if a == "-s" and k + 1 < len(toks):
                        if cur:
                            exists(toks[k + 1], cur)
                        k += 2; continue
                    if not a.startswith("-") and a != "discover" and cur and "$" not in a:
                        exists(a.replace(".", "/") + ".py", cur)
                    k += 1
                continue
            if (cur and "$" not in t and "://" not in t and ":" not in t and "@" not in t and "=" not in t
                    and not t.startswith(("-", "/", "^", "__EXPR__")) and ("/" in t or EXT.search(t))):
                exists(t, cur)
            k += 1


def check_workflow(path, root):
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    env = data.get("env") or {}
    top_wd = ((data.get("defaults") or {}).get("run") or {}).get("working-directory")
    report = {"missing": [], "runtime": set(), "combos": 0, "checked": 0}
    for jid, job in data["jobs"].items():
        for combo in matrix_combos(job.get("strategy")):
            report["combos"] += 1
            jenv = dict(env, **(job.get("env") or {}))
            jrun = (job.get("defaults") or {}).get("run") or {}
            jwd = jrun.get("working-directory", top_wd)
            label = ",".join(str(v.get("dir", v) if isinstance(v, dict) else v)
                             for k, v in combo.items() if k in ("os", "lab", "python"))
            os_name = str(combo.get("os") or subst(job.get("runs-on", "ubuntu-latest"), combo, jenv, root))
            for n, st in enumerate(job.get("steps", [])):
                if not step_runs(st.get("if"), combo, os_name):
                    continue
                where = "%s[%s] step %d" % (jid, label, n + 1)
                wd = st.get("working-directory", jwd)
                cwd = os.path.normpath(os.path.join(root, subst(wd, combo, jenv, root))) if wd else root
                if not os.path.isdir(cwd):
                    report["missing"].append("%s: working-directory %s" % (where, os.path.relpath(cwd, root)))
                    continue
                report["checked"] += 1
                for k, v in (st.get("with") or {}).items():
                    if PATH_INPUTS.match(k) and isinstance(v, str):
                        for line in subst(v, combo, jenv, root).split("\n"):
                            if line.strip() and not glob.glob(os.path.join(root, line.strip())):
                                report["runtime"].add("%s: %s (upload-artifact input)" % (where, line.strip()))
                if "run" in st:
                    check_run(subst(st["run"], combo, dict(jenv, **(st.get("env") or {})), root), cwd, root,
                              st.get("shell") or jrun.get("shell"), report, where)
    return report


def path_check(names, base_of, wf_of):
    ok = True
    for t in names:
        rpt = check_workflow(wf_of(t), base_of(t))
        miss = sorted(set(rpt["missing"]))
        runtime = sorted({r.split(": ", 1)[1] for r in rpt["runtime"]})
        print("  %-26s %3d job x matrix combos, %4d path refs ok, missing %d, runtime-created %d"
              % (t, rpt["combos"], rpt["checked"], len(miss), len(runtime)))
        for m in miss:
            print("      MISSING", m)
        for r in runtime:
            print("      runtime", r)
        ok &= not miss
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="write nothing; fail if a root workflow is stale")
    ap.add_argument("--paths", action="store_true", help="only run the path check")
    ap.add_argument("--topic-files", action="store_true",
                    help="also path-check each topic labs.yml with the topic folder as root (for comparison)")
    a = ap.parse_args()
    wf = os.path.join(KB, ".github", "workflows")
    stale = []
    if not a.paths:
        for t in topics():
            dst = os.path.join(wf, t + ".yml")
            new = generate(t)
            old = None
            if os.path.exists(dst):
                with open(dst, encoding="utf-8") as f:
                    old = f.read()
            if old != new:
                stale.append(t)
                if not a.check:
                    with open(dst, "w", encoding="utf-8", newline="\n") as f:
                        f.write(new)
            state = ("STALE" if a.check else "written") if t in stale else "up to date"
            print("%-10s .github/workflows/%s.yml  jobs: %s" % (state, t, ", ".join(yaml.safe_load(new)["jobs"])))
    print("Path check (root workflows, kb/ as repository root):")
    ok = path_check(topics() + ["shared"], lambda t: KB, lambda t: os.path.join(wf, t + ".yml"))
    if a.topic_files:
        print("Path check (topic labs.yml, topic folder as repository root):")
        path_check(topics(), lambda t: os.path.join(KB, t),
                   lambda t: os.path.join(KB, t, ".github", "workflows", "labs.yml"))
    sys.exit(1 if (a.check and stale) or not ok else 0)


if __name__ == "__main__":
    main()
