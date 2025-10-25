"""FastAPI router for deleting file tags."""

from fastapi import APIRouter, Request, Depends, Path, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.file import File
from app.validators.tag_validators import value_validate
from app.schemas.tag_delete import TagDeleteResponse
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND, ERR_VALUE_INVALID
from app.hook import Hook, HOOK_AFTER_TAG_DELETE
from app.auth import auth

router = APIRouter()


@router.delete(
    "/file/{file_id}/tag/{tag_value}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=TagDeleteResponse,
    summary="Delete tag",
    tags=["Files"]
)
async def tag_delete(
    request: Request,
    file_id: int = Path(..., ge=1),
    tag_value: str = Path(..., min_length=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> TagDeleteResponse:
    """
    Delete a tag from a file and return the file ID with its latest
    revision number. The operation is idempotent: if the tag is absent,
    the endpoint still returns 200 and leaves the file unchanged.

    **Authentication:**
    - Requires a valid bearer token with `editor` role.

    **Path parameters:**
    - `file_id` (integer ≥ 1): file identifier.
    - `tag_value` (string, 1-40): tag value to remove; normalized and
    validated.

    **Response:**
    - `TagDeleteResponse` — returns the `file_id` and the
    `latest_revision_number`.

    **Response codes:**
    - `200` — tag removed (or not present; idempotent success).
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — file not found.
    - `422` — invalid `tag_value` (fails normalization/constraints).
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_TAG_DELETE` — executed after successful update.
    """
    config = request.app.state.config

    file_repository = Repository(session, cache, File, config)
    file = await file_repository.select(id=file_id)

    if not file:
        raise E([LOC_PATH, "file_id"], file_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    try:
        normalized_value = value_validate(tag_value)
    except ValueError:
        raise E([LOC_PATH, "tag_value"], tag_value,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    file.file_tags = [t for t in file.file_tags if t.value != normalized_value]
    await file_repository.update(file)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_TAG_DELETE, file, normalized_value)

    return {
        "file_id": file.id,
        "latest_revision_number": file.latest_revision_number,
    }
