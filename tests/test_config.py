# tests/test_config.py
# SPDX-License-Identifier: Apache-2.0

import os
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from app.config import Config, get_config


def _settings(**overrides):
    values = {
        "INSTALL_SOURCE_CODE": "/opt/hidden",
        "INSTALL_CIPHERDIR": "/cipher",
        "INSTALL_MOUNTPOINT": "/mount",
        "INSTALL_SECRETS": "/secrets",
        "UVICORN_HOST": "127.0.0.1",
        "UVICORN_PORT": 8081,
        "WATCHDOG_INTERVAL_SECONDS": 60,
        "WATCHDOG_LIVENESS_SECONDS": 120,
        "API_PREFIX": "/api/v1",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "%(message)s",
        "CORS_ALLOW_ORIGINS": "http://localhost:3000",
        "CORS_MAX_AGE_SECONDS": 86400,
        "VERSITY_HOST": "127.0.0.1",
        "VERSITY_PORT": 9000,
        "VERSITY_WEBGUI_HOST": "127.0.0.1",
        "VERSITY_WEBGUI_PORT": 8080,
        "VERSITY_WEBGUI_GATEWAY": "http://localhost:9000",
        "VERSITY_WEBGUI_CORS_ALLOW_ORIGIN": "http://localhost:8080",
        "VERSITY_START_TIMEOUT_SECONDS": 5.0,
        "VERSITY_STOP_TIMEOUT_SECONDS": 5,
        "VERSITY_POLL_INTERVAL_SECONDS": 0.25,
    }
    values.update(overrides)
    return values


class TestConfig(unittest.TestCase):
    def test_derives_storage_paths(self):
        config = Config(**_settings())

        self.assertEqual(config.UVICORN_PORT, 8081)
        self.assertEqual(config.VERSITY_START_TIMEOUT_SECONDS, 5.0)
        self.assertEqual(
            config.GOCRYPTFS_PASSPHRASE_PATH,
            "/secrets/gocryptfs_passphrase.enc",
        )
        self.assertEqual(
            config.VERSITY_ACCESS_KEY_PATH,
            "/secrets/versity_access_key.enc",
        )
        self.assertEqual(
            config.VERSITY_SECRET_KEY_PATH,
            "/secrets/versity_secret_key.enc",
        )
        self.assertEqual(config.VERSITY_DATA_PATH, "/mount/data")
        self.assertEqual(config.VERSITY_IAM_PATH, "/mount/iam")

    def test_ignores_unknown_settings(self):
        config = Config(**_settings(UNRELATED="ignored"))

        self.assertNotIn("UNRELATED", config.model_dump())

    def test_rejects_missing_setting(self):
        values = _settings()
        del values["INSTALL_CIPHERDIR"]

        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValidationError):
                Config(**values)

    def test_get_config_returns_cached_instance(self):
        sentinel = object()
        get_config.cache_clear()
        try:
            with patch("app.config.Config", return_value=sentinel) as ctor:
                self.assertIs(get_config(), sentinel)
                self.assertIs(get_config(), sentinel)
                ctor.assert_called_once_with()
        finally:
            get_config.cache_clear()
