# app/services/file_list.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.file import File
from app.models.file_tag import FileTag
from app.models.folder import Folder
from app.repositories.orm import ORMRepository
from app.schemas.file_list import FileListRequest

log = logging.getLogger(__name__)


async def list_files(
    session: AsyncSession,
    params: FileListRequest,
) -> tuple[list[File], int]:
    """
    Return files matching params together with the total count.
    When params.folder_id__eq is set, scope to that folder after
    verifying it exists; when null, do not restrict by folder.
    """
    folder_id = params.folder_id__eq
    log.info("event=%s folder_id=%s", E.FILE_LIST_STARTED, folder_id)

    repository = ORMRepository(session)

    if folder_id is not None:
        folder = await repository.select(Folder, obj_id=folder_id)

        if folder is None:
            log.warning("event=%s", E.FILE_LIST_FOLDER_NOT_FOUND)
            raise ResourceNotFoundError

    filters = params.model_dump(
        exclude_none=True,
        exclude={"folder_id__eq", "tag__eq"},
    )

    if "filename__ilike" in filters:
        filters["filename__ilike"] = f"%{filters['filename__ilike']}%"

    if "mimetype__ilike" in filters:
        filters["mimetype__ilike"] = f"%{filters['mimetype__ilike']}%"

    if folder_id is not None:
        filters["folder_id"] = folder_id

    if params.tag__eq is not None:
        filters["id__subquery"] = repository.make_subquery(
            FileTag,
            "file_id",
            tag__eq=params.tag__eq,
        )

    files_count = await repository.count_all(File, **filters)
    files = await repository.select_all(File, **filters)

    log.info("event=%s", E.FILE_LIST_COMPLETED)
    await hooks.emit(E.FILE_LIST_COMPLETED, session, files)
    return files, files_count
