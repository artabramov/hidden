"""Validators for document-related fields."""

from typing import Optional


def summary_validate(summary: Optional[str]) -> Optional[str]:
    """
    Validates document summary by trimming whitespace and converting
    blank strings to None. Returns the normalized document summary.
    """
    if summary is None:
        return None
    return summary.strip() or None
