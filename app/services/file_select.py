# app/services/file_select.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.file import File
from app.repositories.orm import ORMRepository

log = logging.getLogger(__name__)


# TODO: Audit read access to individual files. Currently only
# FILE_DOWNLOAD_COMPLETED is audited; viewing file metadata
# (file_select) and previewing thumbnails (file_thumbnail_retrieve)
# leave no trace. For a privacy-oriented store this breaks the
# "complete audit trail" claim — a viewer can inspect sensitive
# items without any record. Scope when implementing: per-item reads
# (/file/{id}, /file/{id}/thumbnail) yes; bulk listings (file_list,
# folder_list) no, to keep the audit table from exploding. Reuse the
# existing pre-commit audit pattern (write_audit before commit, hooks
# after) so the audit row participates in the read transaction.


async def select_file(
    session: AsyncSession,
    file_id: int,
) -> File:
    """
    Retrieve a file by identifier together with related metadata needed
    for file selection response.
    """
    log.info("event=%s file_id=%s", E.FILE_SELECT_STARTED, file_id)

    repository = ORMRepository(session)
    file = await repository.select(File, obj_id=file_id)

    if file is None:
        log.warning("event=%s", E.FILE_SELECT_NOT_FOUND)
        raise ResourceNotFoundError

    log.info("event=%s", E.FILE_SELECT_COMPLETED)
    await hooks.emit(E.FILE_SELECT_COMPLETED, session, file)

    return file
