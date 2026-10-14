# app/security/randoms.py
# SPDX-License-Identifier: Apache-2.0

import secrets
import string

_ALPHABET = string.ascii_letters + string.digits


def generate_random_string(length: int) -> str:
    """
    Generate a cryptographically secure random string of the specified
    positive length using ASCII letters and digits.
    """
    if length < 1:
        raise ValueError("length must be positive")
    return "".join(
        secrets.choice(_ALPHABET) for _ in range(length)
    )
