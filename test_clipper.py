import unittest
from pathlib import Path
from clipper import sanitize_filename

class TestClipper(unittest.TestCase):
    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename("Hello World!"), "Hello_World_")
        self.assertEqual(sanitize_filename("test/file:name"), "test_file_name")
        self.assertEqual(sanitize_filename("valid_name.123"), "valid_name.123")
        self.assertEqual(sanitize_filename("  spaces  "), "__spaces__")

if __name__ == "__main__":
    unittest.main()
