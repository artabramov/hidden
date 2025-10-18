"""Validators for file and folder related fields."""

import unicodedata
from typing import Optional


# Cross-platform safety: forbid Windows names so
# that names are portable between systems/volumes.
_WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *{f"COM{i}" for i in range(1, 10)},
    *{f"LPT{i}" for i in range(1, 10)},
}

# A set of characters that are not allowed in names on Windows;
# on Unix, many of them are allowed, but all of them for portability.
_INVALID_CHARS = set('<>:"/\\|?*')


def name_validate(name: str) -> str:
    """
    Validates name used as a single component by trimming surrounding
    whitespace and ensuring the result is not empty, rejecting the
    special components '.' and '..', forbidding characters that are
    problematic across platforms as well as any ASCII control characters
    including NUL, disallowing a trailing dot and Windows-reserved names
    regardless of extension, and enforcing a maximum of 255 bytes when
    encoded in UTF-8. The value is Unicode-normalized to NFC prior to
    the byte-length check, and the normalized name is returned.
    """
    if not isinstance(name, str):
        raise ValueError("Name must be a string")

    name = unicodedata.normalize("NFC", name.strip())

    if not name:
        raise ValueError("Name must not be empty")

    # Disallow special path components
    elif name in (".", ".."):
        raise ValueError("Name must not be '.' or '..'")

    # Disallow invalid characters (portable set)
    elif any(ch in _INVALID_CHARS for ch in name):
        raise ValueError("Name contains invalid characters")

    # Disallow ASCII control characters (including NUL) and DEL
    elif any(ord(ch) < 32 or ord(ch) == 127 for ch in name):
        raise ValueError("Name must not contain control characters")

    # Disallow trailing dot (problematic on Windows)
    elif name.endswith("."):
        raise ValueError("Name must not end with a dot")

    # Forbid Windows reserved names regardless of extension
    elif name.split(".", 1)[0].upper() in _WINDOWS_RESERVED:
        raise ValueError("Name must not be a reserved name on Windows")

    elif len(name.encode("utf-8")) > 255:
        raise ValueError("Name must not exceed 255 bytes in UTF-8")

    return name


def summary_validate(summary: Optional[str]) -> Optional[str]:
    """
    Validates file summary by trimming whitespace and converting
    blank strings to None. Returns the normalized file summary.
    """
    if summary is None:
        return None
    return summary.strip() or None
