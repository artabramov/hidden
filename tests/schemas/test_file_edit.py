# tests/schemas/test_file_edit.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.file_edit import (
    FileEditRequest,
    FileEditResponse,
)


class TestFileEditRequest(unittest.TestCase):

    def test_accepts_text_content(self):
        req = FileEditRequest(content="hello")

        self.assertEqual(req.content, "hello")

    def test_accepts_empty_content(self):
        req = FileEditRequest(content="")

        self.assertEqual(req.content, "")

    def test_preserves_whitespace_content(self):
        req = FileEditRequest(content="  hello\n")

        self.assertEqual(req.content, "  hello\n")

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileEditRequest(content="hello", other=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_content(self):
        with self.assertRaises(ValidationError) as cm:
            FileEditRequest()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("content",))
        self.assertEqual(error["type"], "missing")


class TestFileEditResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileEditResponse(id=1)

        self.assertEqual(resp.file_id, 1)

    def test_accepts_valid_payload_by_field_name(self):
        resp = FileEditResponse(file_id=1)

        self.assertEqual(resp.file_id, 1)

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileEditResponse(id=1, other=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_file_id(self):
        with self.assertRaises(ValidationError) as cm:
            FileEditResponse()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("id",))
        self.assertEqual(error["type"], "missing")
