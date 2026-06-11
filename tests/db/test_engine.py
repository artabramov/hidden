# tests/db/test_engine.py
# SPDX-License-Identifier: GPL-3.0-only

import importlib
import os
import unittest
from unittest.mock import MagicMock, call, patch


TEST_ENV = {
    "INSTALL_SOURCE_DIR": "/tmp/hidden/source",
    "INSTALL_STATE_DIR": "/tmp/hidden/state",
    "INSTALL_SECRETS_DIR": "/tmp/hidden/secrets",
    "INSTALL_EXTENSIONS_DIR": "/tmp/hidden/extensions",
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "text",
    "GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS": "60",
    "GOCRYPTFS_WATCHDOG_LIVENESS_SECONDS": "120",
    "SQLITE_JOURNAL_MODE": "WAL",
    "SQLITE_SYNCHRONOUS": "NORMAL",
    "SQLITE_BUSY_TIMEOUT": "10000",
    "SQLITE_TEMP_STORE": "MEMORY",
    "UVICORN_HOST": "127.0.0.1",
    "UVICORN_PORT": "8000",
    "API_PREFIX": "/api",
    "AUTH_TOKEN_TTL_SECONDS": "86400",
    "CORS_ALLOW_ORIGINS": "",
}


def import_engine_module():
    with patch.dict(os.environ, TEST_ENV, clear=False):
        return importlib.import_module("app.db.engine")


class TestSQLitePragma(unittest.TestCase):

    def test_set_sqlite_pragma_executes_configured_values(self):
        engine_module = import_engine_module()

        cursor = MagicMock()
        connection = MagicMock()
        connection.cursor.return_value = cursor

        with patch.object(engine_module, "config") as config:
            config.SQLITE_JOURNAL_MODE = "WAL"
            config.SQLITE_SYNCHRONOUS = "NORMAL"
            config.SQLITE_BUSY_TIMEOUT = "10000"
            config.SQLITE_TEMP_STORE = "MEMORY"

            engine_module.set_sqlite_pragma(connection, MagicMock())

        connection.cursor.assert_called_once()
        self.assertEqual(
            cursor.execute.call_args_list,
            [
                call("PRAGMA foreign_keys=ON"),
                call("PRAGMA journal_mode=WAL"),
                call("PRAGMA synchronous=NORMAL"),
                call("PRAGMA busy_timeout=10000"),
                call("PRAGMA temp_store=MEMORY"),
            ],
        )
        cursor.close.assert_called_once()


class TestLoadAllModels(unittest.TestCase):

    def test_load_all_models_imports_without_error(self):
        engine_module = import_engine_module()

        engine_module.load_all_models()
