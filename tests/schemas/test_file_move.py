# tests/schemas/test_file_move.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.file_move import FileMoveRequest, FileMoveResponse


class TestFileMoveRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = FileMoveRequest(folder_id=2)

        self.assertEqual(req.folder_id, 2)

    def test_rejects_zero_folder_id(self):
        with self.assertRaises(ValidationError) as cm:
            FileMoveRequest(folder_id=0)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("folder_id",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_rejects_negative_folder_id(self):
        with self.assertRaises(ValidationError) as cm:
            FileMoveRequest(folder_id=-1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("folder_id",))
        self.assertEqual(error["type"], "greater_than_equal")

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileMoveRequest(folder_id=2, other=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_folder_id(self):
        with self.assertRaises(ValidationError) as cm:
            FileMoveRequest()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("folder_id",))
        self.assertEqual(error["type"], "missing")


class TestFileMoveResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileMoveResponse(
            id=1,
            folder_id=2,
        )

        self.assertEqual(resp.file_id, 1)
        self.assertEqual(resp.folder_id, 2)

    def test_accepts_valid_payload_by_field_name(self):
        resp = FileMoveResponse(
            file_id=1,
            folder_id=2,
        )

        self.assertEqual(resp.file_id, 1)
        self.assertEqual(resp.folder_id, 2)

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileMoveResponse(
                id=1,
                folder_id=2,
                other=1,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_file_id(self):
        with self.assertRaises(ValidationError) as cm:
            FileMoveResponse(folder_id=2)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("id",))
        self.assertEqual(error["type"], "missing")

    def test_requires_folder_id(self):
        with self.assertRaises(ValidationError) as cm:
            FileMoveResponse(id=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("folder_id",))
        self.assertEqual(error["type"], "missing")
