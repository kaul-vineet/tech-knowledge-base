"""Build-task solution: the 'calls < N' caveat, failing closed on anything else."""


class CallCounter:
    def __init__(self):
        self.used = {}  # (session, caveat) -> calls that passed this caveat

    def check(self, caveat, req):
        kind, op, value = (caveat.split(" ", 2) + ["", ""])[:3]
        if kind != "calls" or op != "<" or not value.isdigit():
            return None  # not ours: stay unknown, so verify() denies (deny by default)
        key = (req["session"], caveat)  # two attenuations ('calls < 5', 'calls < 2') count independently
        if self.used.get(key, 0) >= int(value):
            return False
        self.used[key] = self.used.get(key, 0) + 1
        return True
