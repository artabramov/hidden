"""
The module defines validator for username.
"""

import re


def username_validate(username: str):
    """The username must contain only letters and digits."""
    username = username.lower()
    if not re.match(r"^[a-z0-9]+$", username):
        raise ValueError("Only letters and numbers are allowed.")

    return username
