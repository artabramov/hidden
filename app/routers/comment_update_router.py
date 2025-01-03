"""
The module defines a FastAPI router for updating comment entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.comment_model import Comment
from app.schemas.comment_schemas import (
    CommentUpdateRequest, CommentUpdateResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, ERR_RESOURCE_FORBIDDEN,
    ERR_RESOURCE_LOCKED, HOOK_BEFORE_COMMENT_UPDATE, HOOK_AFTER_COMMENT_UPDATE)

router = APIRouter()


@router.put("/comment/{comment_id}", summary="Update a comment",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=CommentUpdateResponse, tags=["Comments"])
@locked
async def comment_update(
    comment_id: int, schema: CommentUpdateRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> CommentUpdateResponse:
    """
    Update a comment. The router fetches the comment from the repository
    using the provided ID, verifies that the current user is the author
    of the comment, checks that the associated collection is not locked,
    updates the comment content, executes related hooks, and returns the
    updated comment ID in a JSON response. The current user should have
    an editor role or higher. Returns a 200 response on success, a 404
    error if the comment is not found, a 423 error if the collection or
    the application is locked, and a 401 error if authentication failed
    or the user does not have the required permissions, a 403 error if
    the token is missing.

    **Args:**
    - `comment_id`: The ID of the comment to be updated.
    - `CommentUpdateRequest`: The request schema containing the new
    comment content.

    **Returns:**
    - `CommentUpdateResponse`: The response schema containing the ID of
    the updated comment.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `404 Not Found`: Raised if the comment with the specified ID does
    not exist.
    - `422 Unprocessable Entity`: Raised if arguments validation failed.
    - `423 Locked`: Raised if the collection or the application is
    locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `editor` or `admin` user role are required to access this router.
    """
    comment_repository = Repository(session, cache, Comment)
    comment = await comment_repository.select(id=comment_id)

    if not comment:
        raise E([LOC_PATH, "comment_id"], comment_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    elif comment.user_id != current_user.id:
        raise E([LOC_PATH, "comment_id"], comment_id,
                ERR_RESOURCE_FORBIDDEN, status.HTTP_403_FORBIDDEN)

    elif comment.is_locked:
        raise E([LOC_PATH, "comment_id"], comment_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    comment.comment_content = schema.comment_content
    await comment_repository.update(comment, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_COMMENT_UPDATE, comment)

    await comment_repository.commit()
    await hook.do(HOOK_AFTER_COMMENT_UPDATE, comment)

    return {"comment_id": comment.id}
