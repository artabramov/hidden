# app/services/metrics_retrieve.py
# SPDX-License-Identifier: GPL-3.0-only

import platform
import time

import psutil
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.lru import get_thumbnail_cache
from app.config import get_config
from app.repositories.file import get_filesize
from app.runtime.uptime import APPLICATION_START_TIME
from app.version import __version__


async def retrieve_metrics(session: AsyncSession) -> dict:
    config = get_config()

    disk = psutil.disk_usage("/")
    memory = psutil.virtual_memory()
    cpu_freq = psutil.cpu_freq(percpu=False)
    cpu_frequency_hertz = int(cpu_freq.current) * 1000000 if cpu_freq else None
    proc = psutil.Process()

    sqlite_version = (
        await session.execute(text("SELECT sqlite_version()"))
    ).scalar_one()

    sqlite_page_size = (
        await session.execute(text("PRAGMA page_size"))
    ).scalar_one()

    sqlite_page_count = (
        await session.execute(text("PRAGMA page_count"))
    ).scalar_one()

    sqlite_freelist_count = (
        await session.execute(text("PRAGMA freelist_count"))
    ).scalar_one()

    sqlite_journal_mode = (
        await session.execute(text("PRAGMA journal_mode"))
    ).scalar_one()

    sqlite_synchronous = (
        await session.execute(text("PRAGMA synchronous"))
    ).scalar_one()

    sqlite_busy_timeout = (
        await session.execute(text("PRAGMA busy_timeout"))
    ).scalar_one()

    sqlite_temp_store = (
        await session.execute(text("PRAGMA temp_store"))
    ).scalar_one()

    sqlite_used_size_bytes = (
        sqlite_page_count - sqlite_freelist_count
    ) * sqlite_page_size

    sqlite_freelist_size_bytes = sqlite_freelist_count * sqlite_page_size
    sqlite_size = await get_filesize(config.SQLITE_PATH)

    bind = session.bind
    sqlite_pool = getattr(bind, "pool", None)

    sqlite_pool_size = sqlite_pool.size() if sqlite_pool else None
    sqlite_pool_checked_in = (
        sqlite_pool.checkedin() if sqlite_pool else None
    )

    sqlite_pool_checked_out = (
        sqlite_pool.checkedout() if sqlite_pool else None
    )

    sqlite_pool_overflow = (
        sqlite_pool.overflow() if sqlite_pool else None
    )

    start_time = time.perf_counter()
    await session.execute(text("SELECT 1"))
    sqlite_latency = time.perf_counter() - start_time

    return {
        "app_version": __version__,
        "app_uptime_seconds": time.time() - APPLICATION_START_TIME,

        "os_name": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),

        "platform_alias": platform.platform(aliased=True),
        "platform_architecture": platform.architecture()[0],
        "platform_processor": platform.processor(),

        "disk_total_bytes": disk.total,
        "disk_used_bytes": disk.used,
        "disk_free_bytes": disk.free,

        "memory_total_bytes": memory.total,
        "memory_used_bytes": memory.used,
        "memory_free_bytes": memory.free,

        "cpu_core_count": psutil.cpu_count(logical=False),
        "cpu_frequency_hertz": cpu_frequency_hertz,
        "cpu_usage_percent": psutil.cpu_percent(),

        "process_pid": proc.pid,
        "process_memory_rss_bytes": proc.memory_info().rss,
        "process_cpu_percent": proc.cpu_percent(interval=0.0),
        "process_threads": proc.num_threads(),

        "python_compiler": platform.python_compiler(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),

        "sqlite_version": sqlite_version,
        "sqlite_latency_seconds": sqlite_latency,
        "sqlite_size_bytes": sqlite_size,
        "sqlite_page_size_bytes": sqlite_page_size,
        "sqlite_page_count": sqlite_page_count,
        "sqlite_freelist_count": sqlite_freelist_count,
        "sqlite_freelist_size_bytes": sqlite_freelist_size_bytes,
        "sqlite_used_size_bytes": sqlite_used_size_bytes,
        "sqlite_journal_mode": sqlite_journal_mode,
        "sqlite_synchronous": sqlite_synchronous,
        "sqlite_busy_timeout_milliseconds": sqlite_busy_timeout,
        "sqlite_temp_store": sqlite_temp_store,
        "sqlite_pool_size": sqlite_pool_size,
        "sqlite_pool_checked_in": sqlite_pool_checked_in,
        "sqlite_pool_checked_out": sqlite_pool_checked_out,
        "sqlite_pool_overflow": sqlite_pool_overflow,

        "lru_cache_entry_count": get_thumbnail_cache().count,
        "lru_cache_current_bytes": get_thumbnail_cache().current_bytes,
        "lru_cache_max_bytes": get_thumbnail_cache().max_bytes,
    }
