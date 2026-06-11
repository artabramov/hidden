# tests/schemas/test_variable_set.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from pydantic import ValidationError

from app.schemas.variable_set import VariableSetRequest


class TestVariableSetRequest(unittest.TestCase):

    def test_accepts_variable_value(self):
        req = VariableSetRequest(variable_value="320")

        self.assertEqual(req.variable_value, "320")

    def test_strips_whitespace(self):
        req = VariableSetRequest(variable_value="  320  ")

        self.assertEqual(req.variable_value, "320")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            VariableSetRequest(variable_value="320", other=1)

    def test_variable_value_required(self):
        with self.assertRaises(ValidationError):
            VariableSetRequest()
