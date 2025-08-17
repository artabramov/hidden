from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.tag_model import Tag
from app.schemas.document_list_schema import (
    DocumentListRequest, DocumentListResponse)
from app.hook import Hook, HOOK_AFTER_DOCUMENT_LIST
from app.auth import auth
from app.repository import Repository
from app.managers.entity_manager import SUBQUERY
from app.helpers.encrypt_helper import hash_str

router = APIRouter()


@router.get("/documents", summary="Retrieve a list of documents.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentListResponse, tags=["Documents"])
async def document_list(
    schema=Depends(DocumentListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> DocumentListResponse:
    """
    Retrieves a list of documents. Fetches documents from the repository
    based on the provided filter criteria, and includes a counter field
    to indicate the total number of matching documents.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `DocumentListResponse`: Contains the list of documents and the
    total count.

    **Responses:**
    - `200 OK`: If the documents are successfully fetched.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_DOCUMENT_LIST`: Executes after the documents are
    successfully fetched.
    """
    document_repository = Repository(session, cache, Document)

    kwargs = schema.__dict__
    if schema.tag_value__eq:
        tag_value_hash = hash_str(schema.tag_value__eq)
        kwargs[SUBQUERY] = await document_repository.entity_manager.subquery(
            Tag, "document_id", tag_value_hash__eq=tag_value_hash)

    documents = await document_repository.select_all(**kwargs)
    documents_count = await document_repository.count_all(**kwargs)

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_DOCUMENT_LIST, documents, documents_count)

    return {
        "documents": [await document.to_dict() for document in documents],
        "documents_count": documents_count,
    }
