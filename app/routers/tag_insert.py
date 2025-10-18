from fastapi import APIRouter, Request, Depends, status, Path
from fastapi.responses import JSONResponse
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.collection import Collection
from app.models.document import Document
from app.models.document_tag import DocumentTag
from app.hook import Hook, HOOK_AFTER_TAG_INSERT
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.auth import auth
from app.repository import Repository
from app.schemas.tag_insert import TagInsertRequest, TagInsertResponse

router = APIRouter()


@router.post(
    "/collection/{collection_id}/document/{document_id}/tag",
    status_code=status.HTTP_201_CREATED,
    response_class=JSONResponse,
    response_model=TagInsertResponse,
    summary="Add tag",
    tags=["Documents"]
)
async def tag_insert(
    request: Request,
    schema: TagInsertRequest,
    collection_id: int = Path(..., ge=1),
    document_id: int = Path(..., ge=1),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> TagInsertResponse:
    """
    Add a new tag to a document and return the document ID with its
    latest revision number. If the tag already exists for this document,
    the operation is idempotent and no duplicate is created.

    **Authentication:**
    - Requires a valid bearer token with `editor` role or higher.

    **Validation schemas:**
    - `TagInsertRequest` — request body with a single `value` field.
    The value is normalized/validated by `value_validate` (NFKC, trim,
    lower-case).
    - `TagInsertResponse` — contains the `document_id` and the
    `latest_revision_number`.

    **Path parameters:**
    - `collection_id` (int, ≥1): target collection ID.
    - `document_id`  (int, ≥1): target document ID within the collection.

    **Request body:**
    - `value` (string, 1-40): tag value; whitespace-trimmed; normalized.

    **Response codes:**
    - `201` — tag successfully created (or already present; idempotent).
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — collection or document not found.
    - `422` — validation error (path/body).
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Side effects:**
    - Persists a new `DocumentTag` and links it to the target document
    (only if not already present).

    **Hooks:**
    - `HOOK_AFTER_TAG_INSERT`: executed after the tag is ensured on the
    document (newly created or already present).
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

    tag_repository = Repository(session, cache, DocumentTag, config)
    tag = await tag_repository.select(
        document_id__eq=document.id, value__eq=schema.value)

    if not tag:
        tag = DocumentTag(document.id, schema.value)
        document.document_tags.append(tag)
        await document_repository.update(document)

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_TAG_INSERT, document, schema.value)

    return {
        "document_id": document.id,
        "latest_revision_number": document.latest_revision_number,
    }
