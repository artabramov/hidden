"""Validation helpers for user-related fields."""

import re
from typing import Optional

USERNAME_RE = re.compile(r"^[a-z0-9_]+$")
SPECIALS_RE = re.compile(r"[!@#$%^&*()_+={}\[\]:;'<>,.?/\\|\-]")
ALLOWED_ROLES = {"reader", "writer", "editor", "admin"}


def username_validate(username: str) -> str:
    """
    Validates username by lowercasing and ensuring only lowercase
    letters, digits, or underscore are allowed.
    """
    username = username.lower()
    if not USERNAME_RE.match(username):
        raise ValueError("Only lowercase letters, digits, or underscore.")
    return username


def password_validate(password: str) -> str:
    """
    Validates password by disallowing spaces and requiring lowercase,
    uppercase, digit, and special character.
    """
    if " " in password:
        raise ValueError("Must not contain spaces.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Must contain a lowercase letter.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Must contain an uppercase letter.")
    if not re.search(r"\d", password):
        raise ValueError("Must contain a digit.")
    if not SPECIALS_RE.search(password):
        raise ValueError("Must contain a special character.")
    return password


def role_validate(role: str) -> str:
    """
    Normalizes a role string without validating membership. Strips
    leading/trailing whitespace and lowercases the value.
    """
    return role.strip().lower() if isinstance(role, str) else role


def totp_validate(totp: str):
    """The one-time password must contain only digits."""
    if not totp.isnumeric():
        raise ValueError("Must contain numeric characters.")

    return totp


def summary_validate(summary: Optional[str]) -> Optional[str]:
    """
    Validates summary by trimming whitespace and converting blank
    strings to None.
    """
    if summary is None:
        return None
    
    return summary.strip() or None
