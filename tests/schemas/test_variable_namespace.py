# tests/schemas/test_variable_namespace.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.variable_namespace import VariableNamespace


class TestVariableNamespace(unittest.TestCase):

    def test_accepts_namespace(self):
        req = VariableNamespace(namespace="thumbnails")

        self.assertEqual(req.namespace, "thumbnails")

    def test_strips_whitespace(self):
        req = VariableNamespace(namespace="  thumbnails  ")

        self.assertEqual(req.namespace, "thumbnails")

    def test_lowercases_ascii_letters(self):
        req = VariableNamespace(namespace="Thumbnails")

        self.assertEqual(req.namespace, "thumbnails")

    def test_rejects_disallowed_characters(self):
        with self.assertRaises(ValidationError) as cm:
            VariableNamespace(namespace="thumb.nails")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("namespace",))
        self.assertEqual(
            error["type"],
            "value_not_latin_extended",
        )

    def test_namespace_required(self):
        with self.assertRaises(ValidationError):
            VariableNamespace()

    def test_namespace_min_length(self):
        with self.assertRaises(ValidationError) as cm:
            VariableNamespace(namespace="")

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("namespace",))
        self.assertEqual(error["type"], "string_too_short")

    def test_namespace_max_length(self):
        with self.assertRaises(ValidationError) as cm:
            VariableNamespace(namespace="a" * 256)

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("namespace",))
        self.assertEqual(error["type"], "string_too_long")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            VariableNamespace(namespace="thumbnails", other=1)
