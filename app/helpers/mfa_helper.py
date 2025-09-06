"""
Provides a helper to generate a random Base32-encoded secret for
time-based one-time password (TOTP) multi-factor authentication (MFA).
"""

import pyotp


def generate_mfa_secret() -> str:
    """
    Generates and returns a random base32-encoded secret suitable
    for use with time-based one-time password (TOTP) MFA systems.
    """
    return pyotp.random_base32()


def calculate_totp(mfa_secret: str):
    """
    Computes the current time-based one-time password derived from
    the provided Base32 secret, compatible with standard TOTP apps.
    """
    if not isinstance(mfa_secret, str) or not mfa_secret.strip():
        raise ValueError("MFA secret must be a non-empty string")

    totp = pyotp.TOTP(mfa_secret)
    return totp.now()
