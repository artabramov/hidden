# app/routers/variable_list.py
# SPDX-License-Identifier: GPL-3.0-only

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import AccessLevel, require_access
from app.dependencies.session import get_session
from app.models.user import User
from app.paths.variable_namespace import get_variable_namespace
from app.schemas.variable_get import VariableGetResponse
from app.schemas.variable_list import VARIABLE_LIST_ERRORS
from app.schemas.variable_namespace import VariableNamespace
from app.services.variable_list import list_variables

router = APIRouter(tags=["Variables"])


@router.get(
    "/variables/{namespace}",
    response_model=list[VariableGetResponse],
    responses=VARIABLE_LIST_ERRORS,
    summary="List variables by namespace",
)
async def variable_list_router(
    path: VariableNamespace = Depends(get_variable_namespace),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_access(AccessLevel.ADMIN)),
) -> list[VariableGetResponse]:
    """
    Returns all variables that belong to the specified namespace. It
    retrieves the list of stored variables together with their metadata.

    **Hooks:**

    `VARIABLE_LIST_COMPLETED` — executed after variables are listed.

    **Authentication:**

    - Requires a valid token with admin access.

    **Request path:**

    - `namespace` — logical group of variables.

    **Response:**

    `VariableGetResponse` — list of variables in that namespace.

    **Response codes:**

    - `200` — Variables returned successfully.
    - `401` — Invalid, expired, or missing token.
    - `403` — User inactive or blocked.
    - `422` — Input values failed validation.
    - `503` — Service temporarily unavailable.
    """
    return await list_variables(
        session=session,
        namespace=path.namespace,
    )
