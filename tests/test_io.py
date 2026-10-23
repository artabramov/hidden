# tests/test_io.py
# SPDX-License-Identifier: Apache-2.0

import os
import unittest
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.io import (
    _fsync_dir,
    _get_parent_dir,
    delete,
    isdir,
    isfile,
    ismount,
    listdir,
    mkdir,
    read,
    rmtree,
    write,
)


def _open_file(payload=b"", fileno=7):
    file = AsyncMock()
    file.fileno = MagicMock(return_value=fileno)
    file.read.return_value = payload
    handle = AsyncMock()
    handle.__aenter__.return_value = file
    handle.__aexit__.return_value = None
    return MagicMock(return_value=handle), file


@contextmanager
def _patch_sync_io():
    with (
        patch("app.io.os.open", return_value=11) as os_open,
        patch("app.io.os.fsync") as fsync,
        patch("app.io.os.close") as close,
        patch("app.io.os.replace") as replace,
        patch("app.io.os.unlink") as unlink,
    ):
        yield os_open, fsync, close, replace, unlink


class TestPathQueries(unittest.IsolatedAsyncioTestCase):
    async def test_listdir_returns_entry_names(self):
        listed = AsyncMock(return_value=("b", "a"))

        with patch("app.io.aiofiles.os.listdir", new=listed):
            result = await listdir("/data")

        listed.assert_awaited_once_with("/data")
        self.assertEqual(result, ["b", "a"])

    async def test_checks_file_directory_and_mount(self):
        cases = (
            (isfile, "app.io.aiofiles.ospath.isfile", True),
            (isdir, "app.io.aiofiles.ospath.isdir", False),
            (ismount, "app.io.aiofiles.ospath.ismount", True),
        )

        for function, target, expected in cases:
            with self.subTest(function=function.__name__):
                check = AsyncMock(return_value=expected)
                with patch(target, new=check):
                    result = await function("/data")

                check.assert_awaited_once_with("/data")
                self.assertIs(result, expected)


class TestRead(unittest.IsolatedAsyncioTestCase):
    async def test_reads_file_bytes(self):
        opener, file = _open_file(b"secret")

        with patch("app.io.aiofiles.open", new=opener):
            result = await read("/secrets/pass")

        opener.assert_called_once_with("/secrets/pass", mode="rb")
        file.read.assert_awaited_once_with()
        self.assertEqual(result, b"secret")


class TestDelete(unittest.IsolatedAsyncioTestCase):
    async def test_deletes_file_and_syncs_parent(self):
        with _patch_sync_io() as (os_open, fsync, close, _replace, unlink):
            await delete("/secrets/pass")

        unlink.assert_called_once_with("/secrets/pass")
        os_open.assert_called_once_with("/secrets", os.O_RDONLY)
        fsync.assert_called_once_with(11)
        close.assert_called_once_with(11)

    async def test_leaves_missing_file_in_place(self):
        with _patch_sync_io() as (os_open, _fsync, _close, _replace, unlink):
            unlink.side_effect = FileNotFoundError
            await delete("/secrets/pass")

        unlink.assert_called_once_with("/secrets/pass")
        os_open.assert_not_called()


class TestMkdir(unittest.IsolatedAsyncioTestCase):
    async def test_creates_directory_and_syncs_parent(self):
        created = AsyncMock()

        with (
            patch("app.io.aiofiles.os.mkdir", new=created),
            _patch_sync_io() as (os_open, fsync, close, _replace, _unlink),
        ):
            await mkdir("/secrets/new")

        created.assert_awaited_once_with("/secrets/new")
        os_open.assert_called_once_with("/secrets", os.O_RDONLY)
        fsync.assert_called_once_with(11)
        close.assert_called_once_with(11)

    async def test_syncs_current_directory_for_a_bare_name(self):
        created = AsyncMock()

        with (
            patch("app.io.aiofiles.os.mkdir", new=created),
            _patch_sync_io() as (os_open, _fsync, _close, _replace, _unlink),
        ):
            await mkdir("new")

        created.assert_awaited_once_with("new")
        os_open.assert_called_once_with(".", os.O_RDONLY)

    async def test_does_not_sync_parent_when_create_fails(self):
        created = AsyncMock(side_effect=OSError("mkdir"))

        with (
            patch("app.io.aiofiles.os.mkdir", new=created),
            _patch_sync_io() as (os_open, _fsync, _close, _replace, _unlink),
        ):
            with self.assertRaises(OSError):
                await mkdir("/secrets/new")

        os_open.assert_not_called()


