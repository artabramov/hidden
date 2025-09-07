"""
Asynchronous file utilities for atomic writes, chunked I/O, and
multiple-pass overwrite deletion via a system tool. Favors fail-fast
behavior with minimal policy, leaving durability and higher-level
error handling to callers.
"""

import os
import asyncio
import mimetypes
import hashlib
import aiofiles
import aiofiles.os
from typing import AsyncIterable
from app.config import Config


class FileManager:
    """
    Provides asynchronous file operations with atomic writes and
    chunked I/O. Favors fail-fast behavior and avoids durability
    guarantees beyond OS buffering.
    """

    def __init__(self, config: Config):
        """
        Initializes a new instance configured with external parameters.
        """
        self.config = config

    def mimetype(self, filename: str) -> str:
        """
        Returns a media type inferred from a filename, with a fallback.
        Resolution uses standard extension mapping and does not inspect
        contents.
        """
        mime, _ = mimetypes.guess_type(filename)
        return mime or self.config.FILE_DEFAULT_MIMETYPE

    async def filesize(self, path: str) -> int:
        """
        Returns the size of a file in bytes via an async stat call.
        Lets OS errors propagate (e.g., missing path).
        """
        stats = await aiofiles.os.stat(path)
        return int(stats.st_size)

    async def checksum(self, path: str) -> str:
        """
        Computes and returns the SHA-256 hex digest of a file
        asynchronously by streaming it in chunks.
        """
        h = hashlib.sha256()
        async with aiofiles.open(path, "rb") as f:
            while True:
                buf = await f.read(self.config.FILE_CHUNK_SIZE)
                if not buf:
                    break
                h.update(buf)
        return h.hexdigest()

    async def isfile(self, path: str) -> bool:
        """
        Checks whether a path refers to an existing regular file.
        Runs asynchronously and ignores non-file filesystem entries.
        """
        return await aiofiles.os.path.isfile(path)

    async def mkdir(self, path: str, is_file: bool = False) -> None:
        """
        Ensure required directories exist. For file paths, create parent
        directories; for directory paths, create the directory itself.
        Intermediate directories are created as needed; existing ones
        are left untouched.
        """
        target = os.path.dirname(path) if is_file else path
        if target:
            target = target.rstrip("/\\")
            if target:
                await aiofiles.os.makedirs(target, exist_ok=True)

    async def _atomic_write(
            self, path: str, chunk_iter: AsyncIterable) -> None:
        """
        Writes data via a temporary sibling and atomically replaces the
        target. Prevents partially written files from being observed and
        lets errors propagate.
        """
        tmp = f"{path}.part"
        async with aiofiles.open(tmp, "wb") as f:
            async for chunk in chunk_iter:
                await f.write(chunk)
            await f.flush()
        await aiofiles.os.replace(tmp, path)

    async def upload(self, file: object, path: str) -> None:
        """
        Streams data from an asynchronous reader and writes it
        atomically. Reads fixed-size chunks until exhaustion and
        commits the result in one step.
        """
        await self.mkdir(path, is_file=True)

        async def chunks():
            while True:
                buf = await file.read(self.config.FILE_CHUNK_SIZE)
                if not buf:
                    break
                yield buf

        await self._atomic_write(path, chunks())

    async def delete(self, path: str) -> None:
        """
        Runs a system tool that overwrites a file in multiple passes and
        unlinks it. Waits for completion and performs the operation only
        if a regular file is present.
        """
        if await self.isfile(path):
            cmd = ["shred", "-u", "-z", "-n",
                   str(self.config.FILE_SHRED_CYCLES), path]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )

            await process.wait()

    async def write(self, path: str, data: bytes) -> None:
        """
        Writes bytes sequence atomically using the same replace pattern.
        Persists to a temporary file first and exposes the result only
        when complete.
        """
        await self.mkdir(path, is_file=True)

        async def chunks():
            yield data

        await self._atomic_write(path, chunks())

    async def read(self, path: str) -> bytes:
        """
        Reads the entire contents of a file into memory. Suitable for
        small to medium inputs; consider streaming for large data.
        """
        async with aiofiles.open(path, mode="rb") as fn:
            return await fn.read()

    async def copy(self, src_path: str, dst_path: str) -> None:
        """
        Copies a file by streaming bytes and atomically replacing the
        destination. Creates parent directories as needed and avoids
        exposing partial results.
        """
        await self.mkdir(dst_path, is_file=True)

        async def chunks():
            async with aiofiles.open(src_path, "rb") as src:
                while True:
                    buf = await src.read(self.config.FILE_CHUNK_SIZE)
                    if not buf:
                        break
                    yield buf

        await self._atomic_write(dst_path, chunks())

    async def rename(self, src_path: str, dst_path: str) -> None:
        """
        Atomically moves or renames a file, overwriting any existing
        target. Creates the destination’s parent directory when missing
        and completes in one step.
        """
        await self.mkdir(dst_path, is_file=True)
        await aiofiles.os.replace(src_path, dst_path)
