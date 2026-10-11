import unittest
from source import resolve
class Shape(unittest.TestCase):
    def test_keys(self):
        self.assertEqual(set(resolve({}, {})), {"retries", "deadline_ms"})
