"""Lab 18 - gateway side: fleet registry and rollout controller (PC, CPython).

Registry: per device the versions this gateway holds an acknowledgement for (K = staged,
A = applied; factory version 1 counts as acknowledged) and the version it last reported.
Rollout: waves of devices. "push-all" = one wave; "staged" = canary (1 device), then 2, then the rest.
A wave passes when every device in it confirmed (A heard, OK sent); any R (rolled back), N (invalid)
or a wave timeout HALTS the rollout: later waves never receive the version.
Works with one-phase devices (config_agent.py: C -> A) and two-phase ones (solution.py: C -> K, G -> A).
"""
import json

RETRY_MS = 300
WAVE_TIMEOUT_MS = 8000


class Fleet:
    def __init__(self, ep, devices, strategy="staged", encode=None, decode=None, log=None):
        self.ep, self.devices, self.strategy = ep, list(devices), strategy
        self.encode, self.decode = encode, decode
        self.acked = dict((d, {1}) for d in self.devices)
        self.reported = dict((d, 1) for d in self.devices)
        self.job, self.sent, self.log = None, 0, log if log is not None else []

    def waves(self):
        d = self.devices
        return [d] if self.strategy == "push-all" else [d[:1], d[1:3], d[3:]]

    def rollout(self, ver, cfg, now):
        self.job = {"ver": ver, "cfg": cfg, "waves": self.waves(), "wave": 0, "status": "running",
                    "start": now, "end": None}
        self._start_wave(now)

    def _start_wave(self, now):
        job = self.job
        job["phase"] = dict((d, "prepare") for d in job["waves"][job["wave"]])
        job["next"], job["wave_start"] = now, now
        self._event(now, "wave", wave=job["wave"], devices=job["waves"][job["wave"]])

    def _event(self, now, kind, **kw):
        self.log.append(json.dumps(dict({"t": now, "event": kind}, **kw), sort_keys=True))

    def _send(self, kind, dev, ver, payload=""):
        self.ep.send(self.encode(kind, dev, ver, payload))
        self.sent += 1

    def on_message(self, msg, now):
        kind, dev, ver, _ = msg
        if dev not in self.acked:
            return
        if kind in ("K", "A"):
            self.acked[dev].add(ver)           # the registry: what this gateway acknowledged
        if kind == "A":
            self.reported[dev] = ver
            self._send("OK", dev, ver)         # confirm (again, if the last OK was lost)
        job = self.job
        if not job or job["status"] != "running" or dev not in job["phase"] or ver != job["ver"]:
            return
        if kind == "K" and job["phase"][dev] == "prepare":
            job["phase"][dev] = "commit"
        elif kind == "A":
            job["phase"][dev] = "confirmed"
        elif kind in ("R", "N"):
            job["phase"][dev] = "failed"
            self._event(now, "device_failed", dev=dev, ver=ver, reason=kind)

    def step(self, now):
        while True:
            text = self.ep.receive()
            if text is None:
                break
            msg = self.decode(text)
            if msg:
                self.on_message(msg, now)
        job = self.job
        if not job or job["status"] != "running":
            return
        phases = job["phase"]
        if "failed" in phases.values() or now - job["wave_start"] > WAVE_TIMEOUT_MS:
            job["status"], job["end"] = "halted", now
            self._event(now, "halted", ver=job["ver"], wave=job["wave"], phases=phases)
            return
        if all(p == "confirmed" for p in phases.values()):
            job["wave"] += 1
            if job["wave"] == len(job["waves"]):
                job["status"], job["end"] = "done", now
                self._event(now, "done", ver=job["ver"])
            else:
                self._start_wave(now)
            return
        if now >= job["next"]:
            for dev, phase in sorted(phases.items()):
                if phase == "prepare":
                    self._send("C", dev, job["ver"], job["cfg"])
                elif phase == "commit":
                    self._send("G", dev, job["ver"])
            job["next"] = now + RETRY_MS
