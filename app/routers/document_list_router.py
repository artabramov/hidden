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


@router.get("/documents", summary="Retrieve the list of documents.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentListResponse, tags=["Documents"])
@locked
async def document_list(
    schema=Depends(DocumentListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> DocumentListResponse:
    """
    FastAPI router for retrieving a list of document entities. The
    router fetches the list of documents from the repository, executes
    related hooks, and returns the results in a JSON response. The
    current user should have a reader role or higher. Returns a 200
    response on success and a 403 error if authentication fails or
    the user does not have the required role.
    """
    document_repository = Repository(session, cache, Document)

    kwargs = schema.__dict__
    if schema.tag_value__eq:
        kwargs[SUBQUERY] = await document_repository.entity_manager.subquery(
            Tag, "document_id", tag_value__eq=schema.tag_value__eq)

    documents = await document_repository.select_all(**kwargs)
    documents_count = await document_repository.count_all(**kwargs)

    # revision_repository = Repository(session, cache, Revision)
    # for document in documents:
    #     document.latest_revision = await revision_repository.select(
    #       id=document.latest_revision_id)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_DOCUMENT_LIST, documents)

    return {
        "documents": [await document.to_dict() for document in documents],
        "documents_count": documents_count,
    }
