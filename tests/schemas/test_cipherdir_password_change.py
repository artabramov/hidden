# tests/schemas/test_cipherdir_password_change.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.constants import MASTER_PASSWORD_MIN_LENGTH
from app.schemas.cipherdir_password_change import (
    CipherdirPasswordChangeRequest,
)


class TestCipherdirPasswordChangeRequest(unittest.TestCase):

    def test_accepts_valid_payload(self):
        req = CipherdirPasswordChangeRequest(
            current_master_password="StrongMasterKey9",
            changed_master_password="BetterMasterKey7",
        )

        self.assertEqual(req.current_master_password, "StrongMasterKey9")
        self.assertEqual(req.changed_master_password, "BetterMasterKey7")

    def test_not_strip_whitespace(self):
        req = CipherdirPasswordChangeRequest(
            current_master_password="  StrongMasterKey9  ",
            changed_master_password="  BetterMasterKey7  ",
        )

        self.assertEqual(req.current_master_password, "  StrongMasterKey9  ")
        self.assertEqual(req.changed_master_password, "  BetterMasterKey7  ")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            CipherdirPasswordChangeRequest(
                current_master_password="OldMasterPass9",
                changed_master_password="NewMasterPass9",
                other=1,
            )

    def test_current_master_password_required(self):
        with self.assertRaises(ValidationError):
            CipherdirPasswordChangeRequest(
                changed_master_password="NewMasterPass9",
            )

    def test_changed_master_password_required(self):
        with self.assertRaises(ValidationError):
            CipherdirPasswordChangeRequest(
                current_master_password="OldMasterPass9",
            )

    def test_changed_master_password_min_length(self):
        with self.assertRaises(ValidationError) as cm:
            CipherdirPasswordChangeRequest(
                current_master_password="OldMasterPass9",
                changed_master_password=("Aa1" * 5),
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("changed_master_password",))
        self.assertEqual(error["type"], "string_too_short")
        self.assertEqual(
            error["ctx"]["min_length"],
            MASTER_PASSWORD_MIN_LENGTH,
        )

    def test_rejects_changed_password_without_lowercase(self):
        with self.assertRaises(ValidationError) as cm:
            CipherdirPasswordChangeRequest(
                current_master_password="OldMasterPass9",
                changed_master_password="AAAAAAAAAAAAAAA1",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("changed_master_password",))
        self.assertEqual(error["type"], "value_missing_lowercase")

    def test_rejects_changed_password_without_uppercase(self):
        with self.assertRaises(ValidationError) as cm:
            CipherdirPasswordChangeRequest(
                current_master_password="OldMasterPass9",
                changed_master_password="aaaaaaaaaaaaaaa1",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("changed_master_password",))
        self.assertEqual(error["type"], "value_missing_uppercase")

    def test_rejects_changed_password_without_digit(self):
        with self.assertRaises(ValidationError) as cm:
            CipherdirPasswordChangeRequest(
                current_master_password="OldMasterPass9",
                changed_master_password="StrongMasterPass",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("changed_master_password",))
        self.assertEqual(error["type"], "value_missing_digit")
