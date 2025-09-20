"""FastAPI router for document retrieving."""

from fastapi import APIRouter, Depends, status, Request, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.models.document import Document
from app.schemas.document_select import DocumentSelectResponse
from app.hook import Hook, HOOK_AFTER_DOCUMENT_SELECT
from app.auth import auth
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND

router = APIRouter()


@router.get(
    "/collection/{collection_id}/document/{document_id}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=DocumentSelectResponse,
    summary="Retrieve document",
    tags=["Documents"]
)
async def document_select(
    request: Request,
    collection_id: int = Path(..., ge=1),
    document_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> DocumentSelectResponse:
    """
    Retrieve a single document by ID within a given collection and
    return its details, including creator, parent collection, timestamps,
    flagged status, filename, size, MIME type, checksum, summary, and
    latest revision.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Response schema:**
    - `DocumentSelectResponse` — includes document ID; creator; parent
    collection; creation and last-update timestamps (Unix seconds, UTC);
    flagged status; filename; file size; MIME type (optional); content
    checksum; optional summary; and the latest revision number.

    **Path parameters:**
    - `collection_id` (integer ≥ 1): parent collection identifier.
    - `document_id` (integer ≥ 1): document identifier.

    **Response codes:**
    - `200` — document found; details returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection or document not found.
    - `423` — application is temporarily locked.
    - `498` — secret key is missing.
    - `499` — secret key is invalid.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_SELECT`: executed after a successful
    retrieval.
    """
    config = request.app.state.config

    # NOTE: On document select, keep two-step fetch to hit Redis cache;
    # load the collection by ID first, then load the document by ID.

    collection_repository = Repository(session, cache, Collection, config)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    document_repository = Repository(session, cache, Document, config)
    document = await document_repository.select(id=document_id)

    if not document or document.collection_id != collection.id:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_SELECT, document)

    return await document.to_dict()
