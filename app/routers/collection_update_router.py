from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.schemas.collection_update_schema import (
    CollectionUpdateRequest, CollectionUpdateResponse)
from app.repository import Repository
from app.error import (
    E, LOC_PATH, LOC_BODY, ERR_VALUE_NOT_FOUND, ERR_VALUE_EXISTS)
from app.hook import Hook, HOOK_AFTER_COLLECTION_UPDATE
from app.auth import auth
from app.helpers.encrypt_helper import hash_str

router = APIRouter()


@router.put("/collection/{collection_id}", summary="Update the collection",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionUpdateResponse, tags=["Collections"])
async def collection_update(
    collection_id: int, schema: CollectionUpdateRequest, request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> CollectionUpdateResponse:
    """
    Updates a collection. Retrieves the collection from the repository
    using the provided ID, ensures that the collection exists, and
    checks that the new collection name is unique. It updates the
    collection's name and summary, and returns the updated collection ID.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `editor` or `admin` role.

    **Returns:**
    - `CollectionUpdateResponse`: Contains the ID of the updated
    collection.

    **Responses:**
    - `200 OK`: If the collection is successfully updated.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `404 Not Found`: If the collection is not found.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_COLLECTION_UPDATE`: Executes after the colleciton is
    successfully updated.
    """
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    collection_name_hash = hash_str(schema.collection_name)
    collection_exists = await collection_repository.exists(
        collection_name_hash__eq=collection_name_hash, id__ne=collection.id)

    if collection_exists:
        raise E([LOC_BODY, "collection_name"], schema.collection_name,
                ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

    collection.collection_name = schema.collection_name
    collection.collection_summary = schema.collection_summary
    await collection_repository.update(collection)

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_COLLECTION_UPDATE, collection)

    return {"collection_id": collection.id}
