from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.schemas.collection_select_schema import CollectionSelectResponse
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.hook import Hook, HOOK_AFTER_COLLECTION_SELECT
from app.auth import auth

router = APIRouter()


@router.get("/collection/{collection_id}", summary="Retrieve a collection.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionSelectResponse, tags=["Collections"])
async def collection_select(
    collection_id: int, request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
) -> CollectionSelectResponse:
    """
    Retrieves a collection. Fetches the collection from the repository
    using the provided ID and returns the collection details.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `CollectionSelectResponse`: Collection details on success.

    **Responses:**
    - `200 OK`: If the collection is successfully retrieved.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `404 Not Found`: If the collection is not found.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_COLLECTION_SELECT`: Executes after the collection is
    successfully retrieved.
    """
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_COLLECTION_SELECT, collection)

    return await collection.to_dict()
