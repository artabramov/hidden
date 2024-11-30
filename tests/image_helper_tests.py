import unittest
from unittest.mock import MagicMock, patch
import asynctest
from app.helpers.image_helper import (
    is_image, image_resize, thumbnail_create, _image_resize_sync)
from app.config import get_config

cfg = get_config()


class ImageHelperTestCase(asynctest.TestCase):

    async def setUp(self):
        """Set up the test case environment."""
        pass

    async def tearDown(self):
        """Clean up the test case environment."""
        pass

    def test__is_image_true(self):
        """Test that is_image function correctly identifies image."""
        mimetypes = [
            "image/jpeg", "image/png", "image/gif", "image/bmp",
            "image/tiff", "image/webp", "image/svg+xml", "image/x-icon",
            "image/heif", "image/heic", "image/jp2", "image/avif",
            "image/apng", "image/x-tiff", "image/x-cmu-raster",
            "image/x-portable-anymap", "image/x-portable-bitmap",
            "image/x-portable-graymap", "image/x-portable-pixmap"]

        for mimetype in mimetypes:
            result = is_image(mimetype)
            self.assertTrue(result)

    def test__is_image_false(self):
        """Test that is_image function correctly identifies non-image."""
        mimetypes = [
            "video/mp4", "video/avi", "video/mkv", "video/webm",
            "video/x-msvideo", "video/x-matroska", "video/quicktime"]

        for mimetype in mimetypes:
            result = is_image(mimetype)
            self.assertFalse(result)

    @patch("app.helpers.image_helper.Image.open")
    def test__image_resize_sync(self, mock_open):
        """Test for valid image resizing."""
        mock_image = MagicMock()
        mock_image.thumbnail = MagicMock()
        mock_image.save = MagicMock()
        mock_open.return_value = mock_image

        path = "/path/to/image.jpg"
        width, height, quality = 100, 100, 75

        _image_resize_sync(path, width, height, quality)

        mock_image.thumbnail.assert_called_once_with((width, height))
        mock_image.save.assert_called_once_with(
            path, quality=quality, format="JPEG")

    @patch("app.helpers.image_helper.Image.open")
    def test__image_resize_sync_invalid_format(self, mock_open):
        """Test for invalid image format."""
        mock_open.side_effect = IOError("Invalid image format")

        path = "/path/to/invalid_image.jpg"
        width, height, quality = 100, 100, 75

        with self.assertRaises(IOError):
            _image_resize_sync(path, width, height, quality)

    @patch("app.helpers.image_helper.Image.open")
    def test__image_resize_sync_file_not_found(self, mock_open):
        """Test for file not found error when opening an image."""
        mock_open.side_effect = FileNotFoundError("Image file not found")

        path = "/path/to/nonexistent_image.jpg"
        width, height, quality = 100, 100, 75

        with self.assertRaises(FileNotFoundError):
            _image_resize_sync(path, width, height, quality)

    @patch("app.helpers.image_helper.Image.open")
    def test__image_resize_sync_save_error(self, mock_open):
        """Test for error when saving the resized image."""
        mock_image = MagicMock()
        mock_image.thumbnail = MagicMock()

        mock_image.save.side_effect = PermissionError("Permission denied")
        mock_open.return_value = mock_image

        path = "/path/to/image.jpg"
        width, height, quality = 100, 100, 75

        with self.assertRaises(PermissionError):
            _image_resize_sync(path, width, height, quality)

    @patch("app.helpers.image_helper.Image.open")
    def test__image_resize_sync_corrupted_file(self, mock_open):
        """Test for error when opening a corrupted image file."""
        mock_open.side_effect = Exception("Corrupted image file")

        path = "/path/to/corrupted_image.jpg"
        width, height, quality = 100, 100, 75

        with self.assertRaises(Exception):
            _image_resize_sync(path, width, height, quality)

    @patch("app.helpers.image_helper._image_resize_sync")
    async def test__image_resize_error(self, mock_resize):
        """Test for failure in image resizing."""
        mock_resize.side_effect = Exception()

        path = "/path/to/image.jpg"
        width, height, quality = 100, 100, 75

        with self.assertRaises(Exception):
            await image_resize(path, width, height, quality)

    @patch("app.helpers.image_helper.FileManager")
    async def test__thumbnail_create_copy_error(self, file_manager_mock):
        """Test for file copy failure during thumbnail creation."""
        file_manager_mock.copy.side_effect = OSError()
        path = "/path/to/image.jpg"

        result = await thumbnail_create(path)
        self.assertIsNone(result)

    @patch("app.helpers.image_helper.FileManager")
    @patch("app.helpers.image_helper.image_resize")
    async def test__thumbnail_create_resize_error(self, resize_mock,
                                                  file_manager_mock):
        """Test for image resize failure during thumbnail creation."""
        file_manager_mock.copy.return_value = None
        resize_mock.side_effect = Exception("Image resize failed")
        path = "/path/to/image.jpg"

        result = await thumbnail_create(path)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
