"""Validation helpers for file-related fields."""

from typing import Final


def filename_validate(filename: str) -> str:
    """
    Validates a file name used as a single path component. Trims leading
    and trailing whitespace, ensures non-empty, rejects . and .. and
    forbids / and NUL. Enforces ≤255 UTF-8 bytes. Returns the (possibly
    trimmed) filename.
    """
    if not isinstance(filename, str):
        raise ValueError("Filename must be string")

    filename = filename.strip()

    if not filename:
        raise ValueError("Filename must not be empty")

    elif filename in (".", ".."):
        raise ValueError("Filename must not be . or ..'")

    elif "/" in filename or "\x00" in filename:
        raise ValueError("Filename must not contain / or NUL characters")

    elif len(filename.encode("utf-8")) > 255:
        raise ValueError("Filename must not exceed 255 bytes in UTF-8")

    return filename
