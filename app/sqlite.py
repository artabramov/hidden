"""
Sets up async SQLite engine and sessions for SQLAlchemy. The engine
and session factory are created from a Config instance and should be
constructed in FastAPI lifespan and stored in app.state.
"""

from typing import AsyncGenerator
from pathlib import Path
from asyncio import current_task
from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncSession, AsyncEngine, create_async_engine,
    async_scoped_session, async_sessionmaker)
from starlette.requests import Request


class Base(DeclarativeBase):
    pass


class SessionManager:
    """
    Creates and manages the SQLite async engine and session factory
    derived from runtime settings, intended to be instantiated during
    application startup and reused via app.state for handling database
    access.
    """
    def __init__(self, *, sqlite_path: str, sql_echo: bool = False):
        self._sqlite_path = sqlite_path
        self._sql_echo = sql_echo
        self.async_engine = self._create_engine()
        self.async_sessionmaker = self._create_sessionmaker()

    @property
    def db_path(self) -> str:
        """
        Return the absolute filesystem path to the database file with
        user home expansion and normalization applied.
        """
        return str(Path(self._sqlite_path).expanduser().resolve())

    @property
    def connection_string(self) -> str:
        """
        Return the SQLAlchemy async URL for aiosqlite that points
        at the resolved database file path.
        """
        return f"sqlite+aiosqlite:///{self.db_path}"

    def _create_engine(self) -> AsyncEngine:
        """
        Create the engine, ensure the database directory exists, and
        attach a connect hook that applies recommended SQLite PRAGMAs
        for safety and concurrency.
        """
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        engine = create_async_engine(
            self.connection_string,
            echo=self._sql_echo,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(engine.sync_engine, "connect")
        def _set_sqlite_pragmas(dbapi_conn, _):
            """
            Apply SQLite PRAGMAs on every new DB-API connection to
            enforce foreign keys, enable WAL, set synchronous mode,
            use in-memory temp storage, and configure a busy timeout
            for smoother concurrency.
            """
            cur = dbapi_conn.cursor()

            # enforce foreign key constraints on this connection
            cur.execute("PRAGMA foreign_keys = ON;")

            # enable write-ahead logging for better R/W concurrency
            cur.execute("PRAGMA journal_mode = WAL;")

            # balance durability vs speed (FULL for maximum durability)
            cur.execute("PRAGMA synchronous = NORMAL;")

            # keep temporary tables/indices in RAM instead of disk
            cur.execute("PRAGMA temp_store = MEMORY;")

            # wait up to 5s when the database is locked before failing
            cur.execute("PRAGMA busy_timeout = 5000;")

            cur.close()

        return engine

    def _create_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        """
        Build and return an async_sessionmaker configured to avoid
        autoflush and attribute expiration so sessions behave
        predictably in request handlers.
        """
        return async_sessionmaker(
            self.async_engine,
            autoflush=False,
            expire_on_commit=False
        )

    def get_session(self) -> AsyncSession:
        """
        Return a task-scoped AsyncSession so that concurrent coroutines
        receive isolated sessions bound to their current asyncio task.
        """
        scoped = async_scoped_session(
            self.async_sessionmaker, scopefunc=current_task)
        return scoped()


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an AsyncSession obtained from the SessionManager stored in
    app.state and wrap it in a simple unit-of-work pattern that commits
    on success, rolls back on error, and always closes the session.
    """
    session_manager: SessionManager = request.app.state.sessionmanager
    session = session_manager.get_session()
    try:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
    finally:
        await session.close()


async def init_database(session_manager: SessionManager) -> None:
    """
    Create the database schema for all mapped models by running
    create_all against the async engine at application startup.
    """
    async with session_manager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
