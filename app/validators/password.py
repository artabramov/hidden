# app/validators/password.py
# SPDX-License-Identifier: SSPL-1.0

from pydantic_core import PydanticCustomError

from app.validators.validation_errors import (
    VALUE_MISSING_DIGIT,
    VALUE_MISSING_LOWERCASE,
    VALUE_MISSING_UPPERCASE,
)


def validate_password(value: str) -> str:
    if not any(c.islower() for c in value):
        raise PydanticCustomError(*VALUE_MISSING_LOWERCASE)

    if not any(c.isupper() for c in value):
        raise PydanticCustomError(*VALUE_MISSING_UPPERCASE)

    if not any(c.isdigit() for c in value):
        raise PydanticCustomError(*VALUE_MISSING_DIGIT)

    return value
