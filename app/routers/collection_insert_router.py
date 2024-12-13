from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.schemas.collection_schemas import (
    CollectionInsertRequest, CollectionInsertResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_BODY, ERR_VALUE_DUPLICATED, HOOK_BEFORE_COLLECTION_INSERT,
    HOOK_AFTER_COLLECTION_INSERT)

router = APIRouter()


@router.post("/collection", summary="Create a collection",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=CollectionInsertResponse, tags=["Collections"])
@locked
async def collection_insert(
    schema: CollectionInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> CollectionInsertResponse:
    """
    Create a collection. The router verifies if a collection with the
    specified name already exists, inserts the new collection into
    the repository, executes related hooks, and returns the created
    collection ID in a JSON response. The current user should have a
    writer role or higher. Returns a 201 response on success, a 422
    error if arguments validation failed or the collection name is
    duplicated, a 403 error if authentication failed or the user does
    not have the required permissions, and a 423 error if the
    application is locked.

    **Args:**
    - `CollectionInsertRequest`: The request schema containing the data
      for the new collection.

    **Returns:**
    - `CollectionInsertResponse`: The response schema containing the ID
      of the newly created collection.

    **Raises:**
    - `403 Forbidden`: Raised if the current user is not authenticated
      or does not have the required permissions.
    - `422 Unprocessable Entity`: Raised if arguments validation failed
      or the collection name is already exist.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_BEFORE_COLLECTION_INSERT`: Executes before the collection is
      inserted.
    - `HOOK_AFTER_COLLECTION_INSERT`: Executes after the collection is
      inserted.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `writer`, `editor` or `admin` user role is required to access this
      router.
    """
    collection_repository = Repository(session, cache, Collection)

    collection_exists = await collection_repository.exists(
        collection_name__eq=schema.collection_name)

    if collection_exists:
        raise E([LOC_BODY, "collection_name"], schema.collection_name,
                ERR_VALUE_DUPLICATED, status.HTTP_422_UNPROCESSABLE_ENTITY)

    collection = Collection(
        current_user.id, schema.is_locked, schema.collection_name,
        collection_summary=schema.collection_summary)
    await collection_repository.insert(collection, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_COLLECTION_INSERT, collection)

    await collection_repository.commit()
    await hook.do(HOOK_AFTER_COLLECTION_INSERT, collection)

    return {"collection_id": collection.id}
