import unittest
import unicodedata
from app.validators.file_validators import name_validate


class FileValidatorsTest(unittest.TestCase):

    # --- Type & empty handling ---

    def test_non_string(self):
        for v in [None, 123, True, b"bytes", ["list"]]:
            with self.assertRaises(ValueError):
                name_validate(v)  # type: ignore[arg-type]

    def test_empty_after_strip_raises(self):
        for s in ["", " ", "\t\n  "]:
            with self.assertRaises(ValueError):
                name_validate(s)

    # --- Special components ---

    def test_dot_and_dotdot_rejected(self):
        for s in [".", ".."]:
            with self.assertRaises(ValueError):
                name_validate(s)

    # --- Invalid characters (portable set) ---

    def test_invalid_chars_rejected(self):
        bad_chars = '<>:"/\\|?*'
        for ch in bad_chars:
            with self.assertRaises(ValueError):
                name_validate(f"foo{ch}bar")

    # --- Control characters ---

    def test_control_chars_rejected(self):
        for ch in ["\x00", "\n", "\r", "\t", "\x1f", "\x7f"]:
            with self.assertRaises(ValueError):
                name_validate(f"foo{ch}bar")

    # --- Trailing dot ---

    def test_trailing_dot_rejected(self):
        with self.assertRaises(ValueError):
            name_validate("readme.")

    # --- Windows reserved names ---

    def test_windows_reserved_rejected_plain(self):
        for s in ["CON", "prn", "Nul", "aux", "COM1", "lpt9"]:
            with self.assertRaises(ValueError):
                name_validate(s)

    def test_windows_reserved_rejected_with_extension(self):
        for s in ["con.txt", "PRN.md", "aux.jpg", "lpt1.doc"]:
            with self.assertRaises(ValueError):
                name_validate(s)

    # --- Length in bytes (UTF-8) ---

    def test_255_bytes(self):
        # ASCII: 255 'a' bytes
        name = "a" * 255
        res = name_validate(name)
        self.assertEqual(res, name)

    def test_256_bytes_rejected(self):
        # ASCII: 256 'a' bytes
        with self.assertRaises(ValueError):
            name_validate("a" * 256)

    def test_multibyte_near_limit(self):
        # 'é' is 2 bytes in UTF-8; 127 of them = 254 bytes
        name = "é" * 127
        self.assertEqual(len(name.encode("utf-8")), 254)
        res = name_validate(name)
        self.assertEqual(res, name)

    # --- Normalization & trimming ---

    def test_unicode_normalization_nfc(self):
        # "e\u0301" (decomposed) should normalize to "é" (NFC)
        decomposed = "Cafe\u0301"
        expected = unicodedata.normalize("NFC", decomposed)
        res = name_validate(decomposed)
        self.assertEqual(res, expected)
        self.assertEqual(unicodedata.normalize("NFC", res), res)

    def test_leading_trailing_whitespace_stripped(self):
        res = name_validate("  report_final  ")
        self.assertEqual(res, "report_final")

    # --- Valid examples ---

    def test_valid_simple_names(self):
        for s in ["file", "file_name-OK", "数据集", "файл", "notes_2025"]:
            res = name_validate(s)
            self.assertEqual(res, s)
