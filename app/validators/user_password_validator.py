"""
The module defines validator for user password.
"""

import re


def user_password_validate(user_password: str):
    """
    The password must meet specific security requirements: it must
    contain at least one lowercase letter, one uppercase letter, one
    digit, and one special character.
    """
    if " " in user_password:
        raise ValueError("Must not contain spaces.")

    elif not re.search(r"[a-z]", user_password):
        raise ValueError("Must contain a lowercase letter.")

    elif not re.search(r"[A-Z]", user_password):
        raise ValueError("Must contain an uppercase letter.")

    elif not re.search(r"\d", user_password):
        raise ValueError("Must contain at a digit.")

    elif not re.search(r"[!@#$%^&*()_+={}\[\]:;\'<>,.?/\\|]", user_password):
        raise ValueError("Must contain a special character.")

    return user_password
