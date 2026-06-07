# app/paths/variable_namespace.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import HTTPException, Path, status
from pydantic import ValidationError

from app.schemas.variable_namespace import VariableNamespace


def get_variable_namespace(
    namespace: str = Path(
        ...,
        description="Logical namespace used to group related variables.",
    ),
) -> VariableNamespace:
    """Build and validate namespace path parameter for variable routes."""
    try:
        return VariableNamespace.model_validate(
            {"namespace": namespace},
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
