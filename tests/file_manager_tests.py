"""
Unit tests for the FileManager class, covering methods for file
operations such as upload, delete, write, read, encrypt, decrypt, and
copy. The tests verify correct functionality by mocking dependencies
and checking interactions with the filesystem and encryption utilities,
ensuring that each method behaves as expected under different
conditions.
"""

import unittest
import asynctest
from unittest.mock import AsyncMock, patch, call
from app.managers.file_manager import (
    FileManager, FILE_UPLOAD_CHUNK_SIZE, FILE_COPY_CHUNK_SIZE,
    BINARY_EXTENSION)
from app.config import get_config
import os

cfg = get_config()


class FileManagerTestCase(asynctest.TestCase):
    """Test case for FileManager class."""

    async def setUp(self):
        """Set up the test case environment."""
        pass

    async def tearDown(self):
        """Clean up the test case environment."""
        pass

    @patch("app.managers.file_manager.aiofiles")
    async def test__upload(self, aiofiles_mock):
        """Test the upload method to ensure it writes data to a file."""
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
    async def test__upload_open_error(self, aiofiles_open_mock):
        """Test the upload method to ensure it handles open errors."""
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
    async def test__delete_file_exists(self, aiofiles_mock,
                                       create_subprocess_exec_mock):
        """Test the delete method when the file exists."""
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
            "shred", "-u", "-z", "-n", str(cfg.SHRED_OVERWRITE_CYCLES), path)
        subprocess_mock.wait.assert_called_once()

    @patch("app.managers.file_manager.asyncio.create_subprocess_exec")
    @patch("app.managers.file_manager.aiofiles")
    async def test__delete_file_not_exists(self, aiofiles_mock,
                                           create_subprocess_exec_mock):
        """Test the delete method when the file does not exist."""
        os_mock = AsyncMock()
        os_mock.path.isfile.return_value = False
        aiofiles_mock.os = os_mock
        path = "/path"

        result = await FileManager.delete(path)
        self.assertIsNone(result)

        os_mock.path.isfile.assert_called_once_with(path)
        create_subprocess_exec_mock.assert_not_called()

    @patch("app.managers.file_manager.aiofiles")
    async def test__write(self, aiofiles_mock):
        """Test the write method to ensure data is correctly written."""
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
    async def test__write_open_error(self, aiofiles_open_mock):
        """Test the write method to ensure it handles open errors."""
        data = b"some data"
        path = "/path"

        aiofiles_open_mock.side_effect = OSError("Failed to open file")

        with self.assertRaises(OSError):
            await FileManager.write(path, data)

        aiofiles_open_mock.assert_called_once_with(path, mode="wb")

    @patch("app.managers.file_manager.aiofiles.open")
    async def test__write_write_error(self, aiofiles_open_mock):
        """Test the write method to ensure it handles write errors."""
        data = b"some data"
        path = "/path"

        mock_file = AsyncMock()
        mock_file.write.side_effect = OSError()

        aiofiles_open_mock.return_value.__aenter__.return_value = mock_file

        with self.assertRaises(OSError):
            await FileManager.write(path, data)

        aiofiles_open_mock.assert_called_once_with(path, mode="wb")
        mock_file.write.assert_called_once_with(data)

    @patch("app.managers.file_manager.aiofiles")
    async def test__read(self, aiofiles_mock):
        """Test the read method to ensure data is correctly read."""
        path = "/path"

        result = await FileManager.read(path)
        self.assertTrue(isinstance(result, AsyncMock))
        self.assertEqual(len(result.mock_calls), 1)

        aiofiles_mock.open.assert_called_once_with(path, mode="rb")
        self.assertEqual(len(aiofiles_mock.mock_calls), 5)
        self.assertEqual(aiofiles_mock.mock_calls[0],
                         call.open(path, mode="rb"))
        self.assertEqual(aiofiles_mock.mock_calls[1],
                         call.open().__aenter__())
        self.assertEqual(aiofiles_mock.mock_calls[2],
                         call.open().__aenter__().read())
        self.assertEqual(aiofiles_mock.mock_calls[3],
                         call.open().__aexit__(None, None, None))
        self.assertEqual(aiofiles_mock.mock_calls[2],
                         call.open().__aenter__().read())

    # Test scenario: open error
    @patch("app.managers.file_manager.aiofiles.open")
    async def test__read_open_error(self, aiofiles_open_mock):
        """Test the read method to ensure it handles open errors."""
        path = "/path"

        aiofiles_open_mock.side_effect = OSError()

        with self.assertRaises(OSError):
            await FileManager.read(path)

        aiofiles_open_mock.assert_called_once_with(path, mode="rb")

    @patch("app.managers.file_manager.aiofiles.open")
    async def test__read_read_error(self, aiofiles_open_mock):
        """Test the read method to ensure it handles read errors."""
        path = "/path"

        mock_file = AsyncMock()
        mock_file.read.side_effect = IOError()

        aiofiles_open_mock.return_value.__aenter__.return_value = mock_file

        with self.assertRaises(IOError):
            await FileManager.read(path)

        aiofiles_open_mock.assert_called_once_with(path, mode="rb")
        mock_file.read.assert_called_once()

    @patch("app.managers.file_manager.aiofiles")
    async def test__copy(self, aiofiles_mock):
        """Test the copy method to ensure data is copied correctly."""
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
    async def test__copy_open_error_src(self, aiofiles_open_mock):
        """
        Test the copy method to ensure it handles open errors for the
        source file.
        """
        src_path = "/src/path"
        dst_path = "/dst/path"

        aiofiles_open_mock.side_effect = OSError()

        with self.assertRaises(OSError):
            await FileManager.copy(src_path, dst_path)

        aiofiles_open_mock.assert_called_once_with(src_path, mode="rb")

    # Test scenario: Open error (destination file)
    @patch("app.managers.file_manager.aiofiles.open")
    async def test__copy_open_error_dst(self, aiofiles_open_mock):
        """
        Test the copy method to ensure it handles open errors for the
        destination file.
        """
        src_path = "/src/path"
        dst_path = "/dst/path"

        async_mock_src = AsyncMock()
        async_mock_src.__aenter__.return_value = AsyncMock()

        aiofiles_open_mock.side_effect = [async_mock_src, OSError()]

        with self.assertRaises(OSError):
            await FileManager.copy(src_path, dst_path)

        aiofiles_open_mock.assert_any_call(src_path, mode="rb")
        aiofiles_open_mock.assert_any_call(dst_path, mode="wb")

    @patch("app.managers.file_manager.aiofiles.os")
    async def test__rename(self, aiofiles_os_mock):
        """Test the rename method."""
        rename_mock = AsyncMock()
        aiofiles_os_mock.rename = rename_mock

        src_path = "/path/to/src/file"
        dst_path = "/path/to/dst/file"

        await FileManager.rename(src_path, dst_path)

        rename_mock.assert_awaited_once_with(src_path, dst_path)

    @patch("app.managers.file_manager.aiofiles.os.rename")
    async def test__rename_error(self, rename_mock):
        """Test the rename method when a common OSError occurs."""
        src_path = "/src/file.txt"
        dst_path = "/dst/file.txt"

        rename_mock.side_effect = OSError()

        with self.assertRaises(OSError):
            await FileManager.rename(src_path, dst_path)

        rename_mock.assert_called_once_with(src_path, dst_path)

    @patch("app.managers.file_manager.aiofiles.os")
    async def test__rename_file_not_found(self, aiofiles_os_mock):
        """Raises FileNotFoundError when the source file doesn't exist."""
        aiofiles_os_mock.rename = AsyncMock(side_effect=FileNotFoundError)

        src_path = "/non/existent/path"
        dst_path = "/path/to/dst/file"

        with self.assertRaises(FileNotFoundError):
            await FileManager.rename(src_path, dst_path)

    @patch("app.managers.file_manager.aiofiles.os")
    async def test__rename_permission_error(self, aiofiles_os_mock):
        """Raises PermissionError when permission is denied."""
        aiofiles_os_mock.rename = AsyncMock(side_effect=PermissionError)

        src_path = "/path/to/src/file"
        dst_path = "/path/to/dst/file"

        with self.assertRaises(PermissionError):
            await FileManager.rename(src_path, dst_path)

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.FileManager.delete")
    async def test__split(self, delete_mock, aiofiles_open_mock):
        """Test splitting data into smaller part files."""
        data_byte = b"A"
        data = data_byte * 300
        base_path = "/path/to/base"
        part_size = 100

        fn_mock = AsyncMock()
        aiofiles_open_mock.return_value = fn_mock

        results = await FileManager.split(data, base_path, part_size)

        self.assertEqual(len(results), 3)
        for filename in results:
            self.assertTrue(filename.endswith(BINARY_EXTENSION))

        self.assertEqual(aiofiles_open_mock.call_count, 3)
        self.assertListEqual(aiofiles_open_mock.call_args_list, [
            call(os.path.join(base_path, results[0]), mode="wb"),
            call(os.path.join(base_path, results[1]), mode="wb"),
            call(os.path.join(base_path, results[2]), mode="wb"),
        ])

        self.assertEqual(len(fn_mock.mock_calls), 9)
        self.assertListEqual(fn_mock.mock_calls, [
            call.__aenter__(),
            call.__aenter__().write(data_byte * part_size),
            call.__aexit__(None, None, None),
            call.__aenter__(),
            call.__aenter__().write(data_byte * part_size),
            call.__aexit__(None, None, None),
            call.__aenter__(),
            call.__aenter__().write(data_byte * part_size),
            call.__aexit__(None, None, None),
        ])

        delete_mock.assert_not_called()

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.FileManager.delete")
    async def test__split_open_error(self, delete_mock, aiofiles_open_mock):
        data_byte = b"A"
        data = data_byte * 300
        base_path = "/path/to/base"
        part_size = 100

        aiofiles_open_mock.side_effect = Exception()

        with self.assertRaises(Exception):
            await FileManager.split(data, base_path, part_size)

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.FileManager.delete")
    async def test__split_write_error(self, delete_mock, aiofiles_open_mock):
        """
        Test that split deletes partial files if an error occurs during
        writing.
        """
        data_byte = b"A"
        data = data_byte * 300
        base_path = "/path/to/base"
        part_size = 100

        fn_mock = AsyncMock()
        fn_mock.write.side_effect = [None, Exception(), None]
        aiofiles_open_mock.return_value.__aenter__.return_value = fn_mock

        with self.assertRaises(Exception):
            await FileManager.split(data, base_path, part_size)

        delete_mock.assert_called_once()
        self.assertTrue(delete_mock.call_args.args[0].startswith(base_path))
        self.assertTrue(delete_mock.call_args.args[0].endswith(
            BINARY_EXTENSION))

    @patch("app.managers.file_manager.aiofiles.open")
    @patch("app.managers.file_manager.FileManager.delete")
    async def test__split_empty_data(self, delete_mock, aiofiles_open_mock):
        data = b""
        base_path = "/path/to/base"
        part_size = 100

        fn_mock = AsyncMock()
        aiofiles_open_mock.return_value = fn_mock

        results = await FileManager.split(data, base_path, part_size)

        self.assertEqual(results, [])
        aiofiles_open_mock.assert_not_called()
        delete_mock.assert_not_called()

    @patch("app.managers.file_manager.aiofiles.open")
    async def test__merge(self, aiofiles_open_mock):
        data_byte = b"A"
        part_size = 100
        paths = ["/path1", "/path2", "/path3"]

        fn_mock1 = AsyncMock()
        fn_mock1.read.side_effect = [data_byte * part_size, b""]

        fn_mock2 = AsyncMock()
        fn_mock2.read.side_effect = [data_byte * part_size, b""]

        fn_mock3 = AsyncMock()
        fn_mock3.read.side_effect = [b""]

        aiofiles_open_mock.return_value.__aenter__.side_effect = [
            fn_mock1, fn_mock2, fn_mock3]

        result = await FileManager.merge(paths, part_size)
        self.assertEqual(result, data_byte * part_size * 2)

        aiofiles_open_mock.assert_any_call(paths[0], mode="rb")
        aiofiles_open_mock.assert_any_call(paths[1], mode="rb")
        aiofiles_open_mock.assert_any_call(paths[2], mode="rb")

        fn_mock1.read.assert_any_call(part_size)
        fn_mock2.read.assert_any_call(part_size)
        fn_mock3.read.assert_any_call(part_size)

        self.assertEqual(fn_mock1.read.call_count, 2)
        self.assertEqual(fn_mock2.read.call_count, 2)
        self.assertEqual(fn_mock3.read.call_count, 1)

    @patch("app.managers.file_manager.aiofiles.open")
    async def test__merge_open_error(self, aiofiles_open_mock):
        data_byte = b"A"
        part_size = 100
        paths = ["/path1", "/path2", "/path3"]

        fn_mock1 = AsyncMock()
        fn_mock1.read.side_effect = [data_byte * part_size, b""]

        fn_mock2 = AsyncMock()
        fn_mock2.read.side_effect = [data_byte * part_size, b""]

        fn_mock3 = AsyncMock()
        fn_mock3.read.side_effect = [b""]

        aiofiles_open_mock.return_value.__aenter__.side_effect = [
            fn_mock1, OSError(), fn_mock3]

        with self.assertRaises(OSError):
            await FileManager.merge(paths, part_size)

        self.assertEqual(fn_mock1.read.call_count, 2)
        fn_mock1.read.assert_any_call(part_size)

        self.assertEqual(fn_mock2.read.call_count, 0)
        self.assertEqual(fn_mock3.read.call_count, 0)

        aiofiles_open_mock.assert_any_call(paths[0], mode="rb")

    @patch("app.managers.file_manager.aiofiles.open")
    async def test__merge_read_error(self, aiofiles_open_mock):
        data_byte = b"A"
        part_size = 100
        paths = ["/path1", "/path2", "/path3"]

        fn_mock1 = AsyncMock()
        fn_mock1.read.side_effect = [data_byte * part_size, b""]

        fn_mock2 = AsyncMock()
        fn_mock2.read.side_effect = OSError()

        fn_mock3 = AsyncMock()
        fn_mock3.read.side_effect = [b""]

        aiofiles_open_mock.return_value.__aenter__.side_effect = [
            fn_mock1, fn_mock2, fn_mock3
        ]

        with self.assertRaises(OSError):
            await FileManager.merge(paths, part_size)

        self.assertEqual(fn_mock1.read.call_count, 2)
        fn_mock1.read.assert_any_call(part_size)

        self.assertEqual(fn_mock2.read.call_count, 1)
        fn_mock2.read.assert_called_with(part_size)

        self.assertEqual(fn_mock3.read.call_count, 0)

        aiofiles_open_mock.assert_any_call(paths[0], mode="rb")
        aiofiles_open_mock.assert_any_call(paths[1], mode="rb")


if __name__ == "__main__":
    unittest.main()
