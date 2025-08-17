from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.schemas.document_select_schema import DocumentSelectResponse
from app.hook import Hook, HOOK_AFTER_DOCUMENT_SELECT
from app.auth import auth
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND

router = APIRouter()


@router.get("/document/{document_id}", summary="Retrieve a document.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentSelectResponse, tags=["Documents"])
async def document_select(
    document_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> DocumentSelectResponse:
    """
    Retrieves a document. Fetches the document from the repository using
    the provided ID, verifies that the document exists, and returns the
    document details.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `DocumentSelectResponse`: Document details on success.

    **Responses:**
    - `200 OK`: If the document is successfully retrieved.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `404 Not Found`: If the document is not found.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_SELECT`: Executes after the document is
    successfully retrieved.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_SELECT, document)

    return await document.to_dict()
