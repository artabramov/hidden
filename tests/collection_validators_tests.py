import unittest
from app.validators.collection_validators import (
    name_validate, summary_validate)


class CollectionValidatorsTest(unittest.TestCase):

    def test_name_valid_cases(self):
        cases = [
            ("Inbox", "Inbox"),
            ("коллекция", "коллекция"),
            ("テスト", "テスト"),
            ("emoji📁", "emoji📁"),
            ("with space", "with space"),
            (" spaced ", " spaced "),  # validator does not trim
            ("__", "__"),
            ("_", "_"),
            ("123456", "123456"),
            ("a" * 255, "a" * 255),  # 255 bytes OK; 256 should fail
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(name_validate(raw), expected)

    def test_name_invalid_cases(self):
        cases = [
            "bad/name",
            "/leading",
            "trailing/",
            "nul\x00inside",
            "some/where/else",
        ]
        for raw in cases:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    name_validate(raw)

    def test_name_max_bytes_ascii_boundary(self):
        ok = "a" * 255          # 255 bytes - ok
        bad = "a" * 256         # 256 bytes - fail
        self.assertEqual(name_validate(ok), ok)
        with self.assertRaises(ValueError):
            name_validate(bad)

    def test_name_max_bytes_cyrillic_boundary(self):
        ok = "я" * 127          # 127 * 2 = 254 bytes - ok
        bad = "я" * 128         # 128 * 2 = 256 bytes - fail
        self.assertEqual(name_validate(ok), ok)
        with self.assertRaises(ValueError):
            name_validate(bad)

    def test_name_max_bytes_emoji_boundary(self):
        ok = "😀" * 63           # 63 * 4 = 252 bytes - ok
        bad = "😀" * 64          # 64 * 4 = 256 bytes - fail
        self.assertEqual(name_validate(ok), ok)
        with self.assertRaises(ValueError):
            name_validate(bad)

    def test_name_max_bytes_mixed_boundary(self):
        ok = ("a" * 251) + "😀"   # 251 + 4 = 255 bytes - ok
        bad = ("a" * 252) + "😀"  # 252 + 4 = 256 bytes - fail
        self.assertEqual(name_validate(ok), ok)
        with self.assertRaises(ValueError):
            name_validate(bad)


    def test_summary_to_none(self):
        cases = [
            (None, None),
            ("", None),
            ("   ", None),
            ("\n\t", None),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertIs(summary_validate(raw), expected)

    def test_summary_trim(self):
        cases = [
            (" summary ", "summary"),
            ("  with tabs\t", "with tabs"),
            ("   new\nline   ", "new\nline"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(summary_validate(raw), expected)

    def test_summary_preserve_inner_spaces(self):
        cases = [
            ("a  b   c", "a  b   c"),
            ("many   whitespaces   inside", "many   whitespaces   inside"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(summary_validate(raw), expected)

    def test_summary_max_length(self):
        long_text = "x" * 4096
        self.assertEqual(summary_validate(long_text), long_text)
