#!/bin/sh
set -eu
umask 077

mkdir -p /etc/hidden
if [ ! -f /etc/hidden/.env ]; then
  cp /opt/hidden/.env /etc/hidden/.env
  chmod 600 /etc/hidden/.env
fi

set -a
. /etc/hidden/.env
set +a

mkdir -p \
  "$INSTALL_CIPHERDIR" \
  "$INSTALL_MOUNTPOINT"

(
  while true; do
    sleep "$WATCHDOG_INTERVAL_SECONDS"
    cd "$INSTALL_SOURCE_CODE" && python3 -m app.runtime.watchdog
  done
) >> /proc/1/fd/1 2>> /proc/1/fd/2 &

exec uvicorn app.main:app \
  --host "$UVICORN_HOST" \
  --port "$UVICORN_PORT" \
  --workers 1
