"""
The module defines a FastAPI router for retrieving the favorite list.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.favorite_model import Favorite
from app.models.revision_model import Revision
from app.schemas.favorite_schemas import (
    FavoriteListRequest, FavoriteListResponse)
from app.repository import Repository
from app.hooks import Hook
from app.auth import auth
from app.constants import HOOK_AFTER_FAVORITE_LIST

router = APIRouter()


@router.get("/favorites", summary="Retrieve favorite list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=FavoriteListResponse, tags=["Favorites"])
@locked
async def favorite_list(
    schema=Depends(FavoriteListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> FavoriteListResponse:
    """
    FastAPI router for retrieving a list of favorite entities. The
    router fetches the list of favorites from the repository for the
    current user, executes related hooks, and returns the results in
    a JSON response. The current user should have a reader role or
    higher. Returns a 200 response on success and a 403 error if
    authentication fails or the user does not have the required role.
    """
    kwargs = schema.__dict__
    kwargs["user_id__eq"] = current_user.id

    favorite_repository = Repository(session, cache, Favorite)
    favorites = await favorite_repository.select_all(**kwargs)
    favorites_count = await favorite_repository.count_all(**kwargs)

    revision_repository = Repository(session, cache, Revision)
    for favorite in favorites:
        favorite.favorite_document.latest_revision = (
                await revision_repository.select(
                    id=favorite.favorite_document.latest_revision_id))

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_FAVORITE_LIST, favorites)

    return {
        "favorites": [favorite.to_dict() for favorite in favorites],
        "favorites_count": favorites_count,
    }
