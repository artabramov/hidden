"""
The module provides asynchronous methods for various file operations.
These include uploading, deleting, writing, reading, copying, renaming.
It supports efficient I/O operations using aiofiles to handle large
files and avoid blocking the event loop.
"""

import os
import asyncio
import mimetypes
import aiofiles
import aiofiles.os
from app.config import get_config
from typing import List
from uuid import uuid4

KB = 1024
MB = 1024 * 1024
FILE_UPLOAD_CHUNK_SIZE = MB * 1
FILE_COPY_CHUNK_SIZE = MB * 1
FILE_READ_CHUNK_SIZE = MB * 1
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

    @staticmethod
    def _determine_shard_size(file_size: int) -> int:
        """
        Determines the shard size (in bytes) for splitting a file into
        up to 5 parts. The algorithm uses a predefined scale of base sizes:
        1 KB, 2 KB, 4 KB, 8 KB, 16 KB, 32 KB, 64 KB, 128 KB, 256 KB, 512 KB,
        1 MB, 2 MB, 4 MB, 8 MB, 16 MB, 32 MB, 64 MB, 128 MB, 256 MB, 512 MB.

        The function selects the largest base size such that four shards of
        that size fit entirely within the file. The fifth shard (if needed)
        contains the remainder.

        If the file size is smaller than the smallest base size (1 KB),
        the function returns 0, indicating no splitting.
        """
        base_sizes = [
            1 * KB,
            2 * KB,
            4 * KB,
            8 * KB,
            16 * KB,
            32 * KB,
            64 * KB,
            128 * KB,
            256 * KB,
            512 * KB,
            1 * MB,
            2 * MB,
            4 * MB,
            8 * MB,
            16 * MB,
            32 * MB,
            64 * MB,
            128 * MB,
            256 * MB,
            512 * MB
        ]

        if file_size < base_sizes[0]:
            return 0

        best_part_size = base_sizes[0]
        for size in base_sizes:
            if size * 4 <= file_size:
                best_part_size = size
            else:
                break

        return best_part_size

    @staticmethod
    async def split(data: bytes, base_path: str) -> List[str]:
        """
        Splits binary data into shards, writes each shard to a file
        in the base path, and returns a list of generated filenames.
        Returns an empty list if the data is smaller than the minimum
        shard size.
        """
        filenames = []
        start = 0

        data_length = len(data)
        shard_size = FileManager._determine_shard_size(data_length)
        if shard_size == 0:
            filename = str(uuid4())
            path = os.path.join(base_path, filename)
            try:
                async with aiofiles.open(path, mode="wb") as fn:
                    await fn.write(data)
            except Exception:
                await FileManager.delete(path)
                raise
            return [filename]

        parts_count = (data_length + shard_size - 1) // shard_size
        for _ in range(parts_count):
            filename = str(uuid4())
            path = os.path.join(base_path, filename)

            end = min(start + shard_size, data_length)
            chunk = data[start:end]
            start = end

            try:
                async with aiofiles.open(path, mode="wb") as fn:
                    await fn.write(chunk)

            except Exception:
                for fname in filenames:
                    fpath = os.path.join(base_path, fname)
                    await FileManager.delete(fpath)
                raise

            filenames.append(filename)
        return filenames

    @staticmethod
    async def merge(paths: List[str]) -> bytes:
        """
        Merges shard files into a single binary object.
        Reads each file in reasonably small chunks until EOF.
        Chunk size here does not depend on shard size.
        """
        merged_data = bytearray()

        for path in paths:
            async with aiofiles.open(path, mode="rb") as fn:
                while True:
                    chunk = await fn.read(FILE_READ_CHUNK_SIZE)
                    if not chunk:
                        break
                    merged_data.extend(chunk)

        return bytes(merged_data)
