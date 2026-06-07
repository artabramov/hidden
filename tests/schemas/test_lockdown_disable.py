# tests/schemas/test_lockdown_disable.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.lockdown_disable import LockdownDisableRequest


class TestLockdownDisableRequest(unittest.TestCase):

    def test_accepts_valid_master_password(self):
        req = LockdownDisableRequest(
            master_password="StrongMasterKey9",
        )

        self.assertEqual(req.master_password, "StrongMasterKey9")

    def test_not_strip_whitespace(self):
        req = LockdownDisableRequest(
            master_password="  StrongMasterKey9  ",
        )

        self.assertEqual(req.master_password, "  StrongMasterKey9  ")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError):
            LockdownDisableRequest(
                master_password="StrongMasterKey9",
                other=1,
            )

    def test_master_password_required(self):
        with self.assertRaises(ValidationError) as cm:
            LockdownDisableRequest()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("master_password",))
        self.assertEqual(error["type"], "missing")
