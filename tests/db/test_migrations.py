# tests/db/test_migrations.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import MagicMock, patch

from app.db import migrations


class TestUpgradeDbSync(unittest.TestCase):

    def test_upgrade_db_sync_runs_alembic_upgrade_to_head(self):
        mock_config = MagicMock()

        with (
            patch(
                "app.db.migrations.Config",
                return_value=mock_config,
            ) as mock_config_cls,
            patch("app.db.migrations.command.upgrade") as mock_upgrade,
        ):
            migrations._upgrade_db_sync()

        mock_config_cls.assert_called_once_with("/opt/hidden/alembic.ini")
        mock_upgrade.assert_called_once_with(mock_config, "head")


class TestUpgradeDb(unittest.IsolatedAsyncioTestCase):

    async def test_upgrade_db_runs_sync_upgrade_in_thread(self):
        with patch("app.db.migrations.asyncio.to_thread") as mock_to_thread:
            await migrations.upgrade_db()

        mock_to_thread.assert_awaited_once_with(migrations._upgrade_db_sync)

    async def test_upgrade_db_propagates_to_thread_exception(self):
        error = RuntimeError("migration failed")

        with patch(
            "app.db.migrations.asyncio.to_thread",
            side_effect=error,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await migrations.upgrade_db()

        self.assertIs(cm.exception, error)


class TestCheckDbIntegritySync(unittest.TestCase):

    def test_passes_when_integrity_check_returns_ok(self):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [("ok",)]

        with patch(
            "app.db.migrations.sqlite3.connect",
            return_value=mock_conn
        ):
            migrations._check_db_integrity_sync("/fake/db.sqlite")

        mock_conn.execute.assert_called_once_with("PRAGMA integrity_check")
        mock_conn.close.assert_called_once()

    def test_raises_runtime_error_when_integrity_check_fails(self):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [
            ("Page 3 is never used",),
            ("rowid 7 missing from index idx_files",),
        ]

        with patch(
            "app.db.migrations.sqlite3.connect",
            return_value=mock_conn
        ):
            with self.assertRaises(RuntimeError) as cm:
                migrations._check_db_integrity_sync("/fake/db.sqlite")

        self.assertIn("integrity check failed", str(cm.exception))
        self.assertIn("Page 3 is never used", str(cm.exception))
        self.assertIn(
            "rowid 7 missing from index idx_files",
            str(cm.exception)
        )
        mock_conn.close.assert_called_once()

    def test_closes_connection_even_when_execute_raises(self):
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("disk I/O error")

        with patch(
            "app.db.migrations.sqlite3.connect",
            return_value=mock_conn
        ):
            with self.assertRaises(Exception):
                migrations._check_db_integrity_sync("/fake/db.sqlite")

        mock_conn.close.assert_called_once()

    def test_connects_to_provided_path(self):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [("ok",)]

        with patch(
            "app.db.migrations.sqlite3.connect", return_value=mock_conn
        ) as mock_connect:
            migrations._check_db_integrity_sync("/some/path/db.sqlite")

        mock_connect.assert_called_once_with("/some/path/db.sqlite")


class TestCheckDbIntegrity(unittest.IsolatedAsyncioTestCase):

    async def test_runs_integrity_check_in_thread(self):
        with patch("app.db.migrations.asyncio.to_thread") as mock_to_thread:
            await migrations.check_db_integrity("/fake/db.sqlite")

        mock_to_thread.assert_awaited_once_with(
            migrations._check_db_integrity_sync,
            "/fake/db.sqlite",
        )

    async def test_propagates_runtime_error_from_thread(self):
        error = RuntimeError(
            "SQLite integrity check failed: Page 3 is never used"
        )

        with patch(
            "app.db.migrations.asyncio.to_thread",
            side_effect=error,
        ):
            with self.assertRaises(RuntimeError) as cm:
                await migrations.check_db_integrity("/fake/db.sqlite")

        self.assertIs(cm.exception, error)
