from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.schemas.collection_delete_schema import CollectionDeleteResponse
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.hook import Hook, HOOK_AFTER_COLLECTION_DELETE
from app.auth import auth

router = APIRouter()


@router.delete("/collection/{collection_id}", summary="Delete a collection.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=CollectionDeleteResponse, tags=["Collections"])
async def collection_delete(
    collection_id: int, request: Request,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> CollectionDeleteResponse:
    """
    Deletes a collection. Retrieves the collection from the repository
    using the provided ID, verifies that it exists, and deletes the
    collection. The associated documents are also deleted from the
    repository.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `admin` role.

    **Returns:**
    - `CollectionDeleteResponse`: Contains the ID of the deleted
    collection.

    **Responses:**
    - `200 OK`: If the collection is successfully deleted.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the secret key is missing.
    - `404 Not Found`: If the collection is not found.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_COLLECTION_DELETE`: Executes after the collection is
    successfully deleted.
    """
    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    await collection_repository.delete(collection)

    document_repository = Repository(session, cache, Document)
    await document_repository.delete_all_from_cache()

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_COLLECTION_DELETE, collection)

    return {"collection_id": collection.id}
