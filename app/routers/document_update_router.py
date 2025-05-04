from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.mixins.meta_mixin import META_UPDATES_COUNT
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.schemas.document_update_schema import (
    DocumentUpdateRequest, DocumentUpdateResponse)
from app.hook import Hook, HOOK_AFTER_DOCUMENT_UPDATE
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.error import E, LOC_PATH, LOC_BODY, ERR_VALUE_NOT_FOUND

cfg = get_config()
router = APIRouter()


@router.put("/document/{document_id}", summary="Update a document.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentUpdateResponse, tags=["Documents"])
async def document_update(
    document_id: int, schema: DocumentUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DocumentUpdateResponse:
    """
    Updates a document. Retrieves the document from the repository using
    the provided ID, ensures that the document exists, and updates the
    documents's original filename, summary, and collection reference.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `editor` or `admin` role.

    **Returns:**
    - `DocumentUpdateResponse`: Contains the ID of the updated document.

    **Responses:**
    - `200 OK`: If the document is successfully updated.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `404 Not Found`: If the document is not found.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_UPDATE`: Executes after the document is
    successfully updated.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    if schema.collection_id:
        collection_repository = Repository(session, cache, Collection)
        collection = await collection_repository.select(
            id=schema.collection_id)

        if not collection:
            raise E([LOC_BODY, "collection_id"], schema.collection_id,
                    ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    document.collection_id = schema.collection_id
    document.original_filename = schema.original_filename
    document.document_summary = schema.document_summary
    document.sum_meta(META_UPDATES_COUNT)
    await document_repository.update(document)

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_UPDATE, document)

    return {
        "document_id": document.id,
    }
