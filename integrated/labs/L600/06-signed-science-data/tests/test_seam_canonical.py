"""Seam S1 (astronomy <-> cryptography): the bytes we hash must not depend on who serialised the floats.
Vectors from RFC 8785 (sections 3.2.2-3.2.4 and Appendix B)."""
import json
import unittest

from _world import world

import canonical as C
import checks
import science

RFC8785_SAMPLE = {"numbers": [333333333.33333329, 1e30, 4.50, 2e-3, 0.000000000000000000000000001],
                  "string": "\u20ac$\u000F\u000aA'\u0042\u0022\u005c\\\"/", "literals": [None, True, False]}
RFC8785_HEX = (  # RFC 8785 section 3.2.4, copied byte for byte
    "7b226c69746572616c73223a5b6e756c6c2c747275652c66616c73655d2c226e756d62657273223a5b33333333333333"
    "33332e333333333333332c31652b33302c342e352c302e3030322c31652d32375d2c22737472696e67223a22e282ac24"
    "5c75303030665c6e4127425c225c5c5c5c5c222f227d")


class SeamCanonical(unittest.TestCase):
    def test_seam(self):
        ok, d = checks.s1_canonical(world())
        self.assertTrue(ok, d)

    def test_rfc8785_section_3_2_4_bytes(self):
        self.assertEqual(C.dumps(RFC8785_SAMPLE).hex(), RFC8785_HEX)

    def test_rfc8785_property_sorting(self):
        obj = {"\u20ac": "Euro Sign", "\r": "Carriage Return", "\ufb33": "Hebrew Letter Dalet With Dagesh", "1": "One",
               "\U0001F600": "Emoji: Grinning Face", "\u0080": "Control", "\u00f6": "Latin Small Letter O With Diaeresis"}
        order = [v for v in json.loads(C.dumps(obj)).values()]
        self.assertEqual(order, ["Carriage Return", "One", "Control", "Latin Small Letter O With Diaeresis",
                                 "Euro Sign", "Emoji: Grinning Face", "Hebrew Letter Dalet With Dagesh"])

    def test_reserialising_is_idempotent_for_every_release(self):
        for v in (1, 2, 3, 4):
            raw = C.dumps(science.catalogue(v))
            self.assertEqual(C.dumps(json.loads(raw)), raw)
            self.assertNotEqual(C.platform_dumps(json.loads(raw)), raw)  # the '%.17g' platform would change it

    def test_strict_parse_rejects_equivalent_but_different_bytes(self):
        raw = C.dumps({"x": 1e30})
        with self.assertRaises(C.NotCanonical):
            C.loads_strict(raw.replace(b"e+30", b"E+30"))  # same value, different bytes
        with self.assertRaises(ValueError):
            C.loads_strict(b'{"a":1,"a":2}')  # duplicate names are not I-JSON

    def test_errors_instead_of_guessing(self):
        for bad in (float("nan"), float("inf"), 2 ** 60, "\ud800"):
            with self.assertRaises((ValueError, TypeError)):
                C.dumps({"v": bad})


if __name__ == "__main__":
    unittest.main()
