"""
The module defines the logging mechanism specifically for user login
actions within the system. It includes models and functions for logging
user activity during login attempts, capturing details such as IP
address, user agent, and timestamp of the login event.
"""

import time
from fastapi import Request
from sqlalchemy import Column, BigInteger, Integer, String, Text
from app.database import Base
from app.models.user_model import User
from app.context import get_context
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository import Repository
from pydantic import BaseModel, Field
from typing import Literal, Optional

ctx = get_context()

LOGS_ENABLED = True
LOGS_ACTION = "logs"


class Log(Base):
    """
    The Log class represents a log entry for a user action within the
    system. It stores details like the user's ID, IP address, user agent,
    and the time of the action. This class is mapped to the 'users_logs'
    table in the database.
    """
    __tablename__ = "users_logs"
    _cacheable = False

    id = Column(BigInteger, primary_key=True)
    created_date = Column(Integer, index=True,
                          default=lambda: int(time.time()))
    user_id = Column(BigInteger, index=True)
    remote_address = Column(String(128), nullable=True)
    user_agent = Column(Text, nullable=True)

    def __init__(self, user: User, request: Request):
        """
        Initializes a new log entry with the provided user and request
        information. The user's ID, remote address, and user agent are
        extracted from the request.
        """
        self.user_id = user.id
        self.remote_address = self.get_remote_address(request)
        self.user_agent = self.get_user_agent(request)

    def get_remote_address(self, request: Request):
        """
        Retrieves the remote address (IP address) of the user from
        the request. If the 'x-forwarded-for' header is available, it
        returns the first IP address, otherwise, it returns the direct
        client's host.
        """
        if request.headers.get("x-forwarded-for"):
            return request.headers.get("x-forwarded-for").split(",")[0]
        else:
            return request.client.host

    def get_user_agent(self, request: Request):
        """
        Retrieves the user agent string from the request headers.
        Returns the user agent that indicates the browser or application
        making the request.
        """
        return ctx.request.headers.get("user-agent")


class LogsRequest(BaseModel):
    """
    A Pydantic model representing the parameters for querying logs. It
    allows filtering logs based on the user ID, offset, limit, and
    sorting options.
    """
    user_id__eq: Optional[int] = None
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
    order_by: Literal["id", "created_date", "user_id"]
    order: Literal["asc", "desc"]


async def after_token_retrieve(session: AsyncSession, cache: Redis,
                               current_user: None, user: User):
    """
    Callback function triggered after retrieving a token. If logging is
    enabled, it creates a log entry for the current user's request.
    """
    if LOGS_ENABLED:
        log_repository = Repository(session, cache, Log)
        log = Log(user, ctx.request)
        await log_repository.insert(log)


async def on_execute(session: AsyncSession, cache: Redis, current_user: User,
                     action: str, params: dict, response: dict):
    """
    Callback function triggered when an action is executed. If the
    action is related to logs, it queries and returns the relevant log
    data based on the provided parameters.
    """
    if action == LOGS_ACTION:
        LogsRequest(**params)

        log_repository = Repository(session, cache, Log)
        response["logs"] = await log_repository.select_all(**params)
        response["logs_count"] = await log_repository.count_all(**params)
