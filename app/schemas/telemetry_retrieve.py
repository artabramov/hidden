"""Pydantic schemas for telemetry retrieve."""

from pydantic import BaseModel


class TelemetryRetrieveResponse(BaseModel):
    """
    Response schema for retrieving telemetry data. Contains information
    operating system, database, cache, platform, Python environment,
    and resource usage metrics.
    """
    app_version: str
    unix_timestamp: int
    timezone_name: str
    timezone_offset: int
    sqlite_version: str
    sqlite_size: int
    redis_version: str
    redis_memory: int
    platform_alias: str
    platform_architecture: str
    platform_processor: str
    python_compiler: str
    python_implementation: str
    python_version: str
    os_name: str
    os_release: str
    os_version: str
    disk_total: int
    disk_used: int
    disk_free: int
    memory_total: int
    memory_used: int
    memory_free: int
    cpu_core_count: int
    cpu_frequency: int
    cpu_usage_percent: float
