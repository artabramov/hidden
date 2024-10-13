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


@router.get("/document/{document_id}/download",
            summary="Download the latest revision of a document.",
            response_class=Response, status_code=status.HTTP_200_OK,
            tags=["Documents"])
@locked
async def document_download(
    document_id: int,
    session=Depends(get_session), cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> Response:
    document_repository = Repository(session, cache, Document)
    document = await document_repository.select(id=document_id)
    if not document:
        raise E([LOC_PATH, "document_id"], document_id,
                ERR_RESOURCE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    revision_repository = Repository(session, cache, Revision)
    document.latest_revision = await revision_repository.select(
        id=document.latest_revision_id)

    data = await FileManager.read(document.latest_revision.revision_path)
    decrypted_data = await FileManager.decrypt(data)

    download_repository = Repository(session, cache, Download)
    download = Download(
        current_user.id, document.id, document.latest_revision.id)
    await download_repository.insert(download, commit=False)

    document_repository = Repository(session, cache, Document)
    document.downloads_count = (
        await download_repository.count_all(document_id__eq=document.id))
    await document_repository.update(document, commit=False)

    hook = Hook(session, cache, current_user=current_user)
    await hook.do(HOOK_BEFORE_REVISION_DOWNLOAD, document.latest_revision)

    await document_repository.commit()
    await hook.do(HOOK_AFTER_REVISION_DOWNLOAD, document.latest_revision)

    headers = {"Content-Disposition": f"attachment; filename={document.latest_revision.original_filename}"}  # noqa E501
    return Response(content=decrypted_data, headers=headers,
                    media_type=document.latest_revision.original_mimetype)
