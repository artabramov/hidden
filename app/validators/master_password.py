# app/validators/master_password.py
# SPDX-License-Identifier: GPL-3.0-only

from pydantic_core import PydanticCustomError

from app.validators.validation_errors import (
    VALUE_MISSING_DIGIT,
    VALUE_MISSING_LOWERCASE,
    VALUE_MISSING_UPPERCASE,
)

PREDICTABLE_SEQUENCE_MIN_LENGTH = 4
PREDICTABLE_SEQUENCES = (
    "0123456789",
    "9876543210",
    "abcdefghijklmnopqrstuvwxyz",
    "zyxwvutsrqponmlkjihgfedcba",
    "qwertyuiop",
    "poiuytrewq",
    "asdfghjkl",
    "lkjhgfdsa",
    "zxcvbnm",
    "mnbvcxz",
)

COMMON_WEAK_FRAGMENTS = (
    "password",
    "qwerty",
    "admin",
    "welcome",
    "letmein",
    "secret",
    "user",
    "login",
    "root",
)

MAX_IDENTICAL_CHARS_IN_ROW = 2


def validate_master_password(value: str) -> str:
    """
    Validate master password complexity requirements.
    """
    if not any(c.islower() for c in value):
        raise PydanticCustomError(*VALUE_MISSING_LOWERCASE)

    if not any(c.isupper() for c in value):
        raise PydanticCustomError(*VALUE_MISSING_UPPERCASE)

    if not any(c.isdigit() for c in value):
        raise PydanticCustomError(*VALUE_MISSING_DIGIT)

    normalized = value.lower()

    if _contains_predictable_sequence(normalized):
        raise PydanticCustomError(
            "value_error",
            "Value contains a predictable character sequence.",
        )

    if _contains_repeated_chars(value):
        raise PydanticCustomError(
            "value_error",
            "Value contains identical characters in a row.",
        )

    if _contains_common_weak_fragment(normalized):
        raise PydanticCustomError(
            "value_error",
            "Value contains a common weak password fragment.",
        )

    return value


def _contains_predictable_sequence(value: str) -> bool:
    for length in range(
        PREDICTABLE_SEQUENCE_MIN_LENGTH,
        len(value) + 1,
    ):
        for start in range(len(value) - length + 1):
            chunk = value[start:start + length]
            for sequence in PREDICTABLE_SEQUENCES:
                if chunk in sequence:
                    return True
    return False


def _contains_repeated_chars(value: str) -> bool:
    run_length = 1

    for index in range(1, len(value)):
        if value[index] == value[index - 1]:
            run_length += 1
            if run_length > MAX_IDENTICAL_CHARS_IN_ROW:
                return True
        else:
            run_length = 1

    return False


def _contains_common_weak_fragment(value: str) -> bool:
    return any(fragment in value for fragment in COMMON_WEAK_FRAGMENTS)
