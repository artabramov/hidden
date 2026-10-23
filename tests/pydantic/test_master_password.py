# tests/pydantic/test_master_password.py
# SPDX-License-Identifier: Apache-2.0

import unittest

from app.pydantic.master_password import validate_master_password


class TestValidateMasterPassword(unittest.TestCase):
    def test_returns_password_that_meets_composition_rules(self):
        password = "Abcdefghijklm 1!"

        self.assertIs(validate_master_password(password), password)

    def test_rejects_password_missing_a_required_character(self):
        cases = {
            "ABCDEFGHIJKLMNO1": (
                "Master password must contain a lowercase letter."
            ),
            "abcdefghijklmno1": (
                "Master password must contain an uppercase letter."
            ),
            "Abcdefghijklmnop": (
                "Master password must contain a digit."
            ),
        }

        for password, message in cases.items():
            with self.subTest(password=password):
                with self.assertRaises(ValueError) as caught:
                    validate_master_password(password)

                self.assertEqual(str(caught.exception), message)

    def test_reports_the_first_missing_character_class(self):
        with self.assertRaises(ValueError) as caught:
            validate_master_password("1234567890123456")

        self.assertEqual(
            str(caught.exception),
            "Master password must contain a lowercase letter.",
        )
