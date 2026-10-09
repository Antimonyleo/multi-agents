import unittest

from handoff_router import destination


class RoutingTests(unittest.TestCase):
    def test_destinations(self):
        self.assertEqual(destination("session"), "HANDOFF.md")
        self.assertEqual(destination("lesson"), "docs/lessons.md")
        self.assertEqual(destination("result"), "docs/results.md")

    def test_user_text(self):
        self.assertEqual(destination("  LeSsOn \n"), "docs/lessons.md")

    def test_invalid_inputs(self):
        for kind in ("", "unknown", None, ["session"], 1):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                destination(kind)


if __name__ == "__main__":
    unittest.main()
