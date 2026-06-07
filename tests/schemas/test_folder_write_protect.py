# tests/schemas/test_folder_write_protect.py
# SPDX-License-Identifier: SSPL-1.0

import unittest

from pydantic import ValidationError

from app.schemas.folder_write_protect import FolderWriteProtectRequest


class TestFolderWriteProtectedRequest(unittest.TestCase):

    def test_accepts_true(self):
        req = FolderWriteProtectRequest(
            is_write_protected=True,
        )

        self.assertIs(req.is_write_protected, True)

    def test_accepts_false(self):
        req = FolderWriteProtectRequest(
            is_write_protected=False,
        )

        self.assertIs(req.is_write_protected, False)

    def test_is_write_protected_required(self):
        with self.assertRaises(ValidationError) as cm:
            FolderWriteProtectRequest()

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("is_write_protected",))
        self.assertEqual(error["type"], "missing")

    def test_extra_field_forbidden(self):
        with self.assertRaises(ValidationError) as cm:
            FolderWriteProtectRequest(
                is_write_protected=True,
                dirname="documents",
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("dirname",))
        self.assertEqual(error["type"], "extra_forbidden")

    def test_rejects_none(self):
        with self.assertRaises(ValidationError) as cm:
            FolderWriteProtectRequest(
                is_write_protected=None,
            )

        error = cm.exception.errors()[0]
        self.assertEqual(error["loc"], ("is_write_protected",))
        self.assertEqual(error["type"], "bool_type")
