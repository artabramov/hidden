
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.schemas.document_delete_schema import DocumentDeleteResponse
from app.hook import Hook, HOOK_AFTER_DOCUMENT_DELETE
from app.auth import auth
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.libraries.collection_library import CollectionLibrary

router = APIRouter()


@router.delete("/document/{document_id}", summary="Delete a document",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=DocumentDeleteResponse, tags=["Documents"])
async def document_delete(
    document_id: int, session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> DocumentDeleteResponse:
    """
    Deletes a document. Retrieves the document from the repository using
    the provided ID, checks if the document exists and deletes the
    document. If the document is associated with a collection, its
    thumbnail is also updated.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `admin` role.

    **Returns:**
    - `DocumentDeleteResponse`: Contains the ID of the deleted document.

    **Responses:**
    - `200 OK`: If the document is successfully deleted.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the secret key is missing.
    - `404 Not Found`: If the document is not found.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_DELETE`: Executes after the document is
    successfully deleted.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    await document_repository.delete(document)

    if document.document_collection:
        collection_library = CollectionLibrary(session, cache)
        await collection_library.create_thumbnail(
            document.document_collection.id)

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_DELETE, document)

    return {"document_id": document.id}
