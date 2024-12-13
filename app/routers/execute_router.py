from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from app.schemas.execute_schemas import ExecuteRequest
from app.hooks import Hook
from app.database import get_session
from app.cache import get_cache
from app.auth import auth
from app.models.user_model import User, UserRole
from app.constants import HOOK_ON_EXECUTE
from app.decorators.locked_decorator import locked

router = APIRouter()


@router.post("/execute", summary="Execute a custom action.",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             tags=["Execute"])
@locked
async def execute(
    schema: ExecuteRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
):
    """
    Execute a custom action. The router executes corresponding hooks
    with defined parameters. The current user must have an admin role.
    Returns a 403 error if authentication failed or the user does not
    have the required permissions, a 423 error if the the application
    is locked.

    **Args:**
    - `ExecuteRequest`: The request schema containing the action to be
    executed and its parameters.

    **Returns:**
    - `JSONResponse`: The response object containing the result of the
    executed action.

    **Raises:**
    - `403 Forbidden`: Raised if the user does not have the required
    permissions.
    - `423 Locked`: Raised if the the application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `admin` roles is required to access this router.
    """
    response = {}

    hook = Hook(session, cache, current_user)
    await hook.do(HOOK_ON_EXECUTE, schema.action, schema.params,
                  response)

    return response
