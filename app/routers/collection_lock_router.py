from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.schemas.collection_schemas import (
    CollectionLockUpdateRequest, CollectionLockUpdateResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_BEFORE_COLLECTION_UPDATE,
    HOOK_AFTER_COLLECTION_UPDATE)

router = APIRouter()


@router.put("/collection/{collection_id}/locked",
            summary="Lock or unlock a collection.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CollectionLockUpdateResponse, tags=["Collections"])
@locked
async def collection_delete(
    collection_id: int, schema: CollectionLockUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> CollectionLockUpdateResponse:
    """
    Change the locking state of a collection. This router allows
    updating the locked status of a collection. The collection is
    retrieved from the repository using the provided ID, and its lock
    status is updated. The current user must have an editor role or
    higher. Returns a 200 response on success, a 404 error if the
    collection is not found, a 422 error if arguments validation failed,
    a 401 error if authentication failed or the user does not have the
    required permissions, a 403 error if the token is missing, and
    a 423 error if the application is locked.

    **Args:**
    - `collection_id`: The ID of the collection to update.
    - `CollectionLockUpdateRequest`: The request schema containing the
    new locked state.

    **Returns:**
    - `CollectionLockUpdateResponse`: The response schema containing the
    ID of the updated collection.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `404 Not Found`: Raised if the collection with the specified
    ID does not exist.
    - `422 Unprocessable Entity`:  Raised if arguments validation failed.
    - `423 Locked`: Raised if the application is locked.

    **Hooks:**
    - `HOOK_BEFORE_COLLECTION_UPDATE`: Executes before the collection
    lock status is updated.
    - `HOOK_AFTER_COLLECTION_UPDATE`: Executes after the collection lock
    status is updated.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `editor` or `admin` user role is required to access this router.
    """
    collection_repository = Repository(session, cache, Collection)

    collection = await collection_repository.select(id=collection_id)
    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    collection.is_locked = schema.is_locked
    await collection_repository.update(collection, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_COLLECTION_UPDATE, collection)

    await collection_repository.commit()
    await hook.do(HOOK_AFTER_COLLECTION_UPDATE, collection)

    return {"collection_id": collection.id}
