from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.revision_model import Revision
from app.schemas.revision_schemas import (
    DocumentRevisionsRequest, DocumentRevisionsResponse)
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.constants import (
    LOC_PATH, HOOK_AFTER_REVISION_LIST, ERR_RESOURCE_NOT_FOUND)
from app.errors import E

router = APIRouter()


@router.get("/document/{document_id}/revisions",
            summary="Retrieve a document revision list.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=DocumentRevisionsResponse, tags=["Documents"])
@locked
async def document_revisions(
    document_id: int, schema=Depends(DocumentRevisionsRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader)),
) -> DocumentRevisionsResponse:
    """
    Retrieve a document revision list. The  router fetches the list of
    revisions from the repository based on the provided filter criteria,
    executes related hooks, and returns the results in a JSON response.
    The current user should have a reader role or higher. Returns a 200
    response on success, a 403 error if authentication failed or the
    user does not have the required permissions, a 422 error if
    arguments validation failed, and a 423 error if the application
    is locked.

    **Args:**
    - `document_id`: The document ID whose revisions need to be fetched.
    - `DocumentRevisionsRequest`: The request schema that contains
    filter and pagination options for the revisions list.

    **Returns:**
    - `DocumentRevisionsResponse`: A response containing a list of
    revisions for the document and the total revision count.

    **Raises:**
    - `403 Forbidden`: Raised if the user does not have the required
    permissions.
    - `404 Not Found`: Raised if the document with the specified ID does
    not exist.
    - `422 Unprocessable Entity`: Raised if arguments validation failed.
    - `423 Locked`: Raised if the application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `reader`, `writer`, `editor`, or `admin` role is required to
    access the router.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    kwargs = schema.__dict__
    kwargs["document_id__eq"] = document_id

    revision_repository = Repository(session, cache, Revision)
    revisions = await revision_repository.select_all(**kwargs)
    revisions_count = await revision_repository.count_all(**kwargs)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_REVISION_LIST, revisions)

    return {
        "revisions": [await revision.to_dict() for revision in revisions],
        "revisions_count": revisions_count,
    }
