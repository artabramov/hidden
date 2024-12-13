"""
The module defines a FastAPI router for deleting comment entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.comment_model import Comment
from app.schemas.comment_schemas import CommentDeleteResponse
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_LOCKED,
    ERR_RESOURCE_FORBIDDEN, HOOK_BEFORE_COMMENT_DELETE,
    HOOK_AFTER_COMMENT_DELETE)

router = APIRouter()


@router.delete("/comment/{comment_id}", summary="Delete a comment",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=CommentDeleteResponse, tags=["Comments"])
@locked
async def comment_delete(
    comment_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> CommentDeleteResponse:
    """
    Delete a comment. The router fetches the comment from the repository
    using the provided ID, verifies that the comment exists, ensures the
    associated collection is not locked, and confirms that the current
    user is the author of the comment. Deletes the comment, executes
    related hooks, and returns the ID of the deleted comment in a JSON
    response. The current user should have an editor role or higher.
    Returns a 200 response on success, a 404 error if the comment is not
    found, a 423 error if the collection or the application is locked,
    and a 403  error if authentication failed or the user does not have the
    required permissions.

    **Args:**
    - `comment_id`: The ID of the comment to be deleted.

    **Returns:**
    - `CommentDeleteResponse`: The response schema containing the ID of
    the deleted comment.

    **Raises:**
    - `403 Forbidden`: Raised if the current user is not the author of
    the comment or lacks the required permissions.
    - `404 Not Found`: Raised if the comment with the specified ID does
    not exist.
    - `423 Locked`: Raised if the corresponding collection or the
    application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `editor` or `admin` user role is required to access this router.
    """
    comment_repository = Repository(session, cache, Comment)
    comment = await comment_repository.select(id=comment_id)

    if not comment:
        raise E([LOC_PATH, "comment_id"], comment_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif comment.is_locked:
        raise E([LOC_PATH, "comment_id"], comment_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    elif comment.user_id != current_user.id:
        raise E([LOC_PATH, "comment_id"], comment_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    await comment_repository.delete(comment, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_COMMENT_DELETE, comment)

    await comment_repository.commit()
    await hook.do(HOOK_AFTER_COMMENT_DELETE, comment)

    return {"comment_id": comment.id}
