#!/bin/sh
set -eu
umask 077

mkdir -p /etc/hidden
if [ ! -f /etc/hidden/.env ]; then
  cp /opt/hidden/.env.example /etc/hidden/.env
  chmod 600 /etc/hidden/.env
  echo "[hidden] created .env"
fi

set -a
. /etc/hidden/.env
set +a

# NOTE (ADR-09): Watchdog runs as a background sleep-loop.
# It periodically validates runtime state and unmounts the gocryptfs
# mountpoint when required (e.g. missing passphrase or no running
# application process).

(
  while true; do
    sleep "$GOCRYPTFS_WATCHDOG_INTERVAL_SECONDS"
    cd /opt/hidden && python3 -m app.runtime.watchdog
  done
) >> /proc/1/fd/1 2>> /proc/1/fd/2 &

# Select uvicorn binary
if [ -x /opt/hidden/.venv/bin/uvicorn ]; then
  UVICORN_BIN=/opt/hidden/.venv/bin/uvicorn
else
  UVICORN_BIN=uvicorn
fi

# NOTE (ADR-12): Application runs with a single Uvicorn worker.
# This is not a tuning choice but a consequence of the encryption stack:
# gocryptfs is hostile to server-class DBs on FUSE, which forces SQLite,
# which is itself single-writer. Multiple workers therefore provide
# near-zero throughput gain on writes and would actively conflict
# with three in-process gates:
# 1. Filesystem locks in app/locks.py are per-process structures;
#    cross-process serialization would require file/IPC-based locks
#    and a redesign.
# 2. The SQLite WAL writer is single-writer by design; write
#    transactions serialize on the same lock regardless of worker
#    count, so adding workers buys no write throughput, only
#    contention.
# 3. Master-password attempt spacing uses in-process asyncio state;
#    splitting that gate across processes would require a file or
#    IPC like the watchdog heartbeat.


# Replace the shell with uvicorn. When the container is started with
# --init, docker-init remains PID 1 and forwards signals to uvicorn.
exec "$UVICORN_BIN" app.main:app \
  --host "$UVICORN_HOST" \
  --port "$UVICORN_PORT" \
  --workers 1
