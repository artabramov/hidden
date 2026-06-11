# app/dependencies/session.py
# SPDX-License-Identifier: GPL-3.0-only

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import SessionLocal


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for a single request.
    The session is automatically closed after the request finishes.
    """
    async with SessionLocal() as session:
        yield session
