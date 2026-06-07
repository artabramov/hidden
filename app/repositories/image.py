# app/repositories/image.py
# SPDX-License-Identifier: SSPL-1.0

import asyncio
from io import BytesIO
from typing import Literal

from PIL import Image, ImageOps

from app.constants import FILE_THUMBNAIL_SIZE
from app.repositories import file as file_repository

ImageRotationAngle = Literal[90, 180, 270]
ImageAxis = Literal["horizontal", "vertical"]


async def get_image_size(source: str) -> tuple[int, int]:
    """
    Return the image dimensions after EXIF orientation normalization.
    """
    return await asyncio.to_thread(_get_image_size_sync, source)


async def create_thumbnail(
    source: str,
    destination: str,
    size: tuple[int, int] = FILE_THUMBNAIL_SIZE,
) -> None:
    """
    Create a thumbnail from an existing image. The source file is
    read from disk, resized to fit within "size", and written to
    "destination" using atomic file replacement. The original image
    format is preserved when possible.
    """
    data = await asyncio.to_thread(_create_thumbnail_sync, source, size)
    await file_repository.write(destination, data)


async def rotate(
    source: str,
    destination: str,
    angle: ImageRotationAngle,
) -> None:
    """
    Rotate an image clockwise by the given angle in degrees. EXIF
    orientation is normalized before applying the transform. The result
    is written to "destination" using atomic replacement.
    """
    data = await asyncio.to_thread(_rotate_sync, source, angle)
    await file_repository.write(destination, data)


async def flip(
    source: str,
    destination: str,
    axis: ImageAxis,
) -> None:
    """
    Flip an image along the specified axis: "horizontal" (left ↔ right),
    "vertical" (top ↔ bottom). EXIF orientation is normalized before
    applying the transform. The result is written to "destination"
    using atomic replacement.
    """
    data = await asyncio.to_thread(_flip_sync, source, axis)
    await file_repository.write(destination, data)


def _get_image_size_sync(source: str) -> tuple[int, int]:
    """
    Synchronous image size reader. Opens the image, applies EXIF
    normalization, and returns the resulting width and height.
    """
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        return image.size


def _create_thumbnail_sync(
    source: str,
    size: tuple[int, int],
) -> bytes:
    """
    Synchronous thumbnail creation. Opens the image, applies EXIF
    normalization, resizes it in-place using high-quality resampling,
    and returns encoded bytes.
    """
    with Image.open(source) as image:
        image_format = image.format

        if image_format is None:
            raise ValueError("Unsupported image format")

        image = ImageOps.exif_transpose(image)
        image.thumbnail(size, Image.Resampling.LANCZOS)
        return _serialize(image, image_format)


def _rotate_sync(source: str, angle: ImageRotationAngle) -> bytes:
    with Image.open(source) as image:
        image_format = image.format

        if image_format is None:
            raise ValueError("Unsupported image format")

        image = ImageOps.exif_transpose(image)

        if angle == 90:
            rotated = image.transpose(Image.Transpose.ROTATE_270)

        elif angle == 180:
            rotated = image.transpose(Image.Transpose.ROTATE_180)

        elif angle == 270:
            rotated = image.transpose(Image.Transpose.ROTATE_90)

        else:
            raise ValueError("Unsupported rotation angle")

        output = BytesIO()
        rotated.save(output, format=image_format)
        return output.getvalue()


def _flip_sync(
    source: str,
    axis: ImageAxis,
) -> bytes:
    """
    Synchronous flip implementation. Applies axis-based transpose and
    returns encoded image bytes.
    """
    transpose = {
        "horizontal": Image.Transpose.FLIP_LEFT_RIGHT,
        "vertical": Image.Transpose.FLIP_TOP_BOTTOM,
    }[axis]

    with Image.open(source) as image:
        image_format = image.format

        if image_format is None:
            raise ValueError("Unsupported image format")

        image = ImageOps.exif_transpose(image)
        image = image.transpose(transpose)
        return _serialize(image, image_format)


def _serialize(
    image: Image.Image,
    image_format: str | None,
) -> bytes:
    """
    Encode an image into bytes. Falls back to PNG if the original
    format is missing. Ensures compatibility between image mode and
    output format.
    """
    output = BytesIO()
    normalized_format = image_format or "PNG"
    image = _normalize_image_mode(image, normalized_format)
    image.save(output, format=normalized_format)
    return output.getvalue()


def _normalize_image_mode(
    image: Image.Image,
    image_format: str,
) -> Image.Image:
    """
    Normalize image mode for target format. JPEG does not support alpha
    channels, so images are converted to RGB when necessary. Other
    formats are returned unchanged.
    """
    if image_format.upper() in {"JPEG", "JPG"}:
        if image.mode in {"RGBA", "LA", "P"}:
            return image.convert("RGB")

    return image
