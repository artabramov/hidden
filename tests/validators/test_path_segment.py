# SPDX-License-Identifier: SSPL-1.0

import unittest
from pydantic_core import PydanticCustomError

from app.validators.path_segment import validate_path_segment


class TestValidatePathSegment(unittest.TestCase):
    def assertInvalidPathSegment(self, value):
        with self.assertRaises(PydanticCustomError) as cm:
            validate_path_segment(value)

        self.assertEqual(cm.exception.type, "value_not_path_segment")

    def assertValidPathSegment(self, value):
        result = validate_path_segment(value)

        self.assertEqual(result, value)

    def test_rejects_dot(self):
        self.assertInvalidPathSegment(".")

    def test_rejects_double_dot(self):
        self.assertInvalidPathSegment("..")

    def test_rejects_forward_slash(self):
        self.assertInvalidPathSegment("foo/bar")

    def test_rejects_leading_forward_slash(self):
        self.assertInvalidPathSegment("/foo")

    def test_rejects_trailing_forward_slash(self):
        self.assertInvalidPathSegment("foo/")

    def test_rejects_only_forward_slash(self):
        self.assertInvalidPathSegment("/")

    def test_rejects_multiple_forward_slashes(self):
        self.assertInvalidPathSegment("foo/bar/baz")

    def test_rejects_backslash(self):
        self.assertInvalidPathSegment("foo\\bar")

    def test_rejects_leading_backslash(self):
        self.assertInvalidPathSegment("\\foo")

    def test_rejects_trailing_backslash(self):
        self.assertInvalidPathSegment("foo\\")

    def test_rejects_only_backslash(self):
        self.assertInvalidPathSegment("\\")

    def test_rejects_multiple_backslashes(self):
        self.assertInvalidPathSegment("foo\\bar\\baz")

    def test_rejects_mixed_separators(self):
        self.assertInvalidPathSegment("foo/bar\\baz")

    def test_rejects_null_byte(self):
        self.assertInvalidPathSegment("foo\x00bar")

    def test_rejects_only_null_byte(self):
        self.assertInvalidPathSegment("\x00")

    def test_rejects_newline(self):
        self.assertInvalidPathSegment("foo\nbar")

    def test_rejects_carriage_return(self):
        self.assertInvalidPathSegment("foo\rbar")

    def test_rejects_tab(self):
        self.assertInvalidPathSegment("foo\tbar")

    def test_rejects_escape_character(self):
        self.assertInvalidPathSegment("foo\x1bbar")

    def test_rejects_unit_separator(self):
        self.assertInvalidPathSegment("foo\x1fbar")

    def test_rejects_all_ascii_control_characters(self):
        for codepoint in range(32):
            value = f"foo{chr(codepoint)}bar"

            with self.subTest(codepoint=codepoint):
                self.assertInvalidPathSegment(value)

    def test_accepts_simple_name(self):
        self.assertValidPathSegment("folder")

    def test_accepts_filename_with_extension(self):
        self.assertValidPathSegment("file.txt")

    def test_accepts_multiple_dots(self):
        self.assertValidPathSegment("archive.tar.gz")

    def test_accepts_inner_dot_segments(self):
        self.assertValidPathSegment("foo..bar")

    def test_accepts_leading_dot_when_not_dot_segment(self):
        self.assertValidPathSegment(".env")

    def test_accepts_trailing_dot(self):
        self.assertValidPathSegment("filename.")

    def test_accepts_spaces(self):
        self.assertValidPathSegment("my folder")

    def test_accepts_leading_space(self):
        self.assertValidPathSegment(" folder")

    def test_accepts_trailing_space(self):
        self.assertValidPathSegment("folder ")

    def test_accepts_only_space(self):
        self.assertValidPathSegment(" ")

    def test_accepts_unicode_cyrillic(self):
        self.assertValidPathSegment("тест")

    def test_accepts_unicode_latin_with_diacritics(self):
        self.assertValidPathSegment("café")

    def test_accepts_unicode_cjk(self):
        self.assertValidPathSegment("資料")

    def test_accepts_unicode_emoji(self):
        self.assertValidPathSegment("folder-📁")

    def test_accepts_dash_underscore_and_parentheses(self):
        self.assertValidPathSegment("my-file_name (copy)")

    def test_accepts_digits(self):
        self.assertValidPathSegment("123456")

    def test_accepts_common_filename_symbols(self):
        self.assertValidPathSegment("report #1 @ draft!.txt")
