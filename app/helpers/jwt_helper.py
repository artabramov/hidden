"""
The module provides utility functions for handling JSON web tokens (JWT),
including creating unique identifiers (JTI), encoding user information
into a JWT, and decoding a JWT to retrieve the payload.
"""

import jwt
import time
import string
import random
from app.config import get_config

cfg = get_config()


def generate_jti() -> str:
    """
    Generates a JSON web token identifier (JTI) by creating a random
    string consisting of alphanumeric characters with a length specified
    in the configuration.
    """
    jti_symbols = string.ascii_letters + string.digits
    return "".join(random.choices(jti_symbols, k=cfg.JTI_LENGTH))


def jwt_encode(user, token_exp: int = None) -> str:
    """
    Encodes user data into a JSON web token (JWT) with an optional
    expiration time. The token includes user ID, role, username, unique
    token identifier (JTI) and issue time (IAT).
    """
    current_time = int(time.time())
    token_payload = {
        "user_id": user.id,
        "user_role": user.user_role,
        "username": user.username,
        "jti": user.jti,
        "iat": current_time,
    }
    if token_exp:
        token_payload["exp"] = token_exp

    token_encoded = jwt.encode(
        token_payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)
    return token_encoded


def jwt_decode(jwt_token: str) -> dict:
    """
    Decodes a JSON web token (JWT) to extract its payload, including
    user ID, role, username, issue time, and optional expiration time.
    """
    token_decoded = jwt.decode(
        jwt_token, cfg.JWT_SECRET, algorithms=cfg.JWT_ALGORITHM)

    token_payload = {
        "user_id": token_decoded["user_id"],
        "user_role": token_decoded["user_role"],
        "username": token_decoded["username"],
        "iat": token_decoded["iat"],
        "jti": token_decoded["jti"],
    }

    if "exp" in token_decoded:
        token_payload["exp"] = token_decoded["exp"]

    return token_payload
