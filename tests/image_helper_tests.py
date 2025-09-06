import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from PIL import Image

from app.helpers.image_helper import image_resize, _image_resize_sync


class ImageResizeHelperTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.helpers.image_helper.asyncio.get_running_loop")
    async def test_async_delegates_to_executor_with_args(self, get_loop_mock):
        loop = AsyncMock()
        get_loop_mock.return_value = loop

        path, w, h, q = "any/path.jpg", 100, 120, 85
        await image_resize(path, w, h, q)

        loop.run_in_executor.assert_awaited_once()
        args, kwargs = loop.run_in_executor.await_args
        self.assertEqual(args[0], None)
        self.assertIs(args[1], _image_resize_sync)
        self.assertEqual(args[2:], (path, w, h, q))
        self.assertFalse(kwargs)

    @patch("app.helpers.image_helper.asyncio.get_running_loop")
    async def test_async_validation_rejects_dimensions(self, get_loop_mock):
        loop = AsyncMock()
        get_loop_mock.return_value = loop

        with self.assertRaises(ValueError):
            await image_resize("p", 0, 10, 80)
        with self.assertRaises(ValueError):
            await image_resize("p", -1, 10, 80)
        with self.assertRaises(ValueError):
            await image_resize("p", 10, 0, 80)
        with self.assertRaises(ValueError):
            await image_resize("p", 10, -1, 80)

        loop.run_in_executor.assert_not_awaited()

    @patch("app.helpers.image_helper.asyncio.get_running_loop")
    async def test_async_validation_rejects_quality(self, get_loop_mock):
        loop = AsyncMock()
        get_loop_mock.return_value = loop

        with self.assertRaises(ValueError):
            await image_resize("p", 10, 10, 0)
        with self.assertRaises(ValueError):
            await image_resize("p", 10, 10, 101)

        loop.run_in_executor.assert_not_awaited()

    @patch("app.helpers.image_helper.ImageOps.exif_transpose")
    @patch("app.helpers.image_helper.Image.open")
    def test_sync_cover_branch_crop_height_then_resize_and_save(self, open_mock, exif_mock):
        im = MagicMock()
        im.width, im.height = 100, 200
        im.mode = "RGBA"

        im.convert.return_value = im
        im.crop.return_value = im
        im.resize.return_value = im

        open_cm = MagicMock()
        open_cm.__enter__.return_value = im
        open_mock.return_value = open_cm

        exif_mock.return_value = im

        _image_resize_sync("path", 100, 100, 85)

        open_mock.assert_called_once_with("path")
        exif_mock.assert_called_once_with(im)
        im.convert.assert_called_once_with("RGB")

        im.crop.assert_called_once_with((0, 50, 100, 150))
        im.resize.assert_called_once_with((100, 100), Image.Resampling.LANCZOS)

        im.save.assert_called_once()
        args, kwargs = im.save.call_args
        self.assertEqual(args[0], "path")
        self.assertEqual(kwargs["quality"], 85)
        self.assertEqual(kwargs["format"], "JPEG")
        self.assertTrue(kwargs["optimize"])
        self.assertTrue(kwargs["progressive"])

    @patch("app.helpers.image_helper.ImageOps.exif_transpose")
    @patch("app.helpers.image_helper.Image.open")
    def test_sync_cover_branch_crop_width_then_resize_and_save(self, open_mock, exif_mock):
        """
        target_ratio <= im_ratio -> обрезаем по ширине: crop((off, 0, off+new_w, height))
        """
        im = MagicMock()
        im.width, im.height = 200, 100
        im.mode = "RGB"

        im.crop.return_value = im
        im.resize.return_value = im
        open_cm = MagicMock()
        open_cm.__enter__.return_value = im
        open_mock.return_value = open_cm
        exif_mock.return_value = im

        _image_resize_sync("path", 100, 100, 90)

        im.convert.assert_not_called()
        im.crop.assert_called_once_with((50, 0, 150, 100))
        im.resize.assert_called_once_with((100, 100), Image.Resampling.LANCZOS)

        args, kwargs = im.save.call_args
        self.assertEqual(args[0], "path")
        self.assertEqual(kwargs["quality"], 90)
        self.assertEqual(kwargs["format"], "JPEG")
        self.assertTrue(kwargs["optimize"])
        self.assertTrue(kwargs["progressive"])

    @patch("app.helpers.image_helper.ImageOps.exif_transpose")
    @patch("app.helpers.image_helper.Image.open")
    def test_sync_no_convert_for_L_mode(self, open_mock, exif_mock):
        im = MagicMock()
        im.width, im.height = 120, 80
        im.mode = "L"

        im.crop.return_value = im
        im.resize.return_value = im
        open_cm = MagicMock()
        open_cm.__enter__.return_value = im
        open_mock.return_value = open_cm
        exif_mock.return_value = im

        _image_resize_sync("p", 60, 40, 75)

        im.convert.assert_not_called()
        im.resize.assert_called_once_with((60, 40), Image.Resampling.LANCZOS)
        im.save.assert_called_once()

    @patch("app.helpers.image_helper.Image.open", side_effect=OSError("cannot open"))
    def test_sync_raises_on_open_error(self, open_mock):
        with self.assertRaises(OSError):
            _image_resize_sync("bad/path", 10, 10, 80)
