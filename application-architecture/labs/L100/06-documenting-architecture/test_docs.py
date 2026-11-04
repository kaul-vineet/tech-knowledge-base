import contextlib
import io
import unittest

from check_docs import DOCS, check_adr, check_dsl, check_mermaid, main


class RealDocsTest(unittest.TestCase):
    def test_all_docs_pass(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(main(), 0, out.getvalue())

    def test_expected_files_are_stored_next_to_the_code(self):
        names = {p.name for p in DOCS.iterdir()}
        self.assertTrue({"c4-context.mmd", "c4-container.mmd", "workspace.dsl"} <= names)
        self.assertTrue(any(n.startswith("adr-001") for n in names))


class LintCatchesMistakesTest(unittest.TestCase):
    def test_adr_missing_consequences(self):
        bad = "# ADR 2: Use X\n\n## Context\nc\n\n## Decision\nWe will use X.\n\n## Status\nAccepted.\n"
        self.assertTrue(check_adr(bad))

    def test_adr_bad_status(self):
        bad = "# ADR 2: Use X\n## Context\n## Decision\n## Status\nMaybe\n## Consequences\n"
        self.assertTrue(any("status" in p for p in check_adr(bad)))

    def test_mermaid_undefined_alias(self):
        bad = 'C4Context\n  Person(a, "A")\n  Rel(a, ghost, "Uses")\n'
        self.assertEqual(check_mermaid(bad), ["Rel uses undefined id 'ghost'"])

    def test_dsl_unbalanced_and_undefined(self):
        bad = 'workspace {\n model {\n  u = person "U"\n  u -> nowhere "Uses"\n }\n'
        self.assertEqual(len(check_dsl(bad)), 2)


if __name__ == "__main__":
    unittest.main()
