# app/runtime/gocryptfs.py
# SPDX-License-Identifier: GPL-3.0-only

import asyncio
import logging
import os
import shutil
import tempfile
from functools import lru_cache

from app.errors import InternalServerError
from app.repositories.file import isdir, isfile, read

logger = logging.getLogger(__name__)


async def is_gocryptfs_initialized(cipherdir: str) -> bool:
    """
    Checks whether the given directory appears to be a valid gocryptfs
    cipherdir by verifying the presence and readability of its config.
    """
    if not await isdir(cipherdir):
        return False

    conf_path = os.path.join(cipherdir, "gocryptfs.conf")
    if not await isfile(conf_path):
        return False

    try:
        content = await read(conf_path)
    except Exception:
        return False

    return bool(content)


# NOTE (ADR-06): Passphrase is provided via a temporary file in tmpfs.
# Command-line arguments and stdin are avoided to prevent exposure
# in process listings (argv) and to bypass TTY-based input behavior.
# The passphrase is written to a temporary file in tmpfs (/dev/shm)
# and passed using -passfile. The file exists only for the duration
# of the mount operation and is removed immediately after use.

async def init_gocryptfs(
    passphrase: str,
    cipherdir: str
) -> None:
    """
    Initialize a gocryptfs cipher directory using the provided
    passphrase. The passphrase is written to a temporary file in
    tmpfs and passed to gocryptfs with -passfile.
    """
    path = _write_passfile(passphrase)
    try:
        process = await asyncio.create_subprocess_exec(
            "gocryptfs",
            "-init",
            "-passfile",
            path,
            cipherdir,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            message = stderr.decode(
                encoding="utf-8",
                errors="replace",
            ).strip() or "unknown error"

            logger.error("gocryptfs init failed: %s", message)
            raise InternalServerError

    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


async def mount_gocryptfs(
    passphrase: str,
    cipherdir: str,
    mountpoint: str
) -> None:
    """
    Mount a gocryptfs cipher directory to the given mountpoint.
    The passphrase is written to a temporary file in tmpfs and
    passed to gocryptfs with -passfile.
    """
    path = _write_passfile(passphrase)
    try:
        process = await asyncio.create_subprocess_exec(
            "gocryptfs",
            "-passfile",
            path,
            cipherdir,
            mountpoint,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.wait()

        if process.returncode != 0:
            stderr = await process.stderr.read()
            message = stderr.decode(
                encoding="utf-8",
                errors="replace",
            ).strip() or "unknown error"

            logger.error("gocryptfs mount failed: %s", message)
            raise InternalServerError

    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


async def unmount_gocryptfs(mountpoint: str) -> None:
    """
    Unmount a gocryptfs mountpoint using fusermount3 or
    fusermount. Raises error if the unmount operation fails.
    """
    unmount_command = _get_unmount_command()
    process = await asyncio.create_subprocess_exec(
        unmount_command,
        "-uz",
        mountpoint,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()

    if process.returncode != 0:
        message = stderr.decode(
            encoding="utf-8",
            errors="replace",
        ).strip() or "unknown error"

        logger.error("gocryptfs unmount failed: %s", message)
        raise InternalServerError


def _write_passfile(passphrase: str) -> str:
    """
    Create a temporary passfile in tmpfs and write the passphrase as
    a single line. The file is fsynced and returned by path. It must
    be removed by the caller.
    """
    fd, path = tempfile.mkstemp(dir="/dev/shm")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(passphrase + "\n")
            f.flush()
            os.fsync(f.fileno())
        return path
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.remove(path)
        except OSError:
            pass
        raise


@lru_cache
def _get_unmount_command() -> str:
    """
    Resolve the available unmount command for FUSE (fusermount3 or
    fusermount). Returns the executable path or raises error if none
    is found.
    """
    command = shutil.which("fusermount3") or shutil.which("fusermount")
    if command is None:
        logger.error("gocryptfs unmount failed: command not found")
        raise InternalServerError
    return command
