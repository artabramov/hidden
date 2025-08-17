from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.postgres import get_session
from app.redis import get_cache
from app.config import get_config
from app.auth import auth
from app.models.user_model import User, UserRole
from app.helpers.encrypt_helper import decrypt_str
from app.managers.entity_manager import EntityManager
from app.hook import Hook, HOOK_AFTER_TAG_LIST
from app.schemas.tag_list_schema import TagListResponse

cfg = get_config()
router = APIRouter()


@router.get("/tags", summary="Retrieve a list of tags.",
            response_class=JSONResponse, status_code=status.HTTP_200_OK,
            response_model=TagListResponse,
            tags=["Tags"])
async def tag_list(
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
):
    """
    Retrieves a list of tags.

    **Auth:**
    - The token must be included in the request header and contain auth
    data for an active user with the `reader`, `writer`, `editor`, or
    `admin` role.

    **Returns:**
    - `TagListResponse`: Contains the list of tags.

    **Raises:**
    - `200 OK`: If tags are successfully retrieved.
    - `401 Unauthorized`: If the token is invalid or lacks permissions.
    - `403 Forbidden`: If the token or secret key is missing.
    - `423 Locked`: If the app is locked.

    **Hooks:**
    - `HOOK_AFTER_TAG_RETRIEVE`: Executes after tag list is successfully
    retrieved.
    """
    entity_manager = EntityManager(session)
    data = await entity_manager.select_rows(
        """
        SELECT
            DISTINCT ON (tag_value_hash) tag_value_hash,
            tag_value_encrypted,
            COUNT(*) OVER (PARTITION BY tag_value_hash) AS documents_count
        FROM documents_tags;
        """)
    tags = [{
        "tag_value": decrypt_str(x.tag_value_encrypted),
        "documents_count": x.documents_count} for x in data]

    hook = Hook(session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_TAG_LIST, tags)

    return {"tags": tags}
