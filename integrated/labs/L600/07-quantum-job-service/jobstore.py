"""Job store: chunk leases with fencing tokens, calibration-version epochs, and the result slots a ledger writes.

Leases (distributed-systems L200 #7): every grant takes the next value of ONE counter that only grows, so a later
attempt always carries a higher token than an earlier one. A ledger subclass decides how a chunk result is written:
  new_slot()                 -> an empty result slot for one chunk
  write(slot, token, counts) -> "accepted" | "REJECTED ..."
  read(slot)                 -> counts dict, or None while the chunk has no result
"""


class JobStore:
    def __init__(self):
        self.counter, self.leases, self.jobs = 0, {}, {}

    def open(self, job_id, chunks):
        self.jobs[job_id] = {"chunks": chunks, "version": None, "slots": [self.new_slot() for _ in range(chunks)]}

    def grant(self, job_id, chunk):
        self.counter += 1
        self.leases[(job_id, chunk)] = self.counter
        return self.counter

    def holds(self, job_id, chunk, token):
        return self.leases.get((job_id, chunk)) == token

    def release(self, job_id, chunk):
        self.leases.pop((job_id, chunk), None)

    def chunk_done(self, job_id, chunk):
        return self.read(self.jobs[job_id]["slots"][chunk]) is not None

    def complete(self, job_id):
        return all(self.chunk_done(job_id, c) for c in range(self.jobs[job_id]["chunks"]))

    def commit(self, job_id, chunk, token, version, counts):
        """-> (status, restarted). A newer calibration version restarts the job: one result = one calibration."""
        job, restarted = self.jobs[job_id], False
        if job["version"] is None:
            job["version"] = version
        elif version < job["version"]:
            return f"REJECTED (calibration v{version} < v{job['version']})", False
        elif version > job["version"]:
            job.update(version=version, slots=[self.new_slot() for _ in range(job["chunks"])])
            restarted = True
        return self.write(job["slots"][chunk], token, counts), restarted

    def counts(self, job_id):
        total = {}
        for slot in self.jobs[job_id]["slots"]:
            for k, v in (self.read(slot) or {}).items():
                total[k] = total.get(k, 0) + v
        return total
