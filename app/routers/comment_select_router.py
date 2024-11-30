"""
The module defines a FastAPI router for retrieving comment entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.comment_model import Comment
from app.schemas.comment_schemas import CommentSelectResponse
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_AFTER_COMMENT_SELECT)

router = APIRouter()


@router.get("/comment/{comment_id}", summary="Retrieve a comment",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CommentSelectResponse, tags=["Comments"])
@locked
async def comment_select(
    comment_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> CommentSelectResponse:
    """
    FastAPI router for retrieving a comment entity. The router fetches
    the comment from the repository using the provided ID, executes
    related hooks, and returns the comment details in a JSON response.
    The current user should have a reader role or higher. Returns a 200
    response on success, a 404 error if the comment is not found, and
    a 403 error if authentication fails or the user does not have the
    required role.
    """
    comment_repository = Repository(session, cache, Comment)
    comment = await comment_repository.select(id=comment_id)

    if not comment:
        raise E([LOC_PATH, "comment_id"], comment_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_COMMENT_SELECT, comment)

    return await comment.to_dict()
