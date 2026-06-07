# app/paths/variable_key.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import HTTPException, Path, status
from pydantic import ValidationError

from app.schemas.variable_path import VariablePath


def get_variable_key(
    namespace: str = Path(
        ...,
        description="Logical namespace used to group related variables.",
    ),
    variable_key: str = Path(
        ...,
        description="Unique variable name within the specified namespace.",
    ),
) -> VariablePath:
    """Build and validate path parameters for variable routes."""
    try:
        return VariablePath.model_validate(
            {"namespace": namespace, "variable_key": variable_key},
        )

    except ValidationError as exc:
        errors = []

        for err in exc.errors():
            errors.append({
                "type": err["type"],
                "loc": ["path", *err["loc"]],
                "msg": err["msg"],
                "input": err.get("input"),
            })

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=errors,
        ) from exc
