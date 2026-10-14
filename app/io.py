# app/io.py
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os

import aiofiles
import aiofiles.os
import aiofiles.ospath


async def listdir(path: str) -> list[str]:
    """Return the entry names contained in a directory."""
    return list(await aiofiles.os.listdir(path))


async def isfile(path: str) -> bool:
    """Return whether the path points to a regular file."""
    return await aiofiles.ospath.isfile(path)


async def isdir(path: str) -> bool:
    """Return whether the path points to a directory."""
    return await aiofiles.ospath.isdir(path)


async def ismount(path: str) -> bool:
    """Return whether the path is a mount point."""
    return await aiofiles.ospath.ismount(path)


async def mkdir(path: str) -> None:
    """
    Create a single directory and persist the parent directory entry.
    The parent directory must already exist.
    """
    await aiofiles.os.mkdir(path)
    await _fsync_dir(_get_parent_dir(path))


async def rmtree(path: str) -> None:
    """
    Remove a directory with the files it contains and persist the
    directory entry updates. A missing directory is left as is.
    """
    if not await isdir(path):
        return

    for name in await listdir(path):
        child = os.path.join(path, name)

        if await isdir(child):
            await rmtree(child)
        else:
            await delete(child)

    await _rmdir(path)


async def write(
    destination: str,
    data: bytes | bytearray | memoryview,
) -> None:
    """
    Atomically write in-memory bytes to destination. Data is written
    to a temporary file, flushed, fsynced, atomically replaced, and
    the parent directory is fsynced.
    """
    payload = bytes(data)
    parent_directory = _get_parent_dir(destination)
    filename = os.path.basename(destination)
    temporary_path = os.path.join(
        parent_directory,
        f".{filename}.tmp",
    )

    try:
        async with aiofiles.open(temporary_path, mode="wb") as file:
            await file.write(payload)
            await file.flush()
            await asyncio.to_thread(os.fsync, file.fileno())

        await asyncio.to_thread(os.replace, temporary_path, destination)
        await _fsync_dir(parent_directory)

    except Exception:
        try:
            await asyncio.to_thread(os.unlink, temporary_path)
        except FileNotFoundError:
            pass
        raise


async def read(path: str) -> bytes:
    """Read the whole file asynchronously."""
    async with aiofiles.open(path, mode="rb") as file:
        return await file.read()


async def delete(path: str) -> None:
    """
    Delete a file and persist the directory entry update. The file
    is unlinked and the parent directory is fsynced if the deletion
    succeeds.
    """
    try:
        await asyncio.to_thread(os.unlink, path)
    except FileNotFoundError:
        return

    await _fsync_dir(_get_parent_dir(path))


def _get_parent_dir(path: str) -> str:
    """
    Return the parent directory of a path. Paths without a directory
    resolve to the current directory.
    """
    parent_directory = os.path.dirname(path)
    return parent_directory or "."


async def _fsync_dir(path: str) -> None:
    """
    Fsync a directory to persist metadata changes. Used after create,
    replace, and delete operations.
    """
    directory_fd = await asyncio.to_thread(os.open, path, os.O_RDONLY)
    try:
        await asyncio.to_thread(os.fsync, directory_fd)
    finally:
        await asyncio.to_thread(os.close, directory_fd)


async def _rmdir(path: str) -> None:
    """Remove an empty directory and persist the directory entry update."""
    parent = _get_parent_dir(path)
    await aiofiles.os.rmdir(path)
    await _fsync_dir(parent)
