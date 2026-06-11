# tests/paths/test_file_tag.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from fastapi import HTTPException, status

from app.paths.file_tag import get_file_tag_path


class TestFileTagPathFromRoute(unittest.TestCase):

    def test_builds_valid_path_request(self):
        out = get_file_tag_path(
            file_id=1,
            tag="important123",
        )

        self.assertEqual(out.file_id, 1)
        self.assertEqual(out.tag, "important123")

    def test_applies_file_id_path_validation(self):
        with self.assertRaises(HTTPException) as cm:
            get_file_tag_path(
                file_id=0,
                tag="important123",
            )

        self.assertEqual(
            cm.exception.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        self.assertEqual(
            cm.exception.detail[0]["loc"],
            ["path", "file_id"],
        )

    def test_applies_tag_path_validation(self):
        with self.assertRaises(HTTPException) as cm:
            get_file_tag_path(
                file_id=1,
                tag="",
            )

        self.assertEqual(
            cm.exception.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        self.assertEqual(
            cm.exception.detail[0]["loc"],
            ["path", "tag"],
        )

    def test_normalizes_case_via_schema(self):
        out = get_file_tag_path(
            file_id=1,
            tag="Important123",
        )

        self.assertEqual(out.tag, "important123")

    def test_accepts_non_latin_letters(self):
        out = get_file_tag_path(
            file_id=1,
            tag="метка123",
        )

        self.assertEqual(out.tag, "метка123")

    def test_accepts_underscores_and_hyphens(self):
        out = get_file_tag_path(
            file_id=1,
            tag="важная_метка-123",
        )

        self.assertEqual(out.tag, "важная_метка-123")

    def test_strips_whitespace_via_schema(self):
        out = get_file_tag_path(
            file_id=1,
            tag="  Important123  ",
        )

        self.assertEqual(out.tag, "important123")

    def test_rejects_invalid_tag_characters(self):
        with self.assertRaises(HTTPException) as cm:
            get_file_tag_path(
                file_id=1,
                tag="invalid.tag",
            )

        self.assertEqual(
            cm.exception.status_code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        self.assertEqual(
            cm.exception.detail[0]["loc"],
            ["path", "tag"],
        )
