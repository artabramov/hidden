"""
The module provides a function for generating a random secret key used
for multi-factor authentication (MFA).
"""

import pyotp


def generate_mfa_secret() -> str:
    """
    Generates and returns a random base32-encoded secret suitable for
    use with time-based one-time password (TOTP) MFA systems.
    """
    return pyotp.random_base32()
