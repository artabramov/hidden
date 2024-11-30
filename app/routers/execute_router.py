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


@router.post("/execute", summary="Execute action",
             response_class=JSONResponse, status_code=status.HTTP_200_OK,
             tags=["Execute"])
@locked
async def execute(
    schema: ExecuteRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
):

    response = {}

    hook = Hook(session, cache, current_user)
    await hook.do(HOOK_ON_EXECUTE, schema.action, schema.params,
                  response)

    return response
