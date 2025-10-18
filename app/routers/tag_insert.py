from fastapi import APIRouter, Request, Depends, status, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.models.file import File
from app.models.file_tag import FileTag
from app.hook import Hook, HOOK_AFTER_TAG_INSERT
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.auth import auth
from app.repository import Repository
from app.schemas.tag_insert import TagInsertRequest, TagInsertResponse

router = APIRouter()


@router.post(
    "/collection/{collection_id}/file/{file_id}/tag",
    status_code=status.HTTP_201_CREATED,
    response_class=JSONResponse,
    response_model=TagInsertResponse,
    summary="Add tag",
    tags=["Files"]
)
async def tag_insert(
    request: Request,
    schema: TagInsertRequest,
    collection_id: int = Path(..., ge=1),
    file_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> TagInsertResponse:
    """
    Add a new tag to a file and return the file ID with its latest
    revision number. If the tag already exists for this file, the
    operation is idempotent and no duplicate is created.

    **Authentication:**
    - Requires a valid bearer token with `editor` role or higher.

    **Validation schemas:**
    - `TagInsertRequest` — request body with a single `value` field.
    The value is normalized/validated by `value_validate` (NFKC, trim,
    lower-case).
    - `TagInsertResponse` — contains the `file_id` and the
    `latest_revision_number`.

    **Path parameters:**
    - `collection_id` (int, ≥1): target collection ID.
    - `file_id`  (int, ≥1): target file ID within the collection.

    **Request body:**
    - `value` (string, 1-40): tag value; whitespace-trimmed; normalized.

    **Response codes:**
    - `201` — tag successfully created (or already present; idempotent).
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection or file not found.
    - `422` — validation error (path/body).
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Side effects:**
    - Persists a new `FileTag` and links it to the target file (only if
    not already present).

    **Hooks:**
    - `HOOK_AFTER_TAG_INSERT`: executed after the tag is ensured on the
    file (newly created or already present).
    """
    config = request.app.state.config

    collection_repository = Repository(session, cache, Collection, config)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    file_repository = Repository(session, cache, File, config)
    file = await file_repository.select(id=file_id)

    if not file or file.collection_id != collection.id:
        raise E([LOC_PATH, "file_id"], file_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    tag_repository = Repository(session, cache, FileTag, config)
    tag = await tag_repository.select(
        file_id__eq=file.id, value__eq=schema.value)

    if not tag:
        tag = FileTag(file.id, schema.value)
        file.file_tags.append(tag)
        await file_repository.update(file)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_TAG_INSERT, file, schema.value)

    return {
        "file_id": file.id,
        "latest_revision_number": file.latest_revision_number,
    }
