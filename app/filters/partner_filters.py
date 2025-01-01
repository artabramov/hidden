"""
The module provides functions for filtering partner-related attributes.
These filters are used within Pydantic schemas.
"""

from typing import Union


def filter_partner_name(partner_name: str = None) -> Union[str, None]:
    """
    Filters a partner name by stripping leading and trailing whitespace.
    If the input is empty, returns None. Otherwise, returns the trimmed
    partner name.
    """
    return partner_name.strip() if partner_name else None


def filter_partner_contacts(partner_contacts: str = None) -> Union[str, None]:
    """
    Filters partner contacts by stripping leading and trailing
    whitespace. If the input is empty or consists only of whitespace,
    returns None. Otherwise, returns the trimmed contacts information.
    """
    if partner_contacts:
        return partner_contacts.strip() or None
    return None


def filter_partner_summary(partner_summary: str = None) -> Union[str, None]:
    """
    Filters a partner summary by stripping leading and trailing
    whitespace. If the input is empty or consists only of whitespace,
    returns None. Otherwise, returns the trimmed partner summary.
    """
    if partner_summary:
        return partner_summary.strip() or None
    return None
