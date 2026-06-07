# app/repositories/file.py
# SPDX-License-Identifier: SSPL-1.0

import asyncio
import hashlib
import mimetypes
import os
import uuid
from typing import AsyncIterable, AsyncIterator, Protocol

import aiofiles
import aiofiles.os
import aiofiles.ospath
import filetype
import magic

from app.config import get_config
from app.constants import (
    FILE_CHUNK_SIZE_BYTES,
    FILE_MIMETYPE_READ_BYTES,
)

TEXT_APPLICATION_MIME_TYPES = {
    "application/json",
    "application/xml",
    "application/yaml",
    "application/x-yaml",
    "application/javascript",
}

IMAGE_MIME_TYPES: set[str] = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


class AsyncReadable(Protocol):
    """Async source that returns bytes from read(size)."""

    async def read(self, size: int = -1) -> bytes: ...


def get_tmp_path() -> str:
    """
    Return a unique temporary file path inside the encrypted storage.
    """
    config = get_config()
    return os.path.join(config.FILES_TMP_DIR, str(uuid.uuid4()))


async def get_mimetype(path: str) -> str | None:
    """
    Guess MIME type from file content using libmagic and filetype,
    falling back to the file extension.
    """
    try:
        async with aiofiles.open(path, "rb") as f:
            head = await f.read(FILE_MIMETYPE_READ_BYTES)
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        return None

    if not head:
        guessed = mimetypes.guess_type(path)[0]
        return guessed.lower().strip() if guessed else None

    value = await asyncio.to_thread(_detect_mime_with_magic, head)
    if value:
        return value

    try:
        kind = filetype.guess(head)
        if kind and kind.mime:
            return kind.mime.lower().strip()
    except (TypeError, ValueError):
        pass

    guessed = mimetypes.guess_type(path)[0]
    return guessed.lower().strip() if guessed else None


async def get_filesize(path: str) -> int:
    """Return the size of the filesystem object in bytes."""
    stats = await aiofiles.os.stat(path)
    return stats.st_size


async def get_checksum(path: str) -> str:
    """Return a hexadecimal SHA-256 checksum of the file."""
    digest = hashlib.sha256()

    async for chunk in _iter_read(path):
        digest.update(chunk)

    return digest.hexdigest()


async def isfile(path: str) -> bool:
    """Return whether the path points to a regular file."""
    return await aiofiles.ospath.isfile(path)


async def isdir(path: str) -> bool:
    """Return whether the path points to a directory."""
    return await aiofiles.ospath.isdir(path)


async def ismount(path: str) -> bool:
    """
    Return whether the path is a mount point.
    """
    return await aiofiles.ospath.ismount(path)


def istext(mimetype: str | None) -> bool:
    """
    Return whether the MIME type is supported for text editing.
    """
    if not mimetype:
        return False

    if mimetype.startswith("text/"):
        return True

    return mimetype in TEXT_APPLICATION_MIME_TYPES


def isimage(mimetype: str | None) -> bool:
    """
    Return whether the MIME type is supported for image processing. Only
    formats that are reliably handled by Pillow are accepted. This check
    is used to decide whether thumbnail generation should be attempted.
    """
    return mimetype in IMAGE_MIME_TYPES if mimetype else False


async def mkdir(path: str) -> None:
    """
    Create a directory and persist the directory entry update.
    """
    parent = _parent_dir(path)
    await asyncio.to_thread(os.mkdir, path)
    await _fsync_directory(parent)


async def rmdir(path: str) -> None:
    """Remove an empty directory and persist the directory entry update."""
    parent = _parent_dir(path)
    await aiofiles.os.rmdir(path)
    await _fsync_directory(parent)


async def touch(path: str) -> None:
    """
    Create an empty file if it does not exist, or update its
    modification time if it does. The parent directory is fsynced.
    """
    parent = _parent_dir(path)
    await asyncio.to_thread(_touch_sync, path)
    await _fsync_directory(parent)


async def upload(
    file: AsyncReadable,
    destination: str,
) -> None:
    """
    Atomically write data from an async readable source to destination.
    Data is read in chunks, written to a temporary file in the same
    directory, then flushed, fsynced, atomically replaced, and the
    parent directory is fsynced.
    """
    async def data_iter() -> AsyncIterator[bytes]:
        while True:
            chunk = await file.read(FILE_CHUNK_SIZE_BYTES)
            if not chunk:
                break
            yield chunk

    await _atomic_write_stream(data_iter(), destination)


