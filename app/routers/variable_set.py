# app/routers/variable_set.py
# SPDX-License-Identifier: SSPL-1.0

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.paths.variable_key import get_variable_key
from app.schemas.variable_path import VariablePath
from app.schemas.variable_set import VARIABLE_SET_ERRORS, VariableSetRequest
from app.services.variable_set import set_variable

router = APIRouter(tags=["Variables"])


@router.put(
    "/variable/{namespace}/{variable_key}",
    responses=VARIABLE_SET_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Set variable value",
)
async def variable_set_router(
    data: VariableSetRequest,
    path: VariablePath = Depends(get_variable_key),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.ADMIN)),
) -> Response:
    """
    Creates or updates a variable identified by namespace and key from
    the request path. The endpoint creates a new variable if it does not
    exist or replaces the stored value if it already exists.

    **Hooks:**

    `VARIABLE_SET_COMPLETED` — executed after the variable is created or
    updated.

    **Authentication:**

    - Requires a valid token with admin access.

    **Request path:**

    - `namespace` — logical group of variables.
    - `variable_key` — variable identifier within the namespace.

    **Request body:**

    - `VariableSetRequest` — variable value only.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — Variable created or updated.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive or blocked.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    await set_variable(
        session=session,
        user=current_user,
        data=data,
        path=path,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
