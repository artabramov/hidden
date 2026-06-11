# tests/schemas/test_cipherdir_unmount.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest

from pydantic import ValidationError

from app.schemas.cipherdir_unmount import CipherdirUnmountRequest


class TestCipherdirUnmountRequest(unittest.TestCase):

    def test_accepts_valid_master_password(self):
        req = CipherdirUnmountRequest(
            master_password="StrongMasterKey9",
        )

        self.assertEqual(req.master_password, "StrongMasterKey9")

    def test_not_strip_whitespace(self):
        req = CipherdirUnmountRequest(
            master_password="  StrongMasterKey9  ",
        )

        self.assertEqual(req.master_password, "  StrongMasterKey9  ")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            CipherdirUnmountRequest(
                master_password="StrongMasterKey9",
                other=1,
            )

    def test_master_password_required(self):
        with self.assertRaises(ValidationError) as cm:
            CipherdirUnmountRequest()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("master_password",))
        self.assertEqual(error["type"], "missing")
