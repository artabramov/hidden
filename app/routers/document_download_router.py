"""
The module defines a FastAPI router for downloading revision entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.revision_model import Revision
from app.models.download_model import Download
from app.models.shard_model import Shard
from app.hooks import Hook
from app.errors import E
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_BEFORE_REVISION_DOWNLOAD)
from app.helpers.encryption_helper import decrypt_bytes
from app.config import get_config

cfg = get_config()
router = APIRouter()


@router.get("/document/{document_id}/revision/{revision_id}",
            summary="Download a document revision.",
            response_class=Response, status_code=status.HTTP_200_OK,
            tags=["Files"])
@locked
async def document_download(
    document_id: int, revision_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> Response:
    """
    Download a document revision. The router retrieves the specified
    revision from the repository, decrypts the associated file, executes
    related hooks, and returns the file as an attachment. The current
    user should have a reader role or higher. Returns a 200 response on
    success, a 404 error if the revision or the document is not found,
    a 403 error if authentication failed or the user does not have the
    required permissions, and a 423 error if the application is locked.

    **Args:**
    - `document_id`: The ID of the document.
    - `revision_id`: The ID of the revision to download.

    **Returns:**
    - `Response`: A response containing the decrypted file content as
      an attachment.

    **Raises:**
    - `403 Forbidden`: Raised if the user does not have the required
      permissions.
    - `404 Not Found`: Raised if the revision or the document with the
      specified ID does not exist.
    - `423 Locked`: Raised if the application is locked.

    **Auth:**
    - The user must provide a valid `JWT token` in the request header.
    - `reader`, `writer`, `editor`, or `admin` roles are required to
      access this router.
    """
    revision_repository = Repository(session, cache, Revision)
    revision = await revision_repository.select(id=revision_id)
    if (not revision or revision.document_id != document_id):
        raise E([LOC_PATH, "revision_id"], revision_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    # merge file from shards
    shard_repository = Repository(session, cache, Shard)
    shards = await shard_repository.select_all(
        revision_id__eq=revision.id, order_by="shard_index", order="asc")
    encrypted_data = await FileManager.merge(
        [shard.shard_path for shard in shards], cfg.SHARD_SIZE)

    decrypted_data = decrypt_bytes(encrypted_data)

    download_repository = Repository(session, cache, Download)
    download = Download(current_user.id, revision.document_id, revision.id)
    await download_repository.insert(download, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_REVISION_DOWNLOAD, revision)

    headers = {"Content-Disposition": f"attachment; filename={revision.revision_filename}"}  # noqa E501
    return Response(content=decrypted_data, headers=headers,
                    media_type=revision.revision_mimetype)
