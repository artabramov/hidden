"""
Provides authentication and permission checks based on JWT tokens,
mapping user roles to functions that validate their access rights
and raising detailed errors on invalid or expired tokens.
"""

import time
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from fastapi import Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from app.models.user import User, UserRole
from app.sqlite import get_session
from app.redis import get_cache
from app.repository import Repository
from app.managers.encryption_manager import EncryptionManager
from app.helpers.jwt_helper import decode_jwt
from app.error import (
    E, LOC_HEADER, ERR_TOKEN_MISSING, ERR_TOKEN_INVALID,
    ERR_TOKEN_EXPIRED, ERR_ROLE_FORBIDDEN, ERR_USER_NOT_FOUND,
    ERR_USER_INACTIVE, ERR_USER_SUSPENDED, ERR_USER_REJECTED
)

auth_scheme = HTTPBearer(auto_error=False)


def auth(user_role: UserRole) -> Callable:
    """
    Returns a FastAPI dependency enforcing permissions for the specified
    role by mapping application roles to permission-check functions that
    gate access to protected routes.
    """
    if user_role == UserRole.reader:
        return _can_read
    elif user_role == UserRole.writer:
        return _can_write
    elif user_role == UserRole.editor:
        return _can_edit
    elif user_role == UserRole.admin:
        return _can_admin
    else:
        raise ValueError(f"Unknown user role: {user_role}")


async def _can_read(
    request: Request,
    session: AsyncSession = Depends(get_session),
    cache: Redis = Depends(get_cache),
    header: HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> User:
    """
    Authenticates the bearer token, loads the user, verifies read
    permissions, and returns the user object. Raises 401 for a missing,
    invalid, or expired token; raises 403 for insufficient permissions
    or when the account is not permitted (user not found, inactive,
    suspended, or JTI mismatch).
    """
    if (not header or not header.credentials
            or header.scheme.lower() != "bearer"):
        raise E([LOC_HEADER, "Authorization"], None,
                ERR_TOKEN_MISSING, status.HTTP_401_UNAUTHORIZED)

    user = await _auth(request, header.credentials, session, cache)
    if not user.can_read:
        raise E([LOC_HEADER, "Authorization"], header.credentials,
                ERR_ROLE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    request.state.log.debug("auth completed; role=reader; user_id=%s", user.id)
    return user


async def _can_write(
    request: Request,
    session: AsyncSession = Depends(get_session),
    cache: Redis = Depends(get_cache),
    header: HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> User:
    """
    Authenticates the bearer token, loads the user, verifies write
    permissions, and returns the user object. Raises 401 for a missing,
    invalid, or expired token; raises 403 for insufficient permissions
    or when the account is not permitted (user not found, inactive,
    suspended, or JTI mismatch).
    """
    if (not header or not header.credentials
            or header.scheme.lower() != "bearer"):
        raise E([LOC_HEADER, "Authorization"], None,
                ERR_TOKEN_MISSING, status.HTTP_401_UNAUTHORIZED)

    user = await _auth(request, header.credentials, session, cache)
    if not user.can_write:
        raise E([LOC_HEADER, "Authorization"], header.credentials,
                ERR_ROLE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    request.state.log.debug("auth completed; role=writer; user_id=%s", user.id)
    return user


async def _can_edit(
    request: Request,
    session: AsyncSession = Depends(get_session),
    cache: Redis = Depends(get_cache),
    header: HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> User:
    """
    Authenticates the bearer token, loads the user, verifies edit
    permissions, and returns the user object. Raises 401 for a missing,
    invalid, or expired token; raises 403 for insufficient permissions
    or when the account is not permitted (user not found, inactive,
    suspended, or JTI mismatch).
    """
    if (not header or not header.credentials
            or header.scheme.lower() != "bearer"):
        raise E([LOC_HEADER, "Authorization"], None,
                ERR_TOKEN_MISSING, status.HTTP_401_UNAUTHORIZED)

    user = await _auth(request, header.credentials, session, cache)
    if not user.can_edit:
        raise E([LOC_HEADER, "Authorization"], header.credentials,
                ERR_ROLE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    request.state.log.debug("auth completed; role=editor; user_id=%s", user.id)
    return user


async def _can_admin(
    request: Request,
    session: AsyncSession = Depends(get_session),
    cache: Redis = Depends(get_cache),
    header: HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> User:
    """
    Authenticates the bearer token, loads the user, verifies admin
    permissions, and returns the user object. Raises 401 for a missing,
    invalid, or expired token; raises 403 for insufficient permissions
    or when the account is not permitted (user not found, inactive,
    suspended, or JTI mismatch).
    """
    if (not header or not header.credentials
            or header.scheme.lower() != "bearer"):
        raise E([LOC_HEADER, "Authorization"], None,
                ERR_TOKEN_MISSING, status.HTTP_401_UNAUTHORIZED)

    user = await _auth(request, header.credentials, session, cache)
    if not user.can_admin:
        raise E([LOC_HEADER, "Authorization"], header.credentials,
                ERR_ROLE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    request.state.log.debug("auth completed; role=admin; user_id=%s", user.id)
    return user


async def _auth(
    request: Request, user_token: str,
    session: AsyncSession, cache: Redis,
) -> User:
    """
    Decodes and validates the JWT, checks expiration and signature,
    fetches the user from storage, verifies account state and JTI
    consistency, and returns the user object. Raises 401 for a missing,
    invalid, or expired token; raises 403 for insufficient permissions
    or when the account is not permitted (user not found, inactive,
    suspended, or JTI mismatch).
    """
    config = request.app.state.config

    # Decode JWT
    try:
        token_payload = decode_jwt(
            user_token, config.JWT_SECRET, config.JWT_ALGORITHMS)

    except ExpiredSignatureError:
        raise E([LOC_HEADER, "Authorization"], user_token,
                ERR_TOKEN_EXPIRED, status.HTTP_401_UNAUTHORIZED)

    except PyJWTError:
        raise E([LOC_HEADER, "Authorization"], user_token,
                ERR_TOKEN_INVALID, status.HTTP_401_UNAUTHORIZED)

    # Basic payload sanity checks
    user_id = token_payload.get("user_id")
    jti = token_payload.get("jti")
    if not isinstance(user_id, int) or not isinstance(jti, str) or not jti:
        raise E([LOC_HEADER, "Authorization"], user_token,
                ERR_TOKEN_INVALID, status.HTTP_401_UNAUTHORIZED)

    # Load & check user
    user_repository = Repository(session, cache, User, config)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_HEADER, "Authorization"], user_token,
                ERR_USER_NOT_FOUND, status.HTTP_403_FORBIDDEN)

    elif not user.active:
        raise E([LOC_HEADER, "Authorization"], user_token,
                ERR_USER_INACTIVE, status.HTTP_403_FORBIDDEN)

    elif user.suspended_until_date > int(time.time()):
        raise E([LOC_HEADER, "Authorization"], user_token,
                ERR_USER_SUSPENDED, status.HTTP_403_FORBIDDEN)

    # JTI consistency check
    encryption_manager = EncryptionManager(config, request.state.secret_key)
    if jti != encryption_manager.decrypt_str(user.jti_encrypted):
        raise E([LOC_HEADER, "Authorization"], user_token,
                ERR_USER_REJECTED, status.HTTP_403_FORBIDDEN)

    return user
