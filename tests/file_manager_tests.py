import unittest
from unittest.mock import AsyncMock, patch, call
from app.managers.file_manager import (
    FileManager, FILE_COPY_CHUNK_SIZE, FILE_UPLOAD_CHUNK_SIZE,
    FILE_DEFAULT_MIMETYPE)
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


if __name__ == "__main__":
    unittest.main()
