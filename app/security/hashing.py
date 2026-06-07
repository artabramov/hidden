# app/security/hashing.py
# SPDX-License-Identifier: SSPL-1.0

import hashlib
import hmac
import os

_HASHING_ALGORITHM = "sha256"
_HASHING_SALT_SIZE = 16
_HASHING_ITERATIONS = 600_000


def hash_string(value: str) -> str:
    """Return a PBKDF2-HMAC-SHA256 hash string for arbitrary UTF-8 input."""
    salt = os.urandom(_HASHING_SALT_SIZE)

    dk = hashlib.pbkdf2_hmac(
        _HASHING_ALGORITHM,
        value.encode("utf-8"),
        salt,
        _HASHING_ITERATIONS,
    )

    return f"{_HASHING_ITERATIONS}${salt.hex()}${dk.hex()}"


def is_password_correct(password: str, password_hash: str) -> bool:
    """Return True if plaintext matches the stored PBKDF2 hash string."""
    try:
        iterations_str, salt_hex, hash_hex = password_hash.split("$", 2)
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except Exception:
        return False

    dk = hashlib.pbkdf2_hmac(
        _HASHING_ALGORITHM,
        password.encode("utf-8"),
        salt,
        iterations,
    )

    return hmac.compare_digest(dk, expected)
