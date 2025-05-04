from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.schemas.collection_insert_schema import (
    CollectionInsertRequest, CollectionInsertResponse)
from app.repository import Repository
from app.error import E, LOC_BODY, ERR_VALUE_EXISTS
from app.hook import Hook, HOOK_AFTER_COLLECTION_INSERT
from app.auth import auth
from app.helpers.encrypt_helper import hash_str
from app.config import get_config

cfg = get_config()
router = APIRouter()


@router.post("/collection", summary="Create a new collection.",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=CollectionInsertResponse, tags=["Collections"])
async def collection_insert(
    schema: CollectionInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> CollectionInsertResponse:
    """
    Creates a new collection. Checks if the collection name is unique,
    and creates a new collection with the provided name and summary.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `writer`, `editor`, or `admin` role.

    **Returns:**
    - `CollectionInsertResponse`: Contains the newly created collection's
    ID on success.

    **Responses:**
    - `201 Created`: If the collection is successfully created.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the secret key is missing.
    - `422 Unprocessable Entity`: If parameters validation fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_COLLECTION_INSERT`: Executes after the collection is
    successfully created.
    """
    collection_repository = Repository(session, cache, Collection)

    collection_name_hash = hash_str(schema.collection_name)
    collection_exists = await collection_repository.exists(
        collection_name_hash__eq=collection_name_hash)

    if collection_exists:
        raise E([LOC_BODY, "collection_name"], schema.collection_name,
                ERR_VALUE_EXISTS, status.HTTP_422_UNPROCESSABLE_ENTITY)

    collection = Collection(
        current_user.id, schema.collection_name,
        collection_summary=schema.collection_summary)
    await collection_repository.insert(collection)

    hook = Hook(session, cache, current_user=current_user)
    await collection_repository.commit()
    await hook.call(HOOK_AFTER_COLLECTION_INSERT, collection)

    return {"collection_id": collection.id}
