# tests/runtime/test_cipherdir.py
# SPDX-License-Identifier: Apache-2.0

import asyncio
import unittest
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import InternalServerError
from app.runtime.cipherdir import (
    _PASSFILE_DIR,
    _write_passfile,
    cipherdir_create,
    cipherdir_mount,
    cipherdir_unmount,
    is_cipherdir_created,
)


def _process(returncode=0, stderr=b""):
    process = MagicMock()
    process.returncode = returncode
    process.communicate = AsyncMock(return_value=(b"", stderr))
    process.wait = AsyncMock(return_value=returncode)
    process.stderr.read = AsyncMock(return_value=stderr)
    return process


def _text_file():
    handle = MagicMock()
    handle.fileno.return_value = 9
    opener = MagicMock()
    opener.return_value.__enter__.return_value = handle
    opener.return_value.__exit__.return_value = False
    return opener, handle


class TestIsCipherdirCreated(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_missing_directory(self):
        isdir = AsyncMock(return_value=False)
        isfile = AsyncMock()

        with (
            patch("app.runtime.cipherdir.isdir", new=isdir),
            patch("app.runtime.cipherdir.isfile", new=isfile),
        ):
            created = await is_cipherdir_created("/cipher")

        self.assertIs(created, False)
        isdir.assert_awaited_once_with("/cipher")
        isfile.assert_not_awaited()

    async def test_rejects_missing_config_or_diriv(self):
        cases = (
            ("gocryptfs.conf", False, None),
            ("gocryptfs.diriv", True, False),
        )

        for name, conf_exists, diriv_exists in cases:
            with self.subTest(missing=name):
                isfile = AsyncMock(
                    side_effect=[conf_exists, diriv_exists],
                )
                read = AsyncMock()

                with (
                    patch(
                        "app.runtime.cipherdir.isdir",
                        new=AsyncMock(return_value=True),
                    ),
                    patch("app.runtime.cipherdir.isfile", new=isfile),
                    patch("app.runtime.cipherdir.read", new=read),
                ):
                    created = await is_cipherdir_created("/cipher")

                self.assertIs(created, False)
                read.assert_not_awaited()
                expected = 1 if diriv_exists is None else 2
                self.assertEqual(isfile.await_count, expected)

    async def test_rejects_unreadable_or_empty_config(self):
        cases = (OSError("unread"), b"")

        for content in cases:
            with self.subTest(content=content):
                read = AsyncMock(side_effect=content) if isinstance(
                    content, Exception
                ) else AsyncMock(return_value=content)

                with (
                    patch(
                        "app.runtime.cipherdir.isdir",
                        new=AsyncMock(return_value=True),
                    ),
                    patch(
                        "app.runtime.cipherdir.isfile",
                        new=AsyncMock(return_value=True),
                    ),
                    patch("app.runtime.cipherdir.read", new=read),
                ):
                    created = await is_cipherdir_created("/cipher")

                self.assertIs(created, False)
                read.assert_awaited_once_with("/cipher/gocryptfs.conf")

    async def test_accepts_readable_config(self):
        read = AsyncMock(return_value=b"conf")

        with (
            patch(
                "app.runtime.cipherdir.isdir",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "app.runtime.cipherdir.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile,
            patch("app.runtime.cipherdir.read", new=read),
        ):
            created = await is_cipherdir_created("/cipher")

        self.assertIs(created, True)
        self.assertEqual(
            [item.args[0] for item in isfile.await_args_list],
            ["/cipher/gocryptfs.conf", "/cipher/gocryptfs.diriv"],
        )


class TestCipherdirCommands(unittest.IsolatedAsyncioTestCase):
    @contextmanager
    def _command(self, process, remove_error=None):
        remove = MagicMock()
        if remove_error is not None:
            remove.side_effect = remove_error

        with (
            patch(
                "app.runtime.cipherdir._write_passfile",
                return_value="/dev/shm/pass",
            ) as writer,
            patch(
                "app.runtime.cipherdir.asyncio.create_subprocess_exec",
                new=AsyncMock(return_value=process),
            ) as spawn,
            patch("app.runtime.cipherdir.os.remove", new=remove),
            patch("app.runtime.cipherdir.log") as log,
        ):
            yield writer, spawn, remove, log

    async def test_creates_cipherdir(self):
        process = _process()

        with self._command(process) as (writer, spawn, remove, log):
            await cipherdir_create("passphrase", "/cipher")

        writer.assert_called_once_with("passphrase")
        spawn.assert_awaited_once_with(
            "gocryptfs",
            "-init",
            "-passfile",
            "/dev/shm/pass",
            "/cipher",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        process.communicate.assert_awaited_once_with()
        remove.assert_called_once_with("/dev/shm/pass")
        log.error.assert_not_called()

    async def test_create_failure_reports_stderr(self):
        process = _process(returncode=1, stderr=b"init failed\n")

        with self._command(process) as (_, _, remove, log):
            with self.assertRaises(InternalServerError):
                await cipherdir_create("passphrase", "/cipher")

        log.error.assert_called_once_with(
            "msg=cipherdir_init_failed error=%s",
            "init failed",
        )
        remove.assert_called_once_with("/dev/shm/pass")

    async def test_create_failure_without_stderr_is_unknown(self):
        process = _process(returncode=1, stderr=b" \n")

        with self._command(process) as (_, _, remove, log):
            with self.assertRaises(InternalServerError):
                await cipherdir_create("passphrase", "/cipher")

        log.error.assert_called_once_with(
            "msg=cipherdir_init_failed error=%s",
            "unknown error",
        )
        remove.assert_called_once_with("/dev/shm/pass")

    async def test_create_replaces_invalid_stderr_bytes(self):
        process = _process(returncode=1, stderr=b"bad\xff")

        with self._command(process) as (_, _, _, log):
            with self.assertRaises(InternalServerError):
                await cipherdir_create("passphrase", "/cipher")

        log.error.assert_called_once_with(
            "msg=cipherdir_init_failed error=%s",
            "bad\ufffd",
        )

    async def test_create_removes_passfile_when_process_fails(self):
        process = _process()
        process.communicate.side_effect = OSError("spawn")

        with self._command(process) as (_, _, remove, _):
            with self.assertRaises(OSError):
                await cipherdir_create("passphrase", "/cipher")

        remove.assert_called_once_with("/dev/shm/pass")

    async def test_create_ignores_missing_passfile(self):
        with self._command(
            _process(),
            remove_error=FileNotFoundError,
        ):
            await cipherdir_create("passphrase", "/cipher")

    async def test_create_propagates_passfile_removal_error(self):
        with self._command(_process(), remove_error=OSError("busy")):
            with self.assertRaises(OSError):
                await cipherdir_create("passphrase", "/cipher")

    async def test_mounts_cipherdir(self):
        process = _process()

        with self._command(process) as (writer, spawn, remove, log):
            await cipherdir_mount("passphrase", "/cipher", "/mount")

        writer.assert_called_once_with("passphrase")
        spawn.assert_awaited_once_with(
            "gocryptfs",
            "-passfile",
            "/dev/shm/pass",
            "/cipher",
            "/mount",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        process.wait.assert_awaited_once_with()
        process.stderr.read.assert_not_awaited()
        remove.assert_called_once_with("/dev/shm/pass")
        log.error.assert_not_called()

    async def test_mount_failure_reports_stderr(self):
        process = _process(returncode=2, stderr=b"mount failed\n")

        with self._command(process) as (_, _, remove, log):
            with self.assertRaises(InternalServerError):
                await cipherdir_mount("passphrase", "/cipher", "/mount")

        process.stderr.read.assert_awaited_once_with()
        log.error.assert_called_once_with(
            "msg=cipherdir_mount_failed error=%s",
            "mount failed",
        )
        remove.assert_called_once_with("/dev/shm/pass")

    async def test_mount_failure_without_stderr_is_unknown(self):
        process = _process(returncode=2, stderr=b"")

        with self._command(process) as (_, _, _, log):
            with self.assertRaises(InternalServerError):
                await cipherdir_mount("passphrase", "/cipher", "/mount")

        log.error.assert_called_once_with(
            "msg=cipherdir_mount_failed error=%s",
            "unknown error",
        )

    async def test_mount_removes_passfile_when_wait_fails(self):
        process = _process()
        process.wait.side_effect = OSError("wait")

        with self._command(process) as (_, _, remove, _):
            with self.assertRaises(OSError):
                await cipherdir_mount("passphrase", "/cipher", "/mount")

        remove.assert_called_once_with("/dev/shm/pass")

    async def test_mount_ignores_missing_passfile(self):
        with self._command(
            _process(),
            remove_error=FileNotFoundError,
        ):
            await cipherdir_mount("passphrase", "/cipher", "/mount")

    async def test_unmounts_mountpoint(self):
        process = _process()

        with (
            patch(
                "app.runtime.cipherdir.asyncio.create_subprocess_exec",
                new=AsyncMock(return_value=process),
            ) as spawn,
            patch("app.runtime.cipherdir.log") as log,
        ):
            await cipherdir_unmount("/mount")

        spawn.assert_awaited_once_with(
            "fusermount3",
            "-uz",
            "/mount",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        process.communicate.assert_awaited_once_with()
        log.error.assert_not_called()

    async def test_unmount_failure_reports_stderr(self):
        process = _process(returncode=1, stderr=b"busy\n")

        with (
            patch(
                "app.runtime.cipherdir.asyncio.create_subprocess_exec",
                new=AsyncMock(return_value=process),
            ),
            patch("app.runtime.cipherdir.log") as log,
        ):
            with self.assertRaises(InternalServerError):
                await cipherdir_unmount("/mount")

        log.error.assert_called_once_with(
            "msg=cipherdir_unmount_failed error=%s",
            "busy",
        )

    async def test_unmount_failure_without_stderr_is_unknown(self):
        process = _process(returncode=1, stderr=b"\n")

        with (
            patch(
                "app.runtime.cipherdir.asyncio.create_subprocess_exec",
                new=AsyncMock(return_value=process),
            ),
            patch("app.runtime.cipherdir.log") as log,
        ):
            with self.assertRaises(InternalServerError):
                await cipherdir_unmount("/mount")

        log.error.assert_called_once_with(
            "msg=cipherdir_unmount_failed error=%s",
            "unknown error",
        )


class TestWritePassfile(unittest.TestCase):
    def test_writes_passphrase_line(self):
        opener, handle = _text_file()

        with (
            patch(
                "app.runtime.cipherdir.tempfile.mkstemp",
                return_value=(4, "/dev/shm/pass"),
            ) as mkstemp,
            patch("app.runtime.cipherdir.os.fdopen", new=opener),
            patch("app.runtime.cipherdir.os.fsync") as fsync,
            patch("app.runtime.cipherdir.os.close") as close,
            patch("app.runtime.cipherdir.os.remove") as remove,
        ):
            path = _write_passfile("secret")

        self.assertEqual(path, "/dev/shm/pass")
        mkstemp.assert_called_once_with(dir=_PASSFILE_DIR)
        opener.assert_called_once_with(4, "w", encoding="utf-8")
        handle.write.assert_called_once_with("secret\n")
        handle.flush.assert_called_once_with()
        fsync.assert_called_once_with(9)
        close.assert_not_called()
        remove.assert_not_called()

    def test_removes_passfile_when_write_fails(self):
        opener, handle = _text_file()
        handle.write.side_effect = RuntimeError("write")

        with (
            patch(
                "app.runtime.cipherdir.tempfile.mkstemp",
                return_value=(4, "/dev/shm/pass"),
            ),
            patch("app.runtime.cipherdir.os.fdopen", new=opener),
            patch("app.runtime.cipherdir.os.close") as close,
            patch("app.runtime.cipherdir.os.remove") as remove,
        ):
            with self.assertRaises(RuntimeError):
                _write_passfile("secret")

        close.assert_called_once_with(4)
        remove.assert_called_once_with("/dev/shm/pass")

    def test_reraises_when_cleanup_fails(self):
        opener, handle = _text_file()
        handle.flush.side_effect = RuntimeError("flush")

        with (
            patch(
                "app.runtime.cipherdir.tempfile.mkstemp",
                return_value=(4, "/dev/shm/pass"),
            ),
            patch("app.runtime.cipherdir.os.fdopen", new=opener),
            patch(
                "app.runtime.cipherdir.os.close",
                side_effect=OSError("close"),
            ),
            patch(
                "app.runtime.cipherdir.os.remove",
                side_effect=OSError("remove"),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "flush"):
                _write_passfile("secret")
