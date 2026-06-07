# tests/services/test_cipherdir_create.py
# SPDX-License-Identifier: SSPL-1.0

import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.constants import (
    GOCRYPTFS_CIPHERDIR_LOCK_PATH,
    GOCRYPTFS_PASSPHRASE_LENGTH,
    JWT_SIGNING_KEY_LENGTH,
)
from app.errors import ResourceConflictError
from app.locks import LockType
from app.services.cipherdir_create import create_cipherdir


class TestCreateCipherdir(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.log_patcher = patch(
            "app.services.cipherdir_create.log"
        )
        self.log_patcher.start()

    def tearDown(self):
        self.log_patcher.stop()

    def _build_lock_context(self):
        ctx = AsyncMock()
        ctx.__aenter__.return_value = None
        ctx.__aexit__.return_value = None
        return ctx

    def _build_config(self):
        config = MagicMock()
        config.GOCRYPTFS_CIPHERDIR = "/fake/cipherdir"
        config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH = (
            "/fake/passphrase.enc"
        )
        config.JWT_SIGNING_KEY_PATH = "/fake/jwt.key"
        config.FERNET_KEY_PATH = "/fake/fernet.key"
        return config

    def _expected_cleanup_paths(self, config):
        return [
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
            os.path.join(
                config.GOCRYPTFS_CIPHERDIR,
                "gocryptfs.conf",
            ),
            os.path.join(
                config.GOCRYPTFS_CIPHERDIR,
                "gocryptfs.diriv",
            ),
            config.JWT_SIGNING_KEY_PATH,
            config.FERNET_KEY_PATH,
        ]

    async def test_raises_conflict_when_cipherdir_already_initialized(
        self,
    ):
        config = self._build_config()

        with (
            patch(
                "app.services.cipherdir_create.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_create.locks.lock_file",
                return_value=self._build_lock_context(),
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_create.is_gocryptfs_initialized",
                new=AsyncMock(return_value=True),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_create.isfile",
                new=AsyncMock(),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_create.write",
                new=AsyncMock(),
            ) as write_mock,
            patch(
                "app.services.cipherdir_create.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.cipherdir_create.init_gocryptfs",
                new=AsyncMock(),
            ) as init_mock,
            patch(
                "app.services.cipherdir_create.generate_random_string",
            ) as random_mock,
            patch(
                "app.services.cipherdir_create.encrypt_passphrase",
            ) as encrypt_mock,
            patch(
                "app.services.cipherdir_create.generate_fernet_key",
            ) as fernet_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await create_cipherdir("master-password")

        lock_file_mock.assert_called_once_with(
            GOCRYPTFS_CIPHERDIR_LOCK_PATH,
            LockType.WRITE,
        )
        initialized_mock.assert_awaited_once_with(
            config.GOCRYPTFS_CIPHERDIR,
        )
        isfile_mock.assert_not_awaited()
        write_mock.assert_not_awaited()
        delete_mock.assert_not_awaited()
        init_mock.assert_not_awaited()
        random_mock.assert_not_called()
        encrypt_mock.assert_not_called()
        fernet_mock.assert_not_called()

    async def test_raises_conflict_when_passphrase_already_exists(self):
        config = self._build_config()
        isfile_mock = AsyncMock(side_effect=[True])

        with (
            patch(
                "app.services.cipherdir_create.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_create.locks.lock_file",
                return_value=self._build_lock_context(),
            ),
            patch(
                "app.services.cipherdir_create.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.cipherdir_create.isfile",
                new=isfile_mock,
            ),
            patch(
                "app.services.cipherdir_create.write",
                new=AsyncMock(),
            ) as write_mock,
            patch(
                "app.services.cipherdir_create.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.cipherdir_create.init_gocryptfs",
                new=AsyncMock(),
            ) as init_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await create_cipherdir("master-password")

        isfile_mock.assert_awaited_once_with(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        write_mock.assert_not_awaited()
        delete_mock.assert_not_awaited()
        init_mock.assert_not_awaited()

    async def test_raises_conflict_when_jwt_key_already_exists(self):
        config = self._build_config()
        isfile_mock = AsyncMock(side_effect=[False, True])

        with (
            patch(
                "app.services.cipherdir_create.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_create.locks.lock_file",
                return_value=self._build_lock_context(),
            ),
            patch(
                "app.services.cipherdir_create.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.cipherdir_create.isfile",
                new=isfile_mock,
            ),
            patch(
                "app.services.cipherdir_create.write",
                new=AsyncMock(),
            ) as write_mock,
            patch(
                "app.services.cipherdir_create.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.cipherdir_create.init_gocryptfs",
                new=AsyncMock(),
            ) as init_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await create_cipherdir("master-password")

        self.assertEqual(isfile_mock.await_count, 2)
        isfile_mock.assert_any_await(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        isfile_mock.assert_any_await(config.JWT_SIGNING_KEY_PATH)
        write_mock.assert_not_awaited()
        delete_mock.assert_not_awaited()
        init_mock.assert_not_awaited()

    async def test_raises_conflict_when_fernet_key_already_exists(self):
        config = self._build_config()
        isfile_mock = AsyncMock(side_effect=[False, False, True])

        with (
            patch(
                "app.services.cipherdir_create.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_create.locks.lock_file",
                return_value=self._build_lock_context(),
            ),
            patch(
                "app.services.cipherdir_create.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.cipherdir_create.isfile",
                new=isfile_mock,
            ),
            patch(
                "app.services.cipherdir_create.write",
                new=AsyncMock(),
            ) as write_mock,
            patch(
                "app.services.cipherdir_create.delete",
                new=AsyncMock(),
            ) as delete_mock,
            patch(
                "app.services.cipherdir_create.init_gocryptfs",
                new=AsyncMock(),
            ) as init_mock,
        ):
            with self.assertRaises(ResourceConflictError):
                await create_cipherdir("master-password")

        self.assertEqual(isfile_mock.await_count, 3)
        isfile_mock.assert_any_await(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
        )
        isfile_mock.assert_any_await(config.JWT_SIGNING_KEY_PATH)
        isfile_mock.assert_any_await(config.FERNET_KEY_PATH)
        write_mock.assert_not_awaited()
        delete_mock.assert_not_awaited()
        init_mock.assert_not_awaited()

    async def test_creates_cipherdir_and_writes_all_secrets(self):
        config = self._build_config()
        write_mock = AsyncMock()

        with (
            patch(
                "app.services.cipherdir_create.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_create.locks.lock_file",
                return_value=self._build_lock_context(),
            ) as lock_file_mock,
            patch(
                "app.services.cipherdir_create.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ) as initialized_mock,
            patch(
                "app.services.cipherdir_create.isfile",
                new=AsyncMock(side_effect=[False, False, False]),
            ) as isfile_mock,
            patch(
                "app.services.cipherdir_create.generate_random_string",
                side_effect=["generated-passphrase", "generated-jwt-key"],
            ) as random_mock,
            patch(
                "app.services.cipherdir_create.encrypt_passphrase",
                return_value=b"encrypted-passphrase",
            ) as encrypt_mock,
            patch(
                "app.services.cipherdir_create.generate_fernet_key",
                return_value="generated-fernet-key",
            ) as fernet_mock,
            patch(
                "app.services.cipherdir_create.write",
                new=write_mock,
            ),
            patch(
                "app.services.cipherdir_create.init_gocryptfs",
                new=AsyncMock(),
            ) as init_mock,
            patch(
                "app.services.cipherdir_create.delete",
                new=AsyncMock(),
            ) as delete_mock,
        ):
            await create_cipherdir("master-password")

        lock_file_mock.assert_called_once_with(
            GOCRYPTFS_CIPHERDIR_LOCK_PATH,
            LockType.WRITE,
        )
        initialized_mock.assert_awaited_once_with(
            config.GOCRYPTFS_CIPHERDIR,
        )
        self.assertEqual(isfile_mock.await_count, 3)
        random_mock.assert_any_call(GOCRYPTFS_PASSPHRASE_LENGTH)
        random_mock.assert_any_call(JWT_SIGNING_KEY_LENGTH)
        encrypt_mock.assert_called_once_with(
            b"generated-passphrase",
            b"master-password",
        )
        fernet_mock.assert_called_once_with()

        self.assertEqual(write_mock.await_count, 3)
        write_mock.assert_any_await(
            config.GOCRYPTFS_PASSPHRASE_ENCRYPTED_PATH,
            b"encrypted-passphrase",
        )
        write_mock.assert_any_await(
            config.JWT_SIGNING_KEY_PATH,
            b"generated-jwt-key",
        )
        write_mock.assert_any_await(
            config.FERNET_KEY_PATH,
            b"generated-fernet-key",
        )

        init_mock.assert_awaited_once_with(
            "generated-passphrase",
            config.GOCRYPTFS_CIPHERDIR,
        )
        delete_mock.assert_not_awaited()

    async def test_cleans_up_when_first_write_fails(self):
        config = self._build_config()
        delete_mock = AsyncMock()

        write_mock = AsyncMock(
            side_effect=[RuntimeError("write passphrase failed")]
        )

        with (
            patch(
                "app.services.cipherdir_create.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_create.locks.lock_file",
                return_value=self._build_lock_context(),
            ),
            patch(
                "app.services.cipherdir_create.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.cipherdir_create.isfile",
                new=AsyncMock(side_effect=[False, False, False]),
            ),
            patch(
                "app.services.cipherdir_create.generate_random_string",
                side_effect=["generated-passphrase", "generated-jwt-key"],
            ),
            patch(
                "app.services.cipherdir_create.encrypt_passphrase",
                return_value=b"encrypted-passphrase",
            ),
            patch(
                "app.services.cipherdir_create.generate_fernet_key",
                return_value="generated-fernet-key",
            ),
            patch(
                "app.services.cipherdir_create.write",
                new=write_mock,
            ),
            patch(
                "app.services.cipherdir_create.init_gocryptfs",
                new=AsyncMock(),
            ) as init_mock,
            patch(
                "app.services.cipherdir_create.delete",
                new=delete_mock,
            ),
        ):
            with self.assertRaises(RuntimeError):
                await create_cipherdir("master-password")

        init_mock.assert_not_awaited()
        self.assertEqual(delete_mock.await_count, 5)
        for path in self._expected_cleanup_paths(config):
            delete_mock.assert_any_await(path)

    async def test_cleans_up_when_init_gocryptfs_fails(self):
        config = self._build_config()
        delete_mock = AsyncMock()

        with (
            patch(
                "app.services.cipherdir_create.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_create.locks.lock_file",
                return_value=self._build_lock_context(),
            ),
            patch(
                "app.services.cipherdir_create.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.cipherdir_create.isfile",
                new=AsyncMock(side_effect=[False, False, False]),
            ),
            patch(
                "app.services.cipherdir_create.generate_random_string",
                side_effect=["generated-passphrase", "generated-jwt-key"],
            ),
            patch(
                "app.services.cipherdir_create.encrypt_passphrase",
                return_value=b"encrypted-passphrase",
            ),
            patch(
                "app.services.cipherdir_create.generate_fernet_key",
                return_value="generated-fernet-key",
            ),
            patch(
                "app.services.cipherdir_create.write",
                new=AsyncMock(),
            ) as write_mock,
            patch(
                "app.services.cipherdir_create.init_gocryptfs",
                new=AsyncMock(
                    side_effect=RuntimeError("init failed")
                ),
            ) as init_mock,
            patch(
                "app.services.cipherdir_create.delete",
                new=delete_mock,
            ),
        ):
            with self.assertRaises(RuntimeError):
                await create_cipherdir("master-password")

        self.assertEqual(write_mock.await_count, 1)
        init_mock.assert_awaited_once_with(
            "generated-passphrase",
            config.GOCRYPTFS_CIPHERDIR,
        )
        self.assertEqual(delete_mock.await_count, 5)
        for path in self._expected_cleanup_paths(config):
            delete_mock.assert_any_await(path)

    async def test_cleans_up_when_jwt_key_write_fails(self):
        config = self._build_config()
        delete_mock = AsyncMock()

        write_mock = AsyncMock(
            side_effect=[
                None,
                RuntimeError("jwt write failed"),
            ]
        )

        with (
            patch(
                "app.services.cipherdir_create.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_create.locks.lock_file",
                return_value=self._build_lock_context(),
            ),
            patch(
                "app.services.cipherdir_create.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.cipherdir_create.isfile",
                new=AsyncMock(side_effect=[False, False, False]),
            ),
            patch(
                "app.services.cipherdir_create.generate_random_string",
                side_effect=["generated-passphrase", "generated-jwt-key"],
            ),
            patch(
                "app.services.cipherdir_create.encrypt_passphrase",
                return_value=b"encrypted-passphrase",
            ),
            patch(
                "app.services.cipherdir_create.generate_fernet_key",
                return_value="generated-fernet-key",
            ),
            patch(
                "app.services.cipherdir_create.write",
                new=write_mock,
            ),
            patch(
                "app.services.cipherdir_create.init_gocryptfs",
                new=AsyncMock(),
            ),
            patch(
                "app.services.cipherdir_create.delete",
                new=delete_mock,
            ),
        ):
            with self.assertRaises(RuntimeError):
                await create_cipherdir("master-password")

        self.assertEqual(write_mock.await_count, 2)
        self.assertEqual(delete_mock.await_count, 5)
        for path in self._expected_cleanup_paths(config):
            delete_mock.assert_any_await(path)

    async def test_cleans_up_when_fernet_key_write_fails(self):
        config = self._build_config()
        delete_mock = AsyncMock()

        write_mock = AsyncMock(
            side_effect=[
                None,
                None,
                RuntimeError("fernet write failed"),
            ]
        )

        with (
            patch(
                "app.services.cipherdir_create.get_config",
                return_value=config,
            ),
            patch(
                "app.services.cipherdir_create.locks.lock_file",
                return_value=self._build_lock_context(),
            ),
            patch(
                "app.services.cipherdir_create.is_gocryptfs_initialized",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "app.services.cipherdir_create.isfile",
                new=AsyncMock(side_effect=[False, False, False]),
            ),
            patch(
                "app.services.cipherdir_create.generate_random_string",
                side_effect=["generated-passphrase", "generated-jwt-key"],
            ),
            patch(
                "app.services.cipherdir_create.encrypt_passphrase",
                return_value=b"encrypted-passphrase",
            ),
            patch(
                "app.services.cipherdir_create.generate_fernet_key",
                return_value="generated-fernet-key",
            ),
            patch(
                "app.services.cipherdir_create.write",
                new=write_mock,
            ),
            patch(
                "app.services.cipherdir_create.init_gocryptfs",
                new=AsyncMock(),
            ),
            patch(
                "app.services.cipherdir_create.delete",
                new=delete_mock,
            ),
        ):
            with self.assertRaises(RuntimeError):
                await create_cipherdir("master-password")

        self.assertEqual(write_mock.await_count, 3)
        self.assertEqual(delete_mock.await_count, 5)
        for path in self._expected_cleanup_paths(config):
            delete_mock.assert_any_await(path)
