"""
This module contains unit tests for the shuffle function in the shuffle
module. The tests aim to verify the behavior of the shuffle function in
different scenarios, including when shuffle is enabled and there are
shards to shuffle, when no shards are returned from the repository, when
shuffle is disabled in the configuration, and when only a single shard
is present. Each test ensures that the function interacts correctly with
the repository and FileManager, performs the necessary file operations
such as copying, deleting, and renaming shards, and properly manages
lock actions (enabling and disabling) based on the conditions. The tests
also confirm that when shuffle is disabled or when no shards are found,
the function avoids unnecessary file operations and lock management.
These tests use mock objects to isolate the shuffle function and verify
its behavior in a controlled environment.
"""

import unittest
import asynctest
from unittest.mock import MagicMock, AsyncMock, patch, call
from app.helpers.shuffle_helper import shuffle


class ShuffleTestCase(asynctest.TestCase):

    @patch("app.helpers.shuffle_helper.lock_disable")
    @patch("app.helpers.shuffle_helper.lock_enable")
    @patch("app.helpers.shuffle_helper.FileManager", new_callable=AsyncMock)
    @patch("app.helpers.shuffle_helper.Repository")
    @patch("app.helpers.shuffle_helper.cfg")
    async def test_shuffle_when_locked(
            self, cfg_mock, repository_mock, file_manager_mock,
            lock_enable_mock, lock_disable_mock):
        """
        This test ensures that when shuffle is enabled and there are
        shards to shuffle, the shuffle function interacts with the
        repository and FileManager as expected. It checks that the
        function selects the appropriate shards, performs the necessary
        file operations (copy, delete, and rename) for each shard, and
        correctly enables and disables the lock. The test confirms that
        all file operations are executed sequentially for the shards
        returned by the repository.
        """
        cfg_mock.SHUFFLE_LOCKED = True
        cfg_mock.SHUFFLE_LIMIT = 2
        cfg_mock.SHUFFLE_EXTENSION = ".copy"

        shards = [
            MagicMock(id=1, shard_path="/path/to/shard1"),
            MagicMock(id=2, shard_path="/path/to/shard2")
        ]

        shard_repository_mock = AsyncMock()
        shard_repository_mock.select_all.return_value = shards
        repository_mock.return_value = shard_repository_mock

        mock_session = AsyncMock()
        mock_cache = AsyncMock()
        await shuffle(mock_session, mock_cache)

        shard_repository_mock.select_all.assert_called_once_with(
            offset=0, limit=cfg_mock.SHUFFLE_LIMIT, order_by="id",
            order="rand")
        lock_enable_mock.assert_called_once()
        lock_disable_mock.assert_called_once()
        self.assertListEqual(file_manager_mock.mock_calls, [
            call.copy("/path/to/shard1", "/path/to/shard1.copy"),
            call.delete("/path/to/shard1"),
            call.rename("/path/to/shard1.copy", "/path/to/shard1"),
            call.copy("/path/to/shard2", "/path/to/shard2.copy"),
            call.delete("/path/to/shard2"),
            call.rename("/path/to/shard2.copy", "/path/to/shard2")
        ])

    @patch("app.helpers.shuffle_helper.lock_disable")
    @patch("app.helpers.shuffle_helper.lock_enable")
    @patch("app.helpers.shuffle_helper.FileManager", new_callable=AsyncMock)
    @patch("app.helpers.shuffle_helper.Repository")
    @patch("app.helpers.shuffle_helper.cfg")
    async def test_shuffle_when_not_locked(
            self, cfg_mock, repository_mock, file_manager_mock,
            lock_enable_mock, lock_disable_mock):
        cfg_mock.SHUFFLE_LOCKED = False
        cfg_mock.SHUFFLE_LIMIT = 2
        cfg_mock.SHUFFLE_EXTENSION = ".copy"

        shards = [
            MagicMock(id=1, shard_path="/path/to/shard1"),
            MagicMock(id=2, shard_path="/path/to/shard2")
        ]

        shard_repository_mock = AsyncMock()
        shard_repository_mock.select_all.return_value = shards
        repository_mock.return_value = shard_repository_mock

        mock_session = AsyncMock()
        mock_cache = AsyncMock()
        await shuffle(mock_session, mock_cache)

        shard_repository_mock.select_all.assert_called_once_with(
            offset=0, limit=cfg_mock.SHUFFLE_LIMIT, order_by="id",
            order="rand")
        lock_enable_mock.assert_not_called()
        lock_disable_mock.assert_not_called()
        self.assertListEqual(file_manager_mock.mock_calls, [
            call.copy("/path/to/shard1", "/path/to/shard1.copy"),
            call.delete("/path/to/shard1"),
            call.rename("/path/to/shard1.copy", "/path/to/shard1"),
            call.copy("/path/to/shard2", "/path/to/shard2.copy"),
            call.delete("/path/to/shard2"),
            call.rename("/path/to/shard2.copy", "/path/to/shard2")
        ])

    @patch("app.helpers.shuffle_helper.lock_disable")
    @patch("app.helpers.shuffle_helper.lock_enable")
    @patch("app.helpers.shuffle_helper.FileManager", new_callable=AsyncMock)
    @patch("app.helpers.shuffle_helper.Repository")
    @patch("app.helpers.shuffle_helper.cfg")
    async def test_shuffle_when_no_shards_exist(
            self, cfg_mock, repository_mock, file_manager_mock,
            lock_enable_mock, lock_disable_mock):
        """
        This test verifies the behavior of the shuffle function when no
        shards are returned by the repository. It ensures that in such
        cases, no file operations (copy, delete, rename) are performed,
        and no lock actions (enable or disable) are triggered. The test
        checks that the function gracefully handles the absence of
        shards without affecting other components.
        """
        cfg_mock.SHUFFLE_LOCKED = True
        cfg_mock.SHUFFLE_LIMIT = 2
        cfg_mock.SHUFFLE_EXTENSION = ".copy"

        shard_repository_mock = AsyncMock()
        shard_repository_mock.select_all.return_value = []
        repository_mock.return_value = shard_repository_mock

        mock_session = AsyncMock()
        mock_cache = AsyncMock()

        await shuffle(mock_session, mock_cache)

        shard_repository_mock.select_all.assert_called_once_with(
            offset=0, limit=cfg_mock.SHUFFLE_LIMIT, order_by="id",
            order="rand")
        lock_enable_mock.assert_not_called()
        lock_disable_mock.assert_not_called()
        file_manager_mock.mock_calls == []

    @patch("app.helpers.shuffle_helper.lock_disable")
    @patch("app.helpers.shuffle_helper.lock_enable")
    @patch("app.helpers.shuffle_helper.FileManager", new_callable=AsyncMock)
    @patch("app.helpers.shuffle_helper.Repository")
    @patch("app.helpers.shuffle_helper.cfg")
    async def test_shuffle_with_single_shard(
            self, cfg_mock, repository_mock, file_manager_mock,
            lock_enable_mock, lock_disable_mock):
        """
        This test examines the shuffle function's handling of a scenario
        where only a single shard is returned by the repository. It
        verifies that the function performs the correct sequence of file
        operations (copy, delete, and rename) for the single shard, and
        that the lock is enabled and disabled as expected. This test
        ensures that the function correctly handles cases with a minimal
        number of shards.
        """
        cfg_mock.SHUFFLE_ENABLED = True
        cfg_mock.SHUFFLE_LIMIT = 1
        cfg_mock.SHUFFLE_EXTENSION = ".copy"

        shard_repository_mock = AsyncMock()
        shard_repository_mock.select_all.return_value = [
            MagicMock(id=1, shard_path="/path/to/shard1")
        ]
        repository_mock.return_value = shard_repository_mock

        mock_session = AsyncMock()
        mock_cache = AsyncMock()

        await shuffle(mock_session, mock_cache)

        file_manager_mock.copy.assert_called_once_with(
            "/path/to/shard1", "/path/to/shard1.copy")
        file_manager_mock.delete.assert_called_once_with(
            "/path/to/shard1")
        file_manager_mock.rename.assert_called_once_with(
            "/path/to/shard1.copy", "/path/to/shard1")

        lock_enable_mock.assert_called_once()
        lock_disable_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
