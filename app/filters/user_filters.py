"""
The module provides functions for filtering user entity attributes,
such as login, password, first name, last name, TOTP (Time-based
One-Time Password), and token expiration time. These filters are
used within Pydantic schemas.
"""

from typing import Union


def filter_user_login(user_login: str) -> str:
    """
    Filters a user login by stripping leading and trailing whitespace
    and converting it to lowercase. If the input is empty, returns None.
    Otherwise, returns the trimmed and lowercase user login.
    """
    return user_login.strip().lower()


def filter_first_name(first_name: str) -> str:
    """
    Filters a first name by stripping leading and trailing whitespace.
    If the input is empty, returns None. Otherwise, returns the trimmed
    first name.
    """
    return first_name.strip()


def filter_last_name(last_name: str) -> str:
    """
    Filters a last name by stripping leading and trailing whitespace.
    If the input is empty, returns None. Otherwise, returns the trimmed
    last name.
    """
    return last_name.strip()


def filter_user_caption(user_caption: str = None) -> Union[str, None]:
    """
    Filters a user caption by stripping leading and trailing whitespace.
    If the input is empty or None, returns None. Otherwise, returns the
    trimmed user caption.
    """
    if user_caption is None:
        return None

    user_caption = user_caption.strip()
    return None if user_caption == "" else user_caption


def filter_user_contacts(user_contacts: str = None) -> Union[str, None]:
    """
    Filters user contacts by stripping leading and trailing whitespace.
    If the input is empty or None, returns None. Otherwise, returns the
    trimmed contacts.
    """
    if user_contacts:
        return user_contacts.strip() or None
    return None


def filter_user_totp(user_totp: str) -> str:
    """
    Filters a user TOTP by checking if the input is numeric. If not,
    raises a ValueError. Otherwise, returns the original TOTP.
    """
    if not user_totp.isnumeric():
        raise ValueError
    return user_totp
