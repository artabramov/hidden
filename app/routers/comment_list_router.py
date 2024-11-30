"""
The module defines a FastAPI router for retrieving the option list.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.comment_model import Comment
from app.schemas.comment_schemas import (
    CommentListRequest, CommentListResponse)
from app.repository import Repository
from app.hooks import Hook
from app.auth import auth
from app.constants import HOOK_AFTER_COMMENT_LIST

router = APIRouter()


@router.get("/comments", summary="Retrieve comment list",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CommentListResponse, tags=["Comments"])
@locked
async def comment_list(
    schema=Depends(CommentListRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> CommentListResponse:
    """
    FastAPI router for retrieving a list of comment entities. The router
    fetches the list of comments from the repository, executes related
    hooks, and returns the results in a JSON response. The current user
    should have a reader role or higher. Returns a 200 response on
    success and a 403 error if authentication fails or the user does
    not have the required role.
    """
    comment_repository = Repository(session, cache, Comment)
    comments = await comment_repository.select_all(**schema.__dict__)
    comments_count = await comment_repository.count_all(**schema.__dict__)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_AFTER_COMMENT_LIST, comments)

    return {
        "comments": [await comment.to_dict() for comment in comments],
        "comments_count": comments_count,
    }
