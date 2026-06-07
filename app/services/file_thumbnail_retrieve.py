# app/services/file_thumbnail_retrieve.py
# SPDX-License-Identifier: SSPL-1.0

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.lru import get_thumbnail_cache
from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.hooks import hooks
from app.models.file_thumbnail import FileThumbnail
from app.repositories.file import read
from app.repositories.orm import ORMRepository

log = logging.getLogger(__name__)


async def retrieve_file_thumbnail(
    session: AsyncSession,
    file_id: int,
) -> tuple[str, bytes]:
    """
    Return (mimetype, data) for the thumbnail of the given file.

    On a cache hit the bytes are served directly from the in-memory
    LRU cache without touching the encrypted filesystem.  On a miss
    the thumbnail record and file are loaded, the bytes are stored in
    the cache, and the hook is emitted.

    Missing thumbnail records or missing filesystem files are treated
    as not found.
    """
    log.info("event=%s file_id=%s", E.FILE_THUMBNAIL_RETRIEVE_STARTED, file_id)

    cached = get_thumbnail_cache().get(file_id)
    if cached is not None:
        log.info("event=%s", E.FILE_THUMBNAIL_RETRIEVE_COMPLETED)
        return cached

    repository = ORMRepository(session)
    thumbnail = await repository.select(
        FileThumbnail,
        file_id=file_id,
    )

    if thumbnail is None:
        log.warning("event=%s", E.FILE_THUMBNAIL_RETRIEVE_NOT_FOUND)
        raise ResourceNotFoundError

    try:
        data = await read(thumbnail.absolute_path)
    except (FileNotFoundError, IsADirectoryError):
        log.warning("event=%s", E.FILE_THUMBNAIL_RETRIEVE_NOT_FOUND)
        raise ResourceNotFoundError

    mimetype = thumbnail.mimetype
    get_thumbnail_cache().put(file_id, mimetype, data)

    log.info("event=%s", E.FILE_THUMBNAIL_RETRIEVE_COMPLETED)
    await hooks.emit(E.FILE_THUMBNAIL_RETRIEVE_COMPLETED, session, thumbnail)
    return mimetype, data
