# tests/runtime/test_versity.py
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
import signal
import unittest
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, call, patch

from app.constants import (
    VERSITY_ACCESS_KEY_LENGTH,
    VERSITY_SECRET_KEY_LENGTH,
)
from app.errors import InternalServerError
from app.runtime.versity import (
    _get_versity_pid,
    is_versity_created,
    is_versity_running,
    versity_create,
    versity_read,
    versity_start,
    versity_stop,
)

_START = {
    "host": "127.0.0.1",
    "port": 9000,
    "webgui_host": "127.0.0.1",
    "webgui_port": 8080,
    "webgui_gateway": "http://127.0.0.1:9000",
    "webgui_cors_allow_origin": "http://localhost:8080",
    "data_path": "/mount/data",
    "iam_path": "/mount/iam",
    "access_key": "access-key",
    "secret_key": "secret-key",
}


def _config():
    config = MagicMock()
    config.VERSITY_START_TIMEOUT_SECONDS = 5
    config.VERSITY_STOP_TIMEOUT_SECONDS = 5
    config.VERSITY_POLL_INTERVAL_SECONDS = 0.25
    return config


def _clock(step):
    state = {"now": 0.0}
    sleeps = []
    loop = MagicMock()
    loop.time.side_effect = lambda: state["now"]

    async def sleep(seconds):
        sleeps.append(seconds)
        state["now"] += step

    return loop, sleep, sleeps


def _proc_entry(name):
    entry = MagicMock()
    entry.name = name
    entry.path = f"/proc/{name}"
    return entry


def _comm(text):
    handle = MagicMock()
    handle.__enter__.return_value.read.return_value = text
    handle.__exit__.return_value = False
    return handle


