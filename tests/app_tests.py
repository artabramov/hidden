import importlib
import json
import unittest
import logging
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock, MagicMock, call
from starlette.requests import Request
from fastapi.responses import Response
from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from cryptography.exceptions import InvalidKey


class AppTest(unittest.IsolatedAsyncioTestCase):

    @patch("app.app.SessionManager")
    @patch("app.app.RedisClient")
    @patch("app.app.FileManager")
    @patch("app.app.init_database", new_callable=AsyncMock)
    @patch("app.app.init_cache", new_callable=AsyncMock)
    @patch("app.app.init_hooks", return_value=None)
    @patch("app.app.init_logger", return_value=None)
    @patch("app.app.get_config")
    async def test_lifespan_init_and_teardown(
        self, get_config_mock, init_logger_mock, init_hooks_mock,
        init_cache_mock, init_db_mock, FileManagerMock, RedisClientMock,
        SessionManagerMock,
    ):
        cfg = SimpleNamespace(
            SQLITE_PATH=":memory:",
            SQLITE_SQL_ECHO=False,
            REDIS_HOST="localhost",
            REDIS_PORT=6379,
            REDIS_DECODE_RESPONSES=True,
            LRU_TOTAL_SIZE_BYTES=1000,
            LRU_ITEM_SIZE_LIMIT_BYTES=500,
            LOCK_FILE_PATH="/tmp/lock",
            GOCRYPTFS_PASSPHRASE_PATH="/tmp/secret",
            GOCRYPTFS_PASSPHRASE_LENGTH=64,
        )
        get_config_mock.return_value = cfg

        engine = SimpleNamespace(dispose=AsyncMock())
        SessionManagerMock.return_value = SimpleNamespace(async_engine=engine)
        RedisClientMock.return_value = SimpleNamespace(close=AsyncMock())
        FileManagerMock.return_value = SimpleNamespace(
            isfile=AsyncMock(return_value=True),
            delete=AsyncMock(),
        )

        appmod = importlib.import_module("app.app")
        async with appmod.lifespan(appmod.app):
            self.assertIs(appmod.app.state.config, cfg)
            self.assertIsNotNone(appmod.app.state.file_manager)
            self.assertIsNotNone(appmod.app.state.lru)
            self.assertTrue(hasattr(appmod.app.state, "folder_locks"))
            self.assertTrue(hasattr(appmod.app.state, "file_locks"))

            init_db_mock.assert_awaited_once()
            init_cache_mock.assert_awaited_once()
            init_hooks_mock.assert_called_once_with(appmod.app)
            init_logger_mock.assert_called_once_with(appmod.app)

            SessionManagerMock.assert_called_once_with(
                sqlite_path=cfg.SQLITE_PATH, sql_echo=cfg.SQLITE_SQL_ECHO
            )
            RedisClientMock.assert_called_once_with(
                host=cfg.REDIS_HOST,
                port=cfg.REDIS_PORT,
                decode_responses=cfg.REDIS_DECODE_RESPONSES,
            )
            FileManagerMock.assert_called_once_with(cfg)

            FileManagerMock.return_value.delete.assert_awaited_with(
                cfg.LOCK_FILE_PATH)

        engine.dispose.assert_awaited_once()
        RedisClientMock.return_value.close.assert_awaited_once()

    @patch("app.app.uuid4")
    async def test_middleware_handler_lock_exists(self, uuid4_mock):
        uuid4_mock.return_value = "fa5ed3d1-a85d-4f16-8a1f-b2440907"

        file_manager_mock = AsyncMock()
        file_manager_mock.isfile = AsyncMock(return_value=True)

        cfg = SimpleNamespace(
            LOCK_FILE_PATH="/tmp/lock",
            GOCRYPTFS_PASSPHRASE_PATH="/tmp/secret",
            GOCRYPTFS_PASSPHRASE_LENGTH=64,
        )

        log_mock = MagicMock()
        lru_mock = MagicMock()

        appmod = importlib.import_module("app.app")
        appmod.app.state.config = cfg
        appmod.app.state.file_manager = file_manager_mock
        appmod.app.state.log = log_mock
        appmod.app.state.lru = lru_mock

        request = Request({
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "path": "/__test__/ok",
            "headers": [],
            "app": appmod.app,
        })

        call_next_mock = AsyncMock()
        with self.assertRaises(HTTPException) as ctx:
            await appmod.middleware_handler(request, call_next_mock)

        self.assertEqual(ctx.exception.status_code, status.HTTP_423_LOCKED)
        file_manager_mock.isfile.assert_awaited_once_with(cfg.LOCK_FILE_PATH)

        call_next_mock.assert_not_awaited()
        self.assertEqual(request.state.request_uuid, uuid4_mock.return_value)

        self.assertTrue(log_mock.log.called)
        log_level = log_mock.log.call_args[0][0]
        self.assertEqual(log_level, logging.DEBUG)

        lru_mock.clear.assert_called_once()

    @patch("app.app.uuid4")
    async def test_middleware_handler_secret_missing(self, uuid4_mock):
        uuid4_mock.return_value = "fa5ed3d1-a85d-4f16-8a1f-b2440907"

        file_manager_mock = AsyncMock()
        file_manager_mock.isfile = AsyncMock(side_effect=[False, False])

        cfg = SimpleNamespace(
            LOCK_FILE_PATH="/tmp/lock",
            GOCRYPTFS_PASSPHRASE_PATH="/tmp/secret",
            GOCRYPTFS_PASSPHRASE_LENGTH=64,
        )

        log_mock = MagicMock()
        lru_mock = MagicMock()

        appmod = importlib.import_module("app.app")
        appmod.app.state.config = cfg
        appmod.app.state.file_manager = file_manager_mock
        appmod.app.state.log = log_mock
        appmod.app.state.lru = lru_mock

        request = Request({
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "path": "/__test__/ok",
            "headers": [],
            "app": appmod.app,
        })

        call_next_mock = AsyncMock()
        with self.assertRaises(HTTPException) as ctx:
            await appmod.middleware_handler(request, call_next_mock)

        self.assertEqual(
            ctx.exception.status_code, appmod.HTTP_498_GOCRYPTFS_KEY_MISSING)

        file_manager_mock.isfile.assert_has_awaits([
            call(cfg.LOCK_FILE_PATH),
            call(cfg.GOCRYPTFS_PASSPHRASE_PATH),
        ])

        call_next_mock.assert_not_awaited()
        self.assertEqual(request.state.request_uuid, uuid4_mock.return_value)

        self.assertTrue(log_mock.log.called)
        log_level = log_mock.log.call_args[0][0]
        self.assertEqual(log_level, logging.DEBUG)

        lru_mock.clear.assert_called_once()

    @patch("app.app.uuid4")
    async def test_middleware_handler_secret_invalid(self, uuid4_mock):
        uuid4_mock.return_value = "fa5ed3d1-a85d-4f16-8a1f-b2440907"

        file_manager_mock = AsyncMock()
        file_manager_mock.isfile = AsyncMock(side_effect=[False, True])
        file_manager_mock.read = AsyncMock(return_value="short\n")

        cfg = SimpleNamespace(
            LOCK_FILE_PATH="/tmp/lock",
            GOCRYPTFS_PASSPHRASE_PATH="/tmp/secret",
            GOCRYPTFS_PASSPHRASE_LENGTH=64,
        )

        log_mock = MagicMock()
        lru_mock = MagicMock()

        appmod = importlib.import_module("app.app")
        appmod.app.state.config = cfg
        appmod.app.state.file_manager = file_manager_mock
        appmod.app.state.log = log_mock
        appmod.app.state.lru = lru_mock

        request = Request({
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "path": "/__test__/ok",
            "headers": [],
            "app": appmod.app,
        })

        call_next_mock = AsyncMock()
        with self.assertRaises(HTTPException) as ctx:
            await appmod.middleware_handler(request, call_next_mock)

        self.assertEqual(
            ctx.exception.status_code,
            appmod.HTTP_499_GOCRYPTFS_KEY_INVALID
        )

        file_manager_mock.isfile.assert_has_awaits([
            call(cfg.LOCK_FILE_PATH),
            call(cfg.GOCRYPTFS_PASSPHRASE_PATH),
        ])
        file_manager_mock.read.assert_awaited_once_with(
            cfg.GOCRYPTFS_PASSPHRASE_PATH)

        call_next_mock.assert_not_awaited()
        self.assertEqual(request.state.request_uuid, uuid4_mock.return_value)

        self.assertTrue(log_mock.log.called)
        log_level = log_mock.log.call_args[0][0]
        self.assertEqual(log_level, logging.DEBUG)

        lru_mock.clear.assert_called_once()

    @patch("app.app.uuid4")
    async def test_middleware_handler_success(self, uuid4_mock):
        uuid4_mock.return_value = "fa5ed3d1-a85d-4f16-8a1f-b2440907"

        file_manager_mock = AsyncMock()
        file_manager_mock.isfile = AsyncMock(side_effect=[False, True])
        valid_key = "A" * 64
        file_manager_mock.read = AsyncMock(return_value=valid_key + "\n")

        cfg = SimpleNamespace(
            LOCK_FILE_PATH="/tmp/lock",
            GOCRYPTFS_PASSPHRASE_PATH="/tmp/secret",
            GOCRYPTFS_PASSPHRASE_LENGTH=64,
        )

        log_mock = MagicMock()
        log_mock.isEnabledFor.return_value = True
        lru_mock = MagicMock()

        appmod = importlib.import_module("app.app")
        appmod.app.state.config = cfg
        appmod.app.state.file_manager = file_manager_mock
        appmod.app.state.log = log_mock
        appmod.app.state.lru = lru_mock

        request = Request({
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "path": "/__test__/ok",
            "headers": [],
            "app": appmod.app,
        })

        call_next_mock = AsyncMock(return_value=Response(status_code=204))
        resp = await appmod.middleware_handler(request, call_next_mock)

        call_next_mock.assert_awaited_once()

        self.assertEqual(resp.headers.get("X-Request-ID"),
                         uuid4_mock.return_value)
        self.assertEqual(request.state.request_uuid, uuid4_mock.return_value)

        self.assertEqual(request.state.gocryptfs_key, valid_key)

        file_manager_mock.isfile.assert_has_awaits([
            call(cfg.LOCK_FILE_PATH),
            call(cfg.GOCRYPTFS_PASSPHRASE_PATH),
        ])
        file_manager_mock.read.assert_awaited_once_with(
            cfg.GOCRYPTFS_PASSPHRASE_PATH)

        lru_mock.clear.assert_not_called()

        self.assertTrue(log_mock.log.called)
        log_level = log_mock.log.call_args[0][0]
        self.assertEqual(log_level, logging.DEBUG)

        self.assertEqual(resp.status_code, 204)

    async def test_exception_handler_validation_error(self):
        appmod = importlib.import_module("app.app")
        request = Request({
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "path": "/__test__/bad",
            "headers": [],
            "app": appmod.app,
        })
        request.state.request_start_time = 1.0
        request.state.request_uuid = "fa5ed3d1-a85d-4f16-8a1f-b2440907"

        log_mock = MagicMock()
        request.state.log = log_mock

        errors = [{"loc": ["query", "q"], "msg": "field required"}]
        exc = RequestValidationError(errors=errors)
        resp = await appmod.exception_handler(request, exc)

        self.assertEqual(resp.status_code, 422)
        self.assertEqual(json.loads(resp.body), {"detail": errors})
        self.assertEqual(resp.headers.get("X-Request-ID"),
                         request.state.request_uuid)
        self.assertTrue(log_mock.debug.called)

    async def test_exception_handler_secret_invalid(self):
        appmod = importlib.import_module("app.app")
        lru_mock = MagicMock()
        appmod.app.state.lru = lru_mock

        request = Request({
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "path": "/__test__/bad",
            "headers": [],
            "app": appmod.app,
        })
        request.state.request_start_time = 1.0
        request.state.request_uuid = "fa5ed3d1-a85d-4f16-8a1f-b2440907"

        log_mock = MagicMock()
        request.state.log = log_mock

        exc = InvalidKey()
        resp = await appmod.exception_handler(request, exc)

        self.assertEqual(
            resp.status_code,
            appmod.HTTP_499_GOCRYPTFS_KEY_INVALID
        )
        self.assertEqual(
            json.loads(resp.body),
            {"detail": [{"type": appmod.ERR_GOCRYPTFS_KEY_INVALID,
                        "msg": "gocryptfs key is invalid"}]}
        )

        self.assertEqual(resp.headers.get("X-Request-ID"),
                         request.state.request_uuid)
        self.assertTrue(log_mock.error.called)
        lru_mock.clear.assert_called_once()

    async def test_exception_handler_http_exception(self):
        appmod = importlib.import_module("app.app")
        lru_mock = MagicMock()
        appmod.app.state.lru = lru_mock

        request = Request({
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "path": "/__test__/bad",
            "headers": [],
            "app": appmod.app,
        })
        request.state.request_start_time = 1.0
        request.state.request_uuid = "fa5ed3d1-a85d-4f16-8a1f-b2440907"

        log_mock = MagicMock()
        request.state.log = log_mock

        detail = [{"type": "custom_error", "msg": "boom"}]
        exc = HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=detail)

        resp = await appmod.exception_handler(request, exc)

        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(json.loads(resp.body), {"detail": detail})

        self.assertEqual(resp.headers.get("X-Request-ID"),
                         request.state.request_uuid)
        self.assertTrue(log_mock.error.called)

        lru_mock.assert_not_called()

    async def test_exception_handler_server_error(self):
        appmod = importlib.import_module("app.app")
        lru_mock = MagicMock()
        appmod.app.state.lru = lru_mock

        request = Request({
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "path": "/__test__/bad",
            "headers": [],
            "app": appmod.app,
        })
        request.state.request_start_time = 1.0
        request.state.request_uuid = "fa5ed3d1-a85d-4f16-8a1f-b2440907"

        log_mock = MagicMock()
        request.state.log = log_mock

        exc = RuntimeError("kaboom")

        resp = await appmod.exception_handler(request, exc)

        self.assertEqual(resp.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(
            json.loads(resp.body),
            {"detail": [{"type": appmod.ERR_SERVER_ERROR,
                        "msg": "Internal server error"}]}
        )

        self.assertEqual(resp.headers.get("X-Request-ID"),
                         request.state.request_uuid)
        self.assertTrue(log_mock.error.called)

        lru_mock.assert_not_called()
