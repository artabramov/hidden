# app/security/randoms.py
# SPDX-License-Identifier: GPL-3.0-only

import secrets
import string

_ALPHABET = string.ascii_letters + string.digits


def generate_random_string(length: int) -> str:
    """
    Generate a random string of the given length,
    using the default alphabet.
    """
    if length < 1:
        raise ValueError("length must be positive")
    return "".join(
        secrets.choice(_ALPHABET) for _ in range(length)
    )
