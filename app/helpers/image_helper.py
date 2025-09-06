"""Helper for image operations."""

import asyncio
from PIL import Image, ImageOps

IMAGE_FORMAT = "JPEG"
IMAGE_MEDIATYPE = "image/jpeg"
IMAGE_EXTENSION = ".jpeg"

async def image_resize(path: str, width: int, height: int, quality: int):
    """
    Asynchronously runs the sync resizer in a worker thread: applies
    EXIF orientation, center-crops to the target aspect ratio, resizes
    with Lanczos, and overwrites the file as a progressive JPEG.
    """
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive")

    elif not 1 <= quality <= 100:
        raise ValueError("Quality must be in 1..100")

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, _image_resize_sync, path, width, height, quality)


def _image_resize_sync(path: str, width: int, height: int, quality: int):
    """
    Opens the image, fixes EXIF orientation, converts to RGB if needed,
    center-crops, resizes with Lanczos, and saves over the original as
    an optimized progressive JPEG.
    """
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im)

        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")

        im_ratio = im.width / im.height
        target_ratio = width / height

        if target_ratio > im_ratio:
            new_height = int(im.width / target_ratio)
            offset = (im.height - new_height) // 2
            im = im.crop((0, offset, im.width, offset + new_height))
        else:
            new_width = int(im.height * target_ratio)
            offset = (im.width - new_width) // 2
            im = im.crop((offset, 0, offset + new_width, im.height))

        im = im.resize((width, height), Image.Resampling.LANCZOS)
        im.save(
            path, quality=quality, format=IMAGE_FORMAT, optimize=True,
            progressive=True)
