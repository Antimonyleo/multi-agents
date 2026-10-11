import unittest
from source import square
class Square(unittest.TestCase):
    def test_square(self):
        self.assertEqual(square(3), 9)
