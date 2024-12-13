from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.schemas.document_schemas import DocumentDeleteResponse
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    HOOK_BEFORE_DOCUMENT_DELETE, HOOK_AFTER_DOCUMENT_DELETE)

router = APIRouter()


@router.delete("/document/{document_id}", summary="Delete a document",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=DocumentDeleteResponse, tags=["Documents"])
@locked
async def document_delete(
    document_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.admin))
) -> DocumentDeleteResponse:
    """
    Delete a document. The router retrieves the document from the
    repository using the provided ID, checks if the document exists and
    its collection is not locked, deletes the document and all related
    entities, executes related hooks, and returns the deleted document
    ID in a JSON response. The current user should have an admin role.
    Returns a 200 response on success, a 404 error if the document is
    not found, a 423 error if the collection the application is locked,
    and a 403 error if authentication failed or the user does not have
    the required permissions.

    **Args:**
    - `document_id`: The ID of the document to be deleted.

    **Returns:**
    - `DocumentDeleteResponse`: The response schema containing the ID of
      the deleted document.

    **Raises:**
    - `403 Forbidden`: Raised if the user does not have the required
      permissions.
    - `404 Not Found`: Raised if the document with the specified ID does
      not exist.
    - `423 Locked`: Raised if the document or the application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `admin` user role is required to access this router.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif document.is_locked:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    await document_repository.delete(document, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_DOCUMENT_DELETE, document)

    await document_repository.commit()
    await hook.do(HOOK_AFTER_DOCUMENT_DELETE, document)

    return {"document_id": document.id}
