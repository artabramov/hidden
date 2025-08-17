import unittest
import os
from uuid import UUID
from unittest.mock import AsyncMock, patch, call
from app.managers.file_manager import (
    FILE_READ_CHUNK_SIZE, FILE_COPY_CHUNK_SIZE, FILE_UPLOAD_CHUNK_SIZE,
    KB, MB, FILE_DEFAULT_MIMETYPE, FileManager)
from app.config import get_config

cfg = get_config()


class FileManagerTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.managers.file_manager.aiofiles.os.path.isfile")
    async def test_file_exists_true(self, isfile_mock):
        isfile_mock.return_value = True
        result = await FileManager.file_exists("/path")
        self.assertTrue(result)
        isfile_mock.assert_called_with("/path")

    @patch("app.managers.file_manager.aiofiles.os.path.isfile")
    async def test_file_exists_false(self, isfile_mock):
        isfile_mock.return_value = False
        result = await FileManager.file_exists("/path")
        self.assertFalse(result)
        isfile_mock.assert_called_with("/path")

    @patch("app.managers.file_manager.mimetypes")
    async def test_mimetype_jpeg(self, mimetypes_mock):
        path = "/path"
        mimetype = "image/jpeg"

        mimetypes_mock.guess_type.return_value = mimetype, None
        result = await FileManager.mimetype(path)

        self.assertEqual(result, mimetype)
        mimetypes_mock.guess_type.assert_called_with(path)

    @patch("app.managers.file_manager.mimetypes")
    async def test_mimetype_none(self, mimetypes_mock):
        path = "/path"

        mimetypes_mock.guess_type.return_value = None, None
        result = await FileManager.mimetype(path)

        self.assertEqual(result, FILE_DEFAULT_MIMETYPE)
        mimetypes_mock.guess_type.assert_called_with(path)

    @patch("app.managers.file_manager.aiofiles")
    async def test_upload_success(self, aiofiles_mock):
        file_mock = AsyncMock()
        chunk1, chunk2 = b"data1", b"data2"
        file_mock.read.side_effect = [chunk1, chunk2, None]
        path = "/path"

        result = await FileManager.upload(file_mock, path)
        self.assertIsNone(result)

        aiofiles_mock.open.assert_called_once_with(path, mode="wb")
        self.assertEqual(file_mock.read.call_count, 3)
        self.assertListEqual(file_mock.mock_calls, [
            call.read(FILE_UPLOAD_CHUNK_SIZE),
            call.read(FILE_UPLOAD_CHUNK_SIZE),
            call.read(FILE_UPLOAD_CHUNK_SIZE),
        ])
        self.assertEqual(len(aiofiles_mock.mock_calls), 5)
        self.assertEqual(aiofiles_mock.mock_calls[0],
                         call.open(path, mode="wb"))
        self.assertEqual(aiofiles_mock.mock_calls[1],
                         call.open().__aenter__())
        self.assertEqual(aiofiles_mock.mock_calls[2],
                         call.open().__aenter__().write(chunk1))
        self.assertEqual(aiofiles_mock.mock_calls[3],
                         call.open().__aenter__().write(chunk2))
        self.assertEqual(aiofiles_mock.mock_calls[4],
                         call.open().__aexit__(None, None, None))

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_upload_open_error(self, aiofiles_open_mock):
        file_mock = AsyncMock()
        file_mock.read.side_effect = [b"data1", b"data2", None]
        path = "/path"

        aiofiles_open_mock.side_effect = OSError("Failed to open file")

        with self.assertRaises(OSError):
            await FileManager.upload(file_mock, path)

        aiofiles_open_mock.assert_called_once_with(path, mode="wb")

        self.assertEqual(file_mock.read.call_count, 0)

    @patch("app.managers.file_manager.asyncio.create_subprocess_exec")
    @patch("app.managers.file_manager.aiofiles")
    async def test_delete_file_exists(self, aiofiles_mock,
                                      create_subprocess_exec_mock):
        os_mock = AsyncMock()
        os_mock.path.isfile.return_value = True
        aiofiles_mock.os = os_mock
        path = "/path"

        subprocess_mock = AsyncMock()
        create_subprocess_exec_mock.return_value = subprocess_mock

        result = await FileManager.delete(path)
        self.assertIsNone(result)

        os_mock.path.isfile.assert_called_once_with(path)
        create_subprocess_exec_mock.assert_called_once_with(
            "shred", "-u", "-z", "-n", str(cfg.APP_SHRED_CYCLES), path)
        subprocess_mock.wait.assert_called_once()

    @patch("app.managers.file_manager.asyncio.create_subprocess_exec")
    @patch("app.managers.file_manager.aiofiles")
    async def test_delete_file_not_found(self, aiofiles_mock,
                                         create_subprocess_exec_mock):
        os_mock = AsyncMock()
        os_mock.path.isfile.return_value = False
        aiofiles_mock.os = os_mock
        path = "/path"

        result = await FileManager.delete(path)
        self.assertIsNone(result)

        os_mock.path.isfile.assert_called_once_with(path)
        create_subprocess_exec_mock.assert_not_called()

    @patch("app.managers.file_manager.aiofiles")
    async def test_write_success(self, aiofiles_mock):
        path = "/path"
        data = "data"

        result = await FileManager.write(path, data)
        self.assertIsNone(result)

        aiofiles_mock.open.assert_called_once_with(path, mode="wb")
        self.assertEqual(len(aiofiles_mock.mock_calls), 4)
        self.assertEqual(aiofiles_mock.mock_calls[0],
                         call.open(path, mode="wb"))
        self.assertEqual(aiofiles_mock.mock_calls[1],
                         call.open().__aenter__())
        self.assertEqual(aiofiles_mock.mock_calls[2],
                         call.open().__aenter__().write(data))
        self.assertEqual(aiofiles_mock.mock_calls[3],
                         call.open().__aexit__(None, None, None))

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_write_open_error(self, aiofiles_open_mock):
        data = b"some data"
        path = "/path"

        aiofiles_open_mock.side_effect = OSError("Failed to open file")

        with self.assertRaises(OSError):
            await FileManager.write(path, data)

        aiofiles_open_mock.assert_called_once_with(path, mode="wb")

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_write_write_error(self, aiofiles_open_mock):
        data = b"some data"
        path = "/path"

        mock_file = AsyncMock()
        mock_file.write.side_effect = OSError()

        aiofiles_open_mock.return_value.__aenter__.return_value = mock_file

        with self.assertRaises(OSError):
            await FileManager.write(path, data)

        aiofiles_open_mock.assert_called_once_with(path, mode="wb")
        mock_file.write.assert_called_once_with(data)

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_write_permission_error(self, aiofiles_open_mock):
        data = b"some data"
        path = "/path"

        aiofiles_open_mock.side_effect = PermissionError("Permission denied")

        with self.assertRaises(PermissionError):
            await FileManager.write(path, data)

        aiofiles_open_mock.assert_called_once_with(path, mode="wb")

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_read_success(self, aiofiles_mock):
        path = "/path"
        expected_content = b"File content"

        mock_file = AsyncMock()
        mock_file.read.return_value = expected_content

        aiofiles_mock.return_value.__aenter__.return_value = mock_file

        result = await FileManager.read(path)

        self.assertEqual(result, expected_content)

        aiofiles_mock.assert_called_once_with(path, mode="rb")

        self.assertEqual(aiofiles_mock.mock_calls[0],
                         call(path, mode="rb"))
        self.assertEqual(aiofiles_mock.mock_calls[1],
                         call().__aenter__())
        self.assertEqual(aiofiles_mock.mock_calls[2],
                         call().__aenter__().read())
        self.assertEqual(aiofiles_mock.mock_calls[3],
                         call().__aexit__(None, None, None))

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_read_open_error(self, aiofiles_open_mock):
        path = "/path"

        aiofiles_open_mock.side_effect = OSError()

        with self.assertRaises(OSError):
            await FileManager.read(path)

        aiofiles_open_mock.assert_called_once_with(path, mode="rb")

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_read_read_error(self, aiofiles_open_mock):
        path = "/path"

        mock_file = AsyncMock()
        mock_file.read.side_effect = IOError()

        aiofiles_open_mock.return_value.__aenter__.return_value = mock_file

        with self.assertRaises(IOError):
            await FileManager.read(path)

        aiofiles_open_mock.assert_called_once_with(path, mode="rb")
        mock_file.read.assert_called_once()

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_read_permission_error(self, aiofiles_open_mock):
        path = "/path"

        aiofiles_open_mock.side_effect = PermissionError("Permission denied")

        with self.assertRaises(PermissionError):
            await FileManager.read(path)

        aiofiles_open_mock.assert_called_once_with(path, mode="rb")

    @patch("app.managers.file_manager.aiofiles")
    async def test_copy_success(self, aiofiles_mock):
        src_path = "/src_path"
        dst_path = "/dst_path"

        src_context_mock = AsyncMock()
        chunk1, chunk2 = b"data1", b"data2"
        src_context_mock.__aenter__.return_value.read.side_effect = [
            chunk1, chunk2, None]

        dst_context_mock = AsyncMock()

        aiofiles_mock.open.side_effect = [src_context_mock, dst_context_mock]

        result = await FileManager.copy(src_path, dst_path)
        self.assertIsNone(result)

        self.assertEqual(aiofiles_mock.open.call_count, 2)
        self.assertListEqual(aiofiles_mock.open.call_args_list, [
            call(src_path, mode="rb"), call(dst_path, mode="wb")])
        self.assertListEqual(src_context_mock.mock_calls, [
            call.__aenter__(),
            call.__aenter__().read(FILE_COPY_CHUNK_SIZE),
            call.__aenter__().read(FILE_COPY_CHUNK_SIZE),
            call.__aenter__().read(FILE_COPY_CHUNK_SIZE),
            call.__aexit__(None, None, None)
        ])
        self.assertListEqual(dst_context_mock.mock_calls, [
            call.__aenter__(),
            call.__aenter__().write(chunk1),
            call.__aenter__().write(chunk2),
            call.__aexit__(None, None, None)
        ])

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_copy_open_error_src(self, aiofiles_open_mock):
        src_path = "/src/path"
        dst_path = "/dst/path"

        aiofiles_open_mock.side_effect = OSError()

        with self.assertRaises(OSError):
            await FileManager.copy(src_path, dst_path)

        aiofiles_open_mock.assert_called_once_with(src_path, mode="rb")

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_copy_open_error_dst(self, aiofiles_open_mock):
        src_path = "/src/path"
        dst_path = "/dst/path"

        async_mock_src = AsyncMock()
        async_mock_src.__aenter__.return_value = AsyncMock()

        aiofiles_open_mock.side_effect = [async_mock_src, OSError()]

        with self.assertRaises(OSError):
            await FileManager.copy(src_path, dst_path)

        aiofiles_open_mock.assert_any_call(src_path, mode="rb")
        aiofiles_open_mock.assert_any_call(dst_path, mode="wb")

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_copy_permission_error_dst(self, aiofiles_open_mock):
        src_path = "/src/path"
        dst_path = "/dst/path"

        async_mock_src = AsyncMock()
        async_mock_src.__aenter__.return_value = AsyncMock()

        aiofiles_open_mock.side_effect = [
            async_mock_src, PermissionError("Permission denied")]

        with self.assertRaises(PermissionError):
            await FileManager.copy(src_path, dst_path)

        aiofiles_open_mock.assert_any_call(src_path, mode="rb")
        aiofiles_open_mock.assert_any_call(dst_path, mode="wb")

    @patch("app.managers.file_manager.aiofiles.os")
    async def test_rename_success(self, aiofiles_os_mock):
        rename_mock = AsyncMock()
        aiofiles_os_mock.rename = rename_mock

        src_path = "/path/to/src/file"
        dst_path = "/path/to/dst/file"

        await FileManager.rename(src_path, dst_path)

        rename_mock.assert_awaited_once_with(src_path, dst_path)

    @patch("app.managers.file_manager.aiofiles.os.rename")
    async def test_rename_error(self, rename_mock):
        src_path = "/src/file.txt"
        dst_path = "/dst/file.txt"

        rename_mock.side_effect = OSError()

        with self.assertRaises(OSError):
            await FileManager.rename(src_path, dst_path)

        rename_mock.assert_called_once_with(src_path, dst_path)

    @patch("app.managers.file_manager.aiofiles.os")
    async def test_rename_file_not_found(self, aiofiles_os_mock):
        aiofiles_os_mock.rename = AsyncMock(side_effect=FileNotFoundError)

        src_path = "/non/existent/path"
        dst_path = "/path/to/dst/file"

        with self.assertRaises(FileNotFoundError):
            await FileManager.rename(src_path, dst_path)

    @patch("app.managers.file_manager.aiofiles.os")
    async def test_rename_permission_error(self, aiofiles_os_mock):
        aiofiles_os_mock.rename = AsyncMock(side_effect=PermissionError)

        src_path = "/path/to/src/file"
        dst_path = "/path/to/dst/file"

        with self.assertRaises(PermissionError):
            await FileManager.rename(src_path, dst_path)

    def test_get_shard_size_allocation(self):
        size = FileManager._determine_shard_size(10 * 1024 * 1024)
        self.assertEqual(size, 2 * 1024 * 1024)

    def test_get_shard_size_large_file(self):
        size = FileManager._determine_shard_size(80 * 1024 * 1024)
        self.assertEqual(size, 16 * 1024 * 1024)

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.FileManager.delete")
    @patch("app.managers.file_manager.FileManager._determine_shard_size", return_value=100)  # noqa E501
    async def test__split(self, shard_size_mock, delete_mock,
                          aiofiles_open_mock):
        data_byte = b"A"
        data = data_byte * 300
        base_path = "/path/to/base"

        fn_mock = AsyncMock()
        aiofiles_open_mock.return_value = fn_mock

        results = await FileManager.split(data, base_path)

        self.assertEqual(len(results), 3)
        for filename in results:
            UUID(filename)

        self.assertEqual(aiofiles_open_mock.call_count, 3)
        expected_calls = [
            call(os.path.join(base_path, results[0]), mode="wb"),
            call(os.path.join(base_path, results[1]), mode="wb"),
            call(os.path.join(base_path, results[2]), mode="wb"),
        ]
        self.assertListEqual(aiofiles_open_mock.call_args_list, expected_calls)

        self.assertEqual(fn_mock.__aenter__.return_value.write.call_count, 3)
        fn_mock.__aenter__.return_value.write.assert_has_calls([
            call(data_byte * 100),
            call(data_byte * 100),
            call(data_byte * 100),
        ])

        delete_mock.assert_not_called()

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.FileManager.delete")
    @patch("app.managers.file_manager.FileManager._determine_shard_size", return_value=100)  # noqa E501
    async def test_split_open_error(self, shard_size_mock, delete_mock,
                                    aiofiles_open_mock):
        data_byte = b"A"
        data = data_byte * 300
        base_path = "/path/to/base"

        mock_file = AsyncMock()
        aiofiles_open_mock.side_effect = [mock_file, Exception("open failed")]

        mock_file.__aenter__.return_value.write.return_value = None

        with self.assertRaises(Exception) as ctx:
            await FileManager.split(data, base_path)

        self.assertEqual(str(ctx.exception), "open failed")

        self.assertEqual(delete_mock.call_count, 1)
        called_path = delete_mock.call_args[0][0]
        self.assertTrue(called_path.startswith(base_path + os.sep))

        self.assertEqual(aiofiles_open_mock.call_count, 2)

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.FileManager.delete")
    @patch("app.managers.file_manager.FileManager._determine_shard_size", return_value=100)  # noqa E501
    async def test_split_write_error(self, shard_size_mock, delete_mock,
                                     aiofiles_open_mock):
        data_byte = b"A"
        data = data_byte * 300
        base_path = "/path/to/base"

        fn_mock = AsyncMock()
        fn_mock.write.side_effect = [None, Exception("write failed"), None]
        aiofiles_open_mock.return_value.__aenter__.return_value = fn_mock

        with self.assertRaises(Exception) as ctx:
            await FileManager.split(data, base_path)

        self.assertEqual(str(ctx.exception), "write failed")

        self.assertGreaterEqual(delete_mock.call_count, 1)
        for call_args in delete_mock.call_args_list:
            deleted_path = call_args.args[0]
            self.assertTrue(deleted_path.startswith(base_path + os.sep))

        self.assertGreaterEqual(aiofiles_open_mock.call_count, 2)

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.FileManager.delete")
    @patch("app.managers.file_manager.FileManager._determine_shard_size", return_value=1024)  # noqa E501
    async def test_split_empty_file(self, shard_size_mock, delete_mock, aiofiles_open_mock):  # noqa E501
        data = b""
        base_path = "/some/path"

        results = await FileManager.split(data, base_path)

        assert results == []
        aiofiles_open_mock.assert_not_called()
        delete_mock.assert_not_called()

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.FileManager.delete")
    @patch("app.managers.file_manager.FileManager._determine_shard_size", return_value=0)  # noqa E501
    async def test_split_data_smaller_than_shard(self, shard_size_mock,
                                                 delete_mock,
                                                 aiofiles_open_mock):
        data = b"tiny payload"
        base_path = "/path/to/base"

        fn_mock = AsyncMock()
        aiofiles_open_mock.return_value.__aenter__.return_value = fn_mock

        results = await FileManager.split(data, base_path)

        assert len(results) == 1
        filename = results[0]
        UUID(filename)

        aiofiles_open_mock.assert_called_once_with(
            os.path.join(base_path, filename), mode="wb")
        fn_mock.write.assert_awaited_once_with(data)
        delete_mock.assert_not_called()

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_merge(self, aiofiles_open_mock):
        data_byte = b"A"
        paths = ["/path1", "/path2", "/path3"]

        fn_mock1 = AsyncMock()
        fn_mock1.read.side_effect = [data_byte * 10, b""]

        fn_mock2 = AsyncMock()
        fn_mock2.read.side_effect = [data_byte * 20, b""]

        fn_mock3 = AsyncMock()
        fn_mock3.read.side_effect = [b""]

        aiofiles_open_mock.return_value.__aenter__.side_effect = [
            fn_mock1, fn_mock2, fn_mock3
        ]

        result = await FileManager.merge(paths)
        self.assertEqual(result, data_byte * 30)

        aiofiles_open_mock.assert_any_call(paths[0], mode="rb")
        aiofiles_open_mock.assert_any_call(paths[1], mode="rb")
        aiofiles_open_mock.assert_any_call(paths[2], mode="rb")

        fn_mock1.read.assert_called_with(FILE_READ_CHUNK_SIZE)
        fn_mock2.read.assert_called_with(FILE_READ_CHUNK_SIZE)
        fn_mock3.read.assert_called_with(FILE_READ_CHUNK_SIZE)

        self.assertEqual(fn_mock1.read.call_count, 2)
        self.assertEqual(fn_mock2.read.call_count, 2)
        self.assertEqual(fn_mock3.read.call_count, 1)

        @patch("app.managers.file_manager.aiofiles.open")
        async def test_merge_open_error(self, aiofiles_open_mock):
            paths = ["/path1", "/path2", "/path3"]

            fn_mock1 = AsyncMock()
            fn_mock1.read.side_effect = [b"A" * 100, b""]

            aiofiles_open_mock.return_value.__aenter__.side_effect = [
                fn_mock1, OSError("open failed")
            ]

            with self.assertRaises(OSError):
                await FileManager.merge(paths)

            self.assertEqual(fn_mock1.read.call_count, 2)

    @patch("app.managers.file_manager.aiofiles.open")
    async def test_merge_read_error(self, aiofiles_open_mock):
        paths = ["/path1", "/path2", "/path3"]

        fn_mock1 = AsyncMock()
        fn_mock1.read.side_effect = [b"A" * 100, b""]

        fn_mock2 = AsyncMock()
        fn_mock2.read.side_effect = OSError("read failed")

        aiofiles_open_mock.return_value.__aenter__.side_effect = [
            fn_mock1, fn_mock2
        ]

        with self.assertRaises(OSError):
            await FileManager.merge(paths)

        self.assertEqual(fn_mock1.read.call_count, 2)
        self.assertEqual(fn_mock2.read.call_count, 1)

    def test_determine_shard_size_too_small_file(self):
        self.assertEqual(FileManager._determine_shard_size(512), 0)

    def test_determine_shard_size_exact_1kb_returns_1kb(self):
        self.assertEqual(FileManager._determine_shard_size(1 * KB), 1 * KB)

    def test_determine_shard_size_enough_for_1kb_parts(self):
        self.assertEqual(FileManager._determine_shard_size(4 * KB), 1 * KB)

    def test_determine_shard_size_between_1kb_and_2kb_threshold(self):
        self.assertEqual(FileManager._determine_shard_size(6 * KB), 1 * KB)

    def test_determine_shard_size_enough_for_2kb_parts(self):
        self.assertEqual(FileManager._determine_shard_size(8 * KB), 2 * KB)

    def test_determine_shard_size_between_2kb_and_4kb_threshold(self):
        self.assertEqual(FileManager._determine_shard_size(10 * KB), 2 * KB)

    def test_determine_shard_size_enough_for_4kb_parts(self):
        self.assertEqual(FileManager._determine_shard_size(20 * KB), 4 * KB)

    def test_determine_shard_size_enough_for_16kb_parts(self):
        self.assertEqual(FileManager._determine_shard_size(80 * KB), 16 * KB)

    def test_determine_shard_size_enough_for_512kb_parts(self):
        self.assertEqual(FileManager._determine_shard_size(2 * MB), 512 * KB)

    def test_determine_shard_size_enough_for_4mb_parts(self):
        self.assertEqual(FileManager._determine_shard_size(20 * MB), 4 * MB)

    def test_determine_shard_size_very_large_file(self):
        size = 10 * 1024 * MB
        self.assertEqual(FileManager._determine_shard_size(size), 512 * MB)


if __name__ == "__main__":
    unittest.main()
