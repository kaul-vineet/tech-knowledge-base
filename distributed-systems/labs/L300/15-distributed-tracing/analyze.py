"""Reading spans like a tracing backend does (Jaeger, Grafana): group by trace id, rebuild the tree from parent
ids, find the critical path and report broken traces. Input: span dicts with trace_id, span_id, parent_id,
service, name, start, end (ms)."""
import json


def load_jsonl(text):
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def traces(spans):
    out = {}
    for s in sorted(spans, key=lambda s: s["start"]):
        out.setdefault(s["trace_id"], []).append(s)
    return out


def children(spans, span):
    return sorted((s for s in spans if s["parent_id"] == span["span_id"]), key=lambda s: s["start"])


def critical_path(spans, span):
    """The chain of work that decides when `span` ends. Walk BACKWARD from its end: the child that finished
    last is on the path; continue from that child's start, and so on. Returns [(span, self_ms)]: self time =
    duration minus the children on the path (time spent in the span's own code, or in calls we cannot see)."""
    path, t, covered = [], span["end"], 0.0
    for kid in sorted(children(spans, span), key=lambda k: k["end"], reverse=True):
        if kid["end"] <= t:
            path = critical_path(spans, kid) + path
            covered, t = covered + kid["end"] - kid["start"], kid["start"]
    return [(span, round(span["end"] - span["start"] - covered, 1))] + path


def problems(spans):
    """A healthy request = ONE trace with ONE root, and every parent_id points at a span we have."""
    found, ids = [], {s["span_id"] for s in spans}
    roots = sorted((s for s in spans if s["parent_id"] is None), key=lambda s: s["start"])
    if len(traces(spans)) > 1:
        found.append(f"{len(traces(spans))} trace ids for one request (a hop did not propagate traceparent)")
    found += [f"extra root span: {s['service']} {s['name']} started a new trace" for s in roots[1:]]
    found += [f"orphan: {s['service']} {s['name']} has unknown parent {s['parent_id']}"
              for s in spans if s["parent_id"] and s["parent_id"] not in ids]
    return found