class TestIsVersityCreated(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_missing_credential_file(self):
        cases = (
            ("access", [False]),
            ("secret", [True, False]),
        )

        for name, exists in cases:
            with self.subTest(missing=name):
                isfile = AsyncMock(side_effect=exists)
                read = AsyncMock()

                with (
                    patch("app.runtime.versity.isfile", new=isfile),
                    patch("app.runtime.versity.read", new=read),
                ):
                    created = await is_versity_created(
                        "/secrets/access",
                        "/secrets/secret",
                    )

                self.assertIs(created, False)
                read.assert_not_awaited()

    async def test_rejects_unreadable_or_empty_credentials(self):
        cases = (
            ("unreadable", OSError("unread"), None),
            ("empty-access", b"", b"secret"),
            ("empty-secret", b"access", b""),
        )

        for name, access, secret in cases:
            with self.subTest(case=name):
                if isinstance(access, Exception):
                    read = AsyncMock(side_effect=access)
                else:
                    read = AsyncMock(side_effect=[access, secret])

                with (
                    patch(
                        "app.runtime.versity.isfile",
                        new=AsyncMock(return_value=True),
                    ),
                    patch("app.runtime.versity.read", new=read),
                ):
                    created = await is_versity_created(
                        "/secrets/access",
                        "/secrets/secret",
                    )

                self.assertIs(created, False)

    async def test_accepts_both_credentials(self):
        read = AsyncMock(side_effect=[b"access", b"secret"])

        with (
            patch(
                "app.runtime.versity.isfile",
                new=AsyncMock(return_value=True),
            ) as isfile,
            patch("app.runtime.versity.read", new=read),
        ):
            created = await is_versity_created(
                "/secrets/access",
                "/secrets/secret",
            )

        self.assertIs(created, True)
        self.assertEqual(
            [item.args[0] for item in isfile.await_args_list],
            ["/secrets/access", "/secrets/secret"],
        )
        self.assertEqual(
            [item.args[0] for item in read.await_args_list],
            ["/secrets/access", "/secrets/secret"],
        )


class TestVersityCreate(unittest.IsolatedAsyncioTestCase):
    async def test_stores_encrypted_credentials(self):
        generate = MagicMock(side_effect=["access-key", "secret-key"])
        encrypt = MagicMock(side_effect=[b"enc-access", b"enc-secret"])
        write = AsyncMock()

        with (
            patch(
                "app.runtime.versity.generate_random_string",
                new=generate,
            ),
            patch("app.runtime.versity.encrypt_passphrase", new=encrypt),
            patch("app.runtime.versity.write", new=write),
        ):
            result = await versity_create(
                "/secrets/access",
                "/secrets/secret",
                "пароль",
            )

        self.assertEqual(result, ("access-key", "secret-key"))
        self.assertEqual(
            generate.call_args_list,
            [
                call(VERSITY_ACCESS_KEY_LENGTH),
                call(VERSITY_SECRET_KEY_LENGTH),
            ],
        )
        self.assertEqual(
            encrypt.call_args_list,
            [
                call(b"access-key", "пароль".encode("utf-8")),
                call(b"secret-key", "пароль".encode("utf-8")),
            ],
        )
        self.assertEqual(
            write.await_args_list,
            [
                call("/secrets/access", b"enc-access"),
                call("/secrets/secret", b"enc-secret"),
            ],
        )

    async def test_propagates_write_failure(self):
        write = AsyncMock(side_effect=OSError("full"))

        with (
            patch(
                "app.runtime.versity.generate_random_string",
                side_effect=["access-key", "secret-key"],
            ),
            patch(
                "app.runtime.versity.encrypt_passphrase",
                side_effect=[b"enc-access", b"enc-secret"],
            ),
            patch("app.runtime.versity.write", new=write),
        ):
            with self.assertRaises(OSError):
                await versity_create(
                    "/secrets/access",
                    "/secrets/secret",
                    "passphrase",
                )

        write.assert_awaited_once_with("/secrets/access", b"enc-access")

    async def test_stored_credentials_round_trip(self):
        stored = {}

        async def write(path, data):
            stored[path] = data

        async def read(path):
            return stored[path]

        with (
            patch("app.runtime.versity.write", new=write),
            patch("app.runtime.versity.read", new=read),
        ):
            created = await versity_create(
                "/secrets/access",
                "/secrets/secret",
                "passphrase",
            )
            restored = await versity_read(
                "/secrets/access",
                "/secrets/secret",
                "passphrase",
            )

        self.assertEqual(restored, created)
        self.assertNotIn(created[0].encode("utf-8"), stored["/secrets/access"])
        self.assertNotIn(created[1].encode("utf-8"), stored["/secrets/secret"])


class TestVersityRead(unittest.IsolatedAsyncioTestCase):
    async def test_decrypts_stored_credentials(self):
        read = AsyncMock(side_effect=[b"enc-access", b"enc-secret"])
        decrypt = MagicMock(side_effect=[b"access-key", "ключ".encode()])

        with (
            patch("app.runtime.versity.read", new=read),
            patch("app.runtime.versity.decrypt_passphrase", new=decrypt),
        ):
            result = await versity_read(
                "/secrets/access",
                "/secrets/secret",
                "пароль",
            )

        self.assertEqual(result, ("access-key", "ключ"))
        self.assertEqual(
            read.await_args_list,
            [call("/secrets/access"), call("/secrets/secret")],
        )
        self.assertEqual(
            decrypt.call_args_list,
            [
                call(b"enc-access", "пароль".encode("utf-8")),
                call(b"enc-secret", "пароль".encode("utf-8")),
            ],
        )

    async def test_propagates_decrypt_failure(self):
        read = AsyncMock(side_effect=[b"plain-access", b"plain-secret"])

        with patch("app.runtime.versity.read", new=read):
            with self.assertRaises(ValueError):
                await versity_read(
                    "/secrets/access",
                    "/secrets/secret",
                    "passphrase",
                )

        read.assert_awaited_once_with("/secrets/access")


class TestVersityStart(unittest.IsolatedAsyncioTestCase):
    @contextmanager
    def _start(self, process=None, spawn_error=None, running=False, step=5):
        loop, sleep, sleeps = _clock(step)
        if isinstance(running, list):
            running_mock = AsyncMock(side_effect=running)
        else:
            running_mock = AsyncMock(return_value=running)

        if spawn_error is not None:
            spawn = AsyncMock(side_effect=spawn_error)
        else:
            spawn = AsyncMock(return_value=process)

        with (
            patch(
                "app.runtime.versity.get_config",
                return_value=_config(),
            ),
            patch(
                "app.runtime.versity.asyncio.create_subprocess_exec",
                new=spawn,
            ),
            patch(
                "app.runtime.versity.asyncio.get_running_loop",
                return_value=loop,
            ),
            patch("app.runtime.versity.asyncio.sleep", new=sleep),
            patch(
                "app.runtime.versity.is_versity_running",
                new=running_mock,
            ),
            patch("app.runtime.versity.log") as log,
        ):
            yield spawn, running_mock, sleeps, log

    async def test_starts_process_and_waits_until_running(self):
        process = MagicMock()
        process.returncode = None

        with self._start(
            process,
            running=[False, True],
            step=1,
        ) as (spawn, running, sleeps, log):
            await versity_start(**_START)

        env = spawn.await_args.kwargs["env"]
        self.assertIsNot(env, os.environ)
        self.assertEqual(env["ROOT_ACCESS_KEY"], "access-key")
        self.assertEqual(env["ROOT_SECRET_KEY"], "secret-key")
        spawn.assert_awaited_once_with(
            "versitygw",
            "--port",
            "127.0.0.1:9000",
            "--webui",
            "127.0.0.1:8080",
            "--webui-gateways",
            "http://127.0.0.1:9000",
            "--cors-allow-origin",
            "http://localhost:8080",
            "--iam-dir",
            "/mount/iam",
            "posix",
            "/mount/data",
            env=env,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=None,
        )
        self.assertEqual(running.await_count, 2)
        self.assertEqual(sleeps, [0.25])
        log.error.assert_not_called()

    async def test_spawn_failure_raises_internal_error(self):
        with self._start(spawn_error=OSError("missing")) as started:
            _, running, sleeps, log = started
            with self.assertRaises(InternalServerError):
                await versity_start(**_START)

        log.exception.assert_called_once_with("msg=versity_start_failed")
        running.assert_not_awaited()
        self.assertEqual(sleeps, [])

    async def test_exited_process_raises_internal_error(self):
        process = MagicMock()
        process.returncode = 3

        with self._start(process) as (_, running, sleeps, log):
            with self.assertRaises(InternalServerError):
                await versity_start(**_START)

        log.error.assert_called_once_with(
            "msg=versity_start_failed returncode=%s",
            3,
        )
        running.assert_not_awaited()
        self.assertEqual(sleeps, [])

    async def test_process_exit_after_poll_raises_internal_error(self):
        process = MagicMock()
        process.returncode = None

        async def exit_while_polling():
            process.returncode = 4
            return False

        with self._start(process, running=False) as (_, _, sleeps, log):
            with patch(
                "app.runtime.versity.is_versity_running",
                new=exit_while_polling,
            ):
                with self.assertRaises(InternalServerError):
                    await versity_start(**_START)

        log.error.assert_called_once_with(
            "msg=versity_start_failed returncode=%s",
            4,
        )
        self.assertEqual(sleeps, [0.25])

    async def test_timeout_without_process_raises_internal_error(self):
        process = MagicMock()
        process.returncode = None

        with self._start(process, running=False) as (_, running, sleeps, log):
            with self.assertRaises(InternalServerError):
                await versity_start(**_START)

        log.error.assert_called_once_with(
            "msg=versity_start_failed process_not_running",
        )
        self.assertEqual(running.await_count, 2)
        self.assertEqual(sleeps, [0.25])


class TestVersityPid(unittest.TestCase):
    def test_returns_matching_pid(self):
        entries = [
            _proc_entry("cpu"),
            _proc_entry("12"),
            _proc_entry("15"),
            _proc_entry("18"),
            _proc_entry("20"),
            _proc_entry("21"),
            _proc_entry("22"),
        ]

        def open_comm(path, mode, encoding):
            if path == "/proc/12/comm":
                raise FileNotFoundError(path)
            if path == "/proc/15/comm":
                raise PermissionError(path)
            if path == "/proc/18/comm":
                raise ProcessLookupError(path)
            if path == "/proc/20/comm":
                return _comm("python\n")
            if path == "/proc/21/comm":
                return _comm(" versitygw \n")
            raise AssertionError(path)

        with (
            patch(
                "app.runtime.versity.os.scandir",
                return_value=entries,
            ) as scandir,
            patch("app.runtime.versity.open", side_effect=open_comm) as opened,
        ):
            pid = _get_versity_pid()

        self.assertEqual(pid, 21)
        scandir.assert_called_once_with("/proc")
        opened.assert_any_call(
            "/proc/21/comm",
            "r",
            encoding="utf-8",
        )
        self.assertNotIn(
            call("/proc/22/comm", "r", encoding="utf-8"),
            opened.call_args_list,
        )

    def test_returns_none_when_process_is_absent(self):
        with (
            patch(
                "app.runtime.versity.os.scandir",
                return_value=[_proc_entry("cpu")],
            ),
            patch("app.runtime.versity.open") as opened,
        ):
            pid = _get_versity_pid()

        self.assertIsNone(pid)
        opened.assert_not_called()

    def test_propagates_unexpected_proc_error(self):
        with (
            patch(
                "app.runtime.versity.os.scandir",
                return_value=[_proc_entry("7")],
            ),
            patch(
                "app.runtime.versity.open",
                side_effect=OSError("proc"),
            ),
        ):
            with self.assertRaises(OSError):
                _get_versity_pid()


class TestIsVersityRunning(unittest.IsolatedAsyncioTestCase):
    async def test_reports_pid_presence(self):
        cases = ((21, True), (None, False))

        for pid, expected in cases:
            with self.subTest(pid=pid):
                with patch(
                    "app.runtime.versity._get_versity_pid",
                    return_value=pid,
                ) as get_pid:
                    running = await is_versity_running()

                self.assertIs(running, expected)
                get_pid.assert_called_once_with()


class TestVersityStop(unittest.IsolatedAsyncioTestCase):
    @contextmanager
    def _stop(self, pids, kill_error=None, step=5):
        loop, sleep, sleeps = _clock(step)
        get_pid = MagicMock(side_effect=pids)
        kill = MagicMock(side_effect=kill_error)

        with (
            patch(
                "app.runtime.versity.get_config",
                return_value=_config(),
            ),
            patch("app.runtime.versity._get_versity_pid", new=get_pid),
            patch("app.runtime.versity.os.kill", new=kill),
            patch(
                "app.runtime.versity.asyncio.get_running_loop",
                return_value=loop,
            ),
            patch("app.runtime.versity.asyncio.sleep", new=sleep),
            patch("app.runtime.versity.log") as log,
        ):
            yield get_pid, kill, sleeps, log

    async def test_returns_when_process_is_absent(self):
        with self._stop([None]) as (_, kill, sleeps, log):
            await versity_stop()

        kill.assert_not_called()
        self.assertEqual(sleeps, [])
        log.warning.assert_not_called()

    async def test_stops_after_sigterm(self):
        with self._stop([42, None]) as (_, kill, sleeps, log):
            await versity_stop()

        kill.assert_called_once_with(42, signal.SIGTERM)
        self.assertEqual(sleeps, [])
        log.warning.assert_not_called()

    async def test_returns_when_sigterm_misses_process(self):
        with self._stop(
            [42],
            kill_error=ProcessLookupError,
        ) as (_, kill, sleeps, _):
            await versity_stop()

        kill.assert_called_once_with(42, signal.SIGTERM)
        self.assertEqual(sleeps, [])

    async def test_kills_process_after_timeout(self):
        with self._stop([42, 42, None]) as (_, kill, sleeps, log):
            await versity_stop()

        self.assertEqual(
            kill.call_args_list,
            [call(42, signal.SIGTERM), call(42, signal.SIGKILL)],
        )
        self.assertEqual(sleeps, [0.25])
        log.warning.assert_called_once_with(
            "msg=versity_stop_timeout pid=%s",
            42,
        )
        log.error.assert_not_called()

    async def test_returns_when_sigkill_misses_process(self):
        with self._stop(
            [42, 42],
            kill_error=[None, ProcessLookupError],
        ) as (_, kill, sleeps, log):
            await versity_stop()

        self.assertEqual(kill.call_count, 2)
        self.assertEqual(sleeps, [0.25])
        log.error.assert_not_called()

    async def test_raises_when_process_survives_sigkill(self):
        with self._stop([42, 42, 42, 42]) as (_, kill, sleeps, log):
            with self.assertRaises(InternalServerError):
                await versity_stop()

        self.assertEqual(
            kill.call_args_list,
            [call(42, signal.SIGTERM), call(42, signal.SIGKILL)],
        )
        self.assertEqual(sleeps, [0.25, 0.25])
        log.error.assert_called_once_with(
            "msg=versity_kill_timeout pid=%s",
            42,
        )
