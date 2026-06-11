# tests/test_config.py
# SPDX-License-Identifier: GPL-3.0-only

import os
import unittest
from unittest.mock import mock_open, patch

from app.config import Config, get_config
from app.constants import (
    FERNET_KEY_FILENAME,
    FIRST_ADMIN_CREATED_FLAG_FILENAME,
    FILES_DIRNAME,
    FILES_REVISIONS_DIRNAME,
    FILES_THUMBNAILS_DIRNAME,
    FILES_TMP_DIRNAME,
    GOCRYPTFS_CIPHER_DIRNAME,
    GOCRYPTFS_MOUNTPOINT_DIRNAME,
    GOCRYPTFS_PASSPHRASE_ENCRYPTED_FILENAME,
    JWT_SIGNING_KEY_FILENAME,
    SQLITE_DIRNAME,
    SQLITE_FILENAME,
)
from tests.helpers import build_default_config_values


def build_config(**overrides) -> Config:
    values = build_default_config_values()
    values.update(overrides)
    return Config(**values)


class TestConfigPaths(unittest.TestCase):

    def test_computes_gocryptfs_paths(self):
        config = build_config()

        self.assertEqual(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
            os.path.join(
                "/secrets",
                GOCRYPTFS_PASSPHRASE_ENCRYPTED_FILENAME,
            ),
        )
        self.assertEqual(
            config.FIRST_ADMIN_CREATED_FLAG_PATH,
            os.path.join(
                "/secrets",
                FIRST_ADMIN_CREATED_FLAG_FILENAME,
            ),
        )
        self.assertEqual(
            config.GOCRYPTFS_CIPHERDIR,
            os.path.join("/state", GOCRYPTFS_CIPHER_DIRNAME),
        )
        self.assertEqual(
            config.GOCRYPTFS_MOUNTPOINT,
            os.path.join("/state", GOCRYPTFS_MOUNTPOINT_DIRNAME),
        )

    def test_computes_sqlite_paths(self):
        config = build_config()

        sqlite_dir = os.path.join(
            "/state",
            GOCRYPTFS_MOUNTPOINT_DIRNAME,
            SQLITE_DIRNAME,
        )
        sqlite_path = os.path.join(sqlite_dir, SQLITE_FILENAME)

        self.assertEqual(config.SQLITE_DIR, sqlite_dir)
        self.assertEqual(config.SQLITE_PATH, sqlite_path)
        self.assertEqual(
            config.SQLITE_URL,
            "sqlite+aiosqlite:///" + sqlite_path,
        )

    def test_computes_files_paths(self):
        config = build_config()
        mountpoint = os.path.join("/state", GOCRYPTFS_MOUNTPOINT_DIRNAME)

        self.assertEqual(
            config.FILES_DIR,
            os.path.join(mountpoint, FILES_DIRNAME),
        )
        self.assertEqual(
            config.FILES_REVISIONS_DIR,
            os.path.join(mountpoint, FILES_REVISIONS_DIRNAME),
        )
        self.assertEqual(
            config.FILES_THUMBNAILS_DIR,
            os.path.join(mountpoint, FILES_THUMBNAILS_DIRNAME),
        )
        self.assertEqual(
            config.FILES_TMP_DIR,
            os.path.join(mountpoint, FILES_TMP_DIRNAME),
        )

    def test_computes_secret_paths(self):
        config = build_config()

        self.assertEqual(
            config.JWT_SIGNING_KEY_PATH,
            os.path.join("/secrets", JWT_SIGNING_KEY_FILENAME),
        )
        self.assertEqual(
            config.FERNET_KEY_PATH,
            os.path.join("/secrets", FERNET_KEY_FILENAME),
        )


class TestConfigSecrets(unittest.TestCase):

    def test_reads_and_strips_jwt_signing_key(self):
        config = build_config()
        opened = mock_open(read_data=" jwt-key \n")

        with patch("builtins.open", opened):
            self.assertEqual(config.JWT_SIGNING_KEY, "jwt-key")

        opened.assert_called_once_with(
            config.JWT_SIGNING_KEY_PATH,
            "r",
            encoding="utf-8",
        )

    def test_reads_and_strips_fernet_key(self):
        config = build_config()
        opened = mock_open(read_data=" fernet-key \n")

        with patch("builtins.open", opened):
            self.assertEqual(config.FERNET_KEY, "fernet-key")

        opened.assert_called_once_with(
            config.FERNET_KEY_PATH,
            "r",
            encoding="utf-8",
        )

    def test_secret_values_are_cached_after_first_access(self):
        config = build_config()
        opened = mock_open(read_data=" jwt-key \n")

        with patch("builtins.open", opened):
            self.assertEqual(config.JWT_SIGNING_KEY, "jwt-key")
            self.assertEqual(config.JWT_SIGNING_KEY, "jwt-key")

        opened.assert_called_once()


class TestConfigExtensions(unittest.TestCase):

    def test_csv_to_list_strips_empty_items(self):
        self.assertEqual(
            Config._csv_to_list(" alpha, beta ,, gamma "),
            ["alpha", "beta", "gamma"],
        )

    def test_extensions_enabled_list_is_empty_by_default(self):
        config = build_config()

        with patch("app.config.os.listdir") as listdir:
            self.assertEqual(config.ENABLED_EXTENSIONS_LIST, [])

        listdir.assert_not_called()

    def test_extensions_enabled_list_returns_requested_extensions(self):
        config = build_config(ENABLED_EXTENSIONS="alpha, beta")

        def isdir(path: str) -> bool:
            return path in {
                os.path.join("/extensions", "alpha"),
                os.path.join("/extensions", "beta"),
            }

        with (
            patch(
                "app.config.os.listdir",
                return_value=["alpha", "beta", "file.txt"],
            ) as listdir,
            patch("app.config.os.path.isdir", side_effect=isdir),
        ):
            self.assertEqual(
                config.ENABLED_EXTENSIONS_LIST,
                ["alpha", "beta"],
            )

        listdir.assert_called_once_with("/extensions")

    def test_extensions_enabled_list_raises_for_missing_extension(self):
        config = build_config(ENABLED_EXTENSIONS="alpha, beta")

        def isdir(path: str) -> bool:
            return path == os.path.join("/extensions", "alpha")

        with (
            patch("app.config.os.listdir", return_value=["alpha"]),
            patch("app.config.os.path.isdir", side_effect=isdir),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "Missing extensions: beta",
            ):
                _ = config.ENABLED_EXTENSIONS_LIST


class TestGetConfig(unittest.TestCase):

    def setUp(self):
        get_config.cache_clear()

    def tearDown(self):
        get_config.cache_clear()

    def test_get_config_loads_from_environment_and_is_cached(self):
        env = {
            key: str(value)
            for key, value in build_default_config_values().items()
        }

        with patch.dict(os.environ, env, clear=True):
            first = get_config()
            second = get_config()

        self.assertIs(first, second)
        self.assertEqual(first.INSTALL_STATE_DIR, "/state")
        self.assertEqual(first.UVICORN_PORT, 80)
        self.assertEqual(first.AUTH_TOKEN_TTL_SECONDS, 86400)
        self.assertEqual(first.ENABLED_EXTENSIONS, "")
