from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.revision_model import Revision
from app.schemas.revision_schemas import RevisionSelectResponse
from app.hooks import Hook
from app.auth import auth
from app.repository import Repository
from app.errors import E
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_AFTER_REVISION_SELECT)

router = APIRouter()


@router.get("/document/{document_id}/revision/{revision_id}",
            summary="Retrieve data for a specific document revision.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=RevisionSelectResponse, tags=["Documents"])
@locked
async def revision_select(
    document_id: int, revision_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> RevisionSelectResponse:
    """
    FastAPI router for retrieving a revision entity. The router fetches
    the revision from the repository using the provided ID, executes
    related hooks, and returns the revision details in a JSON response.
    The current user should have a reader role or higher. Returns a 200
    response on success, a 404 error if the revision is not found, and
    a 403 error if authentication fails or the user does not have the
    required role.
    """
    revision_repository = Repository(session, cache, Revision)
    revision = await revision_repository.select(id=revision_id)

    if not revision or revision.document_id != document_id:
        raise E([LOC_PATH, "revision_id"], revision_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_REVISION_SELECT, revision)

    return revision.to_dict()
