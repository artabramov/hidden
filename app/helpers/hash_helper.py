"""
The module provides functionality for hashing strings using SHA-512 with
a configurable salt.
"""

import hashlib
from app.config import get_config

cfg = get_config()


def get_hash(value: str) -> str:
    """
    Computes a SHA-512 hash of the given string concatenated with a
    configured salt, and returns the hexadecimal digest.
    """
    encoded_value = (value + cfg.HASHLIB_SALT).encode()
    hash = hashlib.sha512(encoded_value)
    return hash.hexdigest()
