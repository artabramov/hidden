"""Validation helpers for collection-related fields."""

from typing import Optional


def name_validate(name: str) -> str:
    """
    Validates collection name by ensuring it does not contain forbidden
    characters such as / or NUL and does not exceed 255 bytes in UTF-8.
    Returns the name unchanged if valid.
    """
    if "/" in name or "\x00" in name:
        raise ValueError("name must not contain '/' or NUL characters")
    
    elif len(name.encode("utf-8")) > 255:
        raise ValueError("name must not exceed 255 bytes in UTF-8")

    return name


def summary_validate(summary: Optional[str]) -> Optional[str]:
    """
    Validates summary by trimming whitespace and converting blank
    strings to None. Returns the normalized summary.
    """
    if summary is None:
        return None
    return summary.strip() or None
