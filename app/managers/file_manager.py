"""
The module provides asynchronous methods for various file operations.
These include uploading, deleting, writing, reading, copying, renaming.
It supports efficient I/O operations using aiofiles to handle large
files and avoid blocking the event loop.
"""

import asyncio
import mimetypes
import aiofiles
import aiofiles.os
from app.config import get_config

FILE_UPLOAD_CHUNK_SIZE = 1024 * 8  # 8 KB
FILE_COPY_CHUNK_SIZE = 1024 * 8  # 8 KB
FILE_DEFAULT_MIMETYPE = "application/octet-stream"

cfg = get_config()


class FileManager:
    """
    Provides methods for async file operations using aiofiles. It
    includes uploading, unrecoverable deleting, writing and reading
    files, and encrypting or decrypting binary data.
    """

    @staticmethod
    async def file_exists(path: str) -> bool:
        """Check if path exists."""
        return await aiofiles.os.path.isfile(path)

    @staticmethod
    async def mimetype(filename: str):
        """Determines the MIME type of a file based on its filename."""
        mimetype, _ = mimetypes.guess_type(filename)
        if mimetype is None:
            mimetype = FILE_DEFAULT_MIMETYPE
        return mimetype

    @staticmethod
    async def upload(file: object, path: str):
        """Uploads a file to the specified path."""
        async with aiofiles.open(path, mode="wb") as fn:
            while content := await file.read(FILE_UPLOAD_CHUNK_SIZE):
                await fn.write(content)

    @staticmethod
    async def delete(path: str):
        """
        Securely deletes the file by overwriting it a number of times,
        ensuring that the file's contents cannot be recovered.
        """
        if await aiofiles.os.path.isfile(path):
            cmd = ["shred", "-u", "-z", "-n",
                   str(cfg.APP_SHRED_CYCLES), path]
            process = await asyncio.create_subprocess_exec(*cmd)
            await process.wait()

    @staticmethod
    async def write(path: str, data: bytes):
        """Writes a binary data to a file at the specified path."""
        async with aiofiles.open(path, mode="wb") as fn:
            await fn.write(data)

    @staticmethod
    async def read(path: str) -> bytes:
        """Reads the contents of a file at the specified path."""
        async with aiofiles.open(path, mode="rb") as fn:
            return await fn.read()

    @staticmethod
    async def copy(src_path: str, dst_path: str):
        """Copies a file from source to destination path."""
        async with aiofiles.open(src_path, mode="rb") as src_context:
            async with aiofiles.open(dst_path, mode="wb") as dst_context:
                while True:
                    chunk = await src_context.read(FILE_COPY_CHUNK_SIZE)
                    if not chunk:
                        break
                    await dst_context.write(chunk)

    @staticmethod
    async def rename(src_path: str, dst_path: str):
        """Renames the file from source to destination path."""
        await aiofiles.os.rename(src_path, dst_path)
