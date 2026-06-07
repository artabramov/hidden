# tests/schemas/test_file_starred_change.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import MagicMock

from pydantic import ValidationError

from app.schemas.file_starred_change import (
    FILE_STARRED_ERRORS,
    FileStarredChangeRequest,
    FileStarredChangeResponse,
)


class TestFileStarredChangeRequest(unittest.TestCase):

    def test_accepts_true_value(self):
        req = FileStarredChangeRequest(is_starred=True)

        self.assertIs(req.is_starred, True)

    def test_accepts_false_value(self):
        req = FileStarredChangeRequest(is_starred=False)

        self.assertIs(req.is_starred, False)

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileStarredChangeRequest(is_starred=True, other=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_is_starred(self):
        with self.assertRaises(ValidationError) as cm:
            FileStarredChangeRequest()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("is_starred",))
        self.assertEqual(error["type"], "missing")


class TestFileStarredChangeResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = FileStarredChangeResponse(id=1)

        self.assertEqual(resp.file_id, 1)

    def test_accepts_valid_payload_by_field_name(self):
        resp = FileStarredChangeResponse(file_id=1)

        self.assertEqual(resp.file_id, 1)

    def test_accepts_object_from_attributes(self):
        file = MagicMock()
        file.id = 1

        resp = FileStarredChangeResponse.model_validate(file)

        self.assertEqual(resp.file_id, 1)

    def test_rejects_extra_field(self):
        with self.assertRaises(ValidationError) as cm:
            FileStarredChangeResponse(id=1, other=1)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("other",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_requires_file_id(self):
        with self.assertRaises(ValidationError) as cm:
            FileStarredChangeResponse()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("id",))
        self.assertEqual(error["type"], "missing")


class TestFileStarredChangeErrors(unittest.TestCase):

    def test_openapi_error_map_has_expected_statuses(self):
        self.assertEqual(
            set(FILE_STARRED_ERRORS),
            {401, 403, 404, 422, 503},
        )
