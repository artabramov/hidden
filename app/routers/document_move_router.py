from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.schemas.document_move_schema import (
    DocumentMoveRequest, DocumentMoveResponse)
from app.hook import Hook, HOOK_AFTER_DOCUMENT_MOVE
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.error import E, LOC_PATH, LOC_BODY, ERR_VALUE_NOT_FOUND

cfg = get_config()
router = APIRouter()


@router.put("/document/{document_id}/collection", summary="Move a document.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentMoveResponse, tags=["Documents"])
async def document_move(
    document_id: int, schema: DocumentMoveRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DocumentMoveResponse:
    """
    Moves a document to a different collection. Retrieves the document
    by its ID, ensures it exists, and optionally verifies the target
    collection exists if a new collection ID is provided. Updates the
    document's collection reference.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `editor` or `admin` role.

    **Returns:**
    - `DocumentMoveResponse`: Contains the ID of the moved document.

    **Responses:**
    - `200 OK`: If the document is successfully moved.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `404 Not Found`: If the collection is not found.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_MOVE`: Executes after the document is
    successfully moved.
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
    await document_repository.update(document)

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_MOVE, document)

    return {"document_id": document.id}
