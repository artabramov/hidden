# tests/runtime/test_gocryptfs.py
# SPDX-License-Identifier: GPL-3.0-only

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import InternalServerError
from app.runtime import gocryptfs as gc


class TestIsGocryptfsInitialized(unittest.IsolatedAsyncioTestCase):
    async def test_false_when_not_dir(self):
        with patch(
            "app.runtime.gocryptfs.isdir",
            new_callable=AsyncMock,
            return_value=False,
        ):
            out = await gc.is_gocryptfs_initialized("/c")

        self.assertFalse(out)

    async def test_false_when_conf_missing(self):
        with (
            patch(
                "app.runtime.gocryptfs.isdir",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.gocryptfs.isfile",
                new_callable=AsyncMock,
                return_value=False,
            ),
        ):
            out = await gc.is_gocryptfs_initialized("/c")

        self.assertFalse(out)

    async def test_false_when_read_fails(self):
        with (
            patch(
                "app.runtime.gocryptfs.isdir",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.gocryptfs.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.gocryptfs.read",
                new_callable=AsyncMock,
                side_effect=OSError("x"),
            ),
        ):
            out = await gc.is_gocryptfs_initialized("/c")

        self.assertFalse(out)

    async def test_false_when_content_empty(self):
        with (
            patch(
                "app.runtime.gocryptfs.isdir",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.gocryptfs.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.gocryptfs.read",
                new_callable=AsyncMock,
                return_value=b"",
            ),
        ):
            out = await gc.is_gocryptfs_initialized("/c")

        self.assertFalse(out)

    async def test_true_when_conf_readable(self):
        with (
            patch(
                "app.runtime.gocryptfs.isdir",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.gocryptfs.isfile",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "app.runtime.gocryptfs.read",
                new_callable=AsyncMock,
                return_value=b"{}\n",
            ),
        ):
            out = await gc.is_gocryptfs_initialized("/c")

        self.assertTrue(out)


