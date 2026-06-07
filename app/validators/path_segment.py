# app/validators/path_segment.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic_core import PydanticCustomError

from app.validators.validation_errors import VALUE_NOT_PATH_SEGMENT


def validate_path_segment(value: str) -> str:
    """
    Ensure the value is a safe single filesystem path segment.
    Rejects ".", "..", path separators ("/", "\\"), null byte,
    and ASCII control characters.
    Returns the original value or raises PydanticCustomError.
    """
    if value in {".", ".."}:
        raise PydanticCustomError(*VALUE_NOT_PATH_SEGMENT)

    if "/" in value or "\\" in value or "\x00" in value:
        raise PydanticCustomError(*VALUE_NOT_PATH_SEGMENT)

    if any(ord(char) < 32 for char in value):
        raise PydanticCustomError(*VALUE_NOT_PATH_SEGMENT)

    return value