class TestFsyncDir(unittest.IsolatedAsyncioTestCase):
    async def test_closes_directory_when_fsync_fails(self):
        with _patch_sync_io() as (os_open, fsync, close, _replace, _unlink):
            fsync.side_effect = OSError("fsync")
            with self.assertRaises(OSError):
                await _fsync_dir("/secrets")

        os_open.assert_called_once_with("/secrets", os.O_RDONLY)
        fsync.assert_called_once_with(11)
        close.assert_called_once_with(11)


class TestParentDirectory(unittest.TestCase):
    def test_returns_parent_or_current_directory(self):
        self.assertEqual(_get_parent_dir("/secrets/pass"), "/secrets")
        self.assertEqual(_get_parent_dir("pass"), ".")


class TestRemoveTree(unittest.IsolatedAsyncioTestCase):
    async def test_leaves_missing_directory_in_place(self):
        is_dir = AsyncMock(return_value=False)
        listed = AsyncMock()

        with (
            patch("app.io.aiofiles.ospath.isdir", new=is_dir),
            patch("app.io.aiofiles.os.listdir", new=listed),
            patch("app.io.aiofiles.os.rmdir", new=AsyncMock()) as removed,
        ):
            await rmtree("/data")

        is_dir.assert_awaited_once_with("/data")
        listed.assert_not_awaited()
        removed.assert_not_awaited()

    async def test_removes_nested_files_and_directories(self):
        directories = {"/data", "/data/nested"}

        async def fake_isdir(path):
            return path in directories

        async def fake_listdir(path):
            if path == "/data":
                return ["nested", "file.txt"]
            return []

        removed = AsyncMock()

        with (
            patch(
                "app.io.aiofiles.ospath.isdir",
                new=AsyncMock(side_effect=fake_isdir),
            ),
            patch(
                "app.io.aiofiles.os.listdir",
                new=AsyncMock(side_effect=fake_listdir),
            ),
            patch("app.io.aiofiles.os.rmdir", new=removed),
            _patch_sync_io() as (_open, _fsync, _close, _replace, unlink),
        ):
            await rmtree("/data")

        unlink.assert_called_once_with("/data/file.txt")
        self.assertEqual(
            removed.await_args_list,
            [call("/data/nested"), call("/data")],
        )


class TestWrite(unittest.IsolatedAsyncioTestCase):
    async def test_replaces_destination_and_syncs_parent(self):
        opener, file = _open_file(fileno=7)

        with (
            patch("app.io.aiofiles.open", new=opener),
            _patch_sync_io() as (os_open, fsync, close, replace, unlink),
        ):
            await write("/secrets/pass", memoryview(b"secret"))

        opener.assert_called_once_with(
            "/secrets/.pass.tmp",
            mode="wb",
        )
        file.write.assert_awaited_once_with(b"secret")
        file.flush.assert_awaited_once_with()
        replace.assert_called_once_with(
            "/secrets/.pass.tmp",
            "/secrets/pass",
        )
        fsync.assert_has_calls([call(7), call(11)])
        os_open.assert_called_once_with("/secrets", os.O_RDONLY)
        close.assert_called_once_with(11)
        unlink.assert_not_called()

    async def test_removes_temporary_file_when_replace_fails(self):
        opener, _file = _open_file()

        with (
            patch("app.io.aiofiles.open", new=opener),
            _patch_sync_io() as (os_open, _fsync, _close, replace, unlink),
        ):
            replace.side_effect = OSError("replace")
            with self.assertRaises(OSError) as caught:
                await write("/secrets/pass", b"secret")

        self.assertEqual(str(caught.exception), "replace")
        unlink.assert_called_once_with("/secrets/.pass.tmp")
        os_open.assert_not_called()

    async def test_raises_original_error_when_temporary_file_is_gone(self):
        opener, _file = _open_file()

        with (
            patch("app.io.aiofiles.open", new=opener),
            _patch_sync_io() as (_open, _fsync, _close, replace, unlink),
        ):
            replace.side_effect = OSError("replace")
            unlink.side_effect = FileNotFoundError
            with self.assertRaises(OSError) as caught:
                await write("/secrets/pass", b"secret")

        self.assertEqual(str(caught.exception), "replace")

    async def test_removes_temporary_file_when_write_fails(self):
        opener, file = _open_file()
        file.write.side_effect = OSError("write")

        with (
            patch("app.io.aiofiles.open", new=opener),
            _patch_sync_io() as (os_open, _fsync, _close, replace, unlink),
        ):
            with self.assertRaises(OSError) as caught:
                await write("/secrets/pass", b"secret")

        self.assertEqual(str(caught.exception), "write")
        replace.assert_not_called()
        unlink.assert_called_once_with("/secrets/.pass.tmp")
        os_open.assert_not_called()
