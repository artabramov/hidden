# tests/services/test_file_thumbnail_retrieve.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.errors import ResourceNotFoundError
from app.events import Events as E
from app.models.file_thumbnail import FileThumbnail
from app.services.file_thumbnail_retrieve import retrieve_file_thumbnail


class TestRetrieveFileThumbnail(unittest.IsolatedAsyncioTestCase):

    def _build_thumbnail(self):
        thumbnail = MagicMock(spec=FileThumbnail)
        thumbnail.id = 7
        thumbnail.file_id = 42
        thumbnail.absolute_path = "/mnt/files/thumbnails/thumb-uuid"
        thumbnail.mimetype = "image/jpeg"
        return thumbnail

    # --- cache hit ---

    async def test_returns_cached_entry_without_db_or_disk(self):
        session = AsyncMock()

        mock_cache = MagicMock()
        mock_cache.get.return_value = ("image/jpeg", b"cached_bytes")

        with (
            patch(
                "app.services.file_thumbnail_retrieve.get_thumbnail_cache",
                return_value=mock_cache,
            ),
            patch(
                "app.services.file_thumbnail_retrieve.ORMRepository",
            ) as mock_repo_cls,
            patch(
                "app.services.file_thumbnail_retrieve.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            result = await retrieve_file_thumbnail(session, 42)

        self.assertEqual(result, ("image/jpeg", b"cached_bytes"))
        mock_cache.get.assert_called_once_with(42)
        mock_repo_cls.assert_not_called()
        emit_mock.assert_not_awaited()

    # --- cache miss: success path ---

    async def test_reads_file_populates_cache_and_emits_hook(self):
        session = AsyncMock()
        thumbnail = self._build_thumbnail()

        repository = AsyncMock()
        repository.select = AsyncMock(return_value=thumbnail)

        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        with (
            patch(
                "app.services.file_thumbnail_retrieve.get_thumbnail_cache",
                return_value=mock_cache,
            ),
            patch(
                "app.services.file_thumbnail_retrieve.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_thumbnail_retrieve.read",
                new=AsyncMock(return_value=b"raw_bytes"),
            ) as read_mock,
            patch(
                "app.services.file_thumbnail_retrieve.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            mimetype, data = await retrieve_file_thumbnail(session, 42)

        self.assertEqual(mimetype, "image/jpeg")
        self.assertEqual(data, b"raw_bytes")

        repository.select.assert_any_await(FileThumbnail, file_id=42)
        self.assertEqual(repository.select.await_count, 1)

        read_mock.assert_awaited_once_with(thumbnail.absolute_path)

        mock_cache.put.assert_called_once_with(42, "image/jpeg", b"raw_bytes")

        emit_mock.assert_awaited_once_with(
            E.FILE_THUMBNAIL_RETRIEVE_COMPLETED,
            session,
            thumbnail,
        )

    # --- cache miss: not found paths ---

    async def test_raises_not_found_when_thumbnail_missing(self):
        session = AsyncMock()

        repository = AsyncMock()
        repository.select = AsyncMock(return_value=None)

        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        with (
            patch(
                "app.services.file_thumbnail_retrieve.get_thumbnail_cache",
                return_value=mock_cache,
            ),
            patch(
                "app.services.file_thumbnail_retrieve.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_thumbnail_retrieve.read",
                new=AsyncMock(),
            ) as read_mock,
            patch(
                "app.services.file_thumbnail_retrieve.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await retrieve_file_thumbnail(session, 42)

        repository.select.assert_awaited_once_with(FileThumbnail, file_id=42)
        read_mock.assert_not_awaited()
        mock_cache.put.assert_not_called()
        emit_mock.assert_not_awaited()

    async def test_raises_not_found_when_thumbnail_file_missing(self):
        session = AsyncMock()
        thumbnail = self._build_thumbnail()

        repository = AsyncMock()
        repository.select = AsyncMock(return_value=thumbnail)

        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        with (
            patch(
                "app.services.file_thumbnail_retrieve.get_thumbnail_cache",
                return_value=mock_cache,
            ),
            patch(
                "app.services.file_thumbnail_retrieve.ORMRepository",
                return_value=repository,
            ),
            patch(
                "app.services.file_thumbnail_retrieve.read",
                new=AsyncMock(side_effect=FileNotFoundError),
            ) as read_mock,
            patch(
                "app.services.file_thumbnail_retrieve.hooks.emit",
                new=AsyncMock(),
            ) as emit_mock,
        ):
            with self.assertRaises(ResourceNotFoundError):
                await retrieve_file_thumbnail(session, 42)

        read_mock.assert_awaited_once_with(thumbnail.absolute_path)
        mock_cache.put.assert_not_called()
        emit_mock.assert_not_awaited()
