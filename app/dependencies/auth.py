# app/dependencies/auth.py
# SPDX-License-Identifier: GPL-3.0-only

import logging
import time
from enum import Enum

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.context import set_context_var
from app.dependencies.session import get_session
from app.events import Events as E
from app.models.user import User
from app.repositories.orm import ORMRepository
from app.security.encryption import decrypt_string
from app.security.jwt import decode_auth_token

log = logging.getLogger(__name__)
bearer_schema = HTTPBearer(auto_error=False)


class AccessLevel(str, Enum):
    READ = "can_read"
    WRITE = "can_write"
    EDIT = "can_edit"
    ADMIN = "can_admin"


def require_access(access_level: AccessLevel):
    async def auth_user(
        session: AsyncSession = Depends(get_session),
        credentials: HTTPAuthorizationCredentials | None = Depends(
            bearer_schema),
    ) -> User:
        """
        Dependency that authenticates a user using a Bearer token and
        enforces the required access level based on token validity and
        user state. Raises HTTPException:
        401 - Missing credentials, invalid token, malformed payload
        (including non-numeric user id), unknown user, or revoked token.
        403 - User inactive, suspended, or lacks required access level.
        """
        log.info("event=%s", E.AUTH_STARTED)

        if credentials is None or credentials.scheme.lower() != "bearer":
            log.warning("event=%s", E.AUTH_TOKEN_MISSING)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        try:
            payload = decode_auth_token(credentials.credentials)
        except jwt.InvalidTokenError:
            log.warning("event=%s", E.AUTH_TOKEN_INVALID)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        token_jti = payload.get("jti")
        if token_jti is None:
            log.warning("event=%s", E.AUTH_TOKEN_JTI_MISSING)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        user_id = payload.get("sub")
        if user_id is None:
            log.warning("event=%s", E.AUTH_USER_ID_MISSING)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            log.warning("event=%s", E.AUTH_USER_ID_INVALID)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        repository = ORMRepository(session)
        user = await repository.select(User, id=user_id)
        if user is None:
            log.warning("event=%s user_id=%s", E.AUTH_USER_NOT_FOUND, user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        if user.current_jti_encrypted is None:
            log.warning("event=%s user_id=%s", E.AUTH_USER_JTI_MISSING, user_id)  # noqa: E501
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        try:
            current_jti = decrypt_string(user.current_jti_encrypted)
        except Exception:
            log.warning("event=%s user_id=%s", E.AUTH_USER_JTI_INVALID, user_id)  # noqa: E501
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        if current_jti != token_jti:
            log.warning("event=%s user_id=%s", E.AUTH_TOKEN_JTI_MISMATCH, user_id)  # noqa: E501
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        if not user.is_active:
            log.warning("event=%s user_id=%s", E.AUTH_USER_INACTIVE, user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        now = int(time.time())
        if user.suspended_until is not None and user.suspended_until > now:
            log.warning("event=%s user_id=%s", E.AUTH_USER_SUSPENDED, user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        if not getattr(user, access_level.value):
            log.warning("event=%s user_id=%s", E.AUTH_USER_ROLE_INSUFFICIENT, user_id)  # noqa E501
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        set_context_var("current_user_id", user.id)
        log.info("event=%s user_id=%s", E.AUTH_COMPLETED, user_id)
        return user
    return auth_user
