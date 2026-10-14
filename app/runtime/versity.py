# app/runtime/versity.py
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
import os
import signal

from app.config import get_config
from app.constants import (
    VERSITY_ACCESS_KEY_LENGTH,
    VERSITY_SECRET_KEY_LENGTH,
)
from app.errors import InternalServerError
from app.io import isfile, read, write
from app.security.randoms import generate_random_string

log = logging.getLogger(__name__)


async def is_versity_created(
    access_key_path: str,
    secret_key_path: str,
) -> bool:
    """
    Return whether VersityGW credentials have been created by verifying
    that both credential files exist, can be read, and contain non-empty
    values.
    """
    if not await isfile(access_key_path):
        return False

    if not await isfile(secret_key_path):
        return False

    try:
        access_key = await read(access_key_path)
        secret_key = await read(secret_key_path)
    except Exception:
        return False

    return bool(access_key and secret_key)


async def versity_create(
    access_key_path: str,
    secret_key_path: str,
) -> tuple[str, str]:
    """
    Generate random VersityGW root credentials, store them in the
    specified credential files, and return the generated values.
    """
    access_key = generate_random_string(VERSITY_ACCESS_KEY_LENGTH)
    secret_key = generate_random_string(VERSITY_SECRET_KEY_LENGTH)

    await write(
        access_key_path,
        access_key.encode("utf-8"),
    )

    await write(
        secret_key_path,
        secret_key.encode("utf-8"),
    )

    return access_key, secret_key


async def versity_start(
    host: str,
    port: int,
    webgui_host: str,
    webgui_port: int,
    webgui_gateway: str,
    webgui_cors_allow_origin: str,
    data_path: str,
    iam_path: str,
    access_key: str,
    secret_key: str,
) -> None:
    """
    Start VersityGW with the provided root credentials, POSIX storage,
    and IAM directories. Poll until the process is observed running or
    the configured startup timeout expires.
    """
    config = get_config()

    env = os.environ.copy()
    env["ROOT_ACCESS_KEY"] = access_key
    env["ROOT_SECRET_KEY"] = secret_key

    try:
        process = await asyncio.create_subprocess_exec(
            "versitygw",
            "--port",
            f"{host}:{port}",
            "--webui",
            f"{webgui_host}:{webgui_port}",
            "--webui-gateways",
            webgui_gateway,
            "--cors-allow-origin",
            webgui_cors_allow_origin,
            "--iam-dir",
            iam_path,
            "posix",
            data_path,
            env=env,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception:
        log.exception("msg=versity_start_failed")
        raise InternalServerError

    loop = asyncio.get_running_loop()
    deadline = loop.time() + config.VERSITY_START_TIMEOUT_SECONDS

    while loop.time() < deadline:
        if process.returncode is not None:
            stderr = await process.stderr.read()
            error = stderr.decode(
                encoding="utf-8",
                errors="replace",
            ).strip() or "unknown error"

            log.error(
                "msg=versity_start_failed returncode=%s error=%s",
                process.returncode,
                error,
            )
            raise InternalServerError

        if await is_versity_running():
            return

        await asyncio.sleep(config.VERSITY_POLL_INTERVAL_SECONDS)

    if process.returncode is not None:
        stderr = await process.stderr.read()
        error = stderr.decode(
            encoding="utf-8",
            errors="replace",
        ).strip() or "unknown error"

        log.error(
            "msg=versity_start_failed returncode=%s error=%s",
            process.returncode,
            error,
        )
        raise InternalServerError

    if not await is_versity_running():
        log.error("msg=versity_start_failed process_not_running")
        raise InternalServerError


def _get_versity_pid() -> int | None:
    """
    Return the PID of the running VersityGW process by scanning /proc
    for a process whose command name is "versitygw". Return None if no
    matching process is found.
    """
    for entry in os.scandir("/proc"):
        if not entry.name.isdigit():
            continue

        try:
            with open(
                os.path.join(entry.path, "comm"),
                "r",
                encoding="utf-8",
            ) as file:
                if file.read().strip() == "versitygw":
                    return int(entry.name)
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue

    return None


async def is_versity_running() -> bool:
    """
    Check whether a VersityGW process is currently running.
    """
    return _get_versity_pid() is not None


async def versity_stop() -> None:
    """
    Stop the running VersityGW process by first requesting graceful
    termination with SIGTERM. If the process remains running after the
    configured timeout, force termination with SIGKILL and raise an
    error if the process still does not exit.
    """
    config = get_config()

    pid = _get_versity_pid()
    if pid is None:
        return

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return

    loop = asyncio.get_running_loop()
    deadline = loop.time() + config.VERSITY_STOP_TIMEOUT_SECONDS

    while loop.time() < deadline:
        if _get_versity_pid() is None:
            return

        await asyncio.sleep(config.VERSITY_POLL_INTERVAL_SECONDS)

    log.warning("msg=versity_stop_timeout pid=%s", pid)

    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return

    deadline = loop.time() + config.VERSITY_STOP_TIMEOUT_SECONDS

    while loop.time() < deadline:
        if _get_versity_pid() is None:
            return

        await asyncio.sleep(config.VERSITY_POLL_INTERVAL_SECONDS)

    log.error("msg=versity_kill_timeout pid=%s", pid)
    raise InternalServerError
