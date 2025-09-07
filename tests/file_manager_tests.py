import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import hashlib
import types
from app.managers.file_manager import FileManager


class _Cfg:
    FILE_DEFAULT_MIMETYPE = "application/octet-stream"
    FILE_CHUNK_SIZE = 4096
    FILE_SHRED_CYCLES = 2


class FileManagerTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.cfg = _Cfg()
        self.fm = FileManager(self.cfg)

    @patch("app.managers.file_manager.mimetypes.guess_type")
    async def test_mimetype_detected(self, guess_type_mock):
        guess_type_mock.return_value = ("image/jpeg", None)
        res = self.fm.mimetype("photo.jpg")
        self.assertEqual(res, "image/jpeg")
        guess_type_mock.assert_called_once_with("photo.jpg")

    @patch("app.managers.file_manager.mimetypes.guess_type")
    async def test_mimetype_fallback(self, guess_type_mock):
        guess_type_mock.return_value = (None, None)
        res = self.fm.mimetype("unknown.blob")
        self.assertEqual(res, self.cfg.FILE_DEFAULT_MIMETYPE)
        guess_type_mock.assert_called_once_with("unknown.blob")

    @patch("app.managers.file_manager.aiofiles.os.stat", new_callable=AsyncMock)
    async def test_filesize_returns_bytes(self, stat_mock):
        st = types.SimpleNamespace(st_size=987654321)
        stat_mock.return_value = st

        size = await self.fm.filesize("/data/file.bin")

        self.assertEqual(size, 987654321)
        stat_mock.assert_awaited_once_with("/data/file.bin")

    @patch("app.managers.file_manager.aiofiles.os.stat", new_callable=AsyncMock)
    async def test_filesize_casts_to_int(self, stat_mock):
        st = types.SimpleNamespace(st_size=123.0)
        stat_mock.return_value = st

        size = await self.fm.filesize("/data/float.bin")

        self.assertEqual(size, 123)
        stat_mock.assert_awaited_once_with("/data/float.bin")

    @patch("app.managers.file_manager.aiofiles.os.stat", new_callable=AsyncMock)
    async def test_filesize_oserror_propagates(self, stat_mock):
        stat_mock.side_effect = OSError("stat failed")

        with self.assertRaises(OSError):
            await self.fm.filesize("/data/missing.bin")

        stat_mock.assert_awaited_once_with("/data/missing.bin")

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_checksum_streams_and_hashes(self, aopen_mock):
        fh = AsyncMock()
        fh.read.side_effect = [b"abc", b"def", b""]
        aopen_mock.return_value.__aenter__.return_value = fh

        expected = hashlib.sha256(b"abcdef").hexdigest()
        res = await self.fm.checksum("/src/file.bin")

        self.assertEqual(res, expected)
        aopen_mock.assert_called_once_with("/src/file.bin", "rb")
        fh.read.assert_has_awaits([
            unittest.mock.call(self.cfg.FILE_CHUNK_SIZE),
            unittest.mock.call(self.cfg.FILE_CHUNK_SIZE),
            unittest.mock.call(self.cfg.FILE_CHUNK_SIZE),
        ])

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_checksum_empty_file(self, aopen_mock):
        fh = AsyncMock()
        fh.read.side_effect = [b""]
        aopen_mock.return_value.__aenter__.return_value = fh

        expected = hashlib.sha256(b"").hexdigest()
        res = await self.fm.checksum("/src/empty.bin")

        self.assertEqual(res, expected)
        aopen_mock.assert_called_once_with("/src/empty.bin", "rb")
        fh.read.assert_awaited_once_with(self.cfg.FILE_CHUNK_SIZE)

    @patch("app.managers.file_manager.aiofiles.open", side_effect=OSError("open failed"))
    async def test_checksum_open_error_propagates(self, aopen_mock):
        with self.assertRaises(OSError):
            await self.fm.checksum("/bad/path.bin")

        aopen_mock.assert_called_once_with("/bad/path.bin", "rb")

    @patch("app.managers.file_manager.aiofiles.os.path.isfile", new_callable=AsyncMock)
    async def test_isfile_true(self, isfile_mock):
        isfile_mock.return_value = True
        self.assertTrue(await self.fm.isfile("/p"))
        isfile_mock.assert_awaited_once_with("/p")

    @patch("app.managers.file_manager.aiofiles.os.path.isfile", new_callable=AsyncMock)
    async def test_isfile_false(self, isfile_mock):
        isfile_mock.return_value = False
        self.assertFalse(await self.fm.isfile("/p"))
        isfile_mock.assert_awaited_once_with("/p")

    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_mkdir_creates_parent(self, makedirs_mock):
        await self.fm.mkdir("/root/dir/file.bin", is_file=True)
        makedirs_mock.assert_awaited_once()
        args, kwargs = makedirs_mock.call_args
        self.assertTrue(str(args[0]).endswith("/root/dir"))
        self.assertTrue(kwargs.get("exist_ok"))

    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_mkdir_empty_parent_noop(self, makedirs_mock):
        await self.fm.mkdir("file.bin", is_file=True)
        makedirs_mock.assert_not_called()

    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_mkdir_creates_leaf_directory(self, makedirs_mock):
        await self.fm.mkdir("/root/dir/leaf", is_file=False)
        makedirs_mock.assert_awaited_once()
        args, kwargs = makedirs_mock.call_args
        self.assertTrue(str(args[0]).endswith("/root/dir/leaf"))
        self.assertTrue(kwargs.get("exist_ok"))

    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_mkdir_trailing_slash_leaf(self, makedirs_mock):
        await self.fm.mkdir("/root/dir/leaf/", is_file=False)
        makedirs_mock.assert_awaited_once()
        args, _ = makedirs_mock.call_args
        self.assertTrue(str(args[0]).endswith("/root/dir/leaf"))

    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_mkdir_root_path_noop(self, makedirs_mock):
        await self.fm.mkdir("/", is_file=False)
        makedirs_mock.assert_not_called()

    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_mkdir_relative_leaf(self, makedirs_mock):
        await self.fm.mkdir("a/b/c", is_file=False)
        makedirs_mock.assert_awaited_once()
        args, _ = makedirs_mock.call_args
        self.assertEqual(str(args[0]), "a/b/c")

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.aiofiles.os.replace", new_callable=AsyncMock)
    async def test_atomic_write_writes_and_replaces(self, replace_mock, aopen_mock):
        written = []

        fh = AsyncMock()
        async def _write(chunk):
            written.append(chunk)
        fh.write.side_effect = _write
        fh.flush = AsyncMock()

        aopen_mock.return_value.__aenter__.return_value = fh

        async def chunk_iter():
            yield b"A"
            yield b"B"

        await self.fm._atomic_write("/x/file.bin", chunk_iter())

        aopen_mock.assert_called_once()
        tmp_path = aopen_mock.call_args.args[0]
        mode_arg = aopen_mock.call_args.args[1]
        self.assertTrue(tmp_path.endswith(".part"))
        self.assertEqual(mode_arg, "wb")

        self.assertEqual(written, [b"A", b"B"])
        fh.flush.assert_awaited_once()
        replace_mock.assert_awaited_once()
        self.assertEqual(replace_mock.call_args.args[0], tmp_path)
        self.assertEqual(replace_mock.call_args.args[1], "/x/file.bin")

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.aiofiles.os.replace", new_callable=AsyncMock)
    async def test_atomic_write_write_error_no_replace(self, replace_mock, aopen_mock):
        fh = AsyncMock()
        fh.write.side_effect = OSError("write failed")
        fh.flush = AsyncMock()
        aopen_mock.return_value.__aenter__.return_value = fh

        async def chunk_iter():
            yield b"A"
            yield b"B"

        with self.assertRaises(OSError):
            await self.fm._atomic_write("/x/file.bin", chunk_iter())

        replace_mock.assert_not_called()
        fh.flush.assert_not_awaited()

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.aiofiles.os.replace", new_callable=AsyncMock)
    async def test_atomic_write_flush_error_no_replace(self, replace_mock, aopen_mock):
        fh = AsyncMock()
        fh.write = AsyncMock()
        fh.flush.side_effect = OSError("flush failed")
        aopen_mock.return_value.__aenter__.return_value = fh

        async def chunk_iter():
            yield b"A"
            yield b"B"

        with self.assertRaises(OSError):
            await self.fm._atomic_write("/x/file.bin", chunk_iter())

        replace_mock.assert_not_called()
        self.assertEqual(fh.write.await_count, 2)

    @patch.object(FileManager, "_atomic_write", new_callable=AsyncMock)
    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_upload_streams_in_chunks(self, makedirs_mock, atomic_write_mock):
        file_mock = AsyncMock()
        file_mock.read.side_effect = [b"111", b"22", b""]

        captured = []

        async def _consume(path, chunk_iter):
            async for c in chunk_iter:
                captured.append(c)
        atomic_write_mock.side_effect = _consume

        await self.fm.upload(file_mock, "/dst/out.bin")

        makedirs_mock.assert_awaited_once()
        atomic_write_mock.assert_awaited()
        self.assertEqual(captured, [b"111", b"22"])
        file_mock.read.assert_has_awaits([
            unittest.mock.call(self.cfg.FILE_CHUNK_SIZE),
            unittest.mock.call(self.cfg.FILE_CHUNK_SIZE),
            unittest.mock.call(self.cfg.FILE_CHUNK_SIZE),
        ])

    @patch.object(FileManager, "_atomic_write", new_callable=AsyncMock)
    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_upload_empty_stream(self, makedirs_mock, atomic_write_mock):
        file_mock = AsyncMock()
        file_mock.read.side_effect = [b""]

        captured = []

        async def _consume(path, chunk_iter):
            async for c in chunk_iter:
                captured.append(c)
        atomic_write_mock.side_effect = _consume

        await self.fm.upload(file_mock, "/dst/empty.bin")

        makedirs_mock.assert_awaited_once()
        atomic_write_mock.assert_awaited_once()
        self.assertEqual(captured, [])
        file_mock.read.assert_awaited_once_with(self.cfg.FILE_CHUNK_SIZE)

    @patch.object(FileManager, "isfile", new_callable=AsyncMock)
    @patch("app.managers.file_manager.asyncio.create_subprocess_exec")
    async def test_delete_existing_runs_shred(self, create_proc_mock, isfile_mock):
        isfile_mock.return_value = True
        proc = AsyncMock()
        create_proc_mock.return_value = proc

        await self.fm.delete("/data/file.bin")

        isfile_mock.assert_awaited_once_with("/data/file.bin")
        create_proc_mock.assert_called_once()
        args = create_proc_mock.call_args[0]
        self.assertEqual(args[0], "shred")
        self.assertIn("-u", args)
        self.assertIn("-z", args)
        self.assertIn("-n", args)
        self.assertIn(str(self.cfg.FILE_SHRED_CYCLES), args)
        self.assertIn("/data/file.bin", args)
        proc.wait.assert_awaited_once()

    @patch.object(FileManager, "isfile", new_callable=AsyncMock)
    @patch("app.managers.file_manager.asyncio.create_subprocess_exec")
    async def test_delete_missing_noop(self, create_proc_mock, isfile_mock):
        isfile_mock.return_value = False
        await self.fm.delete("/data/miss.bin")
        isfile_mock.assert_awaited_once_with("/data/miss.bin")
        create_proc_mock.assert_not_called()

    @patch.object(FileManager, "_atomic_write", new_callable=AsyncMock)
    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_write_uses_atomic(self, makedirs_mock, atomic_write_mock):
        captured = []

        async def _consume(path, chunk_iter):
            async for c in chunk_iter:
                captured.append(c)

        atomic_write_mock.side_effect = _consume

        data = b"payload"
        await self.fm.write("/dst/file.bin", data)

        makedirs_mock.assert_awaited_once()
        atomic_write_mock.assert_awaited_once()
        self.assertEqual(captured, [data])

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_read_success(self, aopen_mock):
        fh = AsyncMock()
        fh.read.return_value = b"OK"
        aopen_mock.return_value.__aenter__.return_value = fh

        res = await self.fm.read("/src/file.bin")
        self.assertEqual(res, b"OK")
        aopen_mock.assert_called_once_with("/src/file.bin", mode="rb")
        fh.read.assert_awaited_once()

    @patch.object(FileManager, "_atomic_write", new_callable=AsyncMock)
    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_copy_streams_and_atomic(self, makedirs_mock, aopen_mock, atomic_write_mock):
        src_fh = AsyncMock()
        src_fh.read.side_effect = [b"A"*3, b"B", b""]
        aopen_mock.return_value.__aenter__.return_value = src_fh

        captured = []

        async def _consume(dst, chunk_iter):
            async for c in chunk_iter:
                captured.append(c)

        atomic_write_mock.side_effect = _consume

        await self.fm.copy("/src/in.bin", "/dst/out.bin")

        makedirs_mock.assert_awaited_once()
        aopen_mock.assert_called_once_with("/src/in.bin", "rb")
        src_fh.read.assert_has_awaits([
            unittest.mock.call(self.cfg.FILE_CHUNK_SIZE),
            unittest.mock.call(self.cfg.FILE_CHUNK_SIZE),
            unittest.mock.call(self.cfg.FILE_CHUNK_SIZE),
        ])
        self.assertEqual(captured, [b"A"*3, b"B"])

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_copy_src_open_error_propagates(self, makedirs_mock, aopen_mock):
        ok_ctx = AsyncMock()
        ok_ctx.__aenter__.return_value = AsyncMock()

        def open_side_effect(path, mode):
            if path == "/src/miss.bin" and mode == "rb":
                raise OSError("open src failed")
            return ok_ctx

        aopen_mock.side_effect = open_side_effect

        with self.assertRaises(OSError) as ctx:
            await self.fm.copy("/src/miss.bin", "/dst/out.bin")

        self.assertEqual(str(ctx.exception), "open src failed")

        makedirs_mock.assert_awaited_once()

        aopen_mock.assert_any_call("/src/miss.bin", "rb")
        modes = [call.args[1] for call in aopen_mock.call_args_list]
        self.assertIn("wb", modes)


    @patch("app.managers.file_manager.aiofiles.os.replace", new_callable=AsyncMock)
    @patch("app.managers.file_manager.aiofiles.os.makedirs", new_callable=AsyncMock)
    async def test_rename_calls_replace(self, makedirs_mock, replace_mock):
        await self.fm.rename("/src/a.bin", "/dst/b.bin")
        makedirs_mock.assert_awaited_once()
        replace_mock.assert_awaited_once_with("/src/a.bin", "/dst/b.bin")
