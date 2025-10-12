from fastapi import APIRouter, Request, Depends, Path, status
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.models.document import Document
from app.validators.tag_validators import value_validate
from app.schemas.tag_delete_schema import TagDeleteResponse
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND, ERR_VALUE_INVALID
from app.hook import Hook, HOOK_AFTER_TAG_DELETE
from app.auth import auth

router = APIRouter()


@router.delete(
    "/collection/{collection_id}/document/{document_id}/tag/{tag_value}",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    response_model=TagDeleteResponse,
    summary="Delete tag",
    tags=["Documents"]
)
async def tag_delete(
    request: Request,
    collection_id: int = Path(..., ge=1),
    document_id: int = Path(..., ge=1),
    tag_value: str = Path(..., min_length=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> TagDeleteResponse:
    """
    Delete a tag from a document and return the document ID with its
    latest revision number. The operation is idempotent: if the tag is
    absent, the endpoint still returns 200 and leaves the document
    unchanged.

    **Authentication:**
    - Requires a valid bearer token with `editor` role.

    **Path parameters:**
    - `collection_id` (integer ≥ 1): collection identifier.
    - `document_id` (integer ≥ 1): document identifier within the
    collection.
    - `tag_value` (string, 1-40): tag value to remove; normalized and
    validated.

    **Response:**
    - `TagDeleteResponse` — returns the `document_id` and the
    `latest_revision_number`.

    **Response codes:**
    - `200` — tag removed (or not present; idempotent success).
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection or document not found.
    - `422` — invalid `tag_value` (fails normalization/constraints).
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_TAG_DELETE` — executed after successful update.
    """
    config = request.app.state.config

    collection_repository = Repository(session, cache, Collection, config)
    collection = await collection_repository.select(id=collection_id)

    if not collection:
        raise E([LOC_PATH, "collection_id"], collection_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    document_repository = Repository(session, cache, Document, config)
    document = await document_repository.select(id=document_id)

    if not document or document.collection_id != collection.id:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    try:
        normalized_value = value_validate(tag_value)
    except ValueError:
        raise E([LOC_PATH, "tag_value"], tag_value,
                ERR_VALUE_INVALID, status.HTTP_422_UNPROCESSABLE_ENTITY)

    document.document_tags = [
        t for t in document.document_tags if t.value != normalized_value]
    await document_repository.update(document)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_TAG_DELETE, document, normalized_value)

    return {
        "document_id": document.id,
        "latest_revision_number": document.latest_revision_number,
    }
