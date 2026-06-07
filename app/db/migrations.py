# app/db/migrations.py
# SPDX-License-Identifier: SSPL-1.0

import asyncio
import sqlite3
from pathlib import Path

from alembic import command
from alembic.config import Config


def _upgrade_db_sync() -> None:
    alembic_cfg = Config(str(Path("/opt/hidden/alembic.ini")))
    command.upgrade(alembic_cfg, "head")


async def upgrade_db() -> None:
    """
    Apply database migrations after encrypted storage is mounted.
    """
    await asyncio.to_thread(_upgrade_db_sync)


def _check_db_integrity_sync(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("PRAGMA integrity_check").fetchall()
    finally:
        conn.close()

    messages = [row[0] for row in rows]
    if messages != ["ok"]:
        raise RuntimeError(
            "SQLite integrity check failed: " + "; ".join(messages)
        )


async def check_db_integrity(db_path: str) -> None:
    """
    Run PRAGMA integrity_check on the database file.

    Must be called after upgrade_db() and before the application starts
    serving requests. Raises RuntimeError if the database is corrupted so
    that the mount is rolled back and the operator is alerted early rather
    than allowing silent data corruption to propagate.
    """
    await asyncio.to_thread(_check_db_integrity_sync, db_path)
