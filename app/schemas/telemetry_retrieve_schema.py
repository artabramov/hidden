"""
The module defines Pydantic schema for retrieving telemetry.
"""

from pydantic import BaseModel


class TelemetryRetrieveResponse(BaseModel):
    """
    Response schema for retrieving telemetry data. Contains information
    operating system, database, cache, platform, Python environment,
    and resource usage metrics.
    """
    app_version: str
    app_serial: str
    app_uptime: int

    unix_timestamp: int
    timezone_name: str
    timezone_offset: int

    postgres_version: str
    postgres_size: int

    redis_version: str
    redis_mode: str
    redis_memory: int

    platform_architecture: str
    platform_machine: str
    platform_node: str
    platform_alias: str
    platform_processor: str

    python_buildno: str
    python_builddate: str
    python_compiler: str
    python_branch: str
    python_implementation: str
    python_revision: str
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
