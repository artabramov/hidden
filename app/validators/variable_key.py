# app/validators/variable_key.py
# SPDX-License-Identifier: GPL-3.0-only

import re

from pydantic_core import PydanticCustomError

from app.validators.validation_errors import VALUE_NOT_LATIN_EXTENDED

VARIABLE_KEY_PATTERN = re.compile(r"^[a-z0-9_-]+$")


def validate_variable_key(value: object) -> object:
    if not isinstance(value, str):
        return value

    if value == "":
        return value

    if not VARIABLE_KEY_PATTERN.fullmatch(value):
        raise PydanticCustomError(*VALUE_NOT_LATIN_EXTENDED)

    return value
