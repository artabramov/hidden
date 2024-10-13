"""
The module defines a FastAPI router for downloading revision entities.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from app.database import get_session
from app.cache import get_cache
from app.decorators.locked_decorator import locked
from app.models.user_model import User, UserRole
from app.models.document_model import Document
from app.models.revision_model import Revision
from app.models.download_model import Download
from app.hooks import Hook
from app.errors import E
from app.auth import auth
from app.repository import Repository
from app.managers.file_manager import FileManager
from app.constants import (
    LOC_PATH, ERR_RESOURCE_NOT_FOUND, HOOK_BEFORE_REVISION_DOWNLOAD,
    HOOK_AFTER_REVISION_DOWNLOAD)

router = APIRouter()


@router.get("/document/{document_id}/revision/{revision_id}/download",
            summary="Download a specified revision of a document.",
            response_class=Response, status_code=status.HTTP_200_OK,
            tags=["Documents"])
@locked
async def revision_download(
    document_id: int, revision_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> Response:
    """
    FastAPI router for downloading a revision entity. The router
    retrieves the specified revision from the repository, decrypts the
    associated file, executes related hooks, and returns the file as an
    attachment. The current user should have a reader role or higher.
    Returns a 200 response on success, a 404 error if the revision is
    not found, and a 403 error if authentication fails or the user
    does not have the required role.
    """
    revision_repository = Repository(session, cache, Revision)
    revision = await revision_repository.select(id=revision_id)
    if not revision or revision.document_id != document_id:
        raise E([LOC_PATH, "revision_id"], revision_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    data = await FileManager.read(revision.revision_path)
    decrypted_data = await FileManager.decrypt(data)

    download_repository = Repository(session, cache, Download)
    download = Download(
        current_user.id, revision.revision_document.id, revision.id)
    await download_repository.insert(download, commit=False)

    document_repository = Repository(session, cache, Document)
    revision.revision_document.downloads_count = (
        await download_repository.count_all(
            document_id__eq=revision.revision_document.id))
    await document_repository.update(
        revision.revision_document, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_REVISION_DOWNLOAD, revision)

    await revision_repository.commit()
    await hook.do(HOOK_AFTER_REVISION_DOWNLOAD, revision)

    headers = {"Content-Disposition": f"attachment; filename={revision.original_filename}"}  # noqa E501
    return Response(content=decrypted_data, headers=headers,
                    media_type=revision.original_mimetype)
