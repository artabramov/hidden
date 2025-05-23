"""
The module provides utility functions for user auth and permission
checking in the app. It includes functions to validate user roles
and permissions based on JWT tokens. The auth function maps user
roles (reader, writer, editor, admin) to their corresponding
permission-checking functions.
"""

import time
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from fastapi import Depends, status
from fastapi.security import HTTPBearer
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from app.models.user_model import User, UserRole
from app.postgres import get_session
from app.redis import get_cache
from app.repository import Repository
from app.helpers.jwt_helper import jwt_decode
from app.error import (
    E, LOC_HEADER, ERR_TOKEN_INVALID, ERR_TOKEN_EXPIRED, ERR_TOKEN_REJECTED)

jwt = HTTPBearer()


def auth(user_role: UserRole):
    """
    Returns the appropriate permission function based on the given
    user role. The function maps user roles such as reader, writer,
    editor, and admin to their corresponding permission functions.
    """
    if user_role == UserRole.reader:
        return _can_read

    elif user_role == UserRole.writer:
        return _can_write

    elif user_role == UserRole.editor:
        return _can_edit

    elif user_role == UserRole.admin:
        return _can_admin


async def _can_read(session: AsyncSession = Depends(get_session),
                    cache: Redis = Depends(get_cache), header=Depends(jwt)):
    """Verifies if a user has read permission based on the token."""
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_read:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_REJECTED, status.HTTP_401_UNAUTHORIZED)
    return user


async def _can_write(session: AsyncSession = Depends(get_session),
                     cache: Redis = Depends(get_cache), header=Depends(jwt)):
    """Verifies if a user has write permission based on the token."""
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_write:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_REJECTED, status.HTTP_401_UNAUTHORIZED)
    return user


async def _can_edit(session: AsyncSession = Depends(get_session),
                    cache: Redis = Depends(get_cache), header=Depends(jwt)):
    """Verifies if a user has edit permission based on the token."""
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_edit:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_REJECTED, status.HTTP_401_UNAUTHORIZED)
    return user


async def _can_admin(session: AsyncSession = Depends(get_session),
                     cache: Redis = Depends(get_cache), header=Depends(jwt)):
    """Verifies if a user has admin permission based on the token."""
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_admin:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_REJECTED, status.HTTP_401_UNAUTHORIZED)
    return user


async def _auth(user_token: str, session: AsyncSession, cache: Redis):
    """
    Authenticates a user based on the token. It checks the token format
    and handling corresponding validation errors.
    """
    try:
        token_payload = jwt_decode(user_token)

    except ExpiredSignatureError:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_EXPIRED, status.HTTP_401_UNAUTHORIZED)

    except PyJWTError:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_INVALID, status.HTTP_401_UNAUTHORIZED)

    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=token_payload["user_id"])

    if not user:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_REJECTED, status.HTTP_401_UNAUTHORIZED)

    elif not user.is_active:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_REJECTED, status.HTTP_401_UNAUTHORIZED)

    elif user.suspended_date > int(time.time()):
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_REJECTED, status.HTTP_401_UNAUTHORIZED)

    elif token_payload["jti"] != user.jti:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_REJECTED, status.HTTP_401_UNAUTHORIZED)

    return user
