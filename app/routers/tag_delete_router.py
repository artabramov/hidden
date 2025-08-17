from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.tag_model import Tag
from app.schemas.tag_delete_schema import TagDeleteRequest, TagDeleteResponse
from app.helpers.encrypt_helper import hash_str
from app.repository import Repository
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND
from app.hook import Hook, HOOK_AFTER_TAG_DELETE
from app.auth import auth

router = APIRouter()


@router.delete("/document/{document_id}/tag/{tag_value}",
               summary="Delete a tag.",
               response_class=JSONResponse, status_code=status.HTTP_200_OK,
               response_model=TagDeleteResponse, tags=["Documents"])
async def tag_delete(
    document_id: int, request: Request, schema=Depends(TagDeleteRequest),
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.editor))
) -> TagDeleteResponse:
    """
    Deletes a tag. Retrieves the specified document using its ID,
    verifies that the tag exists for the document, and removes it.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `editor` or `admin` role.

    **Returns:**
    - `TagDeleteResponse`: Contains the ID of the deleted tag.

    **Responses:**
    - `200 OK`: If the tag is successfully deleted.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the secret key is missing.
    - `404 Not Found`: If the document or tag is not found.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_TAG_DELETE`: Executes after the tag is successfully
    deleted.
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
        raise E([LOC_PATH, "tag_value"], schema.tag_value,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    await tag_repository.delete(tag)
    await document_repository.delete_from_cache(document)

    hook = Hook(request.app, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_TAG_DELETE, document, tag)

    return {"tag_id": tag.id}
