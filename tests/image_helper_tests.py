import unittest
from unittest.mock import MagicMock, patch
from app.helpers.image_helper import image_resize, _image_resize_sync
from app.config import get_config

cfg = get_config()


class ImageHelperTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.helpers.image_helper.Image.open")
    def test_image_resize_sync(self, mock_open):
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
    def test_image_resize_sync_invalid_format(self, mock_open):
        mock_open.side_effect = IOError("Invalid image format")

        path = "/path/to/invalid_image.jpg"
        width, height, quality = 100, 100, 75

        with self.assertRaises(IOError):
            _image_resize_sync(path, width, height, quality)

    @patch("app.helpers.image_helper.Image.open")
    def test_image_resize_sync_file_not_found(self, mock_open):
        mock_open.side_effect = FileNotFoundError("Image file not found")

        path = "/path/to/nonexistent_image.jpg"
        width, height, quality = 100, 100, 75

        with self.assertRaises(FileNotFoundError):
            _image_resize_sync(path, width, height, quality)

    @patch("app.helpers.image_helper.Image.open")
    def test_image_resize_sync_save_error(self, mock_open):
        mock_image = MagicMock()
        mock_image.thumbnail = MagicMock()

        mock_image.save.side_effect = PermissionError("Permission denied")
        mock_open.return_value = mock_image

        path = "/path/to/image.jpg"
        width, height, quality = 100, 100, 75

        with self.assertRaises(PermissionError):
            _image_resize_sync(path, width, height, quality)

    @patch("app.helpers.image_helper.Image.open")
    def test_image_resize_sync_corrupted_file(self, mock_open):
        mock_open.side_effect = Exception("Corrupted image file")

        path = "/path/to/corrupted_image.jpg"
        width, height, quality = 100, 100, 75

        with self.assertRaises(Exception):
            _image_resize_sync(path, width, height, quality)

    @patch("app.helpers.image_helper._image_resize_sync")
    async def test_image_resize_error(self, mock_resize):
        mock_resize.side_effect = Exception()

        path = "/path/to/image.jpg"
        width, height, quality = 100, 100, 75

        with self.assertRaises(Exception):
            await image_resize(path, width, height, quality)


if __name__ == "__main__":
    unittest.main()
