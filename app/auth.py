"""
The module provides utility functions for user authentication and
permission checking in the application. It includes functions to
validate user roles and permissions based on JWT tokens. The auth
function maps user roles (reader, writer, editor, admin) to their
corresponding permission-checking functions. Dependencies include
database sessions, Redis cache, and JWT headers.
"""

import time
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from fastapi import Depends, status
from fastapi.security import HTTPBearer
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from app.models.user_model import User, UserRole
from app.database import get_session
from app.cache import get_cache
from app.repository import Repository
from app.helpers.jwt_helper import jwt_decode
from app.errors import E
from app.constants import (
    LOC_HEADER, ERR_USER_ROLE_REJECTED, ERR_TOKEN_MISSING,
    ERR_TOKEN_EXPIRED, ERR_TOKEN_INVALID, ERR_TOKEN_REJECTED,
    ERR_TOKEN_ORPHANED, ERR_USER_INACTIVE, ERR_USER_SUSPENDED)

jwt = HTTPBearer()


def auth(user_role: UserRole):
    """
    Returns the appropriate permission function based on the given
    user role. The function maps user roles such as reader, writer,
    editor, and admin to their corresponding permission functions,
    enabling role-based access control. If the role is not recognized,
    it returns None.
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
    """
    Verifies if a user has read permissions based on their JWT token.
    It retrieves the user using the token and checks if the user
    has the corresponding permission. If not, it raises an exception.
    The function depends on the session, cache, and JWT header to
    authenticate and authorize the user.
    """
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_read:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_USER_ROLE_REJECTED, status.HTTP_403_FORBIDDEN)
    return user


async def _can_write(session: AsyncSession = Depends(get_session),
                     cache: Redis = Depends(get_cache), header=Depends(jwt)):
    """
    Verifies if a user has write permissions based on their JWT token.
    It retrieves the user using the token and checks if the user
    has the corresponding permission. If not, it raises an exception.
    The function depends on the session, cache, and JWT header to
    authenticate and authorize the user.
    """
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_write:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_USER_ROLE_REJECTED, status.HTTP_403_FORBIDDEN)
    return user


async def _can_edit(session: AsyncSession = Depends(get_session),
                    cache: Redis = Depends(get_cache), header=Depends(jwt)):
    """
    Verifies if a user has edit permissions based on their JWT token.
    It retrieves the user using the token and checks if the user
    has the corresponding permission. If not, it raises an exception.
    The function depends on the session, cache, and JWT header to
    authenticate and authorize the user.
    """
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_edit:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_USER_ROLE_REJECTED, status.HTTP_403_FORBIDDEN)
    return user


async def _can_admin(session: AsyncSession = Depends(get_session),
                     cache: Redis = Depends(get_cache), header=Depends(jwt)):
    """
    Verifies if a user has admin permissions based on their JWT token.
    It retrieves the user using the token and checks if the user
    has the corresponding permission. If not, it raises an exception.
    The function depends on the session, cache, and JWT header to
    authenticate and authorize the user.
    """
    user_token = header.credentials
    user = await _auth(user_token, session, cache)
    if not user.can_admin:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_USER_ROLE_REJECTED, status.HTTP_403_FORBIDDEN)
    return user


async def _auth(user_token: str, session: AsyncSession, cache: Redis):
    """
    Authenticates a user based on the provided JWT token. The function
    verifies the token, handling errors such as missing, expired, or
    invalid tokens, and checks if the token is associated with a valid
    and active user. It retrieves the user from the repository using the
    token's user ID, validates the token's identifier, and ensures the
    user is not suspended. If any check fails, an exception is raised
    with an appropriate error code. Returns the authenticated user if
    all checks pass.
    """
    if not user_token:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_MISSING, status.HTTP_403_FORBIDDEN)

    try:
        token_payload = jwt_decode(user_token)

    except ExpiredSignatureError:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_EXPIRED, status.HTTP_403_FORBIDDEN)

    except PyJWTError:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_INVALID, status.HTTP_403_FORBIDDEN)

    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=token_payload["user_id"])

    if token_payload["jti"] != user.jti:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_REJECTED, status.HTTP_403_FORBIDDEN)

    elif not user:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_TOKEN_ORPHANED, status.HTTP_403_FORBIDDEN)

    elif not user.is_active:
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_USER_INACTIVE, status.HTTP_403_FORBIDDEN)

    elif user.suspended_date > int(time.time()):
        raise E([LOC_HEADER, "user_token"], user_token,
                ERR_USER_SUSPENDED, status.HTTP_403_FORBIDDEN)

    return user
