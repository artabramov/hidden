import unittest
from unittest.mock import MagicMock, patch
from PIL import Image
from app.helpers.image_helper import (
    image_resize, _image_resize_sync, _create_image, _resize_to_height,
    _crop_center_half, _prepare_area_crop)


class ImageHelperTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.helpers.image_helper.Image.open")
    def test_image_resize_sync_invalid_format(self, mock_open):
        mock_open.side_effect = IOError("Invalid image format")

        with self.assertRaises(IOError):
            _image_resize_sync("/path/to/invalid.jpg", 100, 100, 75)

    @patch("app.helpers.image_helper.Image.open")
    def test_image_resize_sync_file_not_found(self, mock_open):
        mock_open.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError):
            _image_resize_sync("/path/to/missing.jpg", 100, 100, 75)

    @patch("app.helpers.image_helper.Image.open")
    def test_image_resize_sync_save_error(self, mock_open):
        mock_image = MagicMock()
        mock_image.width = 500
        mock_image.height = 500
        mock_image.convert.return_value = mock_image
        mock_image.crop.return_value = mock_image
        mock_image.resize.return_value = mock_image
        mock_image.save.side_effect = PermissionError("Save denied")

        mock_open.return_value = mock_image

        with self.assertRaises(PermissionError):
            _image_resize_sync("/path/to/image.jpg", 100, 100, 80)

    @patch("app.helpers.image_helper.Image.open")
    def test_image_resize_sync_corrupted_file(self, mock_open):
        mock_open.side_effect = Exception("Corrupted image")

        with self.assertRaises(Exception):
            _image_resize_sync("/path/to/corrupted.jpg", 200, 200, 90)

    @patch("app.helpers.image_helper._image_resize_sync")
    async def test_image_resize_async_exception(self, mock_resize):
        mock_resize.side_effect = Exception("Resize failed")

        with self.assertRaises(Exception):
            await image_resize("/path/to/image.jpg", 100, 100, 70)

    @patch("app.helpers.image_helper.Image.open")
    def test_image_resize_sync_horizontal_image(self, mock_open):
        mock_original = MagicMock()
        mock_original.width = 800
        mock_original.height = 400
        mock_original.mode = "RGB"

        mock_cropped = MagicMock()
        mock_cropped.resize.return_value = mock_cropped
        mock_original.crop.return_value = mock_cropped
        mock_open.return_value = mock_original

        path = "/path/to/horizontal.jpg"
        width, height, quality = 300, 300, 85

        _image_resize_sync(path, width, height, quality)

        expected_new_width = int(mock_original.height * (width / height))
        offset = (mock_original.width - expected_new_width) // 2
        expected_crop_box = (offset, 0, offset + expected_new_width,
                             mock_original.height)

        mock_original.crop.assert_called_once_with(expected_crop_box)
        mock_cropped.resize.assert_called_once_with(
            (width, height), Image.LANCZOS)
        mock_cropped.save.assert_called_once_with(
            path, quality=quality, format="JPEG")

    @patch("app.helpers.image_helper.Image.open")
    def test_image_resize_sync_vertical_image(self, mock_open):
        mock_original = MagicMock()
        mock_original.width = 400
        mock_original.height = 800
        mock_original.mode = "RGB"

        mock_cropped = MagicMock()
        mock_cropped.resize.return_value = mock_cropped
        mock_original.crop.return_value = mock_cropped
        mock_open.return_value = mock_original

        path = "/path/to/vertical.jpg"
        width, height, quality = 300, 300, 85

        _image_resize_sync(path, width, height, quality)

        expected_new_height = int(mock_original.width / (width / height))
        offset = (mock_original.height - expected_new_height) // 2
        expected_crop_box = (0, offset, mock_original.width,
                             offset + expected_new_height)

        mock_original.crop.assert_called_once_with(expected_crop_box)
        mock_cropped.resize.assert_called_once_with(
            (width, height), Image.LANCZOS)
        mock_cropped.save.assert_called_once_with(
            path, quality=quality, format="JPEG")

    @patch("app.helpers.image_helper.Image.open")
    def test_create_image_rgba(self, mock_open):
        mock_image = MagicMock()
        mock_image.mode = "RGBA"

        mock_converted_image = MagicMock()
        mock_converted_image.mode = "RGB"

        mock_image.convert.return_value = mock_converted_image
        mock_open.return_value = mock_image

        image_bytes = b"fake image data"
        result_image = _create_image(image_bytes)

        mock_image.convert.assert_called_once_with("RGB")
        self.assertEqual(result_image.mode, "RGB")

    @patch("app.helpers.image_helper.Image.open")
    def test_create_image_p(self, mock_open):
        mock_image = MagicMock()
        mock_image.mode = "P"

        mock_converted_image = MagicMock()
        mock_converted_image.mode = "RGB"

        mock_image.convert.return_value = mock_converted_image
        mock_open.return_value = mock_image

        image_bytes = b"fake image data"
        result_image = _create_image(image_bytes)

        mock_image.convert.assert_called_once_with("RGB")
        self.assertEqual(result_image.mode, "RGB")

    @patch("app.helpers.image_helper.Image.open")
    def test_create_image_rgb(self, mock_open):
        mock_image = MagicMock()
        mock_image.mode = "RGB"
        mock_open.return_value = mock_image

        image_bytes = b"fake image data"
        result_image = _create_image(image_bytes)

        mock_image.convert.assert_not_called()
        self.assertEqual(result_image.mode, "RGB")

    @patch("app.helpers.image_helper.Image.open")
    def test_create_image_invalid(self, mock_open):
        mock_open.side_effect = IOError("Invalid image format")

        image_bytes = b"invalid image data"

        with self.assertRaises(IOError):
            _create_image(image_bytes)

    @patch("PIL.Image.Image.resize")
    def test_resize_to_height_invalid(self, mock_resize):
        mock_image = MagicMock()
        mock_image.size = (400, 0)

        target_height = 300

        with self.assertRaises(ZeroDivisionError):
            _resize_to_height(mock_image, target_height)

    @patch("app.helpers.image_helper.Image.open")
    def test_resize_to_height(self, mock_open):
        mock_image = MagicMock()
        mock_image.size = (400, 200)

        mock_resized_image = MagicMock()
        mock_image.resize.return_value = mock_resized_image

        mock_open.return_value = mock_image

        target_height = 300
        target_width = int(400 * (target_height / 200))

        result_image = _resize_to_height(mock_image, target_height)
        mock_image.resize.assert_called_once_with(
            (target_width, target_height), Image.LANCZOS)

        self.assertIs(result_image, mock_resized_image)

    @patch("app.helpers.image_helper.Image.open")
    def test_resize_to_height_no_change(self, mock_open):
        mock_image = MagicMock()
        mock_image.size = (400, 300)

        mock_resized_image = MagicMock()
        mock_image.resize.return_value = mock_resized_image

        mock_open.return_value = mock_image
        target_height = 300

        result_image = _resize_to_height(mock_image, target_height)

        mock_image.resize.assert_called_once_with(
            (400, target_height), Image.LANCZOS)
        self.assertIs(result_image, mock_resized_image)

    @patch("app.helpers.image_helper.Image.open")
    def test_crop_center_half(self, mock_open):
        mock_image = MagicMock()
        mock_image.size = (400, 200)

        mock_cropped_image = MagicMock()
        mock_image.crop.return_value = mock_cropped_image

        mock_open.return_value = mock_image

        result_image = _crop_center_half(mock_image)

        left = (400 - (400 // 2)) // 2
        mock_image.crop.assert_called_once_with((left, 0, left + 200, 200))

        self.assertIs(result_image, mock_cropped_image)

    @patch("app.helpers.image_helper.Image.open")
    def test_crop_center_half_odd_width(self, mock_open):
        mock_image = MagicMock()
        mock_image.size = (401, 200)

        mock_cropped_image = MagicMock()
        mock_image.crop.return_value = mock_cropped_image

        mock_open.return_value = mock_image

        result_image = _crop_center_half(mock_image)

        left = (401 - (401 // 2)) // 2
        mock_image.crop.assert_called_once_with((left, 0, left + 200, 200))
        self.assertIs(result_image, mock_cropped_image)

    @patch("app.helpers.image_helper.Image.open")
    def test_crop_center_half_no_crop_needed(self, mock_open):
        mock_image = MagicMock()
        mock_image.size = (1, 200)

        mock_cropped_image = MagicMock()
        mock_image.crop.return_value = mock_cropped_image

        mock_open.return_value = mock_image

        result_image = _crop_center_half(mock_image)

        mock_image.crop.assert_not_called()
        self.assertIs(result_image, mock_image)

    @patch("app.helpers.image_helper._create_image")
    def test_prepare_area_crop_small_image(self, mock_create_image):
        mock_image = MagicMock()
        mock_image.size = (50, 50)

        mock_create_image.return_value = mock_image

        target_size = (200, 200)

        mock_resized_image = MagicMock()
        mock_image.resize.return_value = mock_resized_image
        mock_resized_image.size = (200, 200)

        mock_cropped_image = MagicMock()
        mock_resized_image.crop.return_value = mock_cropped_image

        result_image = _prepare_area_crop(b"fake_image_bytes", target_size)

        mock_image.resize.assert_called_once_with((200, 200), Image.LANCZOS)
        mock_resized_image.crop.assert_not_called()
        self.assertIs(result_image, mock_resized_image)

    @patch("app.helpers.image_helper._create_image")
    def test_prepare_area_crop_already_correct_size(self, mock_create_image):
        mock_image = MagicMock()
        mock_image.size = (200, 150)

        mock_create_image.return_value = mock_image

        target_size = (200, 150)

        result_image = _prepare_area_crop(b"fake_image_bytes", target_size)
        mock_image.resize.assert_not_called()
        mock_image.crop.assert_not_called()
        self.assertIs(result_image, mock_image)

    @patch("app.helpers.image_helper._create_image")
    def test_prepare_area_crop_no_resize_needed(self, mock_create_image):
        mock_image = MagicMock()
        mock_image.size = (300, 300)

        mock_create_image.return_value = mock_image

        target_size = (300, 300)

        result_image = _prepare_area_crop(b"fake_image_bytes", target_size)

        mock_image.resize.assert_not_called()
        mock_image.crop.assert_not_called()
        self.assertIs(result_image, mock_image)


if __name__ == "__main__":
    unittest.main()
