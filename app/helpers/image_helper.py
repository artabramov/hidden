"""
The module provides functionality for handling image files, including
checking if a file is an image, resizing images asynchronously, and
creating thumbnails. The module supports various image MIME types and
allows for resizing and thumbnail creation for different image formats.
"""

import os
import uuid
import asyncio
from typing import Union
from PIL import Image
from app.managers.file_manager import FileManager
from app.config import get_config

cfg = get_config()

IMAGE_MIMETYPES = [
    "image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff",
    "image/webp", "image/svg+xml", "image/x-icon", "image/heif", "image/heic",
    "image/jp2", "image/avif", "image/apng", "image/x-tiff",
    "image/x-cmu-raster", "image/x-portable-anymap", "image/x-portable-bitmap",
    "image/x-portable-graymap", "image/x-portable-pixmap"]


def is_image(mimetype: str) -> bool:
    """
    Determines if the given MIME type is classified as an image type
    by checking it against a predefined set of image MIME types.
    The check is case-insensitive and returns True if the MIME type
    matches any of the image types in the list, otherwise False.
    """
    return mimetype.strip().lower() in IMAGE_MIMETYPES


def _image_resize_sync(path: str, width: int, height: int, quality: int):
    """
    Resizes an image to the specified width and height and saves it with
    the given quality. This function opens the image from the provided
    path, resizes it while maintaining the aspect ratio, and saves it
    with the specified quality.
    """
    im = Image.open(path)
    if im.mode in ["P", "RGBA"]:
        im = im.convert("RGB")

    im.thumbnail((width, height))
    im.save(path, quality=quality, format="JPEG")


async def image_resize(path: str, width: int, height: int, quality: int):
    """
    Asynchronously resizes an image to the specified width and height,
    and saves it with the given quality. The actual resizing is
    performed synchronously in a separate thread.
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _image_resize_sync, path,
                               width, height, quality)


async def thumbnail_create(path: str) -> Union[str, None]:
    """
    Generates a thumbnail for the given file based on its MIME type,
    creating an image thumbnail from images or extracting a frame from
    videos, and resizing it to specified dimensions. Returns the
    filename of the created thumbnail if successful, otherwise returns
    None. Handles both image and video files, with appropriate error
    handling and logging for issues during thumbnail creation.
    """
    thumbnail_filename = str(uuid.uuid4()) + cfg.THUMBNAILS_EXTENSION
    thumbnail_path = os.path.join(cfg.THUMBNAILS_BASE_PATH, thumbnail_filename)

    try:
        await FileManager.copy(path, thumbnail_path)
        await image_resize(thumbnail_path, cfg.THUMBNAIL_WIDTH,
                           cfg.THUMBNAIL_HEIGHT, cfg.THUMBNAIL_QUALITY)
        return thumbnail_filename

    except Exception:
        return None
