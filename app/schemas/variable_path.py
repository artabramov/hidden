# app/schemas/variable_path.py
# SPDX-License-Identifier: SSPL-1.0

from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

from app.validators.variable_key import validate_variable_key
from app.validators.variable_namespace import validate_namespace


class VariablePath(BaseModel):
    """
    Path parameters identifying a variable by namespace and key.
    Leading and trailing whitespace is stripped, ASCII letters are
    lowercased, and each segment must contain only a-z, 0-9,
    underscores, and hyphens.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    namespace: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            to_lower=True,
            min_length=1,
            max_length=255,
        ),
    ] = Field(
        description="Logical namespace used to group related variables.",
    )

    variable_key: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            to_lower=True,
            min_length=1,
            max_length=255,
        ),
    ] = Field(
        description="Unique variable name within the specified namespace.",
    )

    @field_validator("namespace")
    @classmethod
    def validate_namespace(cls, value: object) -> object:
        return validate_namespace(value)

    @field_validator("variable_key")
    @classmethod
    def validate_variable_key(cls, value: object) -> object:
        return validate_variable_key(value)
