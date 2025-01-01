from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.tag_model import Tag
from app.schemas.document_schemas import (
    DocumentListRequest, DocumentListResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.managers.entity_manager import SUBQUERY
from app.constants import HOOK_AFTER_DOCUMENT_LIST

router = APIRouter()


@router.get("/documents", summary="Retrieve document list.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentListResponse, tags=["Documents"])
@locked
async def document_list(
    schema=Depends(DocumentListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> DocumentListResponse:
    """
    Retrieve document list. The router fetches the list of documents
    from the repository based on the provided filter criteria, executes
    related hooks, and returns the results in a JSON response. The
    current user should have a reader role or higher. Returns a 200
    response on success, a 401 error if authentication failed or the
    user does not have the required permissions, a 403 error if the
    token is missing, a 422 error if arguments validation failed, and
    a 423 error if the application is locked.

    **Args:**
    - `DocumentListRequest`: The request schema containing the filters
    for the document list.

    **Returns:**
    - `DocumentListResponse`: The response schema containing the list of
    documents and the total count.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `422 Unprocessable Entity`: Raised if arguments validation failed.
    - `423 Locked`: Raised if the application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `reader`, `writer`, `editor` or `admin` user role is required to
    access this router.
    """
    document_repository = Repository(session, cache, Document)

    kwargs = schema.__dict__
    if schema.tag_value__eq:
        kwargs[SUBQUERY] = await document_repository.entity_manager.subquery(
            Tag, "document_id", tag_value__eq=schema.tag_value__eq)

    documents = await document_repository.select_all(**kwargs)
    documents_count = await document_repository.count_all(**kwargs)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_DOCUMENT_LIST, documents)

    return {
        "documents": [await document.to_dict() for document in documents],
        "documents_count": documents_count,
    }
