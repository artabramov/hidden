"""FastAPI router for document listing."""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.document import Document
from app.schemas.document_list import DocumentListRequest, DocumentListResponse
from app.hook import Hook, HOOK_AFTER_DOCUMENT_LIST
from app.auth import auth
from app.repository import Repository

router = APIRouter()


@router.get(
    "/documents",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=DocumentListResponse,
    summary="Retrieve list of documents",
    tags=["Documents"]
)
async def document_list(
    request: Request,
    schema=Depends(DocumentListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> DocumentListResponse:
    """
    Retrieve documents matching the provided filters and return them
    with the total number of matches.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Query parameters:**
    - `DocumentListRequest` — optional filters (collection_id, creation
    time, creator, flagged status, filename/mimetype, file size),
    pagination (offset and limit), and ordering (order_by and order).

    **Response:**
    - `DocumentListResponse` — page of documents and total match count.

    **Response codes:**
    - `200` — list returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_LIST`: executed after successful retrieval.
    """
    config = request.app.state.config
    kwargs = schema.model_dump(exclude_none=True)

    document_repository = Repository(session, cache, Document, config)
    documents = await document_repository.select_all(**kwargs)
    documents_count = await document_repository.count_all(**kwargs)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_LIST, documents, documents_count)

    return {
        "documents": [await d.to_dict() for d in documents],
        "documents_count": documents_count,
    }
