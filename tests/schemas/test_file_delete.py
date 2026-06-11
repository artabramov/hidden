# tests/schemas/test_file_delete.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import MagicMock

from pydantic import ValidationError

from app.schemas.file_delete import (
    FILE_DELETE_ERRORS,
    FileDeleteResponse,
)


class TestFileDeleteResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileDeleteResponse(
            id=1,
        )

        self.assertEqual(resp.file_id, 1)

    def test_accepts_object_from_attributes(self):
        file = MagicMock()
        file.id = 1

        resp = FileDeleteResponse.model_validate(file)

        self.assertEqual(resp.file_id, 1)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            FileDeleteResponse(
                id=1,
                other=1,
            )

    def test_file_id_required(self):
        with self.assertRaises(ValidationError) as cm:
            FileDeleteResponse()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("id",))
        self.assertEqual(error["type"], "missing")


class TestFileDeleteErrors(unittest.TestCase):

    def test_openapi_error_map_has_expected_statuses(self):
        self.assertEqual(
            set(FILE_DELETE_ERRORS),
            {401, 403, 404, 422, 423, 503},
        )
