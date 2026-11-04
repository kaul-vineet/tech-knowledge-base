"""L400 lesson 21, part 2 (python lincheck.py): a Porcupine-style linearizability checker.
Wing & Gong's search with Lowe's memoisation (the algorithm Porcupine implements): walk the history's call/return
entries in time order, try to linearize each pending call against a sequential model, backtrack on a return that
cannot be explained, and cache (linearized set, model state) so no configuration is explored twice. It checks the
lab 17 quorum histories (thousands of operations) that the exhaustive L300 checker cannot."""
import importlib.util, sys, time
from pathlib import Path

LABS = Path(__file__).resolve().parents[2]


def register_step(state, op):
    """Sequential spec of a read/write register: (legal?, next state)."""
    if op["f"] == "write":
        return True, op["value"]
    return op["value"] == state, state


def check(history, step=register_step, init=0):
    """Returns (linearizable, stats): steps taken, cache size, the longest partial linearization and, when the
    history is not linearizable, the earliest-ending operation that no linearization of that length could place."""
    ops = [op for op in history if op["ok"]]
    events = sorted([(op["start"], 0, k) for k, op in enumerate(ops)] + [(op["end"], 1, k) for k, op in enumerate(ops)])
    order, n = [(kind, k) for _, kind, k in events], 2 * len(ops)  # calls sort before returns on equal times
    nxt, prv, top = list(range(1, n + 1)), list(range(-1, n - 1)), [0]  # doubly linked list; top[0] = first entry
    ret_pos = {k: pos for pos, (kind, k) in enumerate(order) if kind == 1}

    def unlink(p):
        if prv[p] < 0:
            top[0] = nxt[p]
        else:
            nxt[prv[p]] = nxt[p]
        if nxt[p] < n:
            prv[nxt[p]] = prv[p]

    def relink(p):  # exact inverse of unlink (dancing links)
        if prv[p] < 0:
            top[0] = p
        else:
            nxt[prv[p]] = p
        if nxt[p] < n:
            prv[nxt[p]] = p

    state, linearized, stack, cache, steps, deepest, pos = init, 0, [], set(), 0, (0, 0), 0
    while top[0] < n:
        steps += 1
        kind, k = order[pos]
        if kind == 0:  # a pending call: can it take effect now, given the model state?
            ok, new_state = step(state, ops[k])
            key = (linearized | 1 << k, new_state)
            if ok and key not in cache:  # memoisation: never explore the same configuration twice
                cache.add(key)
                stack.append((pos, k, state))
                state, linearized = new_state, linearized | 1 << k
                unlink(ret_pos[k])
                unlink(pos)  # lift the call and its return out of the list
                deepest = max(deepest, (len(stack), linearized))
                pos = top[0]
            else:
                pos = nxt[pos]
        else:  # we reached a return whose call is not linearized yet: dead end, backtrack
            if not stack:
                blocker = min((ops[j]["end"], j) for j in range(len(ops)) if not deepest[1] >> j & 1)[1]
                return False, {"steps": steps, "cache": len(cache), "longest": deepest[0], "blocker": ops[blocker]}
            pos, k, state = stack.pop()
            linearized &= ~(1 << k)
            relink(pos)
            relink(ret_pos[k])
            pos = nxt[pos]
    return True, {"steps": steps, "cache": len(cache), "longest": len(ops), "blocker": None}


def load_lab17(name):
    """Import lab 17's quorum.py / solution_quorum.py with lab 17's own helpers.py."""
    lab = LABS / "L400" / "17-consistency-quorums"
    saved = list(sys.path)
    sys.path.insert(0, str(lab))
    sys.modules.pop("helpers", None)
    try:
        spec = importlib.util.spec_from_file_location(f"lab17_{name}", lab / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path[:] = saved
        sys.modules.pop("helpers", None)


if __name__ == "__main__":
    put = lambda c, v, s, e: {"process": c, "f": "write", "value": v, "start": s, "end": e, "ok": True}  # noqa: E731
    get = lambda c, v, s, e: {"process": c, "f": "read", "value": v, "start": s, "end": e, "ok": True}  # noqa: E731
    readme1 = [put("C0", 100, 0, 10), get("C1", 100, 1, 8), get("C2", 0, 2, 5)]  # Porcupine README: linearizable
    readme2 = [put("C0", 200, 0, 10), get("C1", 200, 1, 3), get("C2", 0, 4, 6)]  # Porcupine README: not
    print(f"1) Porcupine README histories: {check(readme1)[0]}, {check(readme2)[0]} (README says true, false)")
    for name, wb in (("quorum", False), ("solution_quorum", True)):
        hist = load_lab17(name).run(2, 2, write_back=wb)
        t = time.perf_counter()
        ok, stats = check(hist)
        ms = round(1000 * (time.perf_counter() - t))
        b = stats["blocker"]
        where = "" if ok else (f"\n   longest partial linearization {stats['longest']} ops; cannot place {b['process']}"
                               f" {b['f']} -> {b['value']} [{b['start']:.1f}, {b['end']:.1f}] ms")
        print(f"2) lab 17 R=2 W=2 write-back={wb}: {len(hist)} ops, linearizable {ok}, {stats['steps']} steps,"
              f" {ms} ms{where}")
