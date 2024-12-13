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


@router.get("/collection/{collection_id}", summary="Retrieve a collection.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionSelectResponse, tags=["Collections"])
@locked
async def collection_select(
    collection_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
) -> CollectionSelectResponse:
    """
    Retrieve a collection. The router fetches the collection from the
    repository using the provided ID, executes related hooks, and
    returns the collection details in a JSON response. The current user
    should have a reader role or higher. Returns a 200 response on
    success, a 404 error if the collection is not found, a 403 error if
    authentication failed or the user does not have the required
    permissions, and a 423 error if the application is locked.

    **Args:**
    - `collection_id`: The ID of the collection to retrieve.

    **Returns:**
    - `CollectionSelectResponse`: The response schema containing the
      details of the selected collection.

    **Raises:**
    - `403 Forbidden`: Raised if the current user is not authenticated
      or does not have the required permissions.
    - `404 Not Found`: Raised if the collection with the specified ID
      does not exist.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_AFTER_COLLECTION_SELECT`: Executes after the collection is
      successfully selected.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `reader`, `writer`, `editor` or `admin` user role is required to
      access this router.
    """
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_COLLECTION_SELECT, collection)

    return await collection.to_dict()