async def write(
    destination: str,
    data: bytes | bytearray | memoryview,
) -> None:
    """
    Atomically write in-memory bytes to destination. Data is chunked,
    written to a temporary file, then flushed, fsynced, atomically
    replaced, and the parent directory is fsynced.
    """
    async def data_iter() -> AsyncIterator[bytes]:
        view = memoryview(data)
        for offset in range(0, len(view), FILE_CHUNK_SIZE_BYTES):
            yield bytes(view[offset:offset + FILE_CHUNK_SIZE_BYTES])

    await _atomic_write_stream(data_iter(), destination)


async def read(path: str) -> bytes:
    """
    Read the whole file asynchronously in chunks. Data is read
    incrementally and accumulated into a single bytes object returned
    to the caller.
    """
    result = bytearray()

    async for chunk in _iter_read(path):
        result.extend(chunk)

    return bytes(result)


async def delete(
    path: str,
) -> None:
    """
    Delete a file and persist the directory entry update. The file
    is unlinked and the parent directory is fsynced if the deletion
    succeeds.
    """
    try:
        await asyncio.to_thread(os.unlink, path)
    except FileNotFoundError:
        return

    await _fsync_directory(_parent_dir(path))


async def copy(
    source: str,
    destination: str,
) -> None:
    """
    Copy a file to destination using chunked asynchronous I/O. Data is
    read in chunks, written to a temporary file, then flushed, fsynced,
    atomically replaced, and the parent directory is fsynced.
    """
    async def source_iter() -> AsyncIterator[bytes]:
        async for chunk in _iter_read(source):
            yield chunk

    await _atomic_write_stream(source_iter(), destination)


async def rename(source: str, destination: str) -> None:
    """
    Atomically rename or replace a file or directory. The operation
    uses os.replace, and affected parent directories are fsynced.
    """
    await asyncio.to_thread(os.replace, source, destination)

    source_parent = _parent_dir(source)
    destination_parent = _parent_dir(destination)

    if source_parent == destination_parent:
        await _fsync_directory(destination_parent)
    else:
        await _fsync_directory(source_parent)
        await _fsync_directory(destination_parent)


async def _iter_read(
    path: str,
    chunk_size: int = FILE_CHUNK_SIZE_BYTES,
) -> AsyncIterator[bytes]:
    """
    Read a file asynchronously and yield chunks. The file remains open
    during iteration and data is yielded without loading the whole file
    into memory.
    """
    async with aiofiles.open(path, mode="rb") as file:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            yield chunk


# NOTE (ADR-46): File writes follow POSIX durability semantics.
# The file is fsynced before atomic replace, then the parent
# directory is fsynced to persist the directory entry update.

async def _atomic_write_stream(
    data: AsyncIterable[bytes],
    destination: str,
) -> None:
    """
    Atomically write a byte stream to destination. Data is written to
    a temporary file, then flushed, fsynced, atomically replaced, and
    the parent directory is fsynced.
    """
    parent_directory = _parent_dir(destination)
    temporary_path = _build_temp_path(destination)

    try:
        async with aiofiles.open(temporary_path, mode="wb") as file:
            async for chunk in data:
                await file.write(chunk)

            await file.flush()
            await asyncio.to_thread(os.fsync, file.fileno())

        await asyncio.to_thread(os.replace, temporary_path, destination)
        await _fsync_directory(parent_directory)

    except Exception:
        try:
            await asyncio.to_thread(os.unlink, temporary_path)
        except FileNotFoundError:
            pass
        raise


def _touch_sync(path: str) -> None:
    with open(path, "a"):
        os.utime(path, None)


def _build_temp_path(destination: str) -> str:
    """
    Build a unique temporary path next to destination. The file
    is created in the same directory to allow atomic replace.
    """
    parent_directory = _parent_dir(destination)
    filename = os.path.basename(destination)
    temporary_name = f".{filename}.{uuid.uuid4().hex}.tmp"
    return os.path.join(parent_directory, temporary_name)


def _parent_dir(path: str) -> str:
    """
    Return the parent directory of a path. Paths without a directory
    resolve to the current directory.
    """
    parent_directory = os.path.dirname(path)
    return parent_directory or "."


async def _fsync_directory(path: str) -> None:
    """
    Fsync a directory to persist metadata changes. Used after create,
    replace, rename, and delete operations.
    """
    directory_fd = await asyncio.to_thread(os.open, path, os.O_RDONLY)
    try:
        await asyncio.to_thread(os.fsync, directory_fd)
    finally:
        await asyncio.to_thread(os.close, directory_fd)


def _detect_mime_with_magic(head: bytes) -> str | None:
    """Detect MIME type from a byte buffer using libmagic."""
    try:
        value = magic.Magic(mime=True).from_buffer(head)
        if value:
            value = value.split(";", 1)[0].strip().lower()
            if value and value != "application/octet-stream":
                return value
    except (magic.MagicException, OSError):
        return None

    return None
