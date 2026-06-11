# app/routers/variable_get.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.paths.variable_key import get_variable_key
from app.schemas.variable_get import VARIABLE_GET_ERRORS, VariableGetResponse
from app.schemas.variable_path import VariablePath
from app.services.variable_get import get_variable as get_variable_service

router = APIRouter(tags=["Variables"])


@router.get(
    "/variable/{namespace}/{variable_key}",
    response_model=VariableGetResponse,
    responses=VARIABLE_GET_ERRORS,
    status_code=status.HTTP_200_OK,
    summary="Get variable",
)
async def variable_get_router(
    path: VariablePath = Depends(get_variable_key),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.ADMIN)),
) -> VariableGetResponse:
    """
    Returns a variable identified by namespace and key from the request
    path. It retrieves the stored value together with its metadata.

    **Hooks:**

    `VARIABLE_GET_COMPLETED` — executed after the variable is retrieved.

    **Authentication:**

    - Requires a valid token with admin access.

    **Request path:**

    - `namespace` — logical group of variables.
    - `variable_key` — variable identifier within the namespace.

    **Response:**

    `VariableGetResponse` — variable value and metadata.

    **Response codes:**

    - `200` — Variable returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive or blocked.
    - `404` — Variable not found.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    variable = await get_variable_service(
        session=session,
        path=path,
    )

    return variable
