# tests/schemas/test_variable_path.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from pydantic import ValidationError

from app.schemas.variable_path import VariablePath


class TestVariablePath(unittest.TestCase):

    def test_accepts_all_fields(self):
        req = VariablePath(
            namespace="thumbnails",
            variable_key="max_width",
        )

        self.assertEqual(req.namespace, "thumbnails")
        self.assertEqual(req.variable_key, "max_width")

    def test_strips_whitespace(self):
        req = VariablePath(
            namespace="  thumbnails  ",
            variable_key="  max_width  ",
        )

        self.assertEqual(req.namespace, "thumbnails")
        self.assertEqual(req.variable_key, "max_width")

    def test_lowercases_ascii_letters(self):
        req = VariablePath(
            namespace="Thumbnails",
            variable_key="MAX_WIDTH",
        )

        self.assertEqual(req.namespace, "thumbnails")
        self.assertEqual(req.variable_key, "max_width")

    def test_rejects_disallowed_characters_in_namespace(self):
        with self.assertRaises(ValidationError) as cm:
            VariablePath(
                namespace="thumb.nails",
                variable_key="k",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("namespace",))
        self.assertEqual(
            error["type"],
            "value_not_latin_extended",
        )

    def test_rejects_disallowed_characters_in_variable_key(self):
        with self.assertRaises(ValidationError) as cm:
            VariablePath(
                namespace="ns",
                variable_key="max width",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("variable_key",))
        self.assertEqual(
            error["type"],
            "value_not_latin_extended",
        )

    def test_allows_hyphen_and_underscore(self):
        req = VariablePath(
            namespace="thumb-nails",
            variable_key="max-width_v2",
        )

        self.assertEqual(req.namespace, "thumb-nails")
        self.assertEqual(req.variable_key, "max-width_v2")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            VariablePath(
                namespace="thumbnails",
                variable_key="max_width",
                other=1,
            )

    def test_namespace_required(self):
        with self.assertRaises(ValidationError):
            VariablePath(
                variable_key="max_width",
            )

    def test_variable_key_required(self):
        with self.assertRaises(ValidationError):
            VariablePath(
                namespace="thumbnails",
            )

    def test_namespace_min_length(self):
        with self.assertRaises(ValidationError) as cm:
            VariablePath(
                namespace="",
                variable_key="k",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("namespace",))
        self.assertEqual(error["type"], "string_too_short")

    def test_variable_key_min_length(self):
        with self.assertRaises(ValidationError) as cm:
            VariablePath(
                namespace="ns",
                variable_key="",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("variable_key",))
        self.assertEqual(error["type"], "string_too_short")

    def test_namespace_max_length(self):
        with self.assertRaises(ValidationError) as cm:
            VariablePath(
                namespace="a" * 256,
                variable_key="k",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("namespace",))
        self.assertEqual(error["type"], "string_too_long")

    def test_variable_key_max_length(self):
        with self.assertRaises(ValidationError) as cm:
            VariablePath(
                namespace="ns",
                variable_key="a" * 256,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("variable_key",))
        self.assertEqual(error["type"], "string_too_long")