class TestInitGocryptfs(unittest.IsolatedAsyncioTestCase):
    async def test_success_removes_passfile(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with (
            patch(
                "app.runtime.gocryptfs._write_passfile",
                return_value="/shm/p",
            ),
            patch("app.runtime.gocryptfs.os.remove") as mock_rm,
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
        ):
            await gc.init_gocryptfs("pw", "/cipher")

        mock_rm.assert_called_once_with("/shm/p")

    async def test_failure_raises_and_removes_passfile(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.communicate = AsyncMock(
            return_value=(b"", b"bad init"),
        )

        with (
            patch(
                "app.runtime.gocryptfs._write_passfile",
                return_value="/shm/p",
            ),
            patch("app.runtime.gocryptfs.os.remove") as mock_rm,
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
        ):
            with self.assertRaises(InternalServerError):
                await gc.init_gocryptfs("pw", "/cipher")

        mock_rm.assert_called_once_with("/shm/p")

    async def test_failure_with_empty_stderr_uses_unknown_error(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with (
            patch(
                "app.runtime.gocryptfs._write_passfile",
                return_value="/shm/p",
            ),
            patch("app.runtime.gocryptfs.os.remove") as mock_rm,
            patch("app.runtime.gocryptfs.logger") as mock_logger,
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
        ):
            with self.assertRaises(InternalServerError):
                await gc.init_gocryptfs("pw", "/cipher")

        mock_logger.error.assert_called_once_with(
            "gocryptfs init failed: %s",
            "unknown error",
        )
        mock_rm.assert_called_once_with("/shm/p")

    async def test_success_ignores_missing_passfile_on_cleanup(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with (
            patch(
                "app.runtime.gocryptfs._write_passfile",
                return_value="/shm/p",
            ),
            patch(
                "app.runtime.gocryptfs.os.remove",
                side_effect=FileNotFoundError,
            ) as mock_rm,
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
        ):
            await gc.init_gocryptfs("pw", "/cipher")

        mock_rm.assert_called_once_with("/shm/p")

    async def test_init_invokes_subprocess_with_expected_arguments(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with (
            patch(
                "app.runtime.gocryptfs._write_passfile",
                return_value="/shm/p",
            ),
            patch("app.runtime.gocryptfs.os.remove"),
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ) as mock_exec,
        ):
            await gc.init_gocryptfs("pw", "/cipher")

        mock_exec.assert_awaited_once_with(
            "gocryptfs",
            "-init",
            "-passfile",
            "/shm/p",
            "/cipher",
            stdout=gc.asyncio.subprocess.DEVNULL,
            stderr=gc.asyncio.subprocess.PIPE,
        )


class TestMountGocryptfs(unittest.IsolatedAsyncioTestCase):
    async def test_success_removes_passfile(self):
        mock_stderr = MagicMock()
        mock_stderr.read = AsyncMock(return_value=b"")
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = mock_stderr
        mock_proc.wait = AsyncMock()

        with (
            patch(
                "app.runtime.gocryptfs._write_passfile",
                return_value="/shm/p",
            ),
            patch("app.runtime.gocryptfs.os.remove") as mock_rm,
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
        ):
            await gc.mount_gocryptfs("pw", "/c", "/m")

        mock_rm.assert_called_once_with("/shm/p")

    async def test_failure_raises(self):
        mock_stderr = MagicMock()
        mock_stderr.read = AsyncMock(return_value=b"mount err")
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = mock_stderr
        mock_proc.wait = AsyncMock()

        with (
            patch(
                "app.runtime.gocryptfs._write_passfile",
                return_value="/shm/p",
            ),
            patch("app.runtime.gocryptfs.os.remove"),
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
        ):
            with self.assertRaises(InternalServerError):
                await gc.mount_gocryptfs("pw", "/c", "/m")

    async def test_failure_with_empty_stderr_uses_unknown_error(self):
        mock_stderr = MagicMock()
        mock_stderr.read = AsyncMock(return_value=b"")
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = mock_stderr
        mock_proc.wait = AsyncMock()

        with (
            patch(
                "app.runtime.gocryptfs._write_passfile",
                return_value="/shm/p",
            ),
            patch("app.runtime.gocryptfs.os.remove"),
            patch("app.runtime.gocryptfs.logger") as mock_logger,
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
        ):
            with self.assertRaises(InternalServerError):
                await gc.mount_gocryptfs("pw", "/c", "/m")

        mock_logger.error.assert_called_once_with(
            "gocryptfs mount failed: %s",
            "unknown error",
        )

    async def test_success_ignores_missing_passfile_on_cleanup(self):
        mock_stderr = MagicMock()
        mock_stderr.read = AsyncMock(return_value=b"")
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = mock_stderr
        mock_proc.wait = AsyncMock()

        with (
            patch(
                "app.runtime.gocryptfs._write_passfile",
                return_value="/shm/p",
            ),
            patch(
                "app.runtime.gocryptfs.os.remove",
                side_effect=FileNotFoundError,
            ) as mock_rm,
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
        ):
            await gc.mount_gocryptfs("pw", "/c", "/m")

        mock_rm.assert_called_once_with("/shm/p")

    async def test_mount_invokes_subprocess_with_expected_arguments(self):
        mock_stderr = MagicMock()
        mock_stderr.read = AsyncMock(return_value=b"")
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = mock_stderr
        mock_proc.wait = AsyncMock()

        with (
            patch(
                "app.runtime.gocryptfs._write_passfile",
                return_value="/shm/p",
            ),
            patch("app.runtime.gocryptfs.os.remove"),
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ) as mock_exec,
        ):
            await gc.mount_gocryptfs("pw", "/cipher", "/mount")

        mock_exec.assert_awaited_once_with(
            "gocryptfs",
            "-passfile",
            "/shm/p",
            "/cipher",
            "/mount",
            stdout=gc.asyncio.subprocess.DEVNULL,
            stderr=gc.asyncio.subprocess.PIPE,
        )


class TestUnmountGocryptfs(unittest.IsolatedAsyncioTestCase):
    async def test_success(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with (
            patch(
                "app.runtime.gocryptfs._get_unmount_command",
                return_value="fusermount3",
            ),
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
        ):
            await gc.unmount_gocryptfs("/mnt")

    async def test_failure_raises(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.communicate = AsyncMock(return_value=(b"", b"no"))

        with (
            patch(
                "app.runtime.gocryptfs._get_unmount_command",
                return_value="fusermount3",
            ),
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
        ):
            with self.assertRaises(InternalServerError):
                await gc.unmount_gocryptfs("/mnt")

    async def test_failure_with_empty_stderr_uses_unknown_error(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with (
            patch(
                "app.runtime.gocryptfs._get_unmount_command",
                return_value="fusermount3",
            ),
            patch("app.runtime.gocryptfs.logger") as mock_logger,
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ),
        ):
            with self.assertRaises(InternalServerError):
                await gc.unmount_gocryptfs("/mnt")

        mock_logger.error.assert_called_once_with(
            "gocryptfs unmount failed: %s",
            "unknown error",
        )

    async def test_unmount_invokes_subprocess_with_expected_arguments(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.communicate = AsyncMock(return_value=(b"", b""))

        with (
            patch(
                "app.runtime.gocryptfs._get_unmount_command",
                return_value="/bin/fusermount3",
            ),
            patch(
                "app.runtime.gocryptfs.asyncio.create_subprocess_exec",
                new_callable=AsyncMock,
                return_value=mock_proc,
            ) as mock_exec,
        ):
            await gc.unmount_gocryptfs("/mnt")

        mock_exec.assert_awaited_once_with(
            "/bin/fusermount3",
            "-uz",
            "/mnt",
            stdout=gc.asyncio.subprocess.DEVNULL,
            stderr=gc.asyncio.subprocess.PIPE,
        )


class TestGetUnmountCommand(unittest.TestCase):
    def tearDown(self):
        gc._get_unmount_command.cache_clear()

    def test_returns_first_which(self):
        gc._get_unmount_command.cache_clear()
        with patch(
            "app.runtime.gocryptfs.shutil.which",
            side_effect=["/bin/fusermount3", None],
        ):
            self.assertEqual(gc._get_unmount_command(), "/bin/fusermount3")
        gc._get_unmount_command.cache_clear()

    def test_raises_when_no_unmount_binary(self):
        gc._get_unmount_command.cache_clear()
        with patch("app.runtime.gocryptfs.shutil.which", return_value=None):
            with self.assertRaises(InternalServerError):
                gc._get_unmount_command()
        gc._get_unmount_command.cache_clear()

    def test_returns_fusermount_when_fusermount3_missing(self):
        gc._get_unmount_command.cache_clear()
        with patch(
            "app.runtime.gocryptfs.shutil.which",
            side_effect=[None, "/bin/fusermount"],
        ):
            self.assertEqual(gc._get_unmount_command(), "/bin/fusermount")

    def test_uses_cache(self):
        gc._get_unmount_command.cache_clear()
        with patch(
            "app.runtime.gocryptfs.shutil.which",
            side_effect=["/bin/fusermount3", None],
        ) as mock_which:
            first = gc._get_unmount_command()
            second = gc._get_unmount_command()

        self.assertEqual(first, "/bin/fusermount3")
        self.assertEqual(second, "/bin/fusermount3")
        self.assertEqual(mock_which.call_count, 1)


class TestWritePassfile(unittest.TestCase):
    def test_writes_and_returns_path(self):
        with (
            patch(
                "app.runtime.gocryptfs.tempfile.mkstemp",
                return_value=(3, "/p"),
            ),
            patch("app.runtime.gocryptfs.os.fdopen") as mock_fdopen,
            patch("app.runtime.gocryptfs.os.fsync"),
        ):
            mock_file = MagicMock()
            mock_file.fileno.return_value = 3
            mock_fdopen.return_value.__enter__ = MagicMock(
                return_value=mock_file,
            )
            mock_fdopen.return_value.__exit__ = MagicMock(return_value=None)

            path = gc._write_passfile("secret")

        self.assertEqual(path, "/p")
        mock_file.write.assert_called_once_with("secret\n")
        mock_file.flush.assert_called_once_with()

    def test_flush_and_fsync_are_called(self):
        with (
            patch(
                "app.runtime.gocryptfs.tempfile.mkstemp",
                return_value=(3, "/p"),
            ),
            patch("app.runtime.gocryptfs.os.fdopen") as mock_fdopen,
            patch("app.runtime.gocryptfs.os.fsync") as mock_fsync,
        ):
            mock_file = MagicMock()
            mock_file.fileno.return_value = 3
            mock_fdopen.return_value.__enter__ = MagicMock(
                return_value=mock_file,
            )
            mock_fdopen.return_value.__exit__ = MagicMock(return_value=None)

            path = gc._write_passfile("secret")

        self.assertEqual(path, "/p")
        mock_file.write.assert_called_once_with("secret\n")
        mock_file.flush.assert_called_once_with()
        mock_fsync.assert_called_once_with(3)

    def test_write_passfile_removes_path_and_closes_fd_on_fdopen_failure(self):
        with (
            patch(
                "app.runtime.gocryptfs.tempfile.mkstemp",
                return_value=(7, "/p"),
            ),
            patch(
                "app.runtime.gocryptfs.os.fdopen",
                side_effect=OSError("fdopen failed"),
            ),
            patch("app.runtime.gocryptfs.os.close") as mock_close,
            patch("app.runtime.gocryptfs.os.remove") as mock_remove,
        ):
            with self.assertRaises(OSError):
                gc._write_passfile("secret")

        mock_close.assert_called_once_with(7)
        mock_remove.assert_called_once_with("/p")

    def test_write_passfile_ignores_close_and_remove_errors_in_cleanup(self):
        with (
            patch(
                "app.runtime.gocryptfs.tempfile.mkstemp",
                return_value=(7, "/p"),
            ),
            patch(
                "app.runtime.gocryptfs.os.fdopen",
                side_effect=RuntimeError("boom"),
            ),
            patch(
                "app.runtime.gocryptfs.os.close",
                side_effect=OSError("close failed"),
            ) as mock_close,
            patch(
                "app.runtime.gocryptfs.os.remove",
                side_effect=OSError("remove failed"),
            ) as mock_remove,
        ):
            with self.assertRaises(RuntimeError):
                gc._write_passfile("secret")

        mock_close.assert_called_once_with(7)
        mock_remove.assert_called_once_with("/p")
