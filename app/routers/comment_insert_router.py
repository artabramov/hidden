"""
The module defines a FastAPI router for creating comment entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.comment_model import Comment
from app.schemas.comment_schemas import (
    CommentInsertRequest, CommentInsertResponse)
from app.repository import Repository
from app.errors import E
from app.hooks import Hook
from app.auth import auth
from app.constants import (
    LOC_BODY, ERR_RESOURCE_LOCKED, ERR_VALUE_INVALID,
    HOOK_BEFORE_COMMENT_INSERT, HOOK_AFTER_COMMENT_INSERT)

router = APIRouter()


@router.post("/comment", summary="Create a comment",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=CommentInsertResponse, tags=["Comments"])
@locked
async def comment_insert(
    schema: CommentInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.writer))
) -> CommentInsertResponse:
    """
    Create a comment. The router validates that the document exists and
    that its collection is not locked, inserts the new comment into the
    repository, executes related hooks, and returns the created comment
    ID in a JSON response. The current user should have a writer role or
    higher. Returns a 201 response on success, a 404 error if the
    document is not found, a 423 error if the collection or the
    application is locked, and a 401 error if authentication failed
    or the user does not have the required permissions, a 403 error if
    the token is missing.

    **Args:**
    - `CommentInsertRequest`: The request schema containing the data
    for the new comment.

    **Returns:**
    - `CommentInsertResponse`: The response schema containing the ID
    of the newly created comment.

    **Raises:**
    - `401 Unauthorized`: Raised if the token is invalid or expired,
    or if the current user is not authenticated or does not have the
    required permissions.
    - `403 Forbidden`: Raised if the token is missing.
    - `422 Unprocessable Entity`:  Raised if arguments validation failed.
    - `423 Locked`: Raised if the document's collection or the
    application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `writer`, `editor` or `admin` user role is required to access this
    router.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id__eq=schema.document_id)

    if not document:
        raise E([LOC_BODY, "document_id"], schema.document_id,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    elif document.is_locked:
        raise E([LOC_BODY, "document_id"], schema.document_id,
                ERR_RESOURCE_LOCKED, status.HTTP_423_LOCKED)

    comment_repository = Repository(session, cache, Comment)
    comment = Comment(current_user.id, document.id, schema.comment_content)
    await comment_repository.insert(comment, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_COMMENT_INSERT, comment)

    await comment_repository.commit()
    await hook.do(HOOK_AFTER_COMMENT_INSERT, comment)

    return {"comment_id": comment.id}
