# tests/schemas/test_file_upload.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import MagicMock

from pydantic import ValidationError

from app.schemas.file_upload import FileUploadResponse


class TestFileUploadResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileUploadResponse(
            id=1,
        )

        self.assertEqual(resp.file_id, 1)

    def test_accepts_object_from_attributes(self):
        file = MagicMock()
        file.id = 1

        resp = FileUploadResponse.model_validate(file)

        self.assertEqual(resp.file_id, 1)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FileUploadResponse(
                id=1,
                other=1,
            )

    def test_file_id_required(self):
        with self.assertRaises(ValidationError) as cm:
            FileUploadResponse()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("id",))
        self.assertEqual(error["type"], "missing")
