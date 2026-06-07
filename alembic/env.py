# alembic/env.py
# SPDX-License-Identifier: SSPL-1.0

import logging
from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.db.base import Base  # noqa: E402
from app.models.user import User  # noqa: F401, E402
from app.models.folder import Folder  # noqa: F401, E402
from app.models.file import File  # noqa: F401, E402
from app.models.file_revision import FileRevision  # noqa: F401, E402
from app.models.file_comment import FileComment  # noqa: F401, E402
from app.models.file_tag import FileTag  # noqa: F401, E402
from app.models.file_thumbnail import FileThumbnail  # noqa: F401, E402
from app.models.variable import Variable  # noqa: F401, E402
from app.models.audit import Audit  # noqa: F401, E402


config = context.config


if config.config_file_name is not None and not logging.root.handlers:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations() -> None:
    """Run database migrations."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        # NOTE (ADR-XX): SQLite has limited ALTER TABLE support.
        # Batch mode allows Alembic to emulate unsupported schema
        # changes through table recreation.
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations()
