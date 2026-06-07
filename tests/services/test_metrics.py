# tests/services/test_metrics_retrieve.py
# SPDX-License-Identifier: SSPL-1.0

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.metrics_retrieve import retrieve_metrics


class TestRetrieveMetrics(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        _platform_patches = {
            "app.services.metrics_retrieve.platform.system": "Linux",
            "app.services.metrics_retrieve.platform.release": "6.1",
            "app.services.metrics_retrieve.platform.version": "test-version",
            "app.services.metrics_retrieve.platform.platform": "Linux-test",
            "app.services.metrics_retrieve.platform.architecture": ("64bit", ""),  # noqa: E501
            "app.services.metrics_retrieve.platform.processor": "x86_64",
            "app.services.metrics_retrieve.platform.python_compiler": "GCC",
            "app.services.metrics_retrieve.platform.python_implementation": "CPython",  # noqa: E501
            "app.services.metrics_retrieve.platform.python_version": "3.12.0",
        }
        for target, value in _platform_patches.items():
            p = patch(target, return_value=value)
            self.addCleanup(p.stop)
            p.start()

    def _result(self, value):
        result = MagicMock()
        result.scalar_one.return_value = value
        return result

    def _config(self):
        config = MagicMock()
        config.SQLITE_PATH = "/fake/db.sqlite3"
        return config

    async def test_returns_metrics(self):
        session = AsyncMock()

        pool = MagicMock()
        pool.size.return_value = 5
        pool.checkedin.return_value = 3
        pool.checkedout.return_value = 2
        pool.overflow.return_value = 0

        bind = MagicMock()
        bind.pool = pool
        session.bind = bind

        session.execute.side_effect = [
            self._result("3.46.1"),
            self._result(4096),
            self._result(100),
            self._result(10),
            self._result("wal"),
            self._result(1),
            self._result(5000),
            self._result(2),
            self._result(1),
        ]

        disk = MagicMock()
        disk.total = 1000
        disk.used = 400
        disk.free = 600

        memory = MagicMock()
        memory.total = 2000
        memory.used = 700
        memory.free = 1300

        cpu_freq = MagicMock()
        cpu_freq.current = 2400

        proc_memory = MagicMock()
        proc_memory.rss = 123456

        proc = MagicMock()
        proc.pid = 777
        proc.memory_info.return_value = proc_memory
        proc.cpu_percent.return_value = 12.5
        proc.num_threads.return_value = 8

        cache_mock = MagicMock()
        cache_mock.count = 12
        cache_mock.current_bytes = 204800
        cache_mock.max_bytes = 52428800

        with (
            patch(
                "app.services.metrics_retrieve.get_config",
                return_value=self._config(),
            ) as get_config_mock,
            patch(
                "app.services.metrics_retrieve.get_filesize",
                new=AsyncMock(return_value=987654),
            ) as get_filesize_mock,
            patch(
                "app.services.metrics_retrieve.get_thumbnail_cache",
                return_value=cache_mock,
            ) as get_thumbnail_cache_mock,
            patch(
                "app.services.metrics_retrieve.APPLICATION_START_TIME",
                1000.0,
            ),
            patch(
                "app.services.metrics_retrieve.time.time",
                return_value=1060.0,
            ),
            patch(
                "app.services.metrics_retrieve.time.perf_counter",
                side_effect=[10.0, 10.25],
            ),
            patch(
                "app.services.metrics_retrieve.psutil.disk_usage",
                return_value=disk,
            ) as disk_usage_mock,
            patch(
                "app.services.metrics_retrieve.psutil.virtual_memory",
                return_value=memory,
            ) as virtual_memory_mock,
            patch(
                "app.services.metrics_retrieve.psutil.cpu_freq",
                return_value=cpu_freq,
            ) as cpu_freq_mock,
            patch(
                "app.services.metrics_retrieve.psutil.cpu_count",
                return_value=4,
            ) as cpu_count_mock,
            patch(
                "app.services.metrics_retrieve.psutil.cpu_percent",
                return_value=33.3,
            ) as cpu_percent_mock,
            patch(
                "app.services.metrics_retrieve.psutil.Process",
                return_value=proc,
            ) as process_mock,
        ):
            out = await retrieve_metrics(session)

        get_config_mock.assert_called_once()
        get_thumbnail_cache_mock.assert_called()
        disk_usage_mock.assert_called_once_with("/")
        virtual_memory_mock.assert_called_once()
        cpu_freq_mock.assert_called_once_with(percpu=False)
        cpu_count_mock.assert_called_once_with(logical=False)
        cpu_percent_mock.assert_called_once()
        process_mock.assert_called_once()

        get_filesize_mock.assert_awaited_once_with("/fake/db.sqlite3")

        proc.memory_info.assert_called_once()
        proc.cpu_percent.assert_called_once_with(interval=0.0)
        proc.num_threads.assert_called_once()

        self.assertEqual(
            [str(item.args[0]) for item in session.execute.await_args_list],
            [
                "SELECT sqlite_version()",
                "PRAGMA page_size",
                "PRAGMA page_count",
                "PRAGMA freelist_count",
                "PRAGMA journal_mode",
                "PRAGMA synchronous",
                "PRAGMA busy_timeout",
                "PRAGMA temp_store",
                "SELECT 1",
            ],
        )

        self.assertEqual(out["app_uptime_seconds"], 60.0)
        self.assertEqual(out["sqlite_latency_seconds"], 0.25)

        self.assertEqual(out["sqlite_version"], "3.46.1")
        self.assertEqual(out["sqlite_size_bytes"], 987654)
        self.assertEqual(out["sqlite_page_size_bytes"], 4096)
        self.assertEqual(out["sqlite_page_count"], 100)
        self.assertEqual(out["sqlite_freelist_count"], 10)
        self.assertEqual(out["sqlite_freelist_size_bytes"], 40960)
        self.assertEqual(out["sqlite_used_size_bytes"], 368640)
        self.assertEqual(out["sqlite_journal_mode"], "wal")
        self.assertEqual(out["sqlite_synchronous"], 1)
        self.assertEqual(out["sqlite_busy_timeout_milliseconds"], 5000)
        self.assertEqual(out["sqlite_temp_store"], 2)

        self.assertEqual(out["sqlite_pool_size"], 5)
        self.assertEqual(out["sqlite_pool_checked_in"], 3)
        self.assertEqual(out["sqlite_pool_checked_out"], 2)
        self.assertEqual(out["sqlite_pool_overflow"], 0)

        self.assertEqual(out["disk_total_bytes"], 1000)
        self.assertEqual(out["disk_used_bytes"], 400)
        self.assertEqual(out["disk_free_bytes"], 600)

        self.assertEqual(out["memory_total_bytes"], 2000)
        self.assertEqual(out["memory_used_bytes"], 700)
        self.assertEqual(out["memory_free_bytes"], 1300)

        self.assertEqual(out["cpu_core_count"], 4)
        self.assertEqual(out["cpu_frequency_hertz"], 2400000000)
        self.assertEqual(out["cpu_usage_percent"], 33.3)

        self.assertEqual(out["process_pid"], 777)
        self.assertEqual(out["process_memory_rss_bytes"], 123456)
        self.assertEqual(out["process_cpu_percent"], 12.5)
        self.assertEqual(out["process_threads"], 8)

        self.assertEqual(out["os_name"], "Linux")
        self.assertEqual(out["os_release"], "6.1")
        self.assertEqual(out["os_version"], "test-version")
        self.assertEqual(out["platform_alias"], "Linux-test")
        self.assertEqual(out["platform_architecture"], "64bit")
        self.assertEqual(out["platform_processor"], "x86_64")
        self.assertEqual(out["python_compiler"], "GCC")
        self.assertEqual(out["python_implementation"], "CPython")
        self.assertEqual(out["python_version"], "3.12.0")

        self.assertEqual(out["lru_cache_entry_count"], 12)
        self.assertEqual(out["lru_cache_current_bytes"], 204800)
        self.assertEqual(out["lru_cache_max_bytes"], 52428800)

    async def test_returns_none_for_pool_metrics_when_pool_is_missing(self):
        session = AsyncMock()

        bind = MagicMock()
        del bind.pool
        session.bind = bind

        session.execute.side_effect = [
            self._result("3.46.1"),
            self._result(4096),
            self._result(100),
            self._result(10),
            self._result("wal"),
            self._result(1),
            self._result(5000),
            self._result(2),
            self._result(1),
        ]

        disk = MagicMock(total=1000, used=400, free=600)
        memory = MagicMock(total=2000, used=700, free=1300)

        proc_memory = MagicMock(rss=123456)
        proc = MagicMock()
        proc.pid = 777
        proc.memory_info.return_value = proc_memory
        proc.cpu_percent.return_value = 12.5
        proc.num_threads.return_value = 8

        with (
            patch(
                "app.services.metrics_retrieve.get_config",
                return_value=self._config(),
            ),
            patch(
                "app.services.metrics_retrieve.get_filesize",
                new=AsyncMock(return_value=987654),
            ),
            patch(
                "app.services.metrics_retrieve.get_thumbnail_cache",
                return_value=MagicMock(count=0, current_bytes=0, max_bytes=0),
            ),
            patch(
                "app.services.metrics_retrieve.APPLICATION_START_TIME",
                1000.0,
            ),
            patch(
                "app.services.metrics_retrieve.time.time",
                return_value=1060.0,
            ),
            patch(
                "app.services.metrics_retrieve.time.perf_counter",
                side_effect=[10.0, 10.25],
            ),
            patch(
                "app.services.metrics_retrieve.psutil.disk_usage",
                return_value=disk,
            ),
            patch(
                "app.services.metrics_retrieve.psutil.virtual_memory",
                return_value=memory,
            ),
            patch(
                "app.services.metrics_retrieve.psutil.cpu_freq",
                return_value=None,
            ),
            patch(
                "app.services.metrics_retrieve.psutil.cpu_count",
                return_value=4,
            ),
            patch(
                "app.services.metrics_retrieve.psutil.cpu_percent",
                return_value=33.3,
            ),
            patch(
                "app.services.metrics_retrieve.psutil.Process",
                return_value=proc,
            ),
        ):
            out = await retrieve_metrics(session)

        self.assertIsNone(out["cpu_frequency_hertz"])
        self.assertIsNone(out["sqlite_pool_size"])
        self.assertIsNone(out["sqlite_pool_checked_in"])
        self.assertIsNone(out["sqlite_pool_checked_out"])
        self.assertIsNone(out["sqlite_pool_overflow"])
