from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import JSONResponse
from app.schemas.execute_schema import ExecuteRequest
from app.hook import Hook, HOOK_ON_EXECUTE
from app.postgres import get_session
from app.redis import get_cache
from app.auth import auth
from app.models.user_model import User, UserRole

router = APIRouter()


@router.post("/execute", summary="Execute a custom action.",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             tags=["Services"])
async def execute(
    schema: ExecuteRequest, request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
):
    """
    Executes a custom action. The router executes corresponding hooks
    with defined parameters and returns custom response.

    **Args:**
    - `ExecuteRequest`: The request schema containing the action to be
    executed and its parameters.

    **Returns:**
    - `JSONResponse`: The response object containing the result of the
    executed action.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `423 Locked`: Raised if the the application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `admin` roles is required to access this router.
    """
    response = {}

    hook = Hook(request.app, session, cache, current_user)
    await hook.call(HOOK_ON_EXECUTE, schema.action, schema.params,
                    response)

    return response
