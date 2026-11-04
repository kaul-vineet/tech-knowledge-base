"""python -m unittest -v : traceparent parsing (W3C examples), span analysis, the services and the broken hop."""
import json
import unittest

import tracing
from analyze import critical_path, load_jsonl, problems, traces

W3C_EXAMPLE = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"


def span(sid, parent, start, end, trace="t1", name="x"):
    return {"trace_id": trace, "span_id": sid, "parent_id": parent, "service": name, "name": name, "start": start, "end": end}


class Traceparent(unittest.TestCase):
    def test_valid_and_invalid_headers(self):
        self.assertEqual(tracing.parse_traceparent(W3C_EXAMPLE), ("4bf92f3577b34da6a3ce929d0e0e4736", "00f067aa0ba902b7", "01"))
        for bad in (None, "", W3C_EXAMPLE.upper(), W3C_EXAMPLE.replace("4bf92f3577b34da6a3ce929d0e0e4736", "0" * 32),
                    W3C_EXAMPLE.replace("00f067aa0ba902b7", "0" * 16), W3C_EXAMPLE[:-1]):
            self.assertIsNone(tracing.parse_traceparent(bad), bad)

    def test_versions_w3c_3_2_4(self):
        ids = ("4bf92f3577b34da6a3ce929d0e0e4736", "00f067aa0ba902b7", "01")
        self.assertEqual(tracing.parse_traceparent("cc" + W3C_EXAMPLE[2:] + "-what-the-future-adds"), ids)
        for bad in ("ff" + W3C_EXAMPLE[2:], W3C_EXAMPLE + "-extra"):  # version ff, or extra fields on version 00
            self.assertIsNone(tracing.parse_traceparent(bad), bad)


class Analysis(unittest.TestCase):
    def test_critical_path_walks_back_from_the_end(self):
        spans = [span("a", None, 0, 100), span("b", "a", 10, 90), span("c", "b", 20, 85), span("d", "a", 5, 8)]
        self.assertEqual([(s["span_id"], ms) for s, ms in critical_path(spans, spans[0])],
                         [("a", 17), ("d", 3), ("b", 15), ("c", 65)])  # d ends before b starts: also on the path
        self.assertEqual(problems(spans), [])

    def test_problems_report_split_traces_and_orphans(self):
        spans = [span("a", None, 0, 10), span("b", None, 2, 5, trace="t2"), span("c", "zz", 3, 4)]
        self.assertEqual(len(problems(spans)), 3)
        self.assertEqual(load_jsonl("\n".join(json.dumps(s) for s in spans)), spans)


class Services(unittest.TestCase):
    def test_incoming_context_is_continued(self):
        spans = tracing.run_checkout(headers={"traceparent": W3C_EXAMPLE})
        gw = [s for s in spans if s["service"] == "gateway"][0]
        self.assertEqual((gw["trace_id"], gw["parent_id"]), ("4bf92f3577b34da6a3ce929d0e0e4736", "00f067aa0ba902b7"))

    def test_sampled_flag_is_propagated_unchanged(self):
        seen = []

        class SpyPayments(tracing.Payments):
            routes = {**tracing.Payments.routes,
                      "/receipt": lambda h: (seen.append(h.headers.get("traceparent")), (200, {}))[-1]}

        for flags in ("00", "01"):  # caller did not sample / did sample: W3C 3.2.2.5.1, pass it on
            seen.clear()
            tracing.run_checkout((tracing.Gateway, tracing.Orders, SpyPayments),
                                 headers={"traceparent": W3C_EXAMPLE[:-2] + flags})
            self.assertTrue(seen[0].startswith("00-4bf92f3577b34da6a3ce929d0e0e4736-"), seen)
            self.assertTrue(seen[0].endswith("-" + flags), seen)

    def test_failure_lab_symptom_one_hop_breaks_the_trace(self):
        spans = tracing.run_checkout()
        self.assertEqual(len(spans), 4)
        self.assertEqual(len(traces(spans)), 2)
        auth = [s for s in spans if s["name"] == "GET /authorize"][0]
        self.assertIsNone(auth["parent_id"])  # payments started a new trace
        self.assertTrue(any("did not propagate" in p for p in problems(spans)))


if __name__ == "__main__":
    unittest.main()
