# app/validators/file_tag.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic_core import PydanticCustomError

from app.validators.validation_errors import VALUE_NOT_ALPHANUMERIC_EXTENDED


def validate_file_tag(value: object) -> str:
    """
    Validate file tag and normalize it to lowercase. The value must be
    a non-empty string containing only letters, digits, underscores and
    hyphens.
    """
    if not isinstance(value, str) or not value:
        raise PydanticCustomError(*VALUE_NOT_ALPHANUMERIC_EXTENDED)

    normalized = value.lower()

    if not all(ch.isalnum() or ch in {"_", "-"} for ch in normalized):
        raise PydanticCustomError(*VALUE_NOT_ALPHANUMERIC_EXTENDED)

    return normalized
