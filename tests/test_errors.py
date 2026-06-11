# tests/test_errors.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from app.errors import (
    InternalServerError,
    PydanticError,
    ResourceConflictError,
    ResourceForbiddenError,
    ResourceLockedError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    TooManyRequestsError,
    ValueAuthenticationError,
    ValueConflictError,
    ValueInvalidError,
    ValueNotFoundError,
)


class TestSimpleErrors(unittest.TestCase):

    def test_simple_errors_are_exceptions(self):
        for error_class in (
            InternalServerError,
            ServiceUnavailableError,
            ResourceNotFoundError,
            ResourceForbiddenError,
            ResourceConflictError,
            ResourceLockedError,
            TooManyRequestsError,
        ):
            with self.subTest(error_class=error_class):
                self.assertIsInstance(error_class(), Exception)


class TestPydanticError(unittest.TestCase):

    def test_stores_fields_and_builds_detail(self):
        error = PydanticError(
            scope="query",
            field="file_id",
            error_type="value_invalid",
            message="Invalid value",
            input_value="abc",
        )

        self.assertEqual(error.loc, ("query", "file_id"))
        self.assertEqual(error.error_type, "value_invalid")
        self.assertEqual(error.message, "Invalid value")
        self.assertEqual(error.input_value, "abc")
        self.assertEqual(
            error.detail,
            [{
                "type": "value_invalid",
                "loc": ["query", "file_id"],
                "msg": "Invalid value",
                "input": "abc",
            }],
        )

    def test_detail_includes_none_input_value(self):
        error = PydanticError(
            scope="body",
            field="name",
            error_type="value_invalid",
            message="Invalid value",
        )

        self.assertEqual(
            error.detail,
            [{
                "type": "value_invalid",
                "loc": ["body", "name"],
                "msg": "Invalid value",
                "input": None,
            }],
        )


class TestFieldLevelErrors(unittest.TestCase):

    def test_value_invalid_error(self):
        error = ValueInvalidError(
            field="name",
            input_value="bad",
        )

        self.assertEqual(
            error.detail,
            [{
                "type": "value_invalid",
                "loc": ["body", "name"],
                "msg": "The value is invalid",
                "input": "bad",
            }],
        )

    def test_value_not_found_error(self):
        error = ValueNotFoundError(
            field="folder_id",
            input_value=404,
        )

        self.assertEqual(
            error.detail,
            [{
                "type": "value_not_found",
                "loc": ["body", "folder_id"],
                "msg": "The value was not found",
                "input": 404,
            }],
        )

    def test_value_conflict_error(self):
        error = ValueConflictError(
            field="name",
            input_value="docs",
        )

        self.assertEqual(
            error.detail,
            [{
                "type": "value_conflict",
                "loc": ["body", "name"],
                "msg": "The value conflicts with existing data",
                "input": "docs",
            }],
        )

    def test_value_authentication_error(self):
        error = ValueAuthenticationError(
            field="username",
            input_value="admin",
        )

        self.assertEqual(
            error.detail,
            [{
                "type": "value_authentication",
                "loc": ["body", "username"],
                "msg": "Authentication failed",
                "input": "admin",
            }],
        )

    def test_field_level_errors_default_input_to_none_in_detail(self):
        err = ValueInvalidError(field="x")
        self.assertIsNone(err.input_value)
        self.assertIsNone(err.detail[0]["input"])
