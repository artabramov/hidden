# app/runtime/cipherdir.py
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
import os
import tempfile

from app.errors import InternalServerError
from app.io import isdir, isfile, read

log = logging.getLogger(__name__)

_PASSFILE_DIR = "/dev/shm"


async def is_cipherdir_created(cipherdir: str) -> bool:
    """
    Checks whether the given directory appears to be a valid gocryptfs
    cipherdir by verifying the presence and readability of its config
    and directory IV.
    """
    if not await isdir(cipherdir):
        return False

    conf_path = os.path.join(cipherdir, "gocryptfs.conf")
    if not await isfile(conf_path):
        return False

    diriv_path = os.path.join(cipherdir, "gocryptfs.diriv")
    if not await isfile(diriv_path):
        return False

    try:
        content = await read(conf_path)
    except Exception:
        return False

    return bool(content)


async def cipherdir_create(
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
            error = stderr.decode(
                encoding="utf-8",
                errors="replace",
            ).strip() or "unknown error"

            log.error("msg=cipherdir_init_failed error=%s", error)
            raise InternalServerError

    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


async def cipherdir_mount(
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
            error = stderr.decode(
                encoding="utf-8",
                errors="replace",
            ).strip() or "unknown error"

            log.error("msg=cipherdir_mount_failed error=%s", error)
            raise InternalServerError

    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


async def cipherdir_unmount(mountpoint: str) -> None:
    """
    Unmount a gocryptfs mountpoint using fusermount3. The command is
    provided by fuse3, which is installed in the application image.
    Raises error if the unmount operation fails.
    """
    process = await asyncio.create_subprocess_exec(
        "fusermount3",
        "-uz",
        mountpoint,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()

    if process.returncode != 0:
        error = stderr.decode(
            encoding="utf-8",
            errors="replace",
        ).strip() or "unknown error"

        log.error("msg=cipherdir_unmount_failed error=%s", error)
        raise InternalServerError


def _write_passfile(passphrase: str) -> str:
    """
    Create a temporary passfile in tmpfs and write the passphrase as
    a single line. The file is fsynced and returned by path. It must
    be removed by the caller.
    """
    fd, path = tempfile.mkstemp(dir=_PASSFILE_DIR)
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
