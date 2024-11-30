from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.schemas.collection_schemas import CollectionSelectResponse
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_AFTER_COLLECTION_SELECT)

router = APIRouter()


@router.get("/collection/{collection_id}", summary="Retrieve collection",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionSelectResponse, tags=["Collections"])
@locked
async def collection_select(
    collection_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
) -> CollectionSelectResponse:
    """
    FastAPI router for retrieving a collection entity. The router
    fetches the collection from the repository using the provided ID,
    executes related hooks, and returns the collection details in a JSON
    response. The current user should have a reader role or higher.
    Returns a 200 response on success, a 404 error if the collection is
    not found, and a 403 error if authentication fails or the user does
    not have the required role.
    """
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_COLLECTION_SELECT, collection)

    return await collection.to_dict()
