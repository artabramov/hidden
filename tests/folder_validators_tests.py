import unittest
from app.validators.folder_validators import summary_validate


class FolderValidatorsTest(unittest.TestCase):

    def test_summary_none(self):
        res = summary_validate(None)
        self.assertIsNone(res)

    def test_summary_string_empty(self):
        res = summary_validate("")
        self.assertIsNone(res)

    def test_summary_string_whitespaces(self):
        res = summary_validate("  ")
        self.assertIsNone(res)

    def test_summary_string_stripped(self):
        res = summary_validate(" Hello ")
        self.assertEqual(res, "Hello")
