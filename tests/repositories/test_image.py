# tests/repositories/test_image.py
# SPDX-License-Identifier: GPL-3.0-only

from io import BytesIO
import unittest
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

from PIL import Image

from app.repositories import image as ri
from app.repositories.image import ImageRotationAngle

from tests.helpers import set_minimal_app_config_env

set_minimal_app_config_env()


def _cfg(max_pixels: int) -> MagicMock:
    cfg = MagicMock()
    cfg.IMAGE_MAX_PIXELS = max_pixels
    return cfg


class TestCheckImageDimensions(unittest.TestCase):

    def test_passes_when_pixel_count_is_within_limit(self):
        image = _image("PNG", size=(10, 10))  # 100 px

        with patch(
            "app.repositories.image.get_config",
            return_value=_cfg(100)
        ):
            ri._check_image_dimensions(image)  # must not raise

    def test_raises_when_pixel_count_exceeds_limit(self):
        image = _image("PNG", size=(11, 11))  # 121 px

        with patch(
            "app.repositories.image.get_config",
            return_value=_cfg(100)
        ):
            with self.assertRaises(ValueError) as cm:
                ri._check_image_dimensions(image)

        self.assertIn("121", str(cm.exception))
        self.assertIn("100", str(cm.exception))

    def test_raises_exactly_at_boundary(self):
        image = _image("PNG", size=(11, 10))  # 110 px > 100

        with patch(
            "app.repositories.image.get_config",
            return_value=_cfg(100)
        ):
            with self.assertRaises(ValueError):
                ri._check_image_dimensions(image)

    def test_passes_exactly_at_limit(self):
        image = _image("PNG", size=(10, 10))  # 100 px == 100

        with patch(
            "app.repositories.image.get_config",
            return_value=_cfg(100)
        ):
            ri._check_image_dimensions(image)  # must not raise

    def test_rotate_sync_raises_on_oversized_image(self):
        image = _image("PNG", size=(11, 11))  # 121 px > 100

        with (
            patch("app.repositories.image.Image.open",
                  return_value=_image_context(image)),
            patch("app.repositories.image.get_config", return_value=_cfg(100)),
            patch("app.repositories.image.ImageOps.exif_transpose") as exif,
        ):
            with self.assertRaises(ValueError):
                ri._rotate_sync("/src/bomb.png", 90)

        exif.assert_not_called()

    def test_flip_sync_raises_on_oversized_image(self):
        image = _image("PNG", size=(11, 11))

        with (
            patch("app.repositories.image.Image.open",
                  return_value=_image_context(image)),
            patch("app.repositories.image.get_config", return_value=_cfg(100)),
            patch("app.repositories.image.ImageOps.exif_transpose") as exif,
        ):
            with self.assertRaises(ValueError):
                ri._flip_sync("/src/bomb.png", "horizontal")

        exif.assert_not_called()

    def test_create_thumbnail_sync_raises_on_oversized_image(self):
        image = _image("PNG", size=(11, 11))

        with (
            patch("app.repositories.image.Image.open",
                  return_value=_image_context(image)),
            patch("app.repositories.image.get_config", return_value=_cfg(100)),
            patch("app.repositories.image.ImageOps.exif_transpose") as exif,
        ):
            with self.assertRaises(ValueError):
                ri._create_thumbnail_sync("/src/bomb.png", (64, 64))

        exif.assert_not_called()

    def test_get_image_size_sync_raises_on_oversized_image(self):
        image = _image("PNG", size=(11, 11))

        with (
            patch("app.repositories.image.Image.open",
                  return_value=_image_context(image)),
            patch("app.repositories.image.get_config", return_value=_cfg(100)),
            patch("app.repositories.image.ImageOps.exif_transpose") as exif,
        ):
            with self.assertRaises(ValueError):
                ri._get_image_size_sync("/src/bomb.png")

        exif.assert_not_called()


class TestImageRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        patcher = patch(
            "app.repositories.image.get_config",
            return_value=_cfg(52428800),
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    async def test_create_thumbnail_writes_generated_bytes(self):
        async def fake_to_thread(fn, /, *args, **kwargs):
            self.assertIs(fn, ri._create_thumbnail_sync)
            self.assertEqual(args, ("/src/image.png", (128, 128)))
            return b"thumbnail"

        with patch(
            "app.repositories.image.asyncio.to_thread",
            side_effect=fake_to_thread,
        ), patch(
            "app.repositories.image.file_repository.write",
            new_callable=AsyncMock,
        ) as write:
            await ri.create_thumbnail(
                "/src/image.png",
                "/dst/thumb.png",
                (128, 128),
            )

        write.assert_awaited_once_with("/dst/thumb.png", b"thumbnail")

    async def test_rotate_writes_generated_bytes(self):
        async def fake_to_thread(fn, /, *args, **kwargs):
            self.assertIs(fn, ri._rotate_sync)
            self.assertEqual(args, ("/src/image.png", 90))
            return b"rotated"

        with patch(
            "app.repositories.image.asyncio.to_thread",
            side_effect=fake_to_thread,
        ), patch(
            "app.repositories.image.file_repository.write",
            new_callable=AsyncMock,
        ) as write:
            await ri.rotate("/src/image.png", "/dst/image.png", 90)

        write.assert_awaited_once_with("/dst/image.png", b"rotated")

    async def test_flip_writes_generated_bytes(self):
        async def fake_to_thread(fn, /, *args, **kwargs):
            self.assertIs(fn, ri._flip_sync)
            self.assertEqual(args, ("/src/image.png", "vertical"))
            return b"flipped"

        with patch(
            "app.repositories.image.asyncio.to_thread",
            side_effect=fake_to_thread,
        ), patch(
            "app.repositories.image.file_repository.write",
            new_callable=AsyncMock,
        ) as write:
            await ri.flip("/src/image.png", "/dst/image.png", "vertical")

        write.assert_awaited_once_with("/dst/image.png", b"flipped")

    def test_create_thumbnail_sync_resizes_without_filesystem_write(self):
        image = _image("PNG", size=(512, 256))

        with patch(
            "app.repositories.image.Image.open",
            return_value=_image_context(image),
        ) as open_image:
            data = ri._create_thumbnail_sync("/src/image.png", (64, 64))

        open_image.assert_called_once_with("/src/image.png")

        result = _load(data)
        self.assertEqual(result.format, "PNG")
        self.assertLessEqual(result.size[0], 64)
        self.assertLessEqual(result.size[1], 64)

    def test_create_thumbnail_sync_raises_when_image_format_unknown(self):
        image = _image(None)

        with patch(
            "app.repositories.image.Image.open",
            return_value=_image_context(image),
        ), patch(
            "app.repositories.image.ImageOps.exif_transpose",
        ) as exif_transpose:
            with self.assertRaises(ValueError) as cm:
                ri._create_thumbnail_sync("/src/unknown.bin", (64, 64))

        self.assertIn("Unsupported image format", str(cm.exception))
        exif_transpose.assert_not_called()

    def test_rotate_sync_90_degrees_clockwise_uses_ROTATE_270(self):
        image = _image("PNG")
        transposed = _image("PNG", size=(20, 10))

        with patch(
            "app.repositories.image.Image.open",
            return_value=_image_context(image),
        ), patch(
            "app.repositories.image.ImageOps.exif_transpose",
            return_value=image,
        ), patch.object(
            image,
            "transpose",
            return_value=transposed,
        ) as transpose:
            ri._rotate_sync("/src/image.png", 90)

        transpose.assert_called_once_with(Image.Transpose.ROTATE_270)

    def test_rotate_sync_180_degrees_uses_ROTATE_180(self):
        image = _image("PNG")
        transposed = _image("PNG", size=(10, 20))

        with patch(
            "app.repositories.image.Image.open",
            return_value=_image_context(image),
        ), patch(
            "app.repositories.image.ImageOps.exif_transpose",
            return_value=image,
        ), patch.object(
            image,
            "transpose",
            return_value=transposed,
        ) as transpose:
            ri._rotate_sync("/src/image.png", 180)

        transpose.assert_called_once_with(Image.Transpose.ROTATE_180)

    def test_rotate_sync_270_degrees_clockwise_uses_ROTATE_90(self):
        image = _image("PNG")
        transposed = _image("PNG", size=(20, 10))

        with patch(
            "app.repositories.image.Image.open",
            return_value=_image_context(image),
        ), patch(
            "app.repositories.image.ImageOps.exif_transpose",
            return_value=image,
        ), patch.object(
            image,
            "transpose",
            return_value=transposed,
        ) as transpose:
            ri._rotate_sync("/src/image.png", 270)

        transpose.assert_called_once_with(Image.Transpose.ROTATE_90)

    def test_rotate_sync_invalid_angle_raises_value_error(self):
        image = _image("PNG")
        transposed = _image("PNG")

        with patch(
            "app.repositories.image.Image.open",
            return_value=_image_context(image),
        ), patch(
            "app.repositories.image.ImageOps.exif_transpose",
            return_value=image,
        ), patch.object(
            image,
            "transpose",
            return_value=transposed,
        ) as transpose:
            with self.assertRaises(ValueError) as cm:
                ri._rotate_sync(
                    "/src/image.png",
                    cast(ImageRotationAngle, 45),
                )

        self.assertIn("Unsupported rotation angle", str(cm.exception))
        transpose.assert_not_called()

    def test_rotate_sync_raises_when_image_format_unknown(self):
        image = _image(None)

        with patch(
            "app.repositories.image.Image.open",
            return_value=_image_context(image),
        ), patch(
            "app.repositories.image.ImageOps.exif_transpose",
        ) as exif_transpose:
            with self.assertRaises(ValueError) as cm:
                ri._rotate_sync("/src/unknown.bin", 90)

        self.assertIn("Unsupported image format", str(cm.exception))
        exif_transpose.assert_not_called()

    def test_flip_sync_horizontal_uses_expected_transpose(self):
        image = _image("PNG")
        transposed = _image("PNG")

        with patch(
            "app.repositories.image.Image.open",
            return_value=_image_context(image),
        ), patch(
            "app.repositories.image.ImageOps.exif_transpose",
            return_value=image,
        ), patch.object(
            image,
            "transpose",
            return_value=transposed,
        ) as transpose:
            ri._flip_sync("/src/image.png", "horizontal")

        transpose.assert_called_once_with(Image.Transpose.FLIP_LEFT_RIGHT)

    def test_flip_sync_vertical_uses_expected_transpose(self):
        image = _image("PNG")
        transposed = _image("PNG")

        with patch(
            "app.repositories.image.Image.open",
            return_value=_image_context(image),
        ), patch(
            "app.repositories.image.ImageOps.exif_transpose",
            return_value=image,
        ), patch.object(
            image,
            "transpose",
            return_value=transposed,
        ) as transpose:
            ri._flip_sync("/src/image.png", "vertical")

        transpose.assert_called_once_with(Image.Transpose.FLIP_TOP_BOTTOM)

    def test_flip_sync_raises_when_image_format_unknown(self):
        image = _image(None)

        with patch(
            "app.repositories.image.Image.open",
            return_value=_image_context(image),
        ), patch(
            "app.repositories.image.ImageOps.exif_transpose",
        ) as exif_transpose:
            with self.assertRaises(ValueError) as cm:
                ri._flip_sync("/src/unknown.bin", "horizontal")

        self.assertIn("Unsupported image format", str(cm.exception))
        exif_transpose.assert_not_called()

    def test_serialize_defaults_to_png_when_format_missing(self):
        data = ri._serialize(_image(None), None)

        result = _load(data)

        self.assertEqual(result.format, "PNG")

    def test_serialize_converts_rgba_to_rgb_for_jpeg(self):
        data = ri._serialize(_image("PNG", mode="RGBA"), "JPEG")

        result = _load(data)

        self.assertEqual(result.format, "JPEG")
        self.assertEqual(result.mode, "RGB")

    def test_normalize_image_mode_returns_original_for_png(self):
        image = _image("PNG", mode="RGBA")

        self.assertIs(ri._normalize_image_mode(image, "PNG"), image)

    def test_normalize_image_mode_converts_palette_for_jpeg(self):
        image = _image("PNG", mode="P")

        result = ri._normalize_image_mode(image, "JPEG")

        self.assertEqual(result.mode, "RGB")

    def test_normalize_image_mode_converts_la_for_jpeg(self):
        image = Image.new("LA", (10, 20), (128, 255))
        image.format = "PNG"

        result = ri._normalize_image_mode(image, "jpeg")

        self.assertEqual(result.mode, "RGB")

    def test_normalize_image_mode_leaves_rgb_unchanged_for_jpeg(self):
        """
        JPEG target but mode already RGB: skip convert (branch 175 -> 178).
        """
        image = _image("JPEG", mode="RGB")

        result = ri._normalize_image_mode(image, "JPEG")

        self.assertIs(result, image)

    async def test_get_image_size_reads_size_in_thread(self):
        async def fake_to_thread(fn, /, *args, **kwargs):
            self.assertIs(fn, ri._get_image_size_sync)
            self.assertEqual(args, ("/src/image.png",))
            return (320, 240)

        with patch(
            "app.repositories.image.asyncio.to_thread",
            side_effect=fake_to_thread,
        ):
            result = await ri.get_image_size("/src/image.png")

        self.assertEqual(result, (320, 240))

    def test_get_image_size_sync_returns_exif_normalized_size(self):
        image = _image("PNG", size=(10, 20))
        normalized = _image("PNG", size=(20, 10))

        with patch(
            "app.repositories.image.Image.open",
            return_value=_image_context(image),
        ) as open_image, patch(
            "app.repositories.image.ImageOps.exif_transpose",
            return_value=normalized,
        ) as exif_transpose:
            result = ri._get_image_size_sync("/src/image.png")

        open_image.assert_called_once_with("/src/image.png")
        exif_transpose.assert_called_once_with(image)
        self.assertEqual(result, (20, 10))


def _image(
    image_format: str | None,
    size: tuple[int, int] = (10, 20),
    mode: str = "RGB",
) -> Image.Image:
    image = Image.new(mode, size)
    image.format = image_format
    return image


def _image_context(image: Image.Image) -> MagicMock:
    context = MagicMock()
    context.__enter__.return_value = image
    context.__exit__.return_value = None
    return context


def _load(data: bytes) -> Image.Image:
    return Image.open(BytesIO(data))
