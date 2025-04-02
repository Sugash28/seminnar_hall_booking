import unittest
from app import your_function  # Replace with the actual function to test

class TestDateHandling(unittest.TestCase):
    def test_empty_date(self):
        with self.assertRaises(ValueError):
            your_function('')

    def test_invalid_date_format(self):
        with self.assertRaises(ValueError):
            your_function('2021-02-30')

    def test_non_date_string(self):
        with self.assertRaises(ValueError):
            your_function('not-a-date')

if __name__ == '__main__':
    unittest.main()