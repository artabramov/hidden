# app/pydantic/master_password.py
# SPDX-License-Identifier: Apache-2.0

"""
Master password validation for the management API.

Strength rules (length 16-1024 and lowercase, uppercase, and digit)
apply only when the password is first set (init) or replaced (rotate).
Mount, unmount, reveal, and reset authenticate the caller by decrypting
the stored passphrase and do not re-check password composition.
"""

MASTER_PASSWORD_AUTH_DESCRIPTION = (
    "Master password used for authentication. Composition is not "
    "validated; correctness is verified by decrypting the stored "
    "passphrase."
)

MASTER_PASSWORD_SET_DESCRIPTION = (
    "Master password to store. Must be 16-1024 characters and include "
    "a lowercase letter, an uppercase letter, and a digit."
)


def validate_master_password(value: str) -> str:
    """
    Validate master password composition for init and rotate.

    Use only when setting or changing the master password, not when
    authenticating an existing password on mount, unmount, reveal, or
    reset.
    """
    if not any(c.islower() for c in value):
        raise ValueError(
            "Master password must contain a lowercase letter."
        )
    if not any(c.isupper() for c in value):
        raise ValueError(
            "Master password must contain an uppercase letter."
        )
    if not any(c.isdigit() for c in value):
        raise ValueError(
            "Master password must contain a digit."
        )
    return value
