"""
This module defines Pydantic schemas for retrieving system and
environment telemetry data. The schemas include details such as Unix
timestamp, time zone, system uptime, version, PostgreSQL version and
database size, platform architecture, Python environment details,
operating system information, and resource usage metrics such as disk,
memory, and CPU statistics.
"""

from pydantic import BaseModel


class TelemetryRetrieveResponse(BaseModel):
    """
    Schema for the response when retrieving system and environment
    telemetry data. Includes information such as the current Unix
    timestamp, time zone details, system uptime, PostgreSQL information,
    platform specifics, Python environment, operating system details,
    and resource usage metrics (disk, memory, and CPU).
    """
    unix_timestamp: int
    timezone_name: str
    timezone_offset: int

    hidden_uptime: int
    hidden_version: str
    hidden_serial: str

    postgres_version: str
    postgres_database_size: str
    postgres_start_time: str

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
