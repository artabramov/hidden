# app/routers/variable_delete.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.paths.variable_key import get_variable_key
from app.schemas.variable_delete import VARIABLE_DELETE_ERRORS
from app.schemas.variable_path import VariablePath
from app.services.variable_delete import delete_variable

router = APIRouter(tags=["Variables"])


@router.delete(
    "/variable/{namespace}/{variable_key}",
    responses=VARIABLE_DELETE_ERRORS,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete variable",
)
async def variable_delete_router(
    path: VariablePath = Depends(get_variable_key),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.ADMIN)),
) -> Response:
    """
    Deletes a variable identified by namespace and key from the request
    path.

    **Hooks:**

    `VARIABLE_DELETE_COMPLETED` — executed after the variable is deleted.

    **Authentication:**

    - Requires a valid token with admin access.

    **Request path:**

    - `namespace` — logical group of variables.
    - `variable_key` — variable identifier within the namespace.

    **Response:**

    Empty response body.

    **Response codes:**

    - `204` — Variable deleted successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive or blocked.
    - `404` — Variable not found.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    await delete_variable(
        session=session,
        path=path,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
