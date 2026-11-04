"""M2: macaroon-style capability tokens - mint, attenuate, verify, expiry on a fake clock (time-sensitive: run 3x)."""
import unittest

import _lab  # noqa: F401
from adapters import T0, FakeClock
from capability import CapabilityError, TokenService, _pack, attenuate, parse, verify

KEY = b"\x08" * 32


def req(tool="search_docs", now=T0, args=None, session="s-1"):
    return {"session": session, "now": now, "tool": tool, "args": args or {}}


class TestCapabilities(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.svc = TokenService(self.clock, root_key=KEY)
        self.tok = self.svc.session_token("s-1", ["search_docs", "read_file"], ttl=60)

    def test_valid_call(self):
        self.assertEqual(verify(self.tok, KEY, req()), "cap-s-1")

    def test_out_of_scope_tool_and_wrong_session(self):
        for r in (req("send_email"), req(session="s-2")):
            with self.assertRaises(CapabilityError):
                verify(self.tok, KEY, r)

    def test_attenuation_narrows_never_widens(self):
        narrow = attenuate(self.tok, "tool in search_docs")
        verify(narrow, KEY, req())
        with self.assertRaises(CapabilityError):
            verify(narrow, KEY, req("read_file"))
        wider = attenuate(self.tok, "tool in search_docs,send_email")
        with self.assertRaisesRegex(CapabilityError, "tool in search_docs,read_file"):
            verify(wider, KEY, req("send_email"))

    def test_removing_a_caveat_breaks_the_chain(self):
        ident, caveats, sig = parse(self.tok)
        forged = _pack(ident, [c for c in caveats if not c.startswith("expires")], sig)  # drop expiry, keep the old sig
        with self.assertRaisesRegex(CapabilityError, "bad signature"):
            verify(forged, KEY, req())

    def test_expiry_fake_clock_three_runs(self):
        for _ in range(3):
            clock = FakeClock()
            tok = TokenService(clock, root_key=KEY).session_token("s-1", ["search_docs"], ttl=30)
            clock.advance(29)
            verify(tok, KEY, req(now=clock()))
            clock.advance(1)
            with self.assertRaisesRegex(CapabilityError, "expires"):
                verify(tok, KEY, req(now=clock()))

    def test_ttl_above_max_refused(self):
        with self.assertRaises(ValueError):
            self.svc.session_token("s-1", ["search_docs"], ttl=301)

    def test_unknown_caveat_denies(self):
        with self.assertRaisesRegex(CapabilityError, "unknown caveat"):
            verify(attenuate(self.tok, "frobnicate = 1"), KEY, req())


if __name__ == "__main__":
    unittest.main()
