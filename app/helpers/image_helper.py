"""
The module contains utility functions for working with image files,
including support for resizing images and defining supported image
MIME types.
"""

import asyncio
from PIL import Image

IMAGE_FORMAT = "JPEG"
IMAGE_MEDIATYPE = "image/jpeg"
IMAGE_MIMETYPES = [
    "image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff",
    "image/webp", "image/svg+xml", "image/x-icon", "image/x-tiff",
    "image/heic", "image/jp2", "image/avif", "image/apng", "image/heif",
    "image/x-cmu-raster", "image/x-portable-anymap", "image/x-portable-bitmap",
    "image/x-portable-graymap", "image/x-portable-pixmap"]


def _image_resize_sync(path: str, width: int, height: int, quality: int):
    """
    Resizes an image at the specified file path to the given width and
    height using the specified quality, and saves it in JPEG format.
    """
    im = Image.open(path)
    if im.mode in ["P", "RGBA"]:
        im = im.convert("RGB")

    im.thumbnail((width, height))
    im.save(path, quality=quality, format=IMAGE_FORMAT)


async def image_resize(path: str, width: int, height: int, quality: int):
    """
    Asynchronously resizes an image by offloading the resizing task to
    a background thread to avoid blocking the event loop.
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _image_resize_sync, path,
                               width, height, quality)
