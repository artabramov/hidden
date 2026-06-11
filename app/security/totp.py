# app/security/totp.py
# SPDX-License-Identifier: GPL-3.0-only

import uuid

import pyotp


def generate_mfa_session_uuid() -> str:
    """Random UUID for MFA step 2 after password verification."""
    return str(uuid.uuid4())


def generate_totp_secret() -> str:
    """Generate a new base32-encoded TOTP secret."""
    return pyotp.random_base32()


def is_totp_correct(secret: str, code: str) -> bool:
    """Verify a TOTP code against the provided secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
