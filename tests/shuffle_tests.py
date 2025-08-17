import unittest
from unittest.mock import MagicMock, AsyncMock, patch, call
from app.helpers.shuffle_helper import (
    shuffle_shards, TMP_EXTENSION, SHUFFLE_LIMIT
)


class ShuffleTestCase(unittest.IsolatedAsyncioTestCase):

    @patch("app.helpers.shuffle_helper.FileManager", new_callable=AsyncMock)
    @patch("app.helpers.shuffle_helper.Repository")
    async def test_shuffle_when(self, repository_mock, file_manager_mock):
        shards = [
            MagicMock(id=1, shard_path="/path/to/shard1"),
            MagicMock(id=2, shard_path="/path/to/shard2")
        ]

        shard_repository_mock = AsyncMock()
        shard_repository_mock.select_all.return_value = shards
        repository_mock.return_value = shard_repository_mock

        mock_session = AsyncMock()
        mock_cache = AsyncMock()
        await shuffle_shards(mock_session, mock_cache)

        shard_repository_mock.select_all.assert_called_once_with(
            offset=0, limit=SHUFFLE_LIMIT, order_by="id", order="rand"
        )
        self.assertListEqual(file_manager_mock.mock_calls, [
            call.copy("/path/to/shard1", "/path/to/shard1" + TMP_EXTENSION),
            call.rename("/path/to/shard1" + TMP_EXTENSION, "/path/to/shard1"),
            call.copy("/path/to/shard2", "/path/to/shard2" + TMP_EXTENSION),
            call.rename("/path/to/shard2" + TMP_EXTENSION, "/path/to/shard2")
        ])


if __name__ == "__main__":
    unittest.main()
