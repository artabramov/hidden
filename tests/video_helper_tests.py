import unittest
from unittest.mock import AsyncMock, patch
from app.helpers.video_helper import video_capture, VIDEO_CAPTURE_EXTENSION
from app.config import get_config

cfg = get_config()


class ImageHelperTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.helpers.video_helper.FileManager", new_callable=AsyncMock)
    @patch("app.helpers.video_helper.ffmpeg")
    async def test_video_capture(self, ffmpeg_mock, FileManagerMock):
        result = await video_capture("src_path", "dst_path")
        self.assertIsNone(result)

        ffmpeg_mock.input.assert_called_with("src_path", ss=0)
        ffmpeg_mock.input.return_value.filter.assert_called_with(
            "scale", cfg.THUMBNAILS_WIDTH, -1)
        ffmpeg_mock.input.return_value.filter.return_value \
            .output.assert_called_with(
                "dst_path" + VIDEO_CAPTURE_EXTENSION, vframes=1)
        ffmpeg_mock.input.return_value.filter.return_value \
            .output.return_value.overwrite_output.assert_called_once()
        ffmpeg_mock.input.return_value.filter.return_value \
            .output.return_value.overwrite_output.return_value \
            .run.assert_called_with(capture_stdout=True, capture_stderr=True)
        FileManagerMock.rename.assert_called_with(
            "dst_path" + VIDEO_CAPTURE_EXTENSION, "dst_path")


if __name__ == "__main__":
    unittest.main()
