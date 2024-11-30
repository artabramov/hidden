from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import RoleUpdateRequest, RoleUpdateResponse
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_FORBIDDEN,
    HOOK_BEFORE_ROLE_CHANGE, HOOK_AFTER_ROLE_CHANGE)

router = APIRouter()


@router.put("/user/{user_id}/role", summary="Change user role",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=RoleUpdateResponse, tags=["Users"])
@locked
async def user_role(
    user_id: int, schema: RoleUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> RoleUpdateResponse:
    """
    FastAPI router for updating a user role. Requires the current user
    to have an admin role. The user being updated must be different from
    the current user. Returns a 200 response with the ID of the updated
    user. Raises a 403 error if the current user tries to update their
    own role, if the user's token is invalid, or if the user does not
    have the required role. Returns a 404 error if the user to be
    updated is not found.
    """
    user_repository = Repository(session, cache, User)
    user = await user_repository.select(id=user_id)

    if not user:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif user_id == current_user.id:
        raise E([LOC_PATH, "user_id"], user_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    user.is_active = schema.is_active
    user.user_role = schema.user_role
    await user_repository.update(user, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_ROLE_CHANGE, user)

    await user_repository.commit()
    await hook.do(HOOK_AFTER_ROLE_CHANGE, user)

    return {"user_id": user.id}
