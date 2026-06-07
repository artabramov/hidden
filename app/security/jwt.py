# app/security/jwt.py
# SPDX-License-Identifier: SSPL-1.0

import time
import uuid

import jwt

from app.config import get_config

_JWT_ALGORITHM = "HS256"


def generate_jti() -> str:
    """
    Generate a unique token identifier (JTI)
    for tracking and revocation.
    """
    return uuid.uuid4().hex


def create_auth_token(
    user_id: int,
    current_jti: str,
    disable_exp: bool = False,
) -> str:
    """
    Create a signed token with user identity and JTI. When disable_exp
    is False, an exp claim is added using the configured TTL. When
    disable_exp is True, exp is omitted and the token does not expire;
    the caller is responsible for ensuring this is permitted.
    """
    config = get_config()

    now = int(time.time())
    payload: dict = {
        "sub": str(user_id),
        "iat": now,
        "jti": current_jti,
    }

    if not disable_exp:
        payload["exp"] = now + config.AUTH_TOKEN_TTL_SECONDS

    return jwt.encode(
        payload,
        config.JWT_SIGNING_KEY,
        algorithm=_JWT_ALGORITHM,
    )


def decode_auth_token(token: str) -> dict:
    """
    Decode and verify token signature; user state
    and JTI must be checked separately.
    """
    config = get_config()

    return jwt.decode(
        token,
        config.JWT_SIGNING_KEY,
        algorithms=[_JWT_ALGORITHM],
    )
