"""
The module defines validator for one-time password.
"""


def user_totp_validate(user_totp: str):
    """The one-time password must contain only digits."""
    if not user_totp.isnumeric():
        raise ValueError("Must contain numeric characters.")

    return user_totp
