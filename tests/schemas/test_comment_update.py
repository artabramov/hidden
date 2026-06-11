# tests/schemas/test_comment_update.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import MagicMock

from pydantic import ValidationError

from app.schemas.comment_update import (
    COMMENT_UPDATE_ERRORS,
    CommentUpdateRequest,
    CommentUpdateResponse,
)


class TestCommentUpdateRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = CommentUpdateRequest(
            body="Updated comment body.",
        )

        self.assertEqual(req.body, "Updated comment body.")

    def test_strips_whitespace(self):
        req = CommentUpdateRequest(
            body="  Updated comment body.  ",
        )

        self.assertEqual(req.body, "Updated comment body.")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            CommentUpdateRequest(
                body="Updated comment body.",
                other=1,
            )

    def test_body_required(self):
        with self.assertRaises(ValidationError) as cm:
            CommentUpdateRequest()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("body",))
        self.assertEqual(error["type"], "missing")

    def test_body_too_short_after_stripping(self):
        with self.assertRaises(ValidationError) as cm:
            CommentUpdateRequest(
                body="   ",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("body",))
        self.assertEqual(error["type"], "string_too_short")

    def test_body_too_long(self):
        with self.assertRaises(ValidationError) as cm:
            CommentUpdateRequest(
                body=("a" * 4097),
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("body",))
        self.assertEqual(error["type"], "string_too_long")


class TestCommentUpdateResponse(unittest.TestCase):

    def test_accepts_valid_payload_by_alias(self):
        resp = CommentUpdateResponse(
            id=1,
        )

        self.assertEqual(resp.comment_id, 1)

    def test_accepts_object_from_attributes(self):
        comment = MagicMock()
        comment.id = 1

        resp = CommentUpdateResponse.model_validate(comment)

        self.assertEqual(resp.comment_id, 1)

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            CommentUpdateResponse(
                id=1,
                other=1,
            )

    def test_comment_id_required(self):
        with self.assertRaises(ValidationError) as cm:
            CommentUpdateResponse()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("id",))
        self.assertEqual(error["type"], "missing")


class TestCommentUpdateErrors(unittest.TestCase):

    def test_openapi_error_map_has_expected_statuses(self):
        self.assertEqual(
            set(COMMENT_UPDATE_ERRORS),
            {401, 403, 404, 422, 423, 503},
        )
