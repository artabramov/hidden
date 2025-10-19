"""
Validators for folder metadata. Provides a simple normalization pass for
textual summaries that trims surrounding whitespace and converts blank
input to a null value.
"""

from typing import Optional


def summary_validate(summary: Optional[str]) -> Optional[str]:
    """
    Validates summary by trimming whitespace and converting blank
    strings to None. Returns the normalized summary.
    """
    if summary is None:
        return None
    return summary.strip() or None
