import os
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.schemas.userpic_delete import UserpicDeleteResponse
from app.error import E, LOC_PATH, ERR_VALUE_INVALID, ERR_VALUE_NOT_FOUND
from app.hook import Hook, HOOK_AFTER_USERPIC_DELETE
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.delete("/user/{user_id}/userpic", summary="Delete userpic",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=UserpicDeleteResponse, tags=["Users"])
async def userpic_delete(
    user_id: int, request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> UserpicDeleteResponse:

    config = request.app.state.config
    lru = request.app.state.lru
    file_manager = request.app.state.file_manager

    if user_id != current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif not current_user.has_thumbnail:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    userpic_path = os.path.join(
        config.THUMBNAILS_DIR, current_user.user_thumbnail.filename)

    lru.delete(userpic_path)
    await file_manager.delete(userpic_path)

    current_user.user_thumbnail = None
    user_repository = Repository(session, cache, User, config)
    await user_repository.update(current_user)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_USERPIC_DELETE)

    request.state.log.debug("userpic deleted; user_id=%s;", current_user.id)
    return {"user_id": current_user.id}
