# tests/schemas/test_file_flip.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from pydantic import ValidationError

from app.schemas.file_flip import (
    FileFlipRequest,
    FileFlipResponse,
)


class TestFileFlipRequest(unittest.TestCase):

    def test_accepts_horizontal_axis(self):
        req = FileFlipRequest(axis="horizontal")

        self.assertEqual(req.axis, "horizontal")

    def test_accepts_vertical_axis(self):
        req = FileFlipRequest(axis="vertical")

        self.assertEqual(req.axis, "vertical")

    def test_rejects_invalid_axis(self):
        with self.assertRaises(ValidationError) as cm:
            FileFlipRequest(axis="diagonal")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("axis",))
        self.assertEqual(error["type"], "literal_error")

    def test_rejects_empty_axis(self):
        with self.assertRaises(ValidationError) as cm:
            FileFlipRequest(axis="")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("axis",))
        self.assertEqual(error["type"], "literal_error")

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileFlipRequest(axis="horizontal", other=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_axis(self):
        with self.assertRaises(ValidationError) as cm:
            FileFlipRequest()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("axis",))
        self.assertEqual(error["type"], "missing")


class TestFileFlipResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileFlipResponse(id=1)

        self.assertEqual(resp.file_id, 1)

    def test_accepts_valid_payload_by_field_name(self):
        resp = FileFlipResponse(file_id=1)

        self.assertEqual(resp.file_id, 1)

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileFlipResponse(id=1, other=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_file_id(self):
        with self.assertRaises(ValidationError) as cm:
            FileFlipResponse()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("id",))
        self.assertEqual(error["type"], "missing")
