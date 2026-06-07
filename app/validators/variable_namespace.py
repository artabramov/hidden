# app/validators/variable_namespace.py
# SPDX-License-Identifier: SSPL-1.0

import re

from pydantic_core import PydanticCustomError

from app.validators.validation_errors import VALUE_NOT_LATIN_EXTENDED

VARIABLE_NAMESPACE_PATTERN = re.compile(r"^[a-z0-9_-]+$")


def validate_namespace(value: object) -> object:
    if not isinstance(value, str):
        return value

    if value == "":
        return value

    if not VARIABLE_NAMESPACE_PATTERN.fullmatch(value):
        raise PydanticCustomError(*VALUE_NOT_LATIN_EXTENDED)

    return value
