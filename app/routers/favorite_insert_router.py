"""
The module defines a FastAPI router for creating favorite entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.favorite_model import Favorite
from app.schemas.favorite_schemas import (
    FavoriteInsertRequest, FavoriteInsertResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_BODY, ERR_VALUE_INVALID, HOOK_BEFORE_FAVORITE_INSERT,
    HOOK_AFTER_FAVORITE_INSERT)

router = APIRouter()


@router.post("/favorite", summary="Create favorite",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=FavoriteInsertResponse, tags=["Favorites"])
@locked
async def favorite_insert(
    schema: FavoriteInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> FavoriteInsertResponse:
    """
    FastAPI router for creating a comment entity. The router verifies
    if the specified document exists, creates a favorite record if it
    does not already exist for the current user and document, updates
    the favorites count for the document, and executes related hooks.
    Returns the ID of the created favorite in a JSON response. The
    current user should have a reader role or higher. Returns a 201
    response on success, a 404 error if the document is not found,
    and a 403 error if authentication fails or the user does not have
    the required role.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id__eq=schema.document_id)

    if not document:
        raise E([LOC_BODY, "document_id"], schema.document_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    favorite_repository = Repository(session, cache, Favorite)
    favorite = await favorite_repository.select(
        user_id__eq=current_user.id, document_id__eq=schema.document_id)

    if not favorite:
        favorite = Favorite(current_user.id, document.id)
        await favorite_repository.insert(favorite, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_FAVORITE_INSERT, favorite)

    await favorite_repository.commit()
    await hook.do(HOOK_AFTER_FAVORITE_INSERT, favorite)

    return {"favorite_id": favorite.id}
