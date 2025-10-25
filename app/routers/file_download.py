"""FastAPI router for file downloading."""

from fastapi import APIRouter, Request, Response, Path, Depends, status
from app.sqlite import get_session
from app.redis import get_cache
from app.models.user import User, UserRole
from app.models.file import File
from app.error import E, LOC_PATH, ERR_VALUE_NOT_FOUND, ERR_FILE_CONFLICT
from app.auth import auth
from app.hook import Hook, HOOK_AFTER_FILE_DOWNLOAD
from app.repository import Repository

router = APIRouter()


@router.get(
    "/file/{file_id}/revision/{revision_number}",
    status_code=status.HTTP_200_OK,
    response_class=Response,
    summary="Download file",
    tags=["Files"]
)
async def file_download(
    request: Request,
    file_id: int = Path(..., ge=1),
    revision_number: int = Path(..., ge=0),
    session=Depends(get_session),
    cache=Depends(get_cache),
    current_user: User = Depends(auth(UserRole.reader))
) -> Response:
    """
    Download a file file (current head or a specific revision). Returns
    the raw file bytes with the file's MIME type, and the original
    filename.

    **Authentication:**
    - Requires a valid bearer token with `reader` role or higher.

    **Path parameters:**
    - `file_id` (integer ≥ 1): file identifier.
    - `revision_number` (integer ≥ 0): 0 for the current file head;
    > 0 for a specific revision.

    **Response codes:**
    - `200` — file returned.
    - `401` — missing, invalid, or expired token.
    - `403` — insufficient role, invalid JTI, user is inactive or
    suspended.
    - `404` — file or revision not found.
    - `409` — file not found on filesystem or checksum mismatch.
    - `423` — application is temporarily locked.
    - `498` — gocryptfs key is missing.
    - `499` — gocryptfs key is invalid.

    **Hooks:**
    - `HOOK_AFTER_FILE_DOWNLOAD` — executed after a successful read.
    """
    config = request.app.state.config
    file_manager = request.app.state.file_manager
    lru = request.app.state.lru

    file_repository = Repository(session, cache, File, config)
    file = await file_repository.select(id=file_id)

    if not file:
        raise E([LOC_PATH, "file_id"], file_id,
                ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

    # NOTE: On file download, checksum verification is applied to
    # prevent replacement with a fake (both head and revisions).

    if revision_number == 0:
        file_path = file.path(config)
        checksum = file.checksum
        filesize = file.filesize

    else:
        revision = next((r for r in file.file_revisions
                        if r.revision_number == revision_number), None)

        if not revision:
            raise E([LOC_PATH, "file_id"], file_id,
                    ERR_VALUE_NOT_FOUND, status.HTTP_404_NOT_FOUND)

        file_path = revision.path(config)
        checksum = revision.checksum
        filesize = revision.filesize

    file_data = lru.load(file_path)
    if file_data is None:

        # Ensure the file exists
        file_exists = await file_manager.isfile(file_path)
        if not file_exists:
            raise E([LOC_PATH, "file_id"], file_id,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

        # Ensure the file checksum is correct
        file_checksum = await file_manager.checksum(file_path)
        if checksum != file_checksum:
            raise E([LOC_PATH, "file_id"], file_id,
                    ERR_FILE_CONFLICT, status.HTTP_409_CONFLICT)

        file_data = await file_manager.read(file_path)
        lru.save(file_path, file_data)

    headers = {
        "Content-Disposition": f'attachment; filename="{file.filename}"',
        "Content-Length": str(filesize),
        "Cache-Control": "no-store",
    }

    hook = Hook(request, session, cache, current_user=current_user)
    await hook.call(HOOK_AFTER_FILE_DOWNLOAD, file, revision_number)

    return Response(
        content=file_data, media_type=file.mimetype, headers=headers)
