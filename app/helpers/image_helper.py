"""
The module contains utility functions for working with image files,
including support for resizing images and defining supported image
MIME types.
"""

import asyncio
import io
from PIL import Image
from typing import List

IMAGE_FORMAT = "JPEG"
IMAGE_MEDIATYPE = "image/jpeg"
IMAGE_MIMETYPES = [
    "image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff",
    "image/webp", "image/svg+xml", "image/x-icon", "image/x-tiff",
    "image/heic", "image/jp2", "image/avif", "image/apng", "image/heif",
    "image/x-cmu-raster", "image/x-portable-anymap", "image/x-portable-bitmap",
    "image/x-portable-graymap", "image/x-portable-pixmap"]


async def image_resize(path: str, width: int, height: int, quality: int):
    """
    Asynchronously resizes an image by offloading the resizing task to
    a background thread to avoid blocking the event loop.
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _image_resize_sync, path,
                               width, height, quality)


async def images_merge(image_data_list: List[bytes], width: int,
                       height: int, quality: int) -> bytes:
    """
    Asynchronously merges images into a single horizontal layout image
    by offloading the operation to a background thread.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _image_concat_horizontal_sync,
        image_data_list, width, height, quality)


def _image_resize_sync(path: str, width: int, height: int, quality: int):
    """
    Opens an image from the specified file path, center-crops it to
    match the target aspect ratio, resizes it to the given width and
    height, and saves the result as a JPEG with the specified quality.
    """
    im = Image.open(path)
    if im.mode in ["P", "RGBA"]:
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

    im = im.resize((width, height), Image.LANCZOS)
    im.save(path, quality=quality, format='JPEG')


def _image_concat_horizontal_sync(image_data_list: List[bytes], width: int,
                                  height: int, quality: int) -> bytes:
    """
    Combines up to 2 images into a single horizontal image of the
    specified height. Each image is resized to match the target height
    and center-cropped horizontally. The resulting image is returned as
    a JPEG byte stream with the given quality. If one image is provided,
    it is returned as-is. If two images are provided, they are
    concatenated side by side. More than two images are ignored.
    """
    if not image_data_list:
        return None

    elif len(image_data_list) == 1:
        return image_data_list[0]

    elif len(image_data_list) >= 2:
        im1 = _crop_center_half(_resize_to_height(
            _create_image(image_data_list[0]), height))
        im2 = _crop_center_half(_resize_to_height(
            _create_image(image_data_list[1]), height))

        result_width = im1.width + im2.width
        new_im = Image.new("RGB", (result_width, height))
        new_im.paste(im1, (0, 0))
        new_im.paste(im2, (im1.width, 0))

    buffer = io.BytesIO()
    new_im.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return buffer.read()


def _create_image(image_bytes: bytes) -> Image.Image:
    """
    Opens an image from the provided byte data and converts it to RGB
    mode if necessary.
    """
    im = Image.open(io.BytesIO(image_bytes))
    if im.mode in ["P", "RGBA"]:
        im = im.convert("RGB")
    return im


def _resize_to_height(im: Image.Image, target_height: int) -> Image.Image:
    """
    Resizes the given image to the specified height while maintaining
    the aspect ratio.
    """
    w, h = im.size
    ratio = target_height / h
    return im.resize((int(w * ratio), target_height), Image.LANCZOS)


def _crop_center_half(im: Image.Image) -> Image.Image:
    """
    Crops the center half of the image width while preserving the full
    height. If the image width is less than or equal to 1, the image is
    returned unmodified.
    """
    w, h = im.size
    if w <= 1:
        return im

    half_w = w // 2
    left = (w - half_w) // 2
    return im.crop((left, 0, left + half_w, h))


def _prepare_area_crop(image_bytes: bytes,
                       target_size: tuple[int, int]) -> Image.Image:
    """
    Resizes and crops an image to fit the target size, preserving the
    center. The image is first scaled to ensure the target size fits
    within the resized dimensions. If no resizing is needed, the
    original image is returned. If resizing is done, the image is
    cropped to match the target size exactly.
    """
    im = _create_image(image_bytes)
    w, h = im.size
    scale = max(target_size[0] / w, target_size[1] / h)

    if scale == 1:
        return im

    resized = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    rw, rh = resized.size

    if rw == target_size[0] and rh == target_size[1]:
        return resized

    left = (rw - target_size[0]) // 2
    top = (rh - target_size[1]) // 2
    return resized.crop((left, top, left + target_size[0],
                         top + target_size[1]))
