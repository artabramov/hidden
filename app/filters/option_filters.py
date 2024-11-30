"""
The module provides functions for filtering option keys and values.
These filters are used within Pydantic schemas.
"""

from typing import Union


def filter_option_key(option_key: str) -> str:
    """
    Filters an option key by stripping leading and trailing whitespace,
    and converting it to lowercase.
    """
    return option_key.strip().lower()


def filter_option_value(option_value: str = None) -> Union[str, None]:
    """
    Filters an option value by stripping leading and trailing whitespace.
    If the value is empty or None, returns None.
    """
    return option_value.strip() if option_value else None
