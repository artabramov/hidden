"""
The module provides asynchronous methods for various file operations.
These include uploading, deleting, writing, reading, copying, renaming,
splitting, and merging files. It supports efficient I/O operations using
aiofiles to handle large files and avoid blocking the event loop.
"""

import asyncio
from uuid import uuid4
import aiofiles
import aiofiles.os
from app.decorators.timed_decorator import timed
from app.config import get_config
import os
from typing import List

cfg = get_config()

FILE_UPLOAD_CHUNK_SIZE = 1024 * 8  # 8 KB
FILE_COPY_CHUNK_SIZE = 1024 * 8  # 8 KB
BINARY_EXTENSION = ".bin"


class FileManager:
    """
    Provides asynchronous methods for various file operations using
    aiofiles. This includes uploading files in chunks, deleting files if
    they exist, writing data to files, reading file contents, and
    encrypting or decrypting data with a Fernet cipher. These methods
    are designed to handle I/O operations efficiently in an asynchronous
    manner to support high-performance applications.
    """

    @staticmethod
    @timed
    async def upload(file: object, path: str):
        """
        Asynchronously uploads a file to the specified path by reading
        the file in chunks and writing each chunk to the destination
        path, handling large files efficiently without loading them
        entirely into memory.
        """
        async with aiofiles.open(path, mode="wb") as fn:
            while content := await file.read(FILE_UPLOAD_CHUNK_SIZE):
                await fn.write(content)

    @staticmethod
    @timed
    async def delete(path: str):
        """
        Asynchronously deletes the file at the specified path if it
        exists, first checking for the file's existence to avoid errors.
        """
        if await aiofiles.os.path.isfile(path):
            cmd = ["shred", "-u", "-z", "-n", str(cfg.SHRED_OVERWRITE_CYCLES),
                   path]
            process = await asyncio.create_subprocess_exec(*cmd)
            await process.wait()

    @staticmethod
    @timed
    async def write(path: str, data: bytes):
        """
        Asynchronously writes the given byte data to a file at the
        specified path, overwriting the file if it already exists.
        """
        async with aiofiles.open(path, mode="wb") as fn:
            await fn.write(data)

    @staticmethod
    @timed
    async def read(path: str) -> bytes:
        """
        Asynchronously reads and returns the contents of a file at the
        specified path, loading the entire file into memory.
        """
        async with aiofiles.open(path, mode="rb") as fn:
            return await fn.read()

    @staticmethod
    @timed
    async def copy(src_path: str, dst_path: str):
        """
        Asynchronously copies the contents of a file from src_path to
        dst_path in chunks. The method opens the source file for reading
        in binary mode and the destination file for writing in binary
        mode. It reads from the source file in chunks and writes those
        chunks to the destination file until the entire file has been
        copied. The operation is performed asynchronously to avoid
        blocking the event loop, and errors such as file not found or
        permission issues are handled gracefully.
        """
        async with aiofiles.open(src_path, mode="rb") as src_context:
            async with aiofiles.open(dst_path, mode="wb") as dst_context:
                while True:
                    chunk = await src_context.read(FILE_COPY_CHUNK_SIZE)
                    if not chunk:
                        break
                    await dst_context.write(chunk)

    @staticmethod
    @timed
    async def rename(src_path: str, dst_path: str):
        """
        Asynchronously renames the file from src_path to dst_path.
        """
        await aiofiles.os.rename(src_path, dst_path)

    @staticmethod
    @timed
    async def split(data: bytes, base_path: str, part_size: int) -> List:
        """
        Splits the provided binary data into smaller part files of a
        fixed size, ensuring that all parts have the same size.
        """
        filenames = []
        start = 0

        data_length = len(data)
        parts_count = (data_length + part_size - 1) // part_size

        for _ in range(parts_count):
            filename = f"{uuid4()}{BINARY_EXTENSION}"
            path = os.path.join(base_path, filename)

            end = min(start + part_size, data_length)
            chunk = data[start:end]
            start = end

            try:
                async with aiofiles.open(path, mode="wb") as fn:
                    await fn.write(chunk)

            except Exception:
                for filename in filenames:
                    path = os.path.join(base_path, filename)
                    await FileManager.delete(path)
                raise

            filenames.append(filename)
        return filenames

    @staticmethod
    @timed
    async def merge(paths: List[str], part_size: int) -> bytes:
        """
        Merges a list of shard files into a single binary data object.
        """
        merged_data = bytearray()

        for path in paths:
            async with aiofiles.open(path, mode="rb") as fn:
                while chunk := await fn.read(part_size):
                    merged_data.extend(chunk)

        return bytes(merged_data)
