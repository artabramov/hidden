from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.collection_model import Collection
from app.models.document_model import Document
from app.schemas.document_schemas import DocumentMoveResponse
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED, ERR_VALUE_INVALID,
    HOOK_BEFORE_DOCUMENT_UPDATE, HOOK_AFTER_DOCUMENT_UPDATE)

cfg = get_config()
router = APIRouter()


@router.put("/document/{document_id}/collection/{collection_id}",
            summary="Move a document to collection.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentMoveResponse, tags=["Documents"])
@locked
async def document_move(
    document_id: int, collection_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DocumentMoveResponse:
    """
    Move a document to collection. The router checks if the document
    and collection exist, verifies that the both collections are not
    locked, moves the document to the specified collection, and executes
    related hooks. The current user must have the editor role or higher.
    Returns a 200 response on success, a 404 error if the document or
    collection is not found, a 423 error if the collection or the
    application is locked.

    **Args:**
    - `document_id`: The ID of the document to be moved.
    - `collection_id`: The ID of the collection to which the document
      will be moved.

    **Returns:**
    - `DocumentMoveResponse`: The response schema containing the
      document's ID and the revision ID.

    **Raises:**
    - `403 Forbidden`: Raised if the user does not have the required
      permissions.
    - `404 Not Found`: Raised if the document or collection with the
      specified ID does not exist.
    - `423 Locked`: Raised if collection or the application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `editor` or `admin` user role is required to access this router.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif document.is_locked:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    collection_repository = Repository(session, cache, Collection)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif collection.is_locked:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    document.collection_id = collection_id
    await document_repository.update(document, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_DOCUMENT_UPDATE, document)

    await document_repository.commit()
    await hook.do(HOOK_AFTER_DOCUMENT_UPDATE, document)

    return {
        "document_id": document.id,
        "revision_id": document.latest_revision_id,
    }
