import unittest
from durations import normalize
from report import generate

class PublicContract(unittest.TestCase):
    def test_duration_zero_and_units(self):
        self.assertEqual(normalize({"value": 0, "unit": "ms"}), 0)
        self.assertEqual(normalize({"value": 0.125, "unit": "s"}), 125)
        self.assertEqual(normalize({"value": 0.125, "unit": "ms"}), 0.125)

    def test_largest_attempt_controls_state(self):
        result = generate({"attempts": [
            {"job": "j", "attempt": 4, "status": "failed", "duration": {"value": 1, "unit": "s"}},
            {"job": "j", "attempt": 2, "status": "success", "duration": {"value": 2, "unit": "ms"}}]})
        row = result["jobs"][0]
        self.assertEqual((row["last_attempt"], row["state"], row["attempts"]), (4, "failed", 2))
        self.assertEqual(row["duration_ms"], 1002)

    def test_unknown_is_separate_from_known_zero(self):
        result = generate({"attempts": [{"job": "j", "attempt": 1, "status": "stopped"}]})
        self.assertIsNone(result["totals"]["duration_ms"])
        self.assertEqual(result["totals"]["unknown_attempts"], 1)
        self.assertEqual(result["totals"]["known_duration_ms"], 0)

    def test_invalid_duration_is_whole_input_error(self):
        self.assertEqual(generate({"attempts": [{"job": "j", "attempt": 1,
            "status": "success", "duration": {"value": True, "unit": "ms"}}]}), {"error": "invalid_input"})
