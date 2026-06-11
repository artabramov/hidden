# tests/schemas/test_comment_delete.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import MagicMock

from pydantic import ValidationError

from app.schemas.comment_delete import (
    COMMENT_DELETE_ERRORS,
    CommentDeleteResponse,
)


class TestCommentDeleteResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = CommentDeleteResponse(
            id=1,
        )

        self.assertEqual(resp.comment_id, 1)

    def test_accepts_object_from_attributes(self):
        comment = MagicMock()
        comment.id = 1

        resp = CommentDeleteResponse.model_validate(comment)

        self.assertEqual(resp.comment_id, 1)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            CommentDeleteResponse(
                id=1,
                other=1,
            )

    def test_comment_id_required(self):
        with self.assertRaises(ValidationError) as cm:
            CommentDeleteResponse()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("id",))
        self.assertEqual(error["type"], "missing")


class TestCommentDeleteErrors(unittest.TestCase):

    def test_openapi_error_map_has_expected_statuses(self):
        self.assertEqual(
            set(COMMENT_DELETE_ERRORS),
            {401, 403, 404, 422, 423, 503},
        )
