# tests/schemas/test_variable_get.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.variable_get import VariableGetResponse


class TestVariableGetResponse(unittest.TestCase):
    def test_accepts_all_fields(self):
        out = VariableGetResponse(
            created_at=1710000000,
            updated_at=1710000100,
            created_by=1,
            updated_by=2,
            namespace="thumbnails",
            variable_key="max_width",
            variable_value="320",
        )

        self.assertEqual(out.created_at, 1710000000)
        self.assertEqual(out.updated_at, 1710000100)
        self.assertEqual(out.created_by, 1)
        self.assertEqual(out.updated_by, 2)
        self.assertEqual(out.namespace, "thumbnails")
        self.assertEqual(out.variable_key, "max_width")
        self.assertEqual(out.variable_value, "320")

    def test_updated_fields_are_optional(self):
        out = VariableGetResponse(
            created_at=1710000000,
            created_by=1,
            namespace="thumbnails",
            variable_key="max_width",
            variable_value="320",
        )

        self.assertEqual(out.created_at, 1710000000)
        self.assertIsNone(out.updated_at)
        self.assertEqual(out.created_by, 1)
        self.assertIsNone(out.updated_by)
        self.assertEqual(out.namespace, "thumbnails")
        self.assertEqual(out.variable_key, "max_width")
        self.assertEqual(out.variable_value, "320")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            VariableGetResponse(
                created_at=1710000000,
                updated_at=1710000100,
                created_by=1,
                updated_by=2,
                namespace="thumbnails",
                variable_key="max_width",
                variable_value="320",
                other=1,
            )

    def test_created_at_required(self):
        with self.assertRaises(ValidationError):
            VariableGetResponse(
                updated_at=1710000100,
                created_by=1,
                updated_by=2,
                namespace="thumbnails",
                variable_key="max_width",
                variable_value="320",
            )

    def test_created_by_required(self):
        with self.assertRaises(ValidationError):
            VariableGetResponse(
                created_at=1710000000,
                updated_at=1710000100,
                updated_by=2,
                namespace="thumbnails",
                variable_key="max_width",
                variable_value="320",
            )

    def test_namespace_required(self):
        with self.assertRaises(ValidationError):
            VariableGetResponse(
                created_at=1710000000,
                updated_at=1710000100,
                created_by=1,
                updated_by=2,
                variable_key="max_width",
                variable_value="320",
            )

    def test_variable_key_required(self):
        with self.assertRaises(ValidationError):
            VariableGetResponse(
                created_at=1710000000,
                updated_at=1710000100,
                created_by=1,
                updated_by=2,
                namespace="thumbnails",
                variable_value="320",
            )

    def test_variable_value_required(self):
        with self.assertRaises(ValidationError):
            VariableGetResponse(
                created_at=1710000000,
                updated_at=1710000100,
                created_by=1,
                updated_by=2,
                namespace="thumbnails",
                variable_key="max_width",
            )

    def test_from_attributes(self):
        class _Row:
            created_at = 1710000000
            updated_at = 1710000100
            created_by = 1
            updated_by = 2
            namespace = "thumbnails"
            variable_key = "max_width"
            variable_value = "320"

        out = VariableGetResponse.model_validate(_Row())

        self.assertEqual(out.created_at, 1710000000)
        self.assertEqual(out.updated_at, 1710000100)
        self.assertEqual(out.created_by, 1)
        self.assertEqual(out.updated_by, 2)
        self.assertEqual(out.namespace, "thumbnails")
        self.assertEqual(out.variable_key, "max_width")
        self.assertEqual(out.variable_value, "320")
