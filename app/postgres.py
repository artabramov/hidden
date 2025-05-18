"""
The module sets up and manages the asynchronous database session and
engine using SQLAlchemy. It provides functions to create and manage
database connections and sessions for an asynchronous environment.
"""

from asyncio import current_task
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_scoped_session, async_sessionmaker)
from app.config import get_config
from app.triggers import triggers

cfg = get_config()
Base = declarative_base()


class SessionManager:
    """
    Manages asynchronous SQLAlchemy sessions and engine creation for the
    application. Handles configuration and provides methods to create
    and retrieve database sessions.
    """

    def __init__(self):
        """
        Manages asynchronous SQLAlchemy sessions and engine creation for
        the application. Handles configuration and provides methods to
        create and retrieve database sessions.
        """
        self.async_engine = self.create_engine()
        self.async_sessionmaker = self.create_sessionmaker()

    @property
    def connection_string(self):
        """
        Generates the PostgreSQL database connection string used by
        SQLAlchemy. This URL includes the username, password, host,
        port, and database name as configured.
        """
        return "postgresql+asyncpg://%s:%s@%s:%s/%s" % (
            cfg.POSTGRES_USERNAME, cfg.POSTGRES_PASSWORD,
            cfg.POSTGRES_HOST, cfg.POSTGRES_PORT,
            cfg.POSTGRES_DATABASE)

    def create_engine(self):
        """
        Creates an asynchronous database engine. In the context of
        FastAPI and SQLAlchemy, this engine handles database connections
        and communication.
        """
        return create_async_engine(
            self.connection_string, echo=True, future=True,
            pool_size=cfg.POSTGRES_POOL_SIZE,
            max_overflow=cfg.POSTGRES_POOL_OVERFLOW)

    def create_sessionmaker(self):
        """
        Creates an asynchronous session class. It's similar to the
        regular sessionmaker but adapted for asynchronous operations.
        """
        return async_sessionmaker(self.async_engine, autoflush=False,
                                  autocommit=False, expire_on_commit=False)

    def get_session(self):
        """
        Creates a scoped session for the current context. It allows to
        work with a single session within a particular scope, such as
        a request in FastAPI.
        """
        async_session = async_scoped_session(self.async_sessionmaker,
                                             scopefunc=current_task)
        return async_session()


sessionmanager = SessionManager()


async def get_session():
    """
    Creates an asynchronous scoped session. This session is scoped to
    the current task, allowing for consistent session management within
    a particular context, such as a request in FastAPI.
    """
    try:
        session = sessionmanager.get_session()
        yield session
    except Exception:
        await session.rollback()
        raise
    else:
        await session.commit()
    finally:
        await session.close()


async def init_database():
    """
    Initializes the database by creating all the tables defined in the
    SQLAlchemy Base metadata. This function is typically called during
    the application startup to ensure the database schema is created.
    """
    async with sessionmanager.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        for sql in triggers:
            await conn.execute(text(sql))
