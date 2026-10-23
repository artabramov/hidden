# tests/test_constants.py
# SPDX-License-Identifier: Apache-2.0

import unittest

from app import constants


class TestConstants(unittest.TestCase):
    def test_exposes_runtime_contracts(self):
        self.assertEqual(
            constants.HIDDEN_TITLE,
            "Hidden S3 — encrypted self-hosted S3 storage",
        )
        self.assertEqual(constants.GOCRYPTFS_PASSPHRASE_LENGTH, 80)
        self.assertEqual(
            constants.GOCRYPTFS_PASSPHRASE_FILENAME,
            "gocryptfs_passphrase.enc",
        )
        self.assertEqual(
            constants.WATCHDOG_HEARTBEAT_PATH,
            "/tmp/gocryptfs-watchdog.touch",
        )
        self.assertEqual(constants.VERSITY_ACCESS_KEY_LENGTH, 20)
        self.assertEqual(
            constants.VERSITY_ACCESS_KEY_FILENAME,
            "versity_access_key.enc",
        )
        self.assertEqual(constants.VERSITY_SECRET_KEY_LENGTH, 40)
        self.assertEqual(
            constants.VERSITY_SECRET_KEY_FILENAME,
            "versity_secret_key.enc",
        )
        self.assertEqual(constants.VERSITY_DATA_DIRNAME, "data")
        self.assertEqual(constants.VERSITY_IAM_DIRNAME, "iam")
