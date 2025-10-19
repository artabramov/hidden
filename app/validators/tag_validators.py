"""
Validator for free-form tag values that enforces a canonical,
search-friendly representation. Input is Unicode-normalized,
whitespace is trimmed, and case is folded to achieve consistent
comparisons across locales. Blank or purely whitespace input is
rejected to prevent meaningless records.
"""

import unicodedata


def value_validate(value: str) -> str:
    """Normalize to NFKC, trim, and lower-case; reject empty."""
    if value is None:
        raise ValueError("Tag value must not be None.")

    v = unicodedata.normalize("NFKC", value).strip().casefold()
    if not v:
        raise ValueError("Tag value must not be empty.")

    return v
