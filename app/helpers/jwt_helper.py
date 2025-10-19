"""
Utilities for working with JSON Web Tokens: generates stable,
collision-resistant token identifiers, assembles signed claim sets
for authenticated users (including issued-at and optional expiry),
produces compact encoded tokens, and verifies and parses incoming
tokens with signature and standard claim validation.
"""

import time
import string
import secrets
import jwt
from app.models.user import User


def generate_jti(key_length: int) -> str:
    """
    Generates a cryptographically random alphanumeric JTI of the given
    length for uniquely identifying and potentially revoking tokens.
    """
    jti_symbols = string.ascii_letters + string.digits
    return "".join(secrets.choice(jti_symbols) for _ in range(key_length))


def create_payload(user: User, jti: str, exp: int = None):
    """
    Builds a JWT claims payload for the given user including user_id,
    role, username, jti, and iat (Unix seconds); if exp is provided it
    is used as an absolute expiration timestamp, otherwise the payload
    is created without an exp claim.
    """
    payload = {
        "user_id": user.id,
        "role": user.role,
        "username": user.username,
        "jti": jti,
        "iat": int(time.time())
    }
    if exp:
        payload["exp"] = exp

    return payload


def encode_jwt(payload: dict, jwt_secret: str, jwt_algorithm: str) -> str:
    """
    Encodes and signs the given claims payload into a compact JWT using
    the supplied secret and algorithm via PyJWT.
    """
    return jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)


def decode_jwt(jwt_token: str, jwt_secret: str, jwt_algorithms: list) -> dict:
    """
    Decodes a JWT using the given secret and allowed algorithms,
    validating the signature and standard claims (such as exp and iat)
    and returning the claims dictionary, raising PyJWT exceptions on
    invalid or expired tokens.
    """
    return jwt.decode(jwt_token, jwt_secret, algorithms=jwt_algorithms)
