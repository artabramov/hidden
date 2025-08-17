"""
The module provides functionality for capturing a frame from a video
file using FFmpeg and saving it as an image, with support for specific
video MIME types.
"""

import ffmpeg
from app.config import get_config
from app.managers.file_manager import FileManager

cfg = get_config()

VIDEO_MIMETYPES = ["video/mp4", "video/x-ms-wmv"]
VIDEO_CAPTURE_EXTENSION = ".jpeg"


async def video_capture(video_path: str, image_path: str):
    """
    Captures a single frame from the beginning of a video file using
    FFmpeg, saves it as a temporary JPEG file, and then renames it to
    the desired output path.
    """
    video_capture_path = image_path + VIDEO_CAPTURE_EXTENSION
    ffmpeg.input(video_path, ss=0) \
        .filter("scale", cfg.THUMBNAILS_WIDTH, -1) \
        .output(video_capture_path, vframes=1) \
        .overwrite_output() \
        .run(capture_stdout=True, capture_stderr=True)
    await FileManager.rename(video_capture_path, image_path)
