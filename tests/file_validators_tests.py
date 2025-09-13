import unittest
from app.validators.file_validators import filename_validate


class FileValidatorsTest(unittest.TestCase):

    def test_filename_valid_basic(self):
        cases = [
            ("doc.pdf", "doc.pdf"),
            (".env", ".env"),
            ("файл.txt", "файл.txt"),
            ("テスト.png", "テスト.png"),
            ("img😀.jpg", "img😀.jpg"),
            ("spaces inside.txt", "spaces inside.txt"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(filename_validate(raw), expected)

    def test_filename_valid_with_trimming(self):
        cases = [
            (" leading.txt", "leading.txt"),
            ("trailing.txt ", "trailing.txt"),
            ("\ttrim\t.pdf\t", "trim\t.pdf"),
            ("  mixed name . md  ", "mixed name . md"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(filename_validate(raw), expected)

    def test_filename_invalid_empty_or_whitespace_only(self):
        for raw in ["", " ", "   ", "\t", "\n"]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    filename_validate(raw)

    def test_filename_invalid_dot_names(self):
        for raw in [".", ".."]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    filename_validate(raw)

    def test_filename_invalid_forbidden_chars(self):
        for raw in ["in/valid.txt", "nul\x00byte", "bad/\x00.txt"]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    filename_validate(raw)

    def test_max_bytes_ascii_boundary(self):
        ok = "a" * 255            # 255 bytes → ok
        bad = "a" * 256           # 256 bytes → fail
        self.assertEqual(filename_validate(ok), ok)
        with self.assertRaises(ValueError):
            filename_validate(bad)

    def test_filename_max_bytes_multibyte_boundary(self):
        # кириллица: ~2 байта/символ
        ok = "я" * 127            # ~254 bytes → ok
        bad = "я" * 128           # ~256 bytes → fail
        self.assertEqual(filename_validate(ok), ok)
        with self.assertRaises(ValueError):
            filename_validate(bad)

    def test_filename_max_bytes_after_trimming(self):
        # до трима длина >255, после трима ≤255 — должно пройти
        raw = " " + ("a" * 255)
        self.assertEqual(filename_validate(raw), "a" * 255)

        # после трима всё ещё >255 — должно упасть
        raw2 = " " + ("a" * 256) + " "
        with self.assertRaises(ValueError):
            filename_validate(raw2)

    def test_filename_trimming_various_whitespace(self):
        # обычные пробелы, табы, переводы строк, NBSP
        cases = [
            ("  name.txt  ", "name.txt"),
            ("\tname.txt\t", "name.txt"),
            ("\nname.txt\n", "name.txt"),
            ("\r\nname.txt\r\n", "name.txt"),
            ("\u00A0name.txt\u00A0", "name.txt"),  # NBSP
        ]
        for raw, expected in cases:
            with self.subTest(raw=repr(raw)):
                self.assertEqual(filename_validate(raw), expected)

    def test_filename_preserve_internal_whitespace_and_backslash(self):
        # внутренние пробелы/табы/бэкслеш сохраняются
        cases = [
            ("in  side.txt", "in  side.txt"),
            ("in\tside.txt", "in\tside.txt"),
            ("back\\slash.txt", "back\\slash.txt"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=repr(raw)):
                self.assertEqual(filename_validate(raw), expected)

    def test_filename_non_string_inputs_raise(self):
        for raw in [None, 123, 3.14, b"bytes"]:
            with self.subTest(raw=repr(raw)):
                with self.assertRaises(ValueError):
                    filename_validate(raw)  # type: ignore[arg-type]

    def test_filename_allows_fullwidth_slash_and_newline_inside(self):
        # разрешаем похожие символы и переводы строк ВНУТРИ имени
        cases = [
            ("fullwidth／slash.txt", "fullwidth／slash.txt"),  # U+FF0F, не '/'
            ("line\nbreak.txt", "line\nbreak.txt"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=repr(raw)):
                self.assertEqual(filename_validate(raw), expected)

    def test_filename_trim_to_dot_or_dotdot_is_invalid(self):
        for raw in [" . ", " .. "]:
            with self.subTest(raw=repr(raw)):
                with self.assertRaises(ValueError):
                    filename_validate(raw)

    def test_filename_mixed_multibyte_boundary(self):
        # 127 'я' (~254 байта) + 'a' (1 байт) = 255 → ок
        ok = "я" * 127 + "a"
        self.assertEqual(filename_validate(ok), ok)
        # добавить ещё один байт → 256 → ошибка
        bad = ok + "a"
        with self.assertRaises(ValueError):
            filename_validate(bad)

    def test_filename_contains_nul_anywhere_invalid(self):
        cases = ["\x00", "a\x00", "\x00b", "pre\x00post.txt"]
        for raw in cases:
            with self.subTest(raw=repr(raw)):
                with self.assertRaises(ValueError):
                    filename_validate(raw)
