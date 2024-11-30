from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.schemas.document_schemas import (
    DocumentPinRequest, DocumentPinResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_BEFORE_DOCUMENT_UPDATE,
    HOOK_AFTER_DOCUMENT_UPDATE)

cfg = get_config()
router = APIRouter()


@router.put("/document/{document_id}/flagged",
            summary="Flag or unflag a document",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentPinResponse, tags=["Documents"])
@locked
async def document_update(
    document_id: int, schema: DocumentPinRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> DocumentPinResponse:
    """
    FastAPI router for flagging or unflagging a document. The router
    checks if the document with the specified ID exists, updates the
    document's `is_flagged` status based on the provided request,
    executes related hooks before and after the update, and returns
    the updated document's ID and revision ID in a JSON response. The
    current user must have the editor role or higher. Returns a 200
    response on success, a 404 error if the document is not found, and
    a 403 error if authentication fails or the user does not have
    the required role.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    document.is_flagged = schema.is_flagged
    await document_repository.update(document, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_DOCUMENT_UPDATE, document)

    await document_repository.commit()
    await hook.do(HOOK_AFTER_DOCUMENT_UPDATE, document)

    return {
        "document_id": document.id,
        "revision_id": document.latest_revision_id,
    }
