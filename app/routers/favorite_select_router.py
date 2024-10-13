"""
The module defines a FastAPI router for retrieving favorite entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.favorite_model import Favorite
from app.models.revision_model import Revision
from app.schemas.favorite_schemas import FavoriteSelectResponse
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_FORBIDDEN,
    HOOK_AFTER_FAVORITE_SELECT)

router = APIRouter()


@router.get("/favorite/{favorite_id}", summary="Retrieve favorite",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=FavoriteSelectResponse, tags=["Favorites"])
@locked
async def favorite_select(
    favorite_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> FavoriteSelectResponse:
    """
    FastAPI router for retrieving a favorite entity. The router fetches
    the favorite from the repository using the provided ID, verifies
    that the favorite exists, and checks that the current user is the
    owner of the favorite. It executes related hooks and returns the
    favorite details in a JSON response. The current user should have
    a reader role or higher. Returns a 200 response on success, a 404
    error if the favorite is not found, and a 403 error if
    authentication fails or the user does not have the required role.
    """
    favorite_repository = Repository(session, cache, Favorite)
    favorite = await favorite_repository.select(id=favorite_id)

    if not favorite:
        raise E([LOC_PATH, "favorite_id"], favorite_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif favorite.user_id != current_user.id:
        raise E([LOC_PATH, "favorite_id"], favorite_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    revision_repository = Repository(session, cache, Revision)
    favorite.favorite_document.latest_revision = (
            await revision_repository.select(
                id=favorite.favorite_document.latest_revision_id))

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_FAVORITE_SELECT, favorite)

    return favorite.to_dict()
