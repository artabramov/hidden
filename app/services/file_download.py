# app/services/file_download.py
# SPDX-License-Identifier: GPL-3.0-only

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import write_audit
from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.file import File
from app.models.file_revision import FileRevision
from app.repositories.file import isfile
from app.repositories.orm import ORMRepository

log = logging.getLogger(__name__)

# NOTE (ADR-56): Shared download links are intentionally unsupported.
# The primary goal of the project is reliable and secure storage of
# sensitive data. Features that intentionally expose files outside the
# authenticated storage boundary are intentionally excluded from the
# project.


async def download_file(
    session: AsyncSession,
    file_id: int,
    revision_number: int,
) -> tuple[File | FileRevision, str]:
    """
    Return metadata and absolute path for download.

    revision_number=0 refers to the HEAD (the current file content).
    revision_number>=1 refers to a historical FileRevision record.

    Missing database records or missing filesystem files are treated as
    not found.
    """
    log.info(
        "event=%s file_id=%s revision_number=%s",
        E.FILE_DOWNLOAD_STARTED,
        file_id,
        revision_number,
    )

    repository = ORMRepository(session)
    file = await repository.select(File, obj_id=file_id)

    if file is None:
        log.warning("event=%s", E.FILE_DOWNLOAD_NOT_FOUND)
        raise ResourceNotFoundError

    if revision_number == 0:
        parent_chain = await repository.select_parent_chain(file.file_folder)
        file_path = file.get_absolute_path(file.file_folder, parent_chain)
        resource = file
    else:
        revision = await repository.select(
            FileRevision,
            file_id=file_id,
            revision_number=revision_number,
        )

        if revision is None:
            log.warning("event=%s", E.FILE_DOWNLOAD_NOT_FOUND)
            raise ResourceNotFoundError

        file_path = revision.absolute_path
        resource = revision

    if not await isfile(file_path):
        log.warning("event=%s", E.FILE_DOWNLOAD_NOT_FOUND)
        raise ResourceNotFoundError

    log.info("event=%s", E.FILE_DOWNLOAD_COMPLETED)

    await write_audit(
        repository=repository,
        event=E.FILE_DOWNLOAD_COMPLETED,
        resource_type=File.__tablename__,
        resource_id=file.id,
    )
    await repository.commit()

    await hooks.emit(E.FILE_DOWNLOAD_COMPLETED, session, file)

    return resource, file_path
