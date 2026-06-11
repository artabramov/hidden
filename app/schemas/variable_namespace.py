# app/schemas/variable_namespace.py
# SPDX-License-Identifier: GPL-3.0-only

from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

from app.validators.variable_namespace import validate_namespace


class VariableNamespace(BaseModel):
    """
    Path parameter identifying a variable namespace. Leading and
    trailing whitespace is stripped, ASCII letters are lowercased,
    and the value must contain only a-z, 0-9, underscores, and
    hyphens.
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

    @field_validator("namespace")
    @classmethod
    def validate_namespace(cls, value: str) -> str:
        return validate_namespace(value)
