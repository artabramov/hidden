"""
The module defines a FastAPI router for deleting favorite entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.favorite_model import Favorite
from app.schemas.favorite_schemas import FavoriteDeleteResponse
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_FORBIDDEN,
    HOOK_BEFORE_FAVORITE_DELETE, HOOK_AFTER_FAVORITE_DELETE)

router = APIRouter()


@router.delete("/favorite/{favorite_id}", summary="Delete favorite",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=FavoriteDeleteResponse, tags=["Favorites"])
@locked
async def favorite_delete(
    favorite_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
) -> FavoriteDeleteResponse:
    """
    FastAPI router for deleting a favorite entity. The router fetches
    the favorite from the repository using the provided ID, verifies
    that the favorite exists and that the current user is the owner of
    the favorite. It updates the favorites count for the associated
    document, executes related hooks, and returns the ID of the deleted
    favorite in a JSON response. The current user should have a reader
    role or higher. Returns a 200 response on success, a 404 error if
    the favorite is not found, and a 403 error if authentication fails
    or the user does not have the required role.
    """
    favorite_repository = Repository(session, cache, Favorite)
    favorite = await favorite_repository.select(id=favorite_id)

    if not favorite:
        raise E([LOC_PATH, "favorite_id"], favorite_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif favorite.user_id != current_user.id:
        raise E([LOC_PATH, "favorite_id"], favorite_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    await favorite_repository.delete(favorite, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_FAVORITE_DELETE, favorite)

    await favorite_repository.commit()
    await hook.do(HOOK_AFTER_FAVORITE_DELETE, favorite)

    return {"favorite_id": favorite.id}
