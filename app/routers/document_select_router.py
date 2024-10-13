from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.revision_model import Revision
from app.schemas.document_schemas import DocumentSelectResponse
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_AFTER_DOCUMENT_SELECT)

router = APIRouter()


@router.get("/document/{document_id}",
            summary="Retrieve a document data",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentSelectResponse, tags=["Documents"])
@locked
async def document_select(
    document_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> DocumentSelectResponse:
    """
    FastAPI router for retrieving a document entity. The router fetches
    the document from the repository using the provided ID, verifies
    that the document exists, executes related hooks, and returns the
    document details in a JSON response. The current user should have
    a reader role or higher. Returns a 200 response on success, a 404
    error if the document is not found, and a 403 error if
    authentication fails or the user does not have the required role.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    revision_repository = Repository(session, cache, Revision)
    document.latest_revision = await revision_repository.select(
        id=document.latest_revision_id)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_DOCUMENT_SELECT, document)

    return document.to_dict()
