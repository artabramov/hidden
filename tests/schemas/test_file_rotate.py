# tests/schemas/test_file_rotate.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from pydantic import ValidationError

from app.schemas.file_rotate import (
    FileRotateRequest,
    FileRotateResponse,
)


class TestFileRotateRequest(unittest.TestCase):

    def test_accepts_90_degrees(self):
        req = FileRotateRequest(angle=90)

        self.assertEqual(req.angle, 90)

    def test_accepts_180_degrees(self):
        req = FileRotateRequest(angle=180)

        self.assertEqual(req.angle, 180)

    def test_accepts_270_degrees(self):
        req = FileRotateRequest(angle=270)

        self.assertEqual(req.angle, 270)

    def test_rejects_zero_degrees(self):
        with self.assertRaises(ValidationError) as cm:
            FileRotateRequest(angle=0)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("angle",))
        self.assertEqual(error["type"], "literal_error")

    def test_rejects_360_degrees(self):
        with self.assertRaises(ValidationError) as cm:
            FileRotateRequest(angle=360)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("angle",))
        self.assertEqual(error["type"], "literal_error")

    def test_rejects_negative_degrees(self):
        with self.assertRaises(ValidationError) as cm:
            FileRotateRequest(angle=-90)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("angle",))
        self.assertEqual(error["type"], "literal_error")

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileRotateRequest(angle=90, other=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_angle(self):
        with self.assertRaises(ValidationError) as cm:
            FileRotateRequest()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("angle",))
        self.assertEqual(error["type"], "missing")


class TestFileRotateResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileRotateResponse(id=1)

        self.assertEqual(resp.file_id, 1)

    def test_accepts_valid_payload_by_field_name(self):
        resp = FileRotateResponse(file_id=1)

        self.assertEqual(resp.file_id, 1)

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileRotateResponse(id=1, other=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_file_id(self):
        with self.assertRaises(ValidationError) as cm:
            FileRotateResponse()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("id",))
        self.assertEqual(error["type"], "missing")
