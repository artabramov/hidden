from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.tag_model import Tag
from app.hook import Hook, HOOK_AFTER_TAG_INSERT
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.auth import auth
from app.repository import Repository
from app.config import get_config
from app.schemas.tag_insert_schema import TagInsertRequest, TagInsertResponse
from app.helpers.encrypt_helper import hash_str

cfg = get_config()
router = APIRouter()


@router.post("/document/{document_id}/tag", summary="Create a tag.",
             response_class=JSONResponse, status_code=status.HTTP_201_CREATED,
             response_model=TagInsertResponse, tags=["Documents"])
async def tag_insert(
    document_id: int, schema: TagInsertRequest,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> TagInsertResponse:
    """
    Creates a tag. Validates the document by its ID, checks if the tag
    already exists, and creates a new tag if it does not. Associates the
    tag with the document.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `editor` or `admin` role.

    **Returns:**
    - `TagInsertResponse`: Contains the ID of the created (or existing)
    tag.

    **Responses:**
    - `201 Created`: If the tag is successfully created.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the secret key is missing.
    - `422 Unprocessable Entity`: If parameters validation fails.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_TAG_INSERT`: Executes after the tag is successfully
    created.
    """
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)

    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    tag_repository = Repository(session, cache, Tag)

    tag_value_hash = hash_str(schema.tag_value)
    tag = await tag_repository.select(
        document_id__eq=document.id, tag_value_hash__eq=tag_value_hash)

    if not tag:
        tag = Tag(document.id, schema.tag_value)
        await tag_repository.insert(tag)
        await document_repository.delete_from_cache(document)

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_TAG_INSERT, document, tag)

    return {"tag_id": tag.id}
