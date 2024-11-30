"""
The module pProvides utility functions for handling JSON Web Tokens
(JWTs), including creating unique identifiers (JTI), encoding user
information into a JWT, and decoding a JWT to retrieve the payload.
Uses the configured secret key and algorithm for encoding and decoding.
"""

import jwt
import time
import string
import random
from app.config import get_config

cfg = get_config()


def jti_create() -> str:
    """
    Generates a JSON Web Token Identifier (JTI) by creating a random
    string consisting of alphanumeric characters with a length specified
    in the configuration.
    """
    return "".join(random.choices(string.ascii_letters + string.digits,
                                  k=cfg.JTI_LENGTH))


def jwt_encode(user, token_exp: int = None) -> str:
    """
    Encodes user information into a JSON Web Token (JWT) with an
    optional expiration time. The token includes user ID, role, login,
    and a unique JTI, and is signed with a secret key.
    """
    current_time = int(time.time())
    token_payload = {
        "user_id": user.id,
        "user_role": user.user_role.value,
        "user_login": user.user_login,
        "jti": user.jti,
        "iat": current_time,
    }
    if token_exp:
        token_payload["exp"] = token_exp

    token_encoded = jwt.encode(token_payload, cfg.JWT_SECRET,
                               algorithm=cfg.JWT_ALGORITHM)
    return token_encoded


def jwt_decode(jwt_token: str) -> dict:
    token_decoded = jwt.decode(jwt_token, cfg.JWT_SECRET,
                               algorithms=cfg.JWT_ALGORITHM)
    """
    Decodes a JSON Web Token (JWT) to extract its payload, including
    user ID, role, login, issue time, and optional expiration time. The
    token is verified using the secret key and the specified algorithm.
    """
    token_payload = {
        "user_id": token_decoded["user_id"],
        "user_role": token_decoded["user_role"],
        "user_login": token_decoded["user_login"],
        "iat": token_decoded["iat"],
        "jti": token_decoded["jti"],
    }

    if "exp" in token_decoded:
        token_payload["exp"] = token_decoded["exp"]

    return token_payload
